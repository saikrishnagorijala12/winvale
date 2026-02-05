from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.services import generate

router = APIRouter(prefix="/generate", tags=["Generate Documents"])

@router.get("/{job_id}")
def get_job_details(
    job_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return generate.get_job_full_details(
        db=db,
        job_id=job_id,
        user_email=current_user["email"]
    )