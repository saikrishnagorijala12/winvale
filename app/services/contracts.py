from sqlalchemy.orm import Session
from app.models.client_profiles import ClientProfile
from app.models.client_contracts import ClientContracts
from app.schemas.client_profile import (
    ClientProfileCreate,
    ClientProfileUpdate,
)
from app.schemas.client_contract import ClientContractCreate
from app.utils.name_to_id import get_status_id_by_name



def get_all_client_contracts(db: Session):
    return db.query(ClientContracts).all()


def get_contract_by_client_id(db: Session, client_id: int):
    return (
        db.query(ClientContracts)
        .filter(ClientContracts.client_id == client_id)
        .first()
    )

def create_contract_by_client_id(
    *,
    db: Session,
    client_id: int,
    payload: ClientContractCreate,
):
    existing = get_contract_by_client_id(db, client_id)
    if existing:
        raise ValueError("Contract already exists for this client")

    contract = ClientContracts(
        client_id=client_id,
        contract_number=payload.contract_number,
        contract_officer_name=payload.contract_officer_name,
        contract_officer_address=payload.contract_officer_address,
        contract_officer_city=payload.contract_officer_city,
        contract_officer_state=payload.contract_officer_state,
        contract_officer_zip=payload.contract_officer_zip,
        origin_country=payload.origin_country,
        gsa_proposed_discount=payload.gsa_proposed_discount,
        q_v_discount=payload.q_v_discount,
        additional_concessions=payload.additional_concessions,
        normal_delivery_time=payload.normal_delivery_time,
        expedited_delivery_time=payload.expedited_delivery_time,
        fob_term=payload.fob_term,
        energy_star_compliance=payload.energy_star_compliance,
        is_deleted=payload.is_deleted or False,
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    return contract



def update_contract_by_client_id(
    *,
    db: Session,
    client_id: int,
    payload: ClientContractCreate,
):
    contract = get_contract_by_client_id(db, client_id)
    if not contract:
        return None

    contract.contract_officer_name = payload.contract_officer_name
    contract.contract_officer_address = payload.contract_officer_address
    contract.contract_officer_city = payload.contract_number
    contract.contract_officer_state = payload.contract_officer_state
    contract.contract_officer_zip = payload.contract_officer_zip
    
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

def delete_contract(db: Session, client_id:int):
    client = db.query(ClientContracts).filter(ClientContracts.client_id == client_id).first()
    if not client:
        raise ClientNotFoundError()

    if client.is_deleted:
        return client

    client.is_deleted = True
    db.commit()
    db.refresh(client)

    return client
