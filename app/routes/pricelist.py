import json

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from redis.exceptions import RedisError

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.services.pricelist import upload_cpl_service
from app.models.product_master import ProductMaster
from app.utils.cache import invalidate_keys, invalidate_pattern
from app.redis_client import redis_client

router = APIRouter(prefix="/cpl", tags=["CPL"])


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


@router.post("/{client_id}")
def upload_cpl(
    client_id: int,
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

    result = upload_cpl_service(
        db=db,
        client_id=client_id,
        files=files,
        user_email=current_user["email"],
    )

    invalidate_pattern(redis_client, "products:all:*")
    invalidate_pattern(redis_client, f"products:client:{client_id}:*")
    invalidate_pattern(redis_client, "clients:all:*")
    invalidate_keys(redis_client, "clients:approved", f"clients:id:{client_id}")

    return result
