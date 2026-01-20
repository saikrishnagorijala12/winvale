from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db

from app.schemas.client_contract import (
    ClientContractRead,
    ClientContractCreate,
    ClientContractUpdate,
)
from app.services import contracts as cont
from app.utils.admin_check import require_admin

router = APIRouter(prefix="/contracts", tags=["Contrats"])


@router.get(
    "",
)
def get_all_client_contracts(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cont.get_all_client_contracts(db)


@router.get(
    "/{client_id}",
    response_model=ClientContractRead,
)
def get_client_contract(
    client_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract = cont.get_contract_by_client_id(db, client_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Client contract not found")
    return contract


@router.post(
    "/{client_id}",
    response_model=ClientContractRead,
)
def create_client_contract(
    client_id: int,
    payload: ClientContractCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract = cont.create_contract_by_client_id(
        db=db,
        client_id=client_id,
        payload=payload,
    )

    if not contract:
        raise HTTPException(status_code=404, detail="Client contract not found")

    return contract

@router.put(
    "/{client_id}",
    response_model=ClientContractRead,
)
def update_client_contract(
    client_id: int,
    payload: ClientContractUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract = cont.update_contract_by_client_id(
        db=db,
        client_id=client_id,
        payload=payload,
    )

    if not contract:
        raise HTTPException(status_code=404, detail="Client contract not found")

    return contract


@router.delete("/{client_id}", response_model=ClientContractRead)
def delete_client(
    client_id : int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(db, current_user["email"])
    return cont.delete_contract(db, client_id)


