from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from monitoring.types.enums import FileProcessingErrorCode, FileProcessingStatus

from .base_schemas import BaseSchema

# Fields a client may sort the upload history listing by, keyed by the same
# camelCase name exposed over the wire (see `_SORT_COLUMNS` in
# `uploaded_file_repository.py`, which maps these to actual DB columns).
UploadedFileSortBy = Literal[
    "originalFilename", "uploadedAt", "status", "fileSizeBytes"
]


class UploadedFileResponse(BaseSchema):
    """Returned by `POST /files` once an uploaded file has been accepted and stored."""

    guid: UUID
    original_filename: str
    status: FileProcessingStatus
    file_size_bytes: int | None
    uploaded_at: datetime


class UploadedFileListItem(BaseSchema):
    """One row of the upload history listing returned by `GET /files`."""

    guid: UUID
    original_filename: str
    status: FileProcessingStatus
    error_code: FileProcessingErrorCode | None
    error_message: str | None
    row_count: int | None
    file_size_bytes: int | None
    uploaded_at: datetime
    processed_at: datetime | None


class UploadedFileListQueryParams(BaseSchema):
    """Query parameters for the paginated, sortable, searchable upload history listing."""

    search_term: str | None = None
    page_size: int = Field(default=10, ge=1, le=100)
    sort_by: UploadedFileSortBy = "uploadedAt"
    sort_direction: Literal["asc", "desc"] = "desc"
    page_number: int = Field(default=1, ge=1)


class UploadedFileListResponse(BaseSchema):
    items: list[UploadedFileListItem]
    total_count: int
    page_number: int
    page_size: int
