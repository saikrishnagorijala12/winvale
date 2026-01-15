from sqlalchemy.orm import Session
from app.models.client_profiles import ClientProfile
from app.models.client_contracts import ClientContracts
from app.schemas.client_profile import ClientProfileCreate
from app.schemas.client_contract import ClientContractCreate
from app.models.client_profiles import ClientProfile
from app.schemas.client_profile import ClientProfileUpdate

def get_all_clients(db: Session):
    return db.query(ClientProfile).all()

def get_all_client_contracts(db: Session):
    return db.query(ClientContracts).all()



def get_client_by_ids(db: Session, client_id:int):
    return db.query(ClientProfile).filter(ClientProfile.client_id == client_id).first()


def get_contract_by_client_id(db: Session, client_id: int):
    """
    Fetch client contract by client_id.
    Returns None if not found.
    """
    contract = db.query(ClientContracts)\
        .filter(ClientContracts.client_id == client_id)\
        .first()
    
    print(client_id)
    return (
        db.query(ClientContracts)\
        .filter(ClientContracts.client_id == client_id)\
        .first()
    )


class ClientAlreadyExistsError(Exception):
    pass


def create_client_profile(db: Session, payload: ClientProfileCreate):
    """
    Create a client profile.
    Business logic only.
    """

    existing = (
        db.query(ClientProfile)
        .filter(ClientProfile.company_email == payload.company_email)
        .first()
    )

    if existing:
        raise ClientAlreadyExistsError()

    client = ClientProfile(
        company_name=payload.company_name,
        company_email=payload.company_email,
        company_phone_no=payload.company_phone_no,
        company_address=payload.company_address,
        company_city=payload.company_city,
        company_state=payload.company_state,
        company_zip=payload.company_zip,

        contact_officer_name=payload.contact_officer_name,
        contact_officer_email=payload.contact_officer_email,
        contact_officer_phone_no=payload.contact_officer_phone_no,
        contact_officer_address=payload.contact_officer_address,
        contact_officer_city=payload.contact_officer_city,
        contact_officer_state=payload.contact_officer_state,
        contact_officer_zip=payload.contact_officer_zip,

        status=payload.status
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    return client


def replace_contract_by_client_id(
    db: Session,
    client_id: int,
    payload: ClientContractCreate
):
    """
    Full replacement of a client contract (PUT semantics).
    """

    contract = (
        db.query(ClientContracts)
        .filter(ClientContracts.client_id == client_id)
        .first()
    )

    if not contract:
        return None

    # FULL overwrite (PUT)
    contract.contract_number = payload.contract_number
    contract.origin_country = payload.origin_country
    contract.gsa_proposed_discount = payload.gsa_proposed_discount
    contract.q_v_discount = payload.q_v_discount
    contract.additional_concessions = payload.additional_concessions
    contract.normal_delivery_time = payload.normal_delivery_time
    contract.expedited_delivery_time = payload.expedited_delivery_time
    contract.fob_term = payload.fob_term
    contract.energy_star_compliance = payload.energy_star_compliance
    contract.client_id = payload.client_id

    db.commit()
    db.refresh(contract)

    return contract

def update_client(
    *,
    db: Session,
    client_id: int,
    data: ClientProfileUpdate
):
    """
    Update an existing client profile.
    Business logic only.
    """

    client = (
        db.query(ClientProfile)
        .filter(ClientProfile.client_id == client_id)
        .first()
    )

    if not client:
        return None

    # Update only fields that were actually sent
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)

    return client