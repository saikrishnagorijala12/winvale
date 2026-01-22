from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Job, User, ClientProfile
from app.utils.name_to_id import get_status_id_by_name

def create_job(db: Session, client_id: int, user_email: str):
    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    client = db.query(ClientProfile).filter_by(client_id=client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    job = Job(
        user_id=user.user_id,
        client_id=client_id,
        status=get_status_id_by_name(db, "pending")
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.job_id,
        "client_id": job.client_id,
        "status": "pending",
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
            "status_id": j.status,
            "created_time": j.created_time,
            "updated_time": j.updated_time
        }
        for j in jobs
    ]