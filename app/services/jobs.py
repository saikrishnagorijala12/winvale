from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Job, User, ClientProfile
from app.utils.name_to_id import get_status_id_by_name

def create_job(db: Session, client_id: int, email: str):
    user = db.query(User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    client = db.query(ClientProfile).filter_by(client_id=client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    job = Job(
        user_id=user.user_id,
        client_id=client_id,
        status_id=get_status_id_by_name(db, "pending")
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.job_id,
        "client_id": job.client_id,
        "status": job.status.status,
        "created_time": job.created_time
    }

def list_jobs(db: Session):
    jobs = (
        db.query(Job)
        .order_by(Job.created_time.desc())
        .all()
    )

    return [
        {
            "job_id": j.job_id,
            "client_id": j.client_id,
            "client" : j.client.company_name,
            "user_id": j.user_id,
            "user" : j.user.name,
            "status_id": j.status.status,
            "modifications_actions" : j.modification_actions,
            "created_time": j.created_time,
            "updated_time": j.updated_time
        }
        for j in jobs
    ]

def list_jobs_by_id(db: Session, job_id: int, user_email: str):
    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    job = db.query(Job).filter_by(job_id=job_id).one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    client_id = job.client_id

    client = db.query(ClientProfile).filter_by(client_id=client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return {
        "job_id": job.job_id,
        "client_id": job.client_id,
        "client" : job.client.company_name,
        "user_id": job.user_id,
        "user" : job.user.name,
        "modifications_actions" : job.modification_actions,
        "status": job.status.status,
        "created_time": job.created_time
    }

def approve_job(db: Session, job_id: int, user_email: str):
    job = db.query(Job).filter_by(job_id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    pending_id = get_status_id_by_name(db, "pending")
    approved_id = get_status_id_by_name(db, "approved")

    if job.status_id != pending_id:
        raise HTTPException(
            status_code=400,
            detail="Only pending jobs can be approved"
        )

    job.status_id = approved_id
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.job_id,
        "status": job.status.status,
        
        "message": "Job approved successfully"
    }


def reject_job(db: Session, job_id: int, user_email: str):
    job = db.query(Job).filter_by(job_id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    pending_id = get_status_id_by_name(db, "pending")
    rejected_id = get_status_id_by_name(db, "rejected")

    if job.status_id != pending_id:
        raise HTTPException(
            status_code=400,
            detail="Only pending jobs can be rejected"
        )

    job.status_id = rejected_id
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.job_id,
        "status": job.status.status,  
        "message": "Job rejected successfully"
    }