from enum import StrEnum


class EnvironmentName(StrEnum):
    """Runtime environment that selects logging handlers and related behaviour."""

    LOCAL = "local"
    PRODUCTION = "production"


class LogFormatName(StrEnum):
    """Log line encoding written to stdout and, locally, to the log file."""

    CONSOLE = "console"
    JSON = "json"


class LogLevelName(StrEnum):
    """Python logging levels accepted by LOG_LEVEL."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StorageProviderName(StrEnum):
    """Backing store selected by STORAGE_PROVIDER; dispatches the storage factory."""

    GCS = "gcs"
