"""
Database table models shared with the `monitoring` FastAPI backend.

This cloud function and the `monitoring` API are two separate deployments
that both read and write the *same* Postgres tables (`uploaded_files` and
`service_logs`). Because this function is deployed independently and cannot
import the `monitoring` package, the table definitions are mirrored here
instead. The `__tablename__` and column definitions below must stay
identical to the originals, or SQLModel will build queries against columns
that don't match the real table.

Source of truth:
- sla-monitoring/backend/monitoring/monitoring/database/models/uploaded_file.py
- sla-monitoring/backend/monitoring/monitoring/database/models/service_log.py
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Index
from sqlmodel import Field, SQLModel

from enums import FileProcessingErrorCode, FileProcessingStatus


class UploadedFile(SQLModel, table=True):
    """One row per CSV file uploaded for SLA log ingestion. See the module docstring."""

    __tablename__ = "uploaded_files"  # type: ignore

    id: int | None = Field(default=None, primary_key=True, index=True)
    guid: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True, nullable=False, index=True)
    original_filename: str = Field(nullable=False, max_length=255)
    file_extension: str = Field(nullable=False, max_length=10)
    content_type: str | None = Field(default=None, max_length=100)
    file_size_bytes: int | None = Field(default=None)
    gcs_bucket_name: str = Field(nullable=False, max_length=255)
    storage_object_name: str = Field(nullable=False, unique=True, index=True, max_length=255)
    status: FileProcessingStatus = Field(default=FileProcessingStatus.QUEUED, nullable=False, index=True)
    error_code: FileProcessingErrorCode | None = Field(default=None)
    error_message: str | None = Field(default=None, max_length=1000)
    row_count: int | None = Field(default=None)
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False, index=True)
    processed_at: datetime | None = Field(default=None)


class ServiceLog(SQLModel, table=True):
    """One row per cleaned log line parsed from an uploaded CSV. See the module docstring."""

    __tablename__ = "service_logs"  # type: ignore

    __table_args__ = (
        Index(
            "ix_service_logs_service_id_recorded_at",
            "service_id",
            "recorded_at",
        ),
    )

    id: int | None = Field(default=None, primary_key=True, index=True)
    upload_id: int = Field(foreign_key="uploaded_files.id", nullable=False, index=True)
    service_id: str = Field(nullable=False, max_length=255, index=True)
    service_name: str = Field(nullable=False, max_length=255)
    recorded_at: datetime = Field(nullable=False, index=True)
    status_code: int = Field(nullable=False, index=True)
    latency_ms: float = Field(nullable=False)
    agent: str | None = Field(default=None, max_length=255)
    region: str | None = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)


__all__ = ["ServiceLog", "UploadedFile"]
