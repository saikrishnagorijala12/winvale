import json
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.services import products as prod
from app.redis_client import redis_client

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("")
def get_all(
    page: int = 1,
    page_size: int = 50,
    search: str | None = None,
    client_id: int | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return prod.get_all(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        client_id=client_id,
    )


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
        json.dumps(jsonable_encoder(data)),
    )
    return data
