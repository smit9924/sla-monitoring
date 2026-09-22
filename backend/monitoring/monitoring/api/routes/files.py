import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Query, UploadFile

from monitoring.api.dependencies import SessionDep
from monitoring.api.services.service_log_service import get_file_logs
from monitoring.api.services.stats_service import get_file_stats
from monitoring.api.services.uploaded_file_service import (
    list_uploaded_files,
    upload_file,
)
from monitoring.doc.upload_exceptions_doc import UPLOAD_EXCEPTIONS_DOC
from monitoring.schemas.service_log_schemas import (
    FileLogsResponse,
    ServiceLogListQueryParams,
)
from monitoring.schemas.stats_schemas import FileStatsResponse
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


@router.get(
    "/{guid}/stats",
    responses={**UPLOAD_EXCEPTIONS_DOC["UploadedFileNotFoundException"]},
)
async def get_file_stats_route(
    session: SessionDep,
    guid: UUID,
) -> FileStatsResponse:
    """
    Return the SLA stats accordion's data for one uploaded file: overall and
    per-service uptime/pass-fail against the SLA threshold, plus per-day
    per-service failure counts for the trend chart.
    """
    return get_file_stats(session=session, guid=guid)


@router.get(
    "/{guid}/logs",
    responses={**UPLOAD_EXCEPTIONS_DOC["UploadedFileNotFoundException"]},
)
async def get_file_logs_route(
    session: SessionDep,
    guid: UUID,
    query: Annotated[ServiceLogListQueryParams, Query()],
) -> FileLogsResponse:
    """
    Return the logs accordion's data for one uploaded file.

    With no `serviceId`, every service in the file is returned, each with
    its total log count and first batch of logs (the accordion's initial,
    on-first-expand load). With `serviceId` (+ `offset`), only that
    service's next batch is returned (a "Show more" click).
    """
    return get_file_logs(session=session, guid=guid, query=query)
