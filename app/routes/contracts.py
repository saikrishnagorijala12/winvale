from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.jobs import Job
from app.redis_client import redis_client
from app.schemas.client_contract import (
    ClientContractCreate,
    ClientContractRead,
    ClientContractUpdate,
)
from app.services import contracts as cont
from app.utils.admin_check import require_admin
from app.utils.cache import cache_get_or_set, invalidate_keys, invalidate_pattern

router = APIRouter(prefix="/contracts", tags=["Contracts"])

CACHE_TTL = 300  # 5 minutes


def _invalidate_job_related_cache_for_client(db: Session, client_id: int):
    invalidate_pattern(redis_client, "jobs:list:*")
    job_ids = (
        db.query(Job.job_id)
        .filter(Job.client_id == client_id)
        .all()
    )
    for (job_id,) in job_ids:
        invalidate_pattern(redis_client, f"jobs:id:{job_id}*")
        invalidate_keys(redis_client, f"generate:job:{job_id}")


def _invalidate_contract_cache(db: Session, client_id: int | None = None):
    keys = ["contracts:all"]
    if client_id is not None:
        keys.append(f"contracts:client:{client_id}")
    invalidate_keys(redis_client, *keys)

    # Contract data is embedded in client and job responses.
    invalidate_pattern(redis_client, "clients:all:*")
    invalidate_keys(redis_client, "clients:approved")
    if client_id is not None:
        invalidate_keys(redis_client, f"clients:id:{client_id}")
        _invalidate_job_related_cache_for_client(db, client_id)


@router.get("")
def get_all_client_contracts(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cache_get_or_set(
        redis_client, "contracts:all", CACHE_TTL, lambda: cont.get_all_client_contracts(db)
    )


@router.get(
    "/{client_id}",
    response_model=ClientContractRead,
)
def get_client_contract(
    client_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract = cache_get_or_set(
        redis_client,
        f"contracts:client:{client_id}",
        CACHE_TTL,
        lambda: cont.get_contract_by_client_id(db, client_id),
    )
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
    try:
        result = cont.create_contract_by_client_id(
            db=db,
            client_id=client_id,
            payload=payload,
        )
        _invalidate_contract_cache(db, client_id)
        return result
    except cont.ContractAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract already exist for this client",
        )


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

    _invalidate_contract_cache(db, client_id)
    return contract


@router.delete("/{client_id}", response_model=ClientContractRead)
def delete_client(
    client_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = cont.delete_contract(db, client_id)
        _invalidate_contract_cache(db, client_id)
        return result
    except cont.ClientNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
