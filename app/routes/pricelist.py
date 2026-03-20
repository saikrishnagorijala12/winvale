from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.services.pricelist import upload_cpl_service
from app.utils.cache import invalidate_keys
from app.redis_client import redis_client

router = APIRouter(prefix="/cpl", tags=["CPL"])


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

    result = upload_cpl_service(
        db=db,
        client_id=client_id,
        files=files,
        user_email=current_user["email"],
    )

    invalidate_keys(
        redis_client,
        "products:all",
        f"products:client:{client_id}",
    )

    return result
