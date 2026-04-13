from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.jobs import Job
from app.redis_client import redis_client
from app.services import jobs as j
from app.utils.cache import cache_get_or_set, invalidate_keys, invalidate_pattern

router = APIRouter(prefix="/jobs", tags=["Jobs"])

CACHE_TTL = 300


def _invalidate_job_cache(job_id: int | None = None):
    invalidate_keys(redis_client, "jobs:all")
    invalidate_pattern(redis_client, "jobs:list:*")
    if job_id is not None:
        invalidate_pattern(redis_client, f"jobs:id:{job_id}*")
        invalidate_keys(redis_client, f"generate:job:{job_id}")


def _invalidate_product_and_client_cache(client_id: int):
    invalidate_pattern(redis_client, "products:all:*")
    invalidate_pattern(redis_client, f"products:client:{client_id}:*")
    invalidate_pattern(redis_client, "clients:all:*")
    invalidate_keys(redis_client, "clients:approved", f"clients:id:{client_id}")


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


@router.post("/{job_id}/status")
def update_job_status(
    job_id: int,
    action: str = Query(..., pattern="^(approve|reject)$"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if action == "approve":
        result = j.approve_job(
            db=db,
            job_id=job_id,
            user_email=current_user["email"],
        )
        _invalidate_job_cache(job_id)
        _invalidate_product_and_client_cache(job.client_id)
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
