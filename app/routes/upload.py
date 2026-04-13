import json
import os
import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from app.database import SessionLocal
from app.auth.dependencies import get_current_user
from app.schemas.upload import ProductUploadStartResponse, ProductUploadStatusResponse
from app.services.upload import upload_products as upload_products_service
from app.utils.cache import invalidate_pattern, invalidate_keys
from app.redis_client import redis_client
from redis.exceptions import RedisError

router = APIRouter(prefix="/upload", tags=["Upload"])

logger = logging.getLogger(__name__)
UPLOAD_STATUS_TTL = 60 * 60 * 24


def _upload_status_key(client_id: int) -> str:
    return f"uploads:client:{client_id}:latest"


def _set_upload_status(client_id: int, payload: dict) -> None:
    try:
        redis_client.setex(
            _upload_status_key(client_id),
            UPLOAD_STATUS_TTL,
            json.dumps(payload),
        )
    except RedisError:
        logger.exception("Failed to persist upload status for client_id=%s", client_id)


def _get_upload_status(client_id: int) -> dict | None:
    try:
        payload = redis_client.get(_upload_status_key(client_id))
    except RedisError:
        logger.exception("Failed to read upload status for client_id=%s", client_id)
        return None
    if not payload:
        return None
    return json.loads(payload)

@router.get("/{client_id}/status", response_model=ProductUploadStatusResponse)
def get_upload_status(
    client_id: int,
    current_user=Depends(get_current_user),
):
    status_payload = _get_upload_status(client_id)
    if not status_payload:
        raise HTTPException(status_code=404, detail="No recent upload found")
    return status_payload


@router.post("/{client_id}/reset", status_code=status.HTTP_200_OK)
def reset_upload_status(
    client_id: int,
    current_user=Depends(get_current_user),
):
    """
    Clears the stuck upload status for a client.
    Use this if the server crashed or the background task was interrupted.
    """
    try:
        redis_client.delete(_upload_status_key(client_id))
        return {"status": "reset", "message": f"Upload status reset for client {client_id}"}
    except RedisError:
        logger.exception("Failed to reset upload status for client_id=%s", client_id)
        raise HTTPException(status_code=500, detail="Database error while resetting status")


@router.post(
    "/{client_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ProductUploadStartResponse,
)
async def upload_products(
    client_id: int,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user=Depends(get_current_user),
):
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only Excel (.xlsx) files are allowed",
        )

    file.file.seek(0, os.SEEK_END)
    total_size = file.file.tell()
    file.file.seek(0)
    file.size = total_size

    upload_id = uuid4().hex
    started_at = datetime.now(timezone.utc).isoformat()
    _set_upload_status(
        client_id,
        {
            "upload_id": upload_id,
            "client_id": client_id,
            "filename": file.filename,
            "status": "processing",
            "message": "Upload started",
            "processed_count": 0,
            "total_count": None,
            "started_at": started_at,
            "finished_at": None,
        },
    )

    background_tasks.add_task(
        run_upload_background,
        upload_id,
        client_id,
        file,
        started_at,
        current_user["email"],
    )

    return {
        "upload_id": upload_id,
        "status": "processing",
        "message": "Upload started"
    }


def run_upload_background(
    upload_id: str,
    client_id: int,
    file: UploadFile,
    started_at: str,
    user_email: str,
):
    db = SessionLocal()
    filename = file.filename

    def progress_callback(processed_count: int, total_count: int, **kwargs):
        current_status = _get_upload_status(client_id)
        if current_status:
            current_status["processed_count"] = processed_count
            current_status["total_count"] = total_count
            _set_upload_status(client_id, current_status)

    try:
        result = upload_products_service(
            db=db,
            client_id=client_id,
            file=file,
            user_email=user_email,
            progress_callback=progress_callback
        )
        _set_upload_status(
            client_id,
            {
                "upload_id": upload_id,
                "client_id": client_id,
                "filename": filename,
                "status": "completed",
                "message": "Upload completed",
                "started_at": started_at,
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "result": result,
            },
        )
    except Exception as exc:
        logger.exception("Product upload failed for client_id=%s filename=%s", client_id, filename)
        _set_upload_status(
            client_id,
            {
                "upload_id": upload_id,
                "client_id": client_id,
                "filename": filename,
                "status": "failed",
                "message": str(exc),
                "started_at": started_at,
                "finished_at": datetime.now(timezone.utc).isoformat(),
            },
        )
    finally:
        if not file.file.closed:
            file.file.close()
        db.close()

    # Invalidate product caches after a successful upload
    invalidate_pattern(redis_client, "products:all:*")
    invalidate_pattern(redis_client, f"products:client:{client_id}:*")
    invalidate_pattern(redis_client, "jobs:list:*")
    invalidate_pattern(redis_client, "clients:all:*")
    invalidate_keys(redis_client, "clients:approved", f"clients:id:{client_id}")
