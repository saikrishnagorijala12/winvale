from datetime import datetime
from fastapi import HTTPException, status, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session,joinedload
from app.models.client_profiles import ClientProfile
from app.models.client_contracts import ClientContracts
from app.models.product_master import ProductMaster
from app.models.status import Status
from app.models.users import User
from app.schemas.client_profile import ClientProfileCreate, ClientProfileUpdate, ClientProfileRead, ClientListRead
from app.utils.name_to_id import get_status_id_by_name
import os
from datetime import datetime, timezone
from app.utils.s3_upload import gsa_upload, clean
from .contracts import _serialize_contract
from app.models.negotiators import Negotiator
 
class ClientNotFoundError(Exception):
    pass

def serialize_client(c: ClientProfile) -> ClientProfileRead:
    data = {
        "client_id": c.client_id,
        "contract_number": c.contracts.contract_number if c.contracts else None,
        "company_name": c.company_name,
        "company_email": c.company_email,
        "company_phone_no": c.company_phone_no,
        "company_address": c.company_address,
        "company_city": c.company_city,
        "company_state": c.company_state,
        "company_zip": c.company_zip,

        "negotiators": [
            {
                "negotiator_id": n.negotiator_id,
                "client_id": n.client_id,
                "name": n.name,
                "title": n.title,
                "email": n.email,
                "phone_no": n.phone_no,
                "address": n.address,
                "city": n.city,
                "state": n.state,
                "zip": n.zip
            } for n in c.negotiators
        ],

        "is_deleted": c.is_deleted,
        "status": c.status.status,
        "created_time": c.created_time,
        "updated_time": c.updated_time,
        "company_logo_url": c.company_logo_url,
        "contract": _serialize_contract(c.contracts) if c.contracts else None,
    }
    return ClientProfileRead.model_validate(data)

 
def get_all_clients(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    search: str | None = None
) -> dict:
    from app.models.client_contracts import ClientContracts
    from app.models.status import Status

    query = db.query(ClientProfile).filter(ClientProfile.is_deleted.is_(False))

    if status and status != "all":
        query = query.join(ClientProfile.status).filter(Status.status == status)

    if search:
        search_filter = or_(
            ClientProfile.company_name.ilike(f"%{search}%"),
            ClientProfile.company_email.ilike(f"%{search}%"),
            ClientProfile.negotiators.any(Negotiator.name.ilike(f"%{search}%")),
            ClientProfile.contracts.has(ClientContracts.contract_number.ilike(f"%{search}%"))
        )
        query = query.filter(search_filter)

    total_count = query.count()
    
    clients = (
        query
        .options(joinedload(ClientProfile.contracts))
        .order_by(ClientProfile.created_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    product_exists_subquery = (
        db.query(ProductMaster.client_id)
        .filter(ProductMaster.is_deleted.is_(False))
        .subquery()
    )
    
    client_ids_with_products = {row[0] for row in db.query(product_exists_subquery).all()}

    result_clients = []
    for c in clients:
        data = serialize_client(c).model_dump()
        data["has_products"] = c.client_id in client_ids_with_products
        result_clients.append(ClientListRead.model_validate(data))

    return {
        "clients": result_clients,
        "total_count": total_count,
        "status_counts": {
            "all": db.query(ClientProfile).filter(ClientProfile.is_deleted.is_(False)).count(),
            "pending": db.query(ClientProfile).join(ClientProfile.status).filter(ClientProfile.is_deleted.is_(False), Status.status == "pending").count(),
            "approved": db.query(ClientProfile).join(ClientProfile.status).filter(ClientProfile.is_deleted.is_(False), Status.status == "approved").count(),
            "rejected": db.query(ClientProfile).join(ClientProfile.status).filter(ClientProfile.is_deleted.is_(False), Status.status == "rejected").count(),
        }
    }
 
    

def get_active_clients(db: Session) -> list[ClientListRead]:
 
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
        .order_by(ClientProfile.created_time.desc())
        .all()
    )
 
    result = []
 
    for client, has_products in clients:
        data = serialize_client(client).model_dump()
        data["has_products"] = bool(has_products)
        result.append(ClientListRead.model_validate(data))
 
    return result
 
def get_client_by_id(db: Session, client_id: int) -> ClientProfileRead | None:
    c = db.query(ClientProfile).filter(ClientProfile.client_id == client_id).first()
    
    if not c:
        return None
    return serialize_client(c)

 
 
def create_client_profile(db: Session, payload: ClientProfileCreate, current_user) -> ClientProfileRead:
    """
    Create a client profile.
    """

    email = current_user["email"]

    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
            )

    data = payload.model_dump()
    status_value = data.pop("status")
    negotiators_data = data.pop("negotiators", [])

    client = ClientProfile(**data)
    client.status_id = get_status_id_by_name(db, status_value)

    db.add(client)
    db.flush()

    for n_data in negotiators_data:
        negotiator = Negotiator(**n_data, client_id=client.client_id)
        db.add(negotiator)

    db.commit()
    db.refresh(client)
    return serialize_client(client)
 
 
 
def update_client(
    db: Session,
    client_id: int,
    data: ClientProfileUpdate,
) -> ClientProfileRead | None:
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



    if "status" in update_data:
        client.status_id = get_status_id_by_name(db, update_data.pop("status"))

    if "negotiators" in update_data:
        negotiators_data = update_data.pop("negotiators")
        db.query(Negotiator).filter(Negotiator.client_id == client_id).delete()
        for n_data in negotiators_data:
            negotiator = Negotiator(**n_data, client_id=client_id)
            db.add(negotiator)

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
) -> ClientProfileRead:
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
        return serialize_client(client)
 
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
 
    return serialize_client(client)
 
def delete_client(db: Session, client_id:int) -> ClientProfileRead:
    client = db.query(ClientProfile).filter(ClientProfile.client_id == client_id).first()
    if not client:
        raise ClientNotFoundError()

    if client.is_deleted:
        return serialize_client(client)

    client.is_deleted = True
    db.commit()
    db.refresh(client)

    return serialize_client(client)


def upload_company_logo(db: Session, client_id: int, file: UploadFile, user_email: str) -> ClientProfileRead:
    client = db.query(ClientProfile).filter_by(client_id=client_id).first()
    if not client:
        raise ClientNotFoundError("Client not found")

    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    _, ext = os.path.splitext(file.filename)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

    filename = (
        f"{clean(client.company_name)}_"
        f"logo_"
        f"{date_str}"
        f"{ext}"
    )

    result = gsa_upload(file, filename, "logo_upload")
    
    client.company_logo_url = result["url"]
    client.updated_time = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(client)
    
    return serialize_client(client)
