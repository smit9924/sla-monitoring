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


class FileProcessingStatus(StrEnum):
    """Lifecycle state of an uploaded CSV file as it moves through parsing."""

    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"


class FileProcessingErrorCode(StrEnum):
    """
    Machine-readable reason a file failed processing; used to render a specific
    message on the frontend.

    This is intentionally separate from `monitoring.types.error_codes.ErrorCodes`:
    `ErrorCodes` describes API *response* failures (e.g. a bad HTTP request to
    this backend), while this enum describes *CSV parsing pipeline* failures
    that happen asynchronously inside the `csv-parser` cloud function, long
    after the original HTTP request has finished. Values are stored on
    `UploadedFile.error_code` so the frontend can show a specific message for
    a file without the cloud function and this API needing to share a process.

    The `csv-parser` cloud function is deployed independently of this backend
    (separate source directory, separate deploy step) and therefore keeps its
    own mirrored copy of this enum rather than importing it directly. If a
    value is added, removed, or renamed here, update the mirrored copy in
    `backend/cloud-functions/enums.py` to match.
    """

    INVALID_EXTENSION = "invalid_extension"
    EMPTY_FILE = "empty_file"
    INVALID_CSV_FORMAT = "invalid_csv_format"
    SCHEMA_MISMATCH = "schema_mismatch"
    DATA_CLEANING_FAILED = "data_cleaning_failed"
    STORAGE_UPLOAD_FAILED = "storage_upload_failed"
    STORAGE_DOWNLOAD_FAILED = "storage_download_failed"
    DATABASE_CONNECTION_FAILED = "database_connection_failed"
    DATABASE_WRITE_FAILED = "database_write_failed"
    FILE_RECORD_NOT_FOUND = "file_record_not_found"
    UNKNOWN_ERROR = "unknown_error"
