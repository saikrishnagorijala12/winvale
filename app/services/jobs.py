from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import (
    Job,
    User,
    ProductMaster,
    ProductHistory,
    ModificationAction,
    ClientProfile
)
from app.utils.name_to_id import get_status_id_by_name
from datetime import datetime
from app.utils.scd_helper import create_product_history_snapshot
from app.utils.upload_helper import identity_signature,history_signature


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
        raise HTTPException(404, "Job not found")

    pending_id = get_status_id_by_name(db, "pending")
    approved_id = get_status_id_by_name(db, "approved")

    if job.status_id != pending_id:
        raise HTTPException(400, "Only pending jobs can be approved")

    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(401, "Invalid user")

    actions = (
        db.query(ModificationAction)
        .filter_by(job_id=job_id)
        .all()
    )

    if not actions:
        raise HTTPException(400, "No modifications found for job")

    client_id = job.client_id
    now = datetime.utcnow()

    for action in actions:
        product = (
            db.query(ProductMaster)
            .filter_by(product_id=action.product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                500,
                f"Product {action.product_id} not found"
            )

        current_history = (
            db.query(ProductHistory)
            .filter_by(
                product_id=product.product_id,
                is_current=True,
            )
            .first()
        )

        if current_history:
            current_history.is_current = False
            current_history.effective_end_date = now

        if action.action_type == "REMOVED_PRODUCT":
            product.is_deleted = True
            db.add(
                create_product_history_snapshot(
                    product,
                    client_id,
                    is_current=False,
                    end_date=now,
                )
            )
            continue

        product.commercial_price = action.new_price
        product.item_description = action.new_description

        db.add(
            create_product_history_snapshot(
                product,
                client_id,
                is_current=True,
            )
        )

    job.status_id = approved_id
    db.commit()

    return {
        "job_id": job.job_id,
        "status": "approved",
        "message": "Job approved successfully",
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