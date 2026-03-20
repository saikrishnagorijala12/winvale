import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.models.base import Base
from app.utils.db_init import seed_static_data
from app.redis_client import redis_client
from app.config import settings

db_engine = None
SessionLocal = None


def create_app():
    global db_engine,SessionLocal
    
    app = FastAPI(
        title= settings.APP_TITLE,
        version= settings.APP_VERSION
    )

    @app.middleware("http")
    async def invalidate_cache_on_mutate(request: Request, call_next):
        response = await call_next(request)
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            if 200 <= response.status_code < 400:
                try:
                    # Clear Redis cache if a modifying request is made and successful
                    redis_client.flushdb()
                except Exception as e:
                    print(f"Error flushing Redis cache: {e}")
        return response

    DB_URL = settings.db_url
    tmp_engine = create_engine(DB_URL)
    try:
        with tmp_engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA}"))
    finally:
        tmp_engine.dispose()
    
    db_engine = create_engine(DB_URL, connect_args={"options": f"-c search_path={settings.DB_SCHEMA}"})
    SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=db_engine)
    Base.metadata.create_all(bind=db_engine)
    seed_static_data(SessionLocal())


    
    from .apirouter import register_routes
    register_routes(app)
    return app

