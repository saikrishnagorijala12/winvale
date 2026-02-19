from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db

from app.services import products as prod
from app.utils.admin_check import require_admin
from app.utils.cache import cache_get_or_set
from app.redis_client import redis_client

router = APIRouter(prefix="/products", tags=["Products"])

CACHE_TTL = 86400


@router.get("")
def get_all(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Items per page"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cache_get_or_set(
        redis_client,
        f"products:all:page:{page}:size:{page_size}",
        CACHE_TTL,
        lambda: prod.get_all(db, page=page, page_size=page_size),
    )


@router.get("/id/{product_id}")
def get_product_by_id(
    product_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cache_get_or_set(
        redis_client,
        f"products:id:{product_id}",
        CACHE_TTL,
        lambda: prod.get_by_id(db, product_id),
    )


@router.get("/client/{client_id}")
def get_product_by_client(
    client_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Items per page"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cache_get_or_set(
        redis_client,
        f"products:client:{client_id}:page:{page}:size:{page_size}",
        CACHE_TTL,
        lambda: prod.get_by_client(db, client_id, page=page, page_size=page_size),
    )
