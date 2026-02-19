from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.services.upload import upload_products as upload_products_service
from app.utils.cache import invalidate_keys
from app.redis_client import redis_client

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/{client_id}", status_code=status.HTTP_201_CREATED)
def upload_products(
    client_id: int,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only Excel (.xlsx) files are allowed",
        )

    result = upload_products_service(
        db=db,
        client_id=client_id,
        file=file,
        user_email=current_user["email"],
    )

    from app.utils.cache import invalidate_pattern
    
    invalidate_pattern(redis_client, "products:all*")
    
    invalidate_pattern(redis_client, f"products:client:{client_id}*")

    return result
