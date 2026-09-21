from os import path
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from monitoring.schemas.logging_schemas import LoggingSettings
from monitoring.types.enums import EnvironmentName, LogFormatName, LogLevelName

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

    def logging_settings(self) -> LoggingSettings:
        return LoggingSettings(
            environment=self.ENVIRONMENT,
            service_name=self.SERVICE_NAME,
            log_level=self.LOG_LEVEL,
            log_format=self.LOG_FORMAT,
            log_retention_days=self.LOG_RETENTION_DAYS,
            log_directory=Path.joinpath(BASE_DIR, "..", "bin", "logs"),
        )


settings = Settings()
