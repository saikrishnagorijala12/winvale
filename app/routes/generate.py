from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.services import generate
from app.utils.cache import cache_get_or_set
from app.redis_client import redis_client

router = APIRouter(prefix="/generate", tags=["Generate Documents"])

CACHE_TTL = 86400


@router.get("/{job_id}")
def get_job_details(
    job_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cache_get_or_set(
        redis_client,
        f"generate:job:{job_id}",
        CACHE_TTL,
        lambda: generate.get_job_full_details(
            db=db,
            job_id=job_id,
            user_email=current_user["email"],
        ),
    )