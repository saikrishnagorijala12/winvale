from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.services.upload import upload_products as upload_products_service

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/{client_id}", status_code=status.HTTP_201_CREATED)
async def upload_products(
    client_id: int,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel (.xlsx) files are allowed",
        )

    result = upload_products_service(
        db=db,
        client_id=client_id,
        file=file,
        user_id=current_user.user_id,
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Client not found")

    return result
