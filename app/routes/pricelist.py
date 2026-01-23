from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.services.pricelist import upload_cpl

router = APIRouter(prefix="/cpl", tags=["CPL"])


@router.post("/{client_id}")
def upload_cpl(
    client_id: int,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(400, "Only Excel (.xlsx) allowed")

    return upload_cpl(
        db=db,
        client_id=client_id,
        file=file,
        user_email=current_user["email"],
    )
