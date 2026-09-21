import logging
from typing import Annotated

from fastapi import APIRouter, File, Query, UploadFile

from monitoring.api.dependencies import SessionDep
from monitoring.api.services.uploaded_file_service import (
    list_uploaded_files,
    upload_file,
)
from monitoring.doc.upload_exceptions_doc import UPLOAD_EXCEPTIONS_DOC
from monitoring.schemas.upload_schemas import (
    UploadedFileListQueryParams,
    UploadedFileListResponse,
    UploadedFileResponse,
)

log = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])


@router.post(
    "",
    responses={
        **UPLOAD_EXCEPTIONS_DOC["InvalidFileTypeException"],
        **UPLOAD_EXCEPTIONS_DOC["FileTooLargeException"],
        **UPLOAD_EXCEPTIONS_DOC["EmptyFileUploadException"],
    },
)
async def upload_file_route(
    session: SessionDep,
    file: Annotated[
        UploadFile, File(description="CSV file to upload for SLA log ingestion.")
    ],
) -> UploadedFileResponse:
    """
    Accept a CSV file upload, validate its type and size, and store it.

    On success, a `uploaded_files` row is created with status `queued`; the
    `csv-parser` cloud function picks it up asynchronously once the object
    finishes uploading to Cloud Storage.
    """
    return upload_file(session=session, file=file)


@router.get("")
async def list_uploaded_files_route(
    session: SessionDep,
    query: Annotated[UploadedFileListQueryParams, Query()],
) -> UploadedFileListResponse:
    """
    Return a paginated, sortable, searchable listing of uploaded files
    (upload history), most recently uploaded first by default.
    """
    return list_uploaded_files(session=session, query=query)
