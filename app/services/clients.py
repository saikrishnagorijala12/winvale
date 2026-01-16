from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.client_profiles import ClientProfile
from app.models.client_contracts import ClientContracts
from app.models.status import Status
from app.schemas.client_profile import ClientProfileCreate, ClientProfileUpdate
 
class ClientAlreadyExistsError(Exception):
    pass
 
 
class ClientNotFoundError(Exception):
    pass
 
def get_all_clients(db: Session):
    clients = (
        db.query(ClientProfile)
        .filter(ClientProfile.is_deleted.is_(False))
        .all()
    )
 
    return [
        {
            "client_id": c.client_id,
            "company_name": c.company_name,
            "company_email": c.company_email,
            "contact_officer_name":c.contact_officer_name,
            "company_address": c.company_address,
            "company_city": c.company_city,
            "company_state": c.company_state,
            "company_zip": c.company_zip,
            "status": c.status_rel.status_code,
            "created_time": c.created_time,
        }
        for c in clients
    ]
 
 
def get_client_by_id(db: Session, client_id: int) -> ClientProfile | None:
    return (
        db.query(ClientProfile)
        .filter(ClientProfile.client_id == client_id)
        .first()
    )
 
 
def create_client_profile(db: Session, payload: ClientProfileCreate):
    """
    Create a client profile with duplicate email / phone checks.
    """
 
    existing = (
        db.query(ClientProfile)
        .filter(
            or_(
                ClientProfile.company_email == payload.company_email,
                ClientProfile.company_phone_no == payload.company_phone_no,
            )
        )
        .first()
    )
 
    if existing:
        if existing.company_email == payload.company_email:
            raise ClientAlreadyExistsError("Company email already registered")
        if existing.company_phone_no == payload.company_phone_no:
            raise ClientAlreadyExistsError("Company phone number already registered")
 
    client = ClientProfile(**payload.model_dump())
 
    db.add(client)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
 
    db.refresh(client)
    return client
 
 
 
def update_client(
    db: Session,
    client_id: int,
    data: ClientProfileUpdate,
) -> ClientProfile | None:
    """
    Partial update (PATCH semantics).
    """
    client = (
        db.query(ClientProfile)
        .filter(ClientProfile.client_id == client_id)
        .first()
    )
 
    if not client:
        return None
 
    update_data = data.model_dump(exclude_unset=True)
 
    for field, value in update_data.items():
        setattr(client, field, value)
 
    client.updated_time = datetime.utcnow()
 
    db.commit()
    db.refresh(client)
 
    return client
 
 
def update_client_status(
    db: Session,
    *,
    client_id: int,
    action: str,
) -> ClientProfile:
    """
    Single service for approve / reject.
    Uses status table (no hard-coded IDs).
    """
 
    client = (
        db.query(ClientProfile)
        .filter(ClientProfile.client_id == client_id)
        .first()
    )
 
    if not client:
        raise ClientNotFoundError()
    
    target_status_name = "approved" if action == "approve" else "rejected"
 
    target_status = (
        db.query(Status)
        .filter(Status.status_code == target_status_name)
        .first()
    )
 
    if not target_status:
        raise RuntimeError(
            f"Status '{target_status_name}' not configured in status table"
        )
 
    if client.status == target_status.status_id:
        return client
 
    if action == "approve":
        rejected_status = (
            db.query(Status)
            .filter(Status.status_code == "rejected")
            .first()
        )
        if rejected_status and client.status == rejected_status.status_id:
            raise ValueError("Rejected client cannot be approved")
 
    client.status = target_status.status_id
    db.commit()
    db.refresh(client)
 
    return client
 
 