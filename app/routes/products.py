from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db

from app.services import products as prod
from app.utils.admin_check import require_admin
import json
from app.redis_client import redis_client
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("")
def get_all(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return prod.get_all(db)


@router.get("/id/{product_id}")
def get_product_by_id(
    product_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return prod.get_by_id(db, product_id)

@router.get("/client/{client_id}")
def get_product_by_client(
    client_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cache_key = f"products:client:{client_id}"

    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    data = prod.get_by_client(db, client_id)

    redis_client.setex(
    cache_key,
    300,
    json.dumps(jsonable_encoder(data))
)
    return data
