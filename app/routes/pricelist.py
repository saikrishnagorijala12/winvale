import json
import io
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from redis.exceptions import RedisError
from fastapi.responses import StreamingResponse

from app.database import get_db, SessionLocal
from app.auth.dependencies import get_current_user
from app.services.pricelist import upload_cpl_service
from app.models.product_master import ProductMaster
from app.utils.cache import invalidate_keys, invalidate_pattern
from app.redis_client import redis_client
from app.utils.sse import event_generator, format_sse_event

router = APIRouter(prefix="/cpl", tags=["CPL"])

ANALYSIS_STATUS_TTL = 60 * 60 * 24

class FileWrapper:
    """
    Small wrapper to mimic UploadFile behavior for background tasks
    after the original request has finished and files are closed.
    """
    def __init__(self, filename: str, content: bytes, content_type: str, size: int):
        self.filename = filename
        self._content = content
        self.content_type = content_type
        self.size = size

    @property
    def file(self):
        return io.BytesIO(self._content)

def _analysis_status_key(client_id: int) -> str:
    return f"analysis:client:{client_id}:latest"

def _set_analysis_status(client_id: int, payload: dict) -> None:
    try:
        redis_client.setex(
            _analysis_status_key(client_id),
            ANALYSIS_STATUS_TTL,
            json.dumps(payload),
        )
    except RedisError:
        pass

def _get_analysis_status(client_id: int) -> dict | None:
    try:
        payload = redis_client.get(_analysis_status_key(client_id))
        return json.loads(payload) if payload else None
    except RedisError:
        return None

def _get_product_upload_payload(client_id: int) -> dict | None:
    try:
        payload = redis_client.get(f"uploads:client:{client_id}:latest")
    except RedisError:
        return None

    if not payload:
        return None

    try:
        parsed_payload = json.loads(payload)
    except (TypeError, json.JSONDecodeError):
        return None

    return parsed_payload if isinstance(parsed_payload, dict) else None

@router.get("/{client_id}/events")
async def get_analysis_events(
    client_id: int,
    current_user=Depends(get_current_user),
):
    """
    SSE endpoint for real-time analysis progress updates.
    """
    channel = f"events:analysis:{client_id}"
    return StreamingResponse(
        event_generator(channel),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@router.post("/{client_id}")
async def upload_cpl(
    client_id: int,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not files or len(files) == 0:
        raise HTTPException(400, "No files uploaded")

    for file in files:
        if not file.filename.lower().endswith((".xlsx", ".xls")):
            raise HTTPException(400, f"Only Excel (.xlsx, .xls) files allowed. Invalid file: {file.filename}")

    product_upload = _get_product_upload_payload(client_id)
    product_upload_status = product_upload.get("status") if product_upload else None

    if product_upload_status == "processing":
        raise HTTPException(
            status_code=409,
            detail="Product upload is still in progress for this client. Please wait until it completes before uploading CPL.",
        )

    if product_upload_status == "failed":
        raise HTTPException(
            status_code=409,
            detail="The latest product upload for this client failed. Re-upload the products successfully before uploading CPL.",
        )

    if product_upload_status in {None, "idle"}:
        has_products = db.query(ProductMaster.product_id).filter(
            ProductMaster.client_id == client_id,
            ProductMaster.is_deleted.is_(False)
        ).first() is not None

        if not has_products:
            raise HTTPException(
                status_code=409,
                detail="Upload products for this client before uploading CPL.",
            )
        else:
            product_upload_status = "completed"

    if product_upload_status != "completed":
        raise HTTPException(
            status_code=409,
            detail=f"Product upload must be completed before uploading CPL. Current status: {product_upload_status}.",
        )

    from app.services.jobs import create_job

    job = create_job(db, client_id, current_user["email"])
    job_id = job.job_id

    invalidate_pattern(redis_client, "jobs:list:*")

    file_data = []
    for file in files:
        content = await file.read()
        file_data.append({
            "filename": file.filename,
            "content": content,
            "content_type": file.content_type,
            "size": file.size
        })

    _set_analysis_status(client_id, {
        "status": "processing",
        "message": "Starting analysis...",
        "percent": 0,
        "job_id": job_id
    })

    background_tasks.add_task(
        run_analysis_background,
        client_id,
        file_data,
        current_user["email"],
        job_id
    )

    return {"status": "processing", "message": "Analysis started in background", "job_id": job_id}

def run_analysis_background(client_id: int, file_data: list[dict], user_email: str, job_id: int):
    db = SessionLocal()
    try:
        wrapped_files = [
            FileWrapper(f["filename"], f["content"], f["content_type"], f["size"])
            for f in file_data
        ]

        def progress_callback(message: str, percent: int, **kwargs):
            payload = {"status": "processing", "message": message, "percent": percent, "job_id": job_id}
            _set_analysis_status(client_id, payload)
            redis_client.publish(f"events:analysis:{client_id}", format_sse_event(payload))

        result = upload_cpl_service(
            db=db,
            client_id=client_id,
            files=wrapped_files,
            user_email=user_email,
            progress_callback=progress_callback,
            job_id=job_id
        )
        
        final_payload = {
            "status": "completed",
            "message": "Analysis completed successfully",
            "percent": 100,
            "result": result.model_dump()
        }
        _set_analysis_status(client_id, final_payload)
        redis_client.publish(f"events:analysis:{client_id}", format_sse_event(final_payload))

        invalidate_pattern(redis_client, "products:all:*")
        invalidate_pattern(redis_client, f"products:client:{client_id}:*")
        invalidate_pattern(redis_client, "jobs:list:*")
        invalidate_pattern(redis_client, "clients:all:*")
        invalidate_keys(redis_client, "clients:approved", f"clients:id:{client_id}")

    except Exception as e:
        error_payload = {"status": "failed", "message": str(e), "percent": 0}
        _set_analysis_status(client_id, error_payload)
        redis_client.publish(f"events:analysis:{client_id}", format_sse_event(error_payload))
    finally:
        db.close()
