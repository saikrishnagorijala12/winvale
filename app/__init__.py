#for aws purpose

import os
from fastapi import FastAPI
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_engine = None
SessionLocal = None

def get_db_config():
    return (
        f"{os.getenv('DB_DIALECT')}://"
        f"{os.getenv('DB_USERNAME')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_SERVER')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('WORKING_DB')}"
    )

def create_app():
    global db_engine, SessionLocal

    load_dotenv()

    app = FastAPI(
        title="Winvale GSA Automation",
        version="1.0.1"
    )

    db_engine = create_engine(
        get_db_config(),
        connect_args={"options": "-c search_path=dev"}
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )

    from .apirouter import register_routes
    register_routes(app)

    return app
