from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.services import products as prod
from app.redis_client import redis_client
from app.utils.cache import cache_get_or_set

router = APIRouter(prefix="/products", tags=["Products"])

CACHE_TTL = 300  # 5 minutes


@router.get("")
def get_all(
    page: int = 1,
    page_size: int = 50,
    search: str | None = None,
    client_id: int | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cache_key = (
        f"products:all:"
        f"page={page}:size={page_size}:search={search}:client={client_id}"
    )
    return cache_get_or_set(
        redis_client,
        cache_key,
        CACHE_TTL,
        lambda: prod.get_all(
            db=db,
            page=page,
            page_size=page_size,
            search=search,
            client_id=client_id,
        ),
    )


@router.get("/client/{client_id}")
def get_product_by_client(
    client_id: int,
    page: int = 1,
    page_size: int = 50,
    search: str | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cache_key = (
        f"products:client:{client_id}:"
        f"page={page}:size={page_size}:search={search}"
    )

    return cache_get_or_set(
        redis_client,
        cache_key,
        CACHE_TTL,
        lambda: prod.get_by_client(
            db=db, 
            client_id=client_id,
            page=page,
            page_size=page_size,
            search=search,
        ),
    )
