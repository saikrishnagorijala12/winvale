from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from datetime import datetime
from fastapi import HTTPException
from collections import Counter
from app.models import (
    Job,
    User,
    ProductMaster,
    ProductHistory,
    ModificationAction,
    ClientProfile,
    ClientContracts,
    Status,
)
from app.utils.name_to_id import get_status_id_by_name
from app.utils.scd_helper import create_product_history_snapshot
from app.utils.upload_helper import identity_signature, history_signature


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
        status_id=get_status_id_by_name(db, "pending"),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.job_id,
        "client_id": job.client_id,
        "status": job.status.status,
        "created_time": job.created_time,
    }


def list_jobs(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    search: str | None = None,
    client_id: int | None = None,
    status: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    query = (
        db.query(Job)
        .join(Job.client)
        .join(ClientProfile.contracts)
        .join(Job.user)
        .join(Job.status)
    )

    if client_id:
        query = query.filter(Job.client_id == client_id)

    if status and status.lower() != "all":
        query = query.filter(Status.status == status)

    if date_from:
        query = query.filter(Job.created_time >= date_from)

    if date_to:
        query = query.filter(Job.created_time <= date_to)

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                ClientProfile.company_name.ilike(term),
                User.name.ilike(term),
                ClientContracts.contract_number.ilike(term),
            )
        )

    total = query.count()
    offset = (page - 1) * page_size

    jobs = (
        query
        .options(
            joinedload(Job.client).joinedload(ClientProfile.contracts),
            joinedload(Job.user),
            joinedload(Job.status),
            joinedload(Job.modification_actions),
        )
        .order_by(Job.created_time.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    response = []
    for j in jobs:
        action_counter = Counter()
        for a in j.modification_actions:
            action_counter[a.action_type] += 1

        response.append({
            "job_id": j.job_id,
            "client_id": j.client_id,
            "contract_number": (
                j.client.contracts.contract_number
                if j.client and j.client.contracts
                else None
            ),
            "client": j.client.company_name if j.client else None,
            "user_id": j.user_id,
            "user": j.user.name if j.user else None,
            "status": j.status.status if j.status else None,
            "action_summary": dict(action_counter),
            "created_time": j.created_time,
            "updated_time": j.updated_time,
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "items": response,
    }


def list_jobs_by_id(db: Session, job_id: int, user_email: str):
    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    job = db.query(Job).filter_by(job_id=job_id).one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    actions = []
    for a in job.modification_actions:
        p_name = None
        p_number = None

        if a.product:
            p_name = a.product.item_name
            p_number = a.product.manufacturer_part_number
        elif a.cpl_item:
            p_name = a.cpl_item.item_name
            p_number = a.cpl_item.manufacturer_part_number

        actions.append({
            "action_id": a.action_id,
            "action_type": a.action_type,
            "product_id": a.product_id,
            "product_name": p_name,
            "manufacturer_part_number": p_number,
            "old_price": a.old_price,
            "new_price": a.new_price,
            "old_description": a.old_description,
            "new_description": a.new_description,
            "number_of_items_impacted": a.number_of_items_impacted,
            "created_time": a.created_time,
        })

    return {
        "job_id": job.job_id,
        "client_id": job.client_id,
        "contract_number": job.client.contracts.contract_number,
        "client": job.client.company_name,
        "user_id": job.user_id,
        "user": job.user.name,
        "status": job.status.status,
        "modifications_actions": actions,
        "created_time": job.created_time,
        "updated_time": job.updated_time,
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

    actions = db.query(ModificationAction).filter_by(job_id=job_id).all()
    if not actions:
        raise HTTPException(400, "No modifications found for job")

    client_id = job.client_id
    now = datetime.utcnow()

    for action in actions:

        if action.action_type == "NEW_PRODUCT":
            if not action.cpl_item:
                raise HTTPException(500, "CPL data missing for new product")

            cpl = action.cpl_item

            existing_product = (
                db.query(ProductMaster)
                .filter(
                    ProductMaster.client_id == client_id,
                    ProductMaster.manufacturer == cpl.manufacturer_name,
                    ProductMaster.manufacturer_part_number == cpl.manufacturer_part_number,
                )
                .first()
            )

            if existing_product:
                existing_product.is_deleted = False
                existing_product.commercial_price = action.new_price
                existing_product.item_description = cpl.item_description
                existing_product.item_name = cpl.item_name
                db.add(create_product_history_snapshot(existing_product, client_id, is_current=True))
                continue

            row_data = {
                "manufacturer": cpl.manufacturer_name,
                "manufacturer_part_number": cpl.manufacturer_part_number,
                "item_name": cpl.item_name,
            }

            new_product = ProductMaster(
                client_id=client_id,
                item_type="B",
                manufacturer=cpl.manufacturer_name,
                manufacturer_part_number=cpl.manufacturer_part_number,
                item_name=cpl.item_name,
                item_description=cpl.item_description,
                commercial_price=action.new_price,
                country_of_origin=cpl.origin_country,
                currency="USD",
                row_signature=identity_signature(row_data),
                is_deleted=False,
            )

            db.add(new_product)
            db.flush()
            db.add(create_product_history_snapshot(new_product, client_id, is_current=True))
            continue

        product = db.query(ProductMaster).filter_by(product_id=action.product_id).first()
        if not product:
            raise HTTPException(500, f"Product {action.product_id} not found")

        current_history = (
            db.query(ProductHistory)
            .filter_by(product_id=product.product_id, is_current=True)
            .first()
        )

        if current_history:
            current_history.is_current = False
            current_history.effective_end_date = now

        if action.action_type == "REMOVED_PRODUCT":
            product.is_deleted = True
            if current_history:
                current_history.is_current = False
                current_history.effective_end_date = now
            continue

        product.commercial_price = action.new_price
        product.item_description = action.new_description
        product.item_name = action.new_name or product.item_name
        db.add(create_product_history_snapshot(product, client_id, is_current=True))

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
        raise HTTPException(status_code=400, detail="Only pending jobs can be rejected")

    job.status_id = rejected_id
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.job_id,
        "status": job.status.status,
        "message": "Job rejected successfully",
    }