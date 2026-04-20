from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db, SessionLocal
from app.services.export import export_products_excel, export_price_modifications_excel, get_master_filename
from io import BytesIO
from typing import List, Optional
from fastapi import Query
from datetime import datetime, timezone
import uuid
import json
import logging
from app.redis_client import redis_client
from app.utils.sse import event_generator, format_sse_event
from app.utils.s3_upload import upload_export, generate_presigned_url
from app.models.client_profiles import ClientProfile
from app.models.client_contracts import ClientContracts
from app.models.jobs import Job
from app.models.modification_action import ModificationAction
from app.models.product_master import ProductMaster



logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["Export"])

EXPORT_TASK_TTL = 60 * 60 * 24

def _export_status_key(task_id: str) -> str:
    return f"export:task:{task_id}"

def _set_export_status(task_id: str, payload: dict) -> None:
    redis_client.setex(_export_status_key(task_id), EXPORT_TASK_TTL, json.dumps(payload))

def _get_export_status(task_id: str) -> dict | None:
    payload = redis_client.get(_export_status_key(task_id))
    return json.loads(payload) if payload else None

def _get_modifications_cache_key(job_id: Optional[int], types: Optional[List[str]]) -> str:
    sorted_types = ",".join(sorted(types)) if types else "all"
    return f"export:cache:modifications:{job_id}:{sorted_types}"

def _get_products_cache_key(client_id: Optional[int]) -> str:
    id_str = client_id if client_id is not None else "all"
    return f"export:cache:products:{id_str}"


@router.get("/events/{task_id}")
async def get_export_events(task_id: str, current_user=Depends(get_current_user)):
    channel = f"events:export:{task_id}"
    
    # Get current status to send initial state
    status = _get_export_status(task_id)
    
    async def sse_wrapper():
        # 1. Send current status if available
        if status:
            yield f"data: {format_sse_event(status)}\n\n"
            # If already finished, we don't need to listen to the channel
            if status.get("status") in ["completed", "failed"]:
                return

        # 2. Otherwise listen to the channel for updates
        async for event in event_generator(channel):
            # Skip the generic 'connected' message from event_generator 
            # as we already sent the status or want to keep it clean
            if 'status": "connected' in event:
                continue
            yield event


    return StreamingResponse(
        sse_wrapper(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/download/{task_id}")
def download_export(task_id: str, current_user=Depends(get_current_user)):
    status = _get_export_status(task_id)
    if not status or status.get("status") != "completed":
        raise HTTPException(404, "Export not found or still processing")

    s3_key = status.get("s3_key")
    filename = status.get("filename")
    url = generate_presigned_url(s3_key, filename=filename)
    return {"url": url, "filename": filename}


@router.post("/price-modifications")
def start_export_price_modifications(
    background_tasks: BackgroundTasks,
    client_id: Optional[int] = Query(None),
    job_id: Optional[int] = Query(None),
    types: Optional[List[str]] = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check cache
    cache_key = _get_modifications_cache_key(job_id, types)
    cached_task_id = redis_client.get(cache_key)
    if cached_task_id:
        if isinstance(cached_task_id, bytes):
            cached_task_id = cached_task_id.decode("utf-8")
        status = _get_export_status(cached_task_id)
        if status and status.get("status") == "completed":
            return {"task_id": cached_task_id}

    # Verify data exists before starting background task
    # Use .first() on ID for faster existence check than .count()
    exists_query = db.query(ModificationAction.action_id)
    if types:
        exists_query = exists_query.filter(ModificationAction.action_type.in_(types))
    if client_id:
        exists_query = exists_query.filter(ModificationAction.client_id == client_id)
    if job_id:
        exists_query = exists_query.filter(ModificationAction.job_id == job_id)
    
    if not exists_query.first():
        raise HTTPException(status_code=404, detail="No price modifications found for the specified filters.")


    task_id = str(uuid.uuid4())
    _set_export_status(task_id, {"status": "processing", "percent": 0, "message": "Starting export..."})
    
    background_tasks.add_task(
        run_export_modifications_background,
        task_id,
        client_id,
        job_id,
        types,
        current_user["email"]
    )
    return {"task_id": task_id}


@router.post("/")
def start_export_products(
    background_tasks: BackgroundTasks,
    client_id: Optional[int] = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if client_id is None:
        raise HTTPException(status_code=400, detail="Client ID is required for product export.")

    # Check cache
    cache_key = _get_products_cache_key(client_id)
    cached_task_id = redis_client.get(cache_key)
    if cached_task_id:
        if isinstance(cached_task_id, bytes):
            cached_task_id = cached_task_id.decode("utf-8")
        status = _get_export_status(cached_task_id)
        if status and status.get("status") == "completed":
            return {"task_id": cached_task_id}

    # Verify products exist before starting background task
    # Use .first() on ID for faster existence check than .count()
    product_exists = db.query(ProductMaster.product_id).filter(
        ProductMaster.client_id == client_id,
        ProductMaster.is_deleted.is_(False)
    ).first()
    
    if not product_exists:
        raise HTTPException(status_code=404, detail="No products found for this client to export.")


    task_id = str(uuid.uuid4())
    _set_export_status(task_id, {"status": "processing", "percent": 0, "message": "Starting export..."})
    
    background_tasks.add_task(
        run_export_products_background,
        task_id,
        client_id,
        current_user["email"]
    )
    return {"task_id": task_id}


def run_export_modifications_background(task_id, client_id, job_id, types, user_email):
    db = SessionLocal()
    try:
        def notify(message, percent):
            payload = {"status": "processing", "percent": percent, "message": message}
            _set_export_status(task_id, payload)
            redis_client.publish(f"events:export:{task_id}", format_sse_event(payload))

        # Count total rows for progress tracking
        total_query = db.query(ModificationAction).filter(ModificationAction.action_type.in_(types if types else []))
        if client_id: total_query = total_query.filter(ModificationAction.client_id == client_id)
        if job_id: total_query = total_query.filter(ModificationAction.job_id == job_id)
        total_rows = total_query.count()

        def progress_callback(processed):
            if total_rows > 0:
                # Map generating phase to 20% - 70%
                percent = 20 + int(50 * (processed / total_rows))
                notify(f"Generating Excel (Row {processed:,} / {total_rows:,})...", percent)

        notify("Preparing data...", 10)
        wb = export_price_modifications_excel(db, client_id, job_id, types, progress_callback=progress_callback)
        
        notify("Saving file...", 70)
        stream = BytesIO()
        wb.save(stream)

        stream.seek(0)
        
        # Generate descriptive filename
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filename = f"modifications_{date_str}.xlsx"
        
        try:
            # If client_id is missing but job_id is present, fetch client_id from job
            if not client_id and job_id:
                job = db.query(Job).filter_by(job_id=job_id).first()
                if job:
                    client_id = job.client_id

            client = db.query(ClientProfile).filter_by(client_id=client_id).first()
            if client:
                clean_name = "".join(c if c.isalnum() else "_" for c in client.company_name)
                contract = db.query(ClientContracts).filter_by(client_id=client_id).first()
                contract_num = contract.contract_number if contract else "NoContract"
                filename = f"{clean_name}_{contract_num}_modifications_{date_str}.xlsx"
        except Exception as e:
            logger.error(f"Error generating descriptive filename: {e}")


        s3_key = upload_export(stream, filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        final_payload = {
            "status": "completed", 
            "percent": 100, 
            "message": "Export ready", 
            "s3_key": s3_key,
            "filename": filename
        }
        _set_export_status(task_id, final_payload)
        redis_client.publish(f"events:export:{task_id}", format_sse_event(final_payload))

        # Update cache
        cache_key = _get_modifications_cache_key(job_id, types)
        redis_client.setex(cache_key, EXPORT_TASK_TTL, task_id)


    except Exception as e:
        error_payload = {"status": "failed", "message": str(e)}
        _set_export_status(task_id, error_payload)
        redis_client.publish(f"events:export:{task_id}", format_sse_event(error_payload))
    finally:
        db.close()

def run_export_products_background(task_id, client_id, user_email):
    db = SessionLocal()
    try:
        def notify(message, percent):
            payload = {"status": "processing", "percent": percent, "message": message}
            _set_export_status(task_id, payload)
            redis_client.publish(f"events:export:{task_id}", format_sse_event(payload))

        # Count total rows for progress tracking
        total_query = db.query(ProductMaster).filter(ProductMaster.is_deleted.is_(False))
        if client_id is not None:
            total_query = total_query.filter(ProductMaster.client_id == client_id)
        total_rows = total_query.count()

        def progress_callback(processed):
            if total_rows > 0:
                # Map generating phase to 20% - 70%
                percent = 20 + int(50 * (processed / total_rows))
                notify(f"Generating Excel (Row {processed:,} / {total_rows:,})...", percent)

        notify("Preparing data...", 10)
        wb = export_products_excel(db, client_id, progress_callback=progress_callback)
        
        notify("Saving file...", 70)
        stream = BytesIO()
        wb.save(stream)

        stream.seek(0)
        
        filename = get_master_filename(db, client_id)
        
        s3_key = upload_export(stream, filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        final_payload = {
            "status": "completed", 
            "percent": 100, 
            "message": "Export ready", 
            "s3_key": s3_key,
            "filename": filename
        }
        _set_export_status(task_id, final_payload)
        redis_client.publish(f"events:export:{task_id}", format_sse_event(final_payload))

        # Update cache
        cache_key = _get_products_cache_key(client_id)
        redis_client.setex(cache_key, EXPORT_TASK_TTL, task_id)


    except Exception as e:

        error_payload = {"status": "failed", "message": str(e)}
        _set_export_status(task_id, error_payload)
        redis_client.publish(f"events:export:{task_id}", format_sse_event(error_payload))
    finally:
        db.close()

