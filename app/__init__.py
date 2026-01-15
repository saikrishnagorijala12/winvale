import os
from fastapi import FastAPI
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL

from app.models.base import Base
from app.utils.db_init import seed_static_data

db_engine = None
SessionLocal = None


def get_db_config() -> URL:
    """
    Build DB URL safely (no string hacks).
    """
    return URL.create(
        drivername=os.getenv("DB_DIALECT"),
        username=os.getenv("DB_USERNAME"),
        # password=os.getenv("DB_PASSWORD"),
        password="Yotta@1234", 
        host=os.getenv("DB_SERVER"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("WORKING_DB"),
    )


def create_app():
    global db_engine, SessionLocal

    load_dotenv()

    app = FastAPI(
        title="Winvale GSA Automation",
        version="1.0.1",
    )

    DB_URL = get_db_config()
    is_test = os.getenv("ENV") == "test"

    if not is_test:
        tmp_engine = create_engine(DB_URL)
        try:
            with tmp_engine.begin() as conn:
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS dev"))
        finally:
            tmp_engine.dispose()

    db_engine = create_engine(
        DB_URL,
        connect_args={"options": "-c search_path=dev"},
    )

    SessionLocal = sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=db_engine,
    )

    if not is_test:
        Base.metadata.create_all(bind=db_engine)
        seed_static_data(SessionLocal())

    from .apirouter import register_routes
    register_routes(app)

    return app
