from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
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
from app.utils.cache import cache_get_or_set, invalidate_keys
from app.redis_client import redis_client

router = APIRouter(prefix="/clients", tags=["Clients"])

CACHE_TTL = 300  # 5 minutes


def _invalidate_client_cache(client_id: int | None = None):
    keys = ["clients:all", "clients:approved"]
    if client_id is not None:
        keys.append(f"clients:id:{client_id}")
    invalidate_keys(redis_client, *keys)


@router.get("")
def get_all_clients(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cache_get_or_set(
        redis_client, "clients:all", CACHE_TTL, lambda: cps.get_all_clients(db)
    )


@router.get("/approved", response_model=list[ClientListRead])
def get_active_clients(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cache_get_or_set(
        redis_client, "clients:approved", CACHE_TTL, lambda: cps.get_active_clients(db)
    )


@router.get("/{client_id}", response_model=ClientProfileRead)
def get_client(
    client_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    client = cache_get_or_set(
        redis_client,
        f"clients:id:{client_id}",
        CACHE_TTL,
        lambda: cps.get_client_by_id(db, client_id),
    )
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
        result = cps.create_client_profile(db, payload, current_user)
        _invalidate_client_cache()
        return result
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

    _invalidate_client_cache(client_id)
    return client


@router.post("/{client_id}/logo", response_model=ClientProfileRead)
def upload_client_logo(
    client_id: int,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        client = cps.upload_company_logo(
            db=db,
            client_id=client_id,
            file=file,
            user_email=current_user["email"],
        )
        _invalidate_client_cache(client_id)
        return client
    except cps.ClientNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


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
        _invalidate_client_cache(client_id)
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
    client_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # require_admin(db, current_user["email"])
    result = cps.delete_client(db, client_id)
    _invalidate_client_cache(client_id)
    return result