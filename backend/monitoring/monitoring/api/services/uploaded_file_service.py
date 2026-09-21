"""Business logic for uploading a CSV file and listing upload history.

Route handlers stay thin and delegate here; this module owns validation and
orchestrates the storage + database side effects, delegating actual
persistence to `api.repositories.uploaded_file_repository`.
"""

import logging
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlmodel import Session

from monitoring.api.repositories.uploaded_file_repository import (
    create_uploaded_file,
    update_uploaded_file_status,
)
from monitoring.api.repositories.uploaded_file_repository import (
    list_uploaded_files as list_uploaded_files_repo,
)
from monitoring.core.config import settings
from monitoring.core.constants import (
    ALLOWED_UPLOAD_EXTENSIONS,
    MAX_UPLOAD_FILE_SIZE_BYTES,
)
from monitoring.database.models.uploaded_file import UploadedFile
from monitoring.exceptions.definitions.storage_exceptions import (
    StorageOperationFailedException,
)
from monitoring.exceptions.definitions.upload_exceptions import (
    EmptyFileUploadException,
    FileTooLargeException,
    InvalidFileTypeException,
)
from monitoring.schemas.upload_schemas import (
    UploadedFileListQueryParams,
    UploadedFileListResponse,
    UploadedFileResponse,
)
from monitoring.storage.factory import get_storage_client
from monitoring.types.enums import FileProcessingErrorCode, FileProcessingStatus

log = logging.getLogger(__name__)


def _validate_upload(file: UploadFile) -> tuple[str, str, int]:
    """Validate type/size and return (original_filename, extension, file_size_bytes)."""
    original_filename = file.filename or "upload"
    extension = Path(original_filename).suffix.lower().lstrip(".")

    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        allowed = ", ".join(f".{ext}" for ext in sorted(ALLOWED_UPLOAD_EXTENSIONS))
        raise InvalidFileTypeException(
            f"Unsupported file type '.{extension or 'unknown'}'. Only {allowed} files are accepted."
        )

    file_size_bytes = file.size or 0
    if file_size_bytes == 0:
        raise EmptyFileUploadException()

    if file_size_bytes > MAX_UPLOAD_FILE_SIZE_BYTES:
        max_size_gb = MAX_UPLOAD_FILE_SIZE_BYTES // (1024 * 1024 * 1024)
        raise FileTooLargeException(
            f"The file is too large. Maximum allowed upload size is {max_size_gb} GB."
        )

    return original_filename, extension, file_size_bytes


def upload_file(*, session: Session, file: UploadFile) -> UploadedFileResponse:
    """
    Validate, persist a tracking row for, and store a newly uploaded CSV file.

    A `uploaded_files` row is created (status QUEUED) before the file is
    handed to the storage backend, matching `UploadedFile`'s documented
    lifecycle. If the storage upload itself fails, the row is updated to
    ERROR (with `STORAGE_UPLOAD_FAILED`) instead of being left QUEUED
    forever, since no cloud function trigger will ever fire for it.
    """
    original_filename, extension, file_size_bytes = _validate_upload(file)

    bucket_name = settings.GCS_BUCKET_NAME
    if not bucket_name:
        raise StorageOperationFailedException("Storage bucket is not configured.")

    file_guid = uuid.uuid4()
    upload_row = UploadedFile(
        guid=file_guid,
        original_filename=original_filename,
        file_extension=extension,
        content_type=file.content_type,
        file_size_bytes=file_size_bytes,
        gcs_bucket_name=bucket_name,
        storage_object_name=f"{file_guid}.{extension}",
    )

    upload_row = create_uploaded_file(session=session, upload_row=upload_row)

    try:
        get_storage_client().upload(
            file=file.file,
            destination_path=upload_row.storage_object_name,
            content_type=file.content_type,
        )
    except StorageOperationFailedException:
        log.exception(
            "Storage upload failed for '%s' (guid=%s)",
            original_filename,
            upload_row.guid,
        )
        update_uploaded_file_status(
            session=session,
            guid=upload_row.guid,
            status=FileProcessingStatus.ERROR,
            error_code=FileProcessingErrorCode.STORAGE_UPLOAD_FAILED,
            error_message="The file could not be saved to cloud storage.",
        )
        raise

    return UploadedFileResponse.model_validate(upload_row, from_attributes=True)


def list_uploaded_files(
    *,
    session: Session,
    query: UploadedFileListQueryParams,
) -> UploadedFileListResponse:
    return list_uploaded_files_repo(session=session, query=query)
