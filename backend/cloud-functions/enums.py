"""
Enums shared with the `monitoring` FastAPI backend.

This `csv-parser` cloud function is deployed on its own (a separate source
directory with its own dependencies), so it cannot simply `import` the
`monitoring` package the way the API does. Instead, the two enums that both
services need to agree on are copied here by hand.

Source of truth: `sla-monitoring/backend/monitoring/monitoring/types/enums.py`
If you add, remove, or rename a value in either place, update the other one
too, otherwise the frontend and the database can disagree on what a status or
error code means.
"""

from enum import StrEnum


class FileProcessingStatus(StrEnum):
    """Lifecycle state of an uploaded CSV file as it moves through parsing."""

    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"


class FileProcessingErrorCode(StrEnum):
    """
    Machine-readable reason a file failed processing.

    Stored on the `uploaded_files.error_code` column so the frontend can show
    a specific, user-friendly message instead of a raw error string. This is
    a different set of codes than any HTTP/API error codes the backend uses
    for its own request/response handling — these codes describe exactly one
    thing: why the CSV pipeline in this function failed for a given file.
    """

    # The uploaded object's file extension is not ".csv".
    INVALID_EXTENSION = "invalid_extension"

    # The file has no data rows to process (or is zero bytes).
    EMPTY_FILE = "empty_file"

    # The file could not be parsed as a CSV at all (bad encoding, broken
    # quoting, ragged rows, etc.).
    INVALID_CSV_FORMAT = "invalid_csv_format"

    # One or more of the required columns is missing from the header.
    SCHEMA_MISMATCH = "schema_mismatch"

    # The file parsed fine structurally, but nothing survived data cleaning
    # (e.g. every row had an unparseable timestamp or latency).
    DATA_CLEANING_FAILED = "data_cleaning_failed"

    # Reserved for the upload API (not raised by this function): failure to
    # write the original file to cloud storage at upload time.
    STORAGE_UPLOAD_FAILED = "storage_upload_failed"

    # This function could not download the file from cloud storage.
    STORAGE_DOWNLOAD_FAILED = "storage_download_failed"

    # This function could not connect to the Postgres database at all.
    DATABASE_CONNECTION_FAILED = "database_connection_failed"

    # The database connection worked, but writing the cleaned rows failed.
    DATABASE_WRITE_FAILED = "database_write_failed"

    # No `uploaded_files` row matches the object that triggered this function.
    FILE_RECORD_NOT_FOUND = "file_record_not_found"

    # Catch-all for anything not covered above.
    UNKNOWN_ERROR = "unknown_error"
