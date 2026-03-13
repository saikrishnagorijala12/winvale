from sqlalchemy.orm import Session
from app.models.client_profiles import ClientProfile
from app.models.client_contracts import ClientContracts
from app.schemas.client_contract import ClientContractCreate, ClientContractUpdate, ClientContractRead
from app.utils.name_to_id import get_status_id_by_name



def get_all_client_contracts(db: Session) -> list[ClientContractRead]:
    contacts = db.query(ClientContracts).order_by(ClientContracts.created_time.desc()).all()
    
    return [
        ClientContractRead.model_validate({
            "client_id" : c.client_id,
            "client" : c.client.company_name,
            "contract_number" : c.contract_number,
            "contract_officer_name" : c.contract_officer_name,
            "contract_officer_address" : c.contract_officer_address,
            "contract_officer_city" : c.contract_officer_city,
            "contract_officer_state" : c.contract_officer_state,
            "contract_officer_zip" : c.contract_officer_zip,
            "origin_country" : c.origin_country,
            "gsa_proposed_discount" : c.gsa_proposed_discount,
            "q_v_discount" : c.q_v_discount,
            "additional_concessions" : c.additional_concessions,
            "normal_delivery_time" : c.normal_delivery_time,
            "expedited_delivery_time" : c.expedited_delivery_time,
            "fob_term" : c.fob_term,
            "energy_star_compliance" : c.energy_star_compliance,
            "epa_method_mechanism" : c.epa_method_mechanism,
            "is_hazardous" : c.is_hazardous,
            "is_deleted" : c.is_deleted or False,
            "created_time" : c.created_time,
            "updated_time" : c.updated_time
        })
        for c in contacts
    ]


def _serialize_contract(c: ClientContracts) -> ClientContractRead:
    return ClientContractRead.model_validate({
        "client_id" : c.client_id,
        "client" : c.client.company_name if c.client else None,
        "contract_number" : c.contract_number,
        "contract_officer_name" : c.contract_officer_name,
        "contract_officer_address" : c.contract_officer_address,
        "contract_officer_city" : c.contract_officer_city,
        "contract_officer_state" : c.contract_officer_state,
        "contract_officer_zip" : c.contract_officer_zip,
        "origin_country" : c.origin_country,
        "gsa_proposed_discount" : c.gsa_proposed_discount,
        "q_v_discount" : c.q_v_discount,
        "additional_concessions" : c.additional_concessions,
        "normal_delivery_time" : c.normal_delivery_time,
        "expedited_delivery_time" : c.expedited_delivery_time,
        "fob_term" : c.fob_term,
        "energy_star_compliance" : c.energy_star_compliance,
        "epa_method_mechanism" : c.epa_method_mechanism,
        "is_hazardous" : c.is_hazardous,
        "is_deleted" : c.is_deleted or False,
        "created_time" : c.created_time,
        "updated_time" : c.updated_time
    })

def get_contract_by_client_id(db: Session, client_id: int) -> ClientContractRead | None:
    c = (
        db.query(ClientContracts)
        .filter(ClientContracts.client_id == client_id)
        .first()
    )
    if not c:
        return None
    return _serialize_contract(c)

class ContractAlreadyExsistsError(Exception):
    pass

def create_contract_by_client_id(
    *,
    db: Session,
    client_id: int,
    payload: ClientContractCreate,
) -> ClientContractRead:
    existing = (
        db.query(ClientContracts)
        .filter(ClientContracts.client_id == client_id)
        .first()
    )
    if existing:
        raise ContractAlreadyExsistsError()

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
        epa_method_mechanism=payload.epa_method_mechanism,
        is_hazardous=payload.is_hazardous,
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    return _serialize_contract(contract)



def update_contract_by_client_id(
    *,
    db: Session,
    client_id: int,
    payload: ClientContractUpdate
) -> ClientContractRead | None:
    from fastapi import HTTPException, status as http_status

    contract = (
        db.query(ClientContracts)
        .filter(ClientContracts.client_id == client_id)
        .first()
    )
    if not contract:
        return None

    # --- Unique constraint check: contract_number ---
    if payload.contract_number and payload.contract_number != contract.contract_number:
        dup = (
            db.query(ClientContracts)
            .filter(
                ClientContracts.contract_number == payload.contract_number,
                ClientContracts.client_id != client_id,
            )
            .first()
        )
        if dup:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=f"Contract number '{payload.contract_number}' is already assigned to another client",
            )
    # ------------------------------------------------

    contract.contract_officer_name = payload.contract_officer_name
    contract.contract_officer_address = payload.contract_officer_address
    contract.contract_officer_city = payload.contract_officer_city
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
    contract.epa_method_mechanism = payload.epa_method_mechanism
    if payload.is_hazardous is not None:
        contract.is_hazardous = payload.is_hazardous

    db.commit()
    db.refresh(contract)

    return _serialize_contract(contract)



class ClientNotFoundError(Exception):
    pass

def delete_contract(db: Session, client_id: int):
    contract = (
        db.query(ClientContracts)
        .filter(ClientContracts.client_id == client_id)
        .first()
    )

    if not contract:
        raise ClientNotFoundError()

    if contract.is_deleted:
        return contract

    contract.is_deleted = True
    contract.client_id = None 

    db.commit()
    db.refresh(contract)

    return contract