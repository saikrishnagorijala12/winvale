# #for aws purpose

# import os
# from fastapi import FastAPI
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# db_engine = None
# SessionLocal = None

# def get_db_config():
#     return (
#         f"{os.getenv('DB_DIALECT')}://"
#         f"{os.getenv('DB_USERNAME')}:"
#         f"{os.getenv('DB_PASSWORD')}@"
#         f"{os.getenv('DB_SERVER')}:"
#         f"{os.getenv('DB_PORT')}/"
#         f"{os.getenv('WORKING_DB')}"
#     )

# def create_app():
#     global db_engine, SessionLocal

#     load_dotenv()

#     app = FastAPI(
#         title="Winvale GSA Automation",
#         version="1.0.1"
#     )

#     db_engine = create_engine(
#         get_db_config(),
#         connect_args={"options": "-c search_path=dev"}
#     )

#     SessionLocal = sessionmaker(
#         autocommit=False,
#         autoflush=False,
#         bind=db_engine
#     )

#     from .apirouter import register_routes
#     register_routes(app)

#     return app

#local

import os
from fastapi import FastAPI
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.models.base import Base
from app.utils.db_init import seed_static_data

db_engine = None
SessionLocal = None


def get_db_config():
    DB_DIALECT = os.getenv('DB_DIALECT')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_SERVER = os.getenv('DB_SERVER')
    DB_PORT =os.getenv('DB_PORT')
    WORKING_DB = os.getenv('WORKING_DB')

    url = f"{DB_DIALECT}://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{WORKING_DB}"
    return url

def create_app():
    global db_engine,SessionLocal
    load_dotenv()
    app = FastAPI(
        title= "Winvale GSA Automation",
        version="1.0.1"
    )

    DB_URL = get_db_config()
    tmp_engine = create_engine(DB_URL)
    try:
        with tmp_engine.begin() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS dev"))
    finally:
        tmp_engine.dispose()
    # print("DB_URL : "+DB_URL)
    db_engine = create_engine(DB_URL, connect_args={"options": "-c search_path=dev"})
    SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=db_engine)
    Base.metadata.create_all(bind=db_engine)
    seed_static_data(SessionLocal())


    
    from .apirouter import register_routes
    register_routes(app)
    return app

