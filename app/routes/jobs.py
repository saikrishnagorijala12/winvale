from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.services import jobs as j
from app.utils.cache import cache_get_or_set, invalidate_keys, invalidate_pattern
from app.redis_client import redis_client

router = APIRouter(prefix="/jobs", tags=["Jobs"])

CACHE_TTL = 300  # 5 minutes


def _invalidate_job_cache(job_id: int | None = None):
    invalidate_keys(redis_client, "jobs:all")
    # Wipe all paginated/filtered list cache entries
    invalidate_pattern(redis_client, "jobs:list:*")
    if job_id is not None:
        # Wipe all paginated/filtered job details cache entries
        invalidate_pattern(redis_client, f"jobs:id:{job_id}*")


@router.post("/{client_id}")
def create_job(
    client_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = j.create_job(
        db=db,
        client_id=client_id,
        user_email=current_user["email"],
    )
    _invalidate_job_cache()
    return result


@router.get("")
def list_jobs(
    page: int = 1,
    page_size: int = 50,
    search: str | None = None,
    client_id: int | None = None,
    status: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cache_key = (
        f"jobs:list:"
        f"page={page}:size={page_size}:search={search}:"
        f"client={client_id}:status={status}:"
        f"from={date_from}:to={date_to}"
    )
    return cache_get_or_set(
        redis_client,
        cache_key,
        CACHE_TTL,
        lambda: j.list_jobs(
            db=db,
            page=page,
            page_size=page_size,
            search=search,
            client_id=client_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
        ),
    )

@router.get("/{job_id}")
def list_jobs_by_id(
    job_id: int,
    page: int = 1,
    page_size: int = 50,
    action_type: str | None = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cache_key = f"jobs:id:{job_id}:page={page}:size={page_size}:action={action_type}"
    return cache_get_or_set(
        redis_client,
        cache_key,
        CACHE_TTL,
        lambda: j.list_jobs_by_id(db, job_id, current_user["email"], page, page_size, action_type),
    )
# @router.get("/{job_id}")
# def list_jobs_by_id(
#     job_id: int,
#     page: int = 1,
#     page_size: int = 50,
#     current_user=Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     cache_key = f"jobs:id:{job_id}:page={page}:size={page_size}"
#     return cache_get_or_set(
#         redis_client,
#         cache_key,
#         CACHE_TTL,
#         lambda: j.list_jobs_by_id(db, job_id, current_user["email"], page, page_size),
#     )


@router.post("/{job_id}/status")
def update_job_status(
    job_id: int,
    action: str = Query(..., regex="^(approve|reject)$"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if action == "approve":
        result = j.approve_job(
            db=db,
            job_id=job_id,
            user_email=current_user["email"],
        )
        _invalidate_job_cache(job_id)
        return result

    if action == "reject":
        result = j.reject_job(
            db=db,
            job_id=job_id,
            user_email=current_user["email"],
        )
        _invalidate_job_cache(job_id)
        return result

    raise HTTPException(status_code=400, detail="Invalid action")
