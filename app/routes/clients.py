from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.schemas.client_profile import ClientProfileRead, ClientProfileCreate, ClientProfileUpdate
from app.schemas.client_contract import ClientContractRead, ClientContractCreate, ClientContractUpdate
from app.services import clients as cps
from app.utils.admin_check import require_admin


router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("", response_model=list[ClientProfileRead])
def get_all_clients(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return cps.get_all_clients(db)

@router.get("/profiles/", response_model=list[ClientContractRead])
def get_all_client_contracts(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return cps.get_all_client_contracts(db)



@router.get("/{client_id}", response_model=ClientProfileRead)
def get_client_by_ids(
    client_id:int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return cps.get_client_by_ids(db, client_id)

@router.get(
    "/profiles/{client_id}",
    response_model=ClientContractRead,
    status_code=status.HTTP_200_OK
)
def get_contract_by_client_id(
    client_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = cps.get_contract_by_client_id(db, client_id)
    print(contract)

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client contract not found"
        )

    return contract





@router.post(
    "",
    response_model=ClientProfileRead,
    status_code=status.HTTP_201_CREATED
)
def create_client(
    payload: ClientProfileCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(db, current_user["email"])

    try:
        return cps.create_client_profile(db, payload)

    except cps.ClientAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client already exists"
        )


@router.put(
    "/profiles/{client_id}",
    response_model=ClientContractRead
)
def replace_client_contract(
    client_id: int,
    payload: ClientContractCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(db, current_user["email"])

    contract = cps.replace_contract_by_client_id(
        db=db,
        client_id=client_id,
        payload=payload
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client contract not found"
        )

    return contract