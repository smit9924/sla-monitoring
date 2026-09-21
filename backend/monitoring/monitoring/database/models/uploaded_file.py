import uuid
from datetime import UTC, datetime

from sqlmodel import Field

from monitoring.types.enums import FileProcessingErrorCode, FileProcessingStatus

from .base import SQLModel


class UploadedFile(SQLModel, table=True):
    """
    Database model tracking every CSV file uploaded for SLA log ingestion.

    One row is created as soon as an uploaded file passes initial validation,
    before it is uploaded to the storage and handed off for asynchronous parsing.
    The row is then updated in place as the file moves through its processing lifecycle.

    Attributes
    ----------
    id : int | None
        Primary key identifier for the upload record (internal use only).
    guid : uuid.UUID
        Globally unique identifier (UUID4) generated for this upload. Used to
        build the object name the file is stored under (`<guid>.<file_extension>`)
        so the original filename never has to be trusted as a cloud storage
        object key (avoids collisions and unsafe characters). Safe for
        external references and API responses.
    original_filename : str
        Filename as provided by the uploading client, kept for display and
        auditing purposes only. Never used to address the object in storage.
    file_extension : str
        Lower-cased file extension without the leading dot (e.g. "csv").
        Only "csv" is accepted at this time; kept as a column rather than a
        hardcoded assumption so future formats can be supported.
    content_type : str | None, optional
        MIME type reported by the client at upload time (e.g. "text/csv").
    file_size_bytes : int | None, optional
        Size of the uploaded file in bytes.
    gcs_bucket_name : str
        Name of the Cloud Storage bucket the object was uploaded to.
    storage_object_name : str
        Object key/path the file was stored under (`<guid>.<file_extension>`).
        This is what the `csv-parser` cloud function's Cloud Storage trigger
        matches back to this row, so it must be set before the file is
        uploaded to storage.
    status : FileProcessingStatus, default=QUEUED
        Current position of the file in the processing lifecycle (queued,
        in_progress, success, error). Indexed to support dashboards that
        filter/count uploads by status.
    error_code : FileProcessingErrorCode | None, optional
        Machine-readable failure reason, set only when `status` is ERROR.
        Lets the frontend show a specific, user-friendly message instead of
        a raw error string.
    error_message : str | None, optional
        Human-readable failure detail for debugging and support. May contain
        internal details and is not necessarily safe to show end users as-is.
    row_count : int | None, optional
        Number of log rows successfully parsed and persisted from this file.
        Populated once processing finishes successfully.
    uploaded_at : datetime
        UTC timestamp when the file was received by the API.
    processed_at : datetime | None, optional
        UTC timestamp when processing reached a terminal state (success or
        error). Null while the file is still queued or in progress.

    Notes
    -----
    - Always address the object in Cloud Storage via `guid` (+ `file_extension`),
      never via `original_filename`.
    - All timestamps are stored in UTC.
    """

    __tablename__ = "uploaded_files"  # type: ignore

    id: int | None = Field(default=None, primary_key=True, index=True)

    guid: uuid.UUID = Field(
        default_factory=uuid.uuid4, unique=True, nullable=False, index=True
    )

    original_filename: str = Field(nullable=False, max_length=255)

    file_extension: str = Field(nullable=False, max_length=10)

    content_type: str | None = Field(default=None, max_length=100)

    file_size_bytes: int | None = Field(default=None)

    gcs_bucket_name: str = Field(nullable=False, max_length=255)

    storage_object_name: str = Field(
        nullable=False, unique=True, index=True, max_length=255
    )

    status: FileProcessingStatus = Field(
        default=FileProcessingStatus.QUEUED,
        nullable=False,
        index=True,
    )

    error_code: FileProcessingErrorCode | None = Field(default=None)

    error_message: str | None = Field(default=None, max_length=1000)

    row_count: int | None = Field(default=None)

    uploaded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    processed_at: datetime | None = Field(default=None)


__all__ = [
    "UploadedFile",
]
