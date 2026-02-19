from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session,joinedload
from app.models.client_profiles import ClientProfile
from app.models.client_contracts import ClientContracts
from app.models.product_master import ProductMaster
from app.models.status import Status
from app.models.users import User
from app.schemas.client_profile import ClientProfileCreate, ClientProfileUpdate
from app.utils.name_to_id import get_status_id_by_name
 
class ClientAlreadyExistsError(Exception):
    pass
 
 
class ClientNotFoundError(Exception):
    pass

def serialize_client(c: ClientProfile) -> dict:
    return {
        "client_id": c.client_id,
        "contract_number": c.contracts.contract_number if c.contracts else None,
        "company_name": c.company_name,
        "company_email": c.company_email,
        "company_phone_no": c.company_phone_no,
        "company_address": c.company_address,
        "company_city": c.company_city,
        "company_state": c.company_state,
        "company_zip": c.company_zip,

        "contact_officer_name": c.contact_officer_name,
        "contact_officer_email": c.contact_officer_email,
        "contact_officer_phone_no": c.contact_officer_phone_no,
        "contact_officer_address": c.contact_officer_address,
        "contact_officer_city": c.contact_officer_city,
        "contact_officer_state": c.contact_officer_state,
        "contact_officer_zip": c.contact_officer_zip,

        "is_deleted": c.is_deleted,
        "status": c.status.status,
        "created_time": c.created_time,
        "updated_time": c.updated_time,
    }

 
def get_all_clients(db: Session):
    clients = (
        db.query(ClientProfile)
        .filter(ClientProfile.is_deleted.is_(False))
        .all()
    )
    return [
        serialize_client(c)
        for c in clients
    ]
 
    

def get_active_clients(db: Session):
 
    product_exists = (
        db.query(ProductMaster.product_id)
        .filter(
            ProductMaster.client_id == ClientProfile.client_id,
            ProductMaster.is_deleted.is_(False)
        )
        .exists()
    )
    clients = (
        db.query(ClientProfile, product_exists.label("has_products"))
        .join(ClientProfile.status)
        .options(joinedload(ClientProfile.status))
        .filter(
            ClientProfile.is_deleted.is_(False),
            Status.status == "approved"
        )
        .all()
    )
 
    result = []
 
    for client, has_products in clients:
        data = serialize_client(client)
        data["has_products"] = bool(has_products)
        result.append(data)
 
    return result
 
def get_client_by_id(db: Session, client_id: int) -> ClientProfile | None:
    c = db.query(ClientProfile).filter(ClientProfile.client_id == client_id).first()
    
    
    return serialize_client(c)

 
 
def create_client_profile(db: Session, payload: ClientProfileCreate, current_user):
    """
    Create a client profile with duplicate email / phone checks.
    """

    email = current_user["email"]

    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
            )
    
    if db.query(ClientProfile).filter(ClientProfile.company_email == payload.company_email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company Email already exsits"
            )
    if db.query(ClientProfile).filter(ClientProfile.company_phone_no == payload.company_phone_no).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company Phone already exsits"
            )
    if db.query(ClientProfile).filter(ClientProfile.contact_officer_email == payload.contact_officer_email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact Officer Email already exsits"
            )
    if db.query(ClientProfile).filter(ClientProfile.contact_officer_phone_no == payload.contact_officer_phone_no).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact Officer Phone already exsits"
            )



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
        raise ClientAlreadyExistsError("Client already exists")

    data = payload.model_dump()
    status_value = data.pop("status")

    client = ClientProfile(**data)
    client.status_id = get_status_id_by_name(db, status_value)

    db.add(client)
    db.commit()
    db.refresh(client)
    return serialize_client(client)
 
 
 
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

    # --- Unique constraint checks (exclude the client being edited) ---
    if "company_email" in update_data:
        dup = (
            db.query(ClientProfile)
            .filter(
                ClientProfile.company_email == update_data["company_email"],
                ClientProfile.client_id != client_id,
            )
            .first()
        )
        if dup:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company email is already in use by another client",
            )

    if "company_phone_no" in update_data:
        dup = (
            db.query(ClientProfile)
            .filter(
                ClientProfile.company_phone_no == update_data["company_phone_no"],
                ClientProfile.client_id != client_id,
            )
            .first()
        )
        if dup:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company phone number is already in use by another client",
            )

    if "contact_officer_email" in update_data:
        dup = (
            db.query(ClientProfile)
            .filter(
                ClientProfile.contact_officer_email == update_data["contact_officer_email"],
                ClientProfile.client_id != client_id,
            )
            .first()
        )
        if dup:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Contact officer email is already in use by another client",
            )

    if "contact_officer_phone_no" in update_data:
        dup = (
            db.query(ClientProfile)
            .filter(
                ClientProfile.contact_officer_phone_no == update_data["contact_officer_phone_no"],
                ClientProfile.client_id != client_id,
            )
            .first()
        )
        if dup:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Contact officer phone number is already in use by another client",
            )
    # -----------------------------------------------------------------

    if "status" in update_data:
        client.status_id = get_status_id_by_name(db, update_data.pop("status"))

    for field, value in update_data.items():
        setattr(client, field, value)

    client.updated_time = datetime.utcnow()

    db.commit()
    db.refresh(client)

    return serialize_client(client)
 
 
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

    target = "approved" if action == "approve" else "rejected"
    target_status_id = get_status_id_by_name(db, target)

    if client.status_id == target_status_id:
        return client
 
    if action == "approve":
        rejected_status = (
            db.query(Status)
            .filter(Status.status == "rejected")
            .first()
        )
        if rejected_status and client.status == rejected_status.status_id:
            raise ValueError("Rejected client cannot be approved")
 
    client.status_id = target_status_id
    db.commit()
    db.refresh(client)
 
    return client
 
def delete_client(db: Session, client_id:int):
    client = db.query(ClientProfile).filter(ClientProfile.client_id == client_id).first()
    if not client:
        raise ClientNotFoundError()

    if client.is_deleted:
        return client

    client.is_deleted = True
    db.commit()
    db.refresh(client)

    return serialize_client(client)

