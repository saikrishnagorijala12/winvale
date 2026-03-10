import os
from typing import List, Union
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App Metadata
    APP_TITLE: str = "Winvale GSA Automation"
    APP_VERSION: str = "1.0.1"
    APP_GREET_MESSAGE: str = "Welcome To Winvale GSA Automation Tool. For more routes go to /docs."

    # Database Configuration
    DB_DIALECT: str = Field(default="postgresql+psycopg2")
    DB_USERNAME: str = Field(default="")
    DB_PASSWORD: str = Field(default="")
    DB_SERVER: str = Field(default="")
    DB_PORT: int = Field(default=5432)
    WORKING_DB: str = Field(default="")
    DB_SCHEMA: str = Field(default="dev")

    @computed_field
    @property
    def db_url(self) -> str:
        return f"{self.DB_DIALECT}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_SERVER}:{self.DB_PORT}/{self.WORKING_DB}"

    # Redis Configuration
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DECODE_RESPONSES: bool = Field(default=True)

    # AWS/S3 Configuration
    S3_BUCKET_NAME: str = Field(default="gsa-upload-master")
    AWS_REGION_S3: str = Field(default="us-east-1")
    AWS_ACCESS_KEY_ID: str = Field(default="")
    AWS_SECRET: str = Field(default="")
    AWS_REGION: str = Field(default="us-east-1")
    USER_POOL_ID: str = Field(default="")
    APP_CLIENT_ID: str = Field(default="")

    # Security Configuration
    CORS_ORIGINS: Union[str, List[str]] = Field(default=["*"])

    @computed_field
    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    CSP_SCRIPT_SRC: List[str] = Field(default=["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"])
    CSP_STYLE_SRC: List[str] = Field(default=["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"])
    CSP_IMG_SRC: List[str] = Field(default=["'self'", "data:", "blob:", "fastapi.tiangolo.com"])

settings = Settings()
