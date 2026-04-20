from sqlalchemy.orm import declarative_base

from app.config import settings

Base = declarative_base()
DB_SCHEMA = settings.DB_SCHEMA
SCHEMA_TABLE_ARGS = {"schema": DB_SCHEMA}


def schema_fk(table_name: str, column_name: str) -> str:
    return f"{DB_SCHEMA}.{table_name}.{column_name}"
