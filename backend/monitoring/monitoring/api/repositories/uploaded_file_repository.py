"""Database access for `UploadedFile` rows.

Follows the same repository pattern used for every other paginated/sortable/
searchable listing in this codebase's reference architecture: sort columns
are resolved through a `dict[str, Column]` lookup table (never by
string-formatting a column name into SQL), search is a single `ILIKE`
predicate applied to both the row-selecting and count statements, and the
listing function assembles the full paginated response schema directly.
"""

from uuid import UUID

from sqlalchemy import Column
from sqlmodel import Session, col, func, or_, select

from monitoring.database.models.uploaded_file import UploadedFile
from monitoring.schemas.upload_schemas import (
    UploadedFileListItem,
    UploadedFileListQueryParams,
    UploadedFileListResponse,
)
from monitoring.types.enums import FileProcessingErrorCode, FileProcessingStatus

_SORT_COLUMNS: dict[str, Column] = {
    "originalFilename": UploadedFile.original_filename,
    "uploadedAt": UploadedFile.uploaded_at,
    "status": UploadedFile.status,
    "fileSizeBytes": UploadedFile.file_size_bytes,
}


def get_uploaded_file_by_guid(*, session: Session, guid: UUID) -> UploadedFile | None:
    """Look up an `uploaded_files` row by its public guid, or `None` if it doesn't exist."""
    return session.exec(select(UploadedFile).where(UploadedFile.guid == guid)).first()


def create_uploaded_file(*, session: Session, upload_row: UploadedFile) -> UploadedFile:
    """Insert a new `uploaded_files` row and return it with DB-generated fields populated."""
    session.add(upload_row)
    session.commit()
    session.refresh(upload_row)
    return upload_row


def update_uploaded_file_status(
    *,
    session: Session,
    guid: UUID,
    status: FileProcessingStatus,
    error_code: FileProcessingErrorCode | None = None,
    error_message: str | None = None,
) -> None:
    """Update an existing row's processing status in place, e.g. after a failed storage upload."""
    upload_row = session.exec(
        select(UploadedFile).where(UploadedFile.guid == guid)
    ).one()
    upload_row.status = status
    upload_row.error_code = error_code
    upload_row.error_message = error_message
    session.add(upload_row)
    session.commit()


def list_uploaded_files(
    *,
    session: Session,
    query: UploadedFileListQueryParams,
) -> UploadedFileListResponse:
    statement = select(UploadedFile)
    count_statement = select(func.count()).select_from(UploadedFile)

    search_term = (query.search_term or "").strip()
    if search_term:
        pattern = f"%{search_term}%"
        search_filter = or_(col(UploadedFile.original_filename).ilike(pattern))
        statement = statement.where(search_filter)
        count_statement = count_statement.where(search_filter)

    sort_column = _SORT_COLUMNS[query.sort_by]
    if query.sort_direction == "desc":
        statement = statement.order_by(col(sort_column).desc())
    else:
        statement = statement.order_by(col(sort_column).asc())

    offset = (query.page_number - 1) * query.page_size
    statement = statement.offset(offset).limit(query.page_size)

    total_count = session.exec(count_statement).one()
    uploaded_files = session.exec(statement).all()

    return UploadedFileListResponse(
        items=[
            UploadedFileListItem.model_validate(uploaded_file, from_attributes=True)
            for uploaded_file in uploaded_files
        ],
        total_count=total_count,
        page_number=query.page_number,
        page_size=query.page_size,
    )
