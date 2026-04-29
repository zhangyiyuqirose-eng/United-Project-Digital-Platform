"""Application settings loaded from environment / .env file."""

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/updg_db"
    database_sync_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/updg_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: SecretStr = SecretStr("")
    jwt_algorithm: str = "HS256"
    jwt_expiration_seconds: int = 86400

    # MinIO
    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = ""
    minio_secret_key: str = ""
    minio_bucket: str = "updg-files"
    minio_secure: bool = False

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: SecretStr) -> SecretStr:
        if len(v.get_secret_value()) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v

    @field_validator("minio_access_key")
    @classmethod
    def validate_minio_access_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("MINIO_ACCESS_KEY must not be empty")
        return v

    @field_validator("minio_secret_key")
    @classmethod
    def validate_minio_secret_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("MINIO_SECRET_KEY must not be empty")
        return v

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # App
    debug: bool = True
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Anti-replay
    anti_replay_enabled: bool = False
    anti_replay_ttl_seconds: int = 300

    # AI / LLM
    finna_api_url: str = "https://www.finna.com.cn"
    finna_api_key: str = ""
    finna_api_model: str = "minimax-m2.7"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
