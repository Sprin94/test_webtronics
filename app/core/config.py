import os
import secrets
from typing import Any, Dict, Optional

from pydantic import BaseSettings, PostgresDsn, RedisDsn, validator


class Settings(BaseSettings):

    BASE_DIR: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
    HOST: str = 'localhost'
    PORT: int = 80

    SECRET_KEY: str = secrets.token_urlsafe(32)

    EMAIL_HUNTER_API_KEY: str

    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = 5432
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    REDIS_PASSWORD: str
    REDIS_PORT: str
    REDIS_HOST: str
    REDIS_URI: Optional[RedisDsn] = None

    @validator('SQLALCHEMY_DATABASE_URI', pre=True)
    def assemble_db_connection(
        cls,
        v: Optional[str],
        values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            user=values.get('POSTGRES_USER'),
            password=values.get('POSTGRES_PASSWORD'),
            host=values.get('POSTGRES_SERVER'),
            path=f'/{values.get("POSTGRES_DB") or ""}',
            port=values.get('POSTGRES_PORT')
        )

    @validator('REDIS_URI', pre=True)
    def assemble_redis_connection(
        cls,
        v: Optional[str],
        values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme='redis',
            host=values.get('REDIS_HOST'),
            port=values.get('REDIS_PORT'),
            password=values.get('REDIS_PASSWORD')
        )

    #  TESTS
    TEST_POSTGRES_SERVER: Optional[str] = None
    TEST_POSTGRES_USER: Optional[str] = None
    TEST_POSTGRES_PASSWORD: Optional[str] = None
    TEST_POSTGRES_DB: Optional[str] = None
    TEST_POSTGRES_PORT: Optional[str] = None

    TEST_REDIS_PASSWORD: Optional[str]
    TEST_REDIS_PORT: Optional[str]
    TEST_REDIS_HOST: Optional[str]

    class Config:
        case_sensitive = True
        env_file = '.env'


settings = Settings()
