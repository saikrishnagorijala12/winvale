from sqlalchemy.orm import Session
from app.models.client_profiles import ClientProfile
from app.models.client_contracts import ClientContracts
from app.schemas.client_profile import (
    ClientProfileCreate,
    ClientProfileUpdate,
)
from app.schemas.client_contract import ClientContractCreate
from app.utils.name_to_id import get_status_id_by_name


class ClientAlreadyExistsError(Exception):
    pass



def get_all_clients(db: Session):
    return db.query(ClientProfile).all()


def get_client_by_id(db: Session, client_id: int):
    return (
        db.query(ClientProfile)
        .filter(ClientProfile.client_id == client_id)
        .first()
    )


def create_client_profile(db: Session, payload: ClientProfileCreate):
    if db.query(ClientProfile).filter(
        ClientProfile.company_email == payload.company_email
    ).first():
        raise ClientAlreadyExistsError()

    status_id = get_status_id_by_name(db, payload.status)

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
        status=status_id,
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    return client


def update_client(
    *,
    db: Session,
    client_id: int,
    data: ClientProfileUpdate,
):
    client = get_client_by_id(db, client_id)
    if not client:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "status" in update_data:
        client.status = get_status_id_by_name(
            db, update_data.pop("status")
        )

    for field, value in update_data.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)

    return client



def get_all_client_contracts(db: Session):
    return db.query(ClientContracts).all()


def get_contract_by_client_id(db: Session, client_id: int):
    return (
        db.query(ClientContracts)
        .filter(ClientContracts.client_id == client_id)
        .first()
    )


def replace_contract_by_client_id(
    *,
    db: Session,
    client_id: int,
    payload: ClientContractCreate,
):
    contract = get_contract_by_client_id(db, client_id)
    if not contract:
        return None

    contract.contract_number = payload.contract_number
    contract.origin_country = payload.origin_country
    contract.gsa_proposed_discount = payload.gsa_proposed_discount
    contract.q_v_discount = payload.q_v_discount
    contract.additional_concessions = payload.additional_concessions
    contract.normal_delivery_time = payload.normal_delivery_time
    contract.expedited_delivery_time = payload.expedited_delivery_time
    contract.fob_term = payload.fob_term
    contract.energy_star_compliance = payload.energy_star_compliance

    db.commit()
    db.refresh(contract)

    return contract

class ClientNotFoundError(Exception):
    pass


def change_client_status(
    *,
    db: Session,
    client_id: int,
    status_name: str,
):
    """
    Change client status (approve / reject).
    Business logic only.
    """

    client = (
        db.query(ClientProfile)
        .filter(ClientProfile.client_id == client_id)
        .first()
    )

    if not client:
        raise ClientNotFoundError()

    status_id = get_status_id_by_name(db, status_name)

    client.status = status_id
    db.commit()
    db.refresh(client)

    return client