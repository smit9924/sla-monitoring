from os import path
from pathlib import Path

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from monitoring.schemas.logging_schemas import LoggingSettings
from monitoring.schemas.storage_schemas import StorageSettings
from monitoring.types.enums import (
    EnvironmentName,
    LogFormatName,
    LogLevelName,
    StorageProviderName,
)

BASE_DIR: Path = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=path.join(BASE_DIR, "../", ".env"),
        env_ignore_empty=True,
        extra="ignore",
    )

    app_name: str = "SLA Monitoring API"

    API_V1_STR: str = "/api/v1"  # Base path for API version 1 endpoints

    ENVIRONMENT: EnvironmentName = ...  # type: ignore
    SERVICE_NAME: str = ...  # type: ignore
    LOG_LEVEL: LogLevelName = ...  # type: ignore
    LOG_FORMAT: LogFormatName = ...  # type: ignore
    LOG_RETENTION_DAYS: int = ...  # type: ignore

    # Ignore Pylance type checks here. These fields are populated by Pydantic Settings at runtime,
    # and the application should fail loudly if any required environment variable is missing.

    # CORS
    ALLOWED_ORIGINS: list[str] = ...  # type: ignore
    ALLOWED_CREDENTIALS: bool = ...  # type: ignore
    ALLOWED_METHODS: list[str] = ...  # type: ignore
    ALLOWED_HEADERS: list[str] = ...  # type: ignore

    # Storage
    STORAGE_PROVIDER: StorageProviderName = ...  # type: ignore
    GCS_BUCKET_NAME: str | None = None
    GCS_CREDENTIALS_PATH: Path | None = None
    GCS_SIGNED_URL_EXPIRATION_SECONDS: int = 3600

    # Postgres configuration
    POSTGRES_SERVER: str = ...  # type: ignore
    POSTGRES_PORT: int = ...  # type: ignore
    POSTGRES_DB: str = ...  # type: ignore
    POSTGRES_USER: str = ...  # type: ignore
    POSTGRES_PASSWORD: str = ...  # type: ignore

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    def logging_settings(self) -> LoggingSettings:
        return LoggingSettings(
            environment=self.ENVIRONMENT,
            service_name=self.SERVICE_NAME,
            log_level=self.LOG_LEVEL,
            log_format=self.LOG_FORMAT,
            log_retention_days=self.LOG_RETENTION_DAYS,
            log_directory=Path.joinpath(BASE_DIR, "..", "bin", "logs"),
        )

    def storage_settings(self) -> StorageSettings:
        return StorageSettings(
            provider=self.STORAGE_PROVIDER,
            gcs_bucket_name=self.GCS_BUCKET_NAME,
            gcs_credentials_path=self.GCS_CREDENTIALS_PATH,
            gcs_signed_url_expiration_seconds=self.GCS_SIGNED_URL_EXPIRATION_SECONDS,
        )


settings = Settings()
