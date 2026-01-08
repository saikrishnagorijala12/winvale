from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.schemas.client_profile import ClientProfileRead, ClientProfileCreate, ClientProfileUpdate
from app.schemas.client_contract import ClientContractRead, ClientContractCreate, ClientContractUpdate
from app.services import clients as cps


router = APIRouter(prefix="/clients", tags=["Clients"])

@router.get("", response_model=list[ClientProfileRead])
def get_all_clients(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return cps.get_all_clients(db)

@router.get("/profiles", response_model=list[ClientContractRead])
def get_all_c_contracts(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return cps.get_all_c_contracts(db)