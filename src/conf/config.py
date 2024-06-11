from typing import Any

from pydantic import ConfigDict, EmailStr, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: str
    postgres_domain: str
    sqlalchemy_database_url: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres'
    secret_key: str
    algorithm: str
    mail_username: EmailStr
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_password: str | None = None
    CLD_NAME: str
    CLD_API_KEY: int
    CLD_API_SECRET: str


    model_config = ConfigDict(env_file =".env", env_file_encoding ="utf-8")

    

config = Settings()

