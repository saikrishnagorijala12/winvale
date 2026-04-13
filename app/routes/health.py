from time import perf_counter

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.redis_client import redis_client

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health_check():
    return {"status": "ok"}


@router.get("/cache")
def cache_health_check():
    start = perf_counter()
    try:
        pong = redis_client.ping()
        latency_ms = round((perf_counter() - start) * 1000, 2)
        return {
            "status": "ok",
            "connected": bool(pong),
            "latency_ms": latency_ms,
        }
    except Exception as exc:
        latency_ms = round((perf_counter() - start) * 1000, 2)
        return {
            "status": "error",
            "connected": False,
            "latency_ms": latency_ms,
            "detail": str(exc),
        }


@router.get("/db-latency")
def db_latency_check(db: Session = Depends(get_db)):
    start = perf_counter()
    try:
        db.execute(text("SELECT 1"))
        latency_ms = round((perf_counter() - start) * 1000, 2)
        return {
            "status": "ok",
            "connected": True,
            "latency_ms": latency_ms,
        }
    except Exception as exc:
        latency_ms = round((perf_counter() - start) * 1000, 2)
        return {
            "status": "error",
            "connected": False,
            "latency_ms": latency_ms,
            "detail": str(exc),
        }
