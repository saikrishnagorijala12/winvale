from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.services import jobs as j

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/{client_id}")
def create_job(
    client_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return j.create_job(
        db=db,
        client_id=client_id,
        user_email=current_user["email"]
    )

@router.get("")
def list_jobs(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return j.list_jobs(db)


@router.get("/{job_id}")
def list_jobs_by_id(
    job_id:int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return j.list_jobs_by_id(db, job_id,current_user["email"])


@router.post("/{job_id}/status")
def update_job_status(
    job_id: int,
    action: str = Query(..., regex="^(approve|reject)$"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if action == "approve":
        return j.approve_job(
            db=db,
            job_id=job_id,
            user_email=current_user["email"],
        )
 
    if action == "reject":
        return j.reject_job(
            db=db,
            job_id=job_id,
            user_email=current_user["email"],
        )
 
    raise HTTPException(status_code=400, detail="Invalid action")
 
