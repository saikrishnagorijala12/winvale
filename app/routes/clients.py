from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
 
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.schemas.client_profile import (
    ClientListRead,
    ClientProfileRead,
    ClientProfileCreate,
    ClientProfileUpdate,
)
from app.services import clients as cps
from app.utils.admin_check import require_admin
 
router = APIRouter(prefix="/clients", tags=["Clients"])
 
 
 
@router.get("")
def get_all_clients(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cps.get_all_clients(db)

@router.get("/approved", response_model=list[ClientListRead])
def get_active_clients(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cps.get_active_clients(db)
 
 
@router.get("/{client_id}", response_model=ClientProfileRead)
def get_client(
    client_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    client = cps.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client
 
 
@router.post(
    "",
    response_model=ClientProfileRead,
    status_code=status.HTTP_201_CREATED,
)
def create_client(
    payload: ClientProfileCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return cps.create_client_profile(db, payload, current_user)
    except cps.ClientAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Client already exists",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
 
 
@router.put("/{client_id}", response_model=ClientProfileRead)
def update_client(
    client_id: int,
    payload: ClientProfileUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        client = cps.update_client(
            db=db,
            client_id=client_id,
            data=payload,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
 
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
 
    return client
 
 
@router.patch("/{client_id}/approve")
def update_client_status(
    client_id: int,
    action: str = Query(..., regex="^(approve|reject)$"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(db, current_user["email"])
 
    try:
        cps.update_client_status(
            db=db,
            client_id=client_id,
            action=action,
        )
        return {"message": f"Client {action}d"}
    except cps.ClientNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
 
@router.delete("/{client_id}", response_model=ClientProfileRead)
def delete_client(
    client_id : int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(db, current_user["email"])
    return cps.delete_client(db, client_id)