from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.schemas.upload import ProductUploadRow
from app.services.upload import upload_products as upload_products_service


router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/{client_id}", status_code=status.HTTP_201_CREATED)
def upload_products(
    client_id: int,
    payload: List[ProductUploadRow],
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = upload_products_service(db, client_id, payload)

    if result is None:
        raise HTTPException(status_code=404, detail="Client not found")

    return result
