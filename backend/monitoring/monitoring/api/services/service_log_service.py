"""Business logic for the paginated, per-service logs accordion on the file
dashboard page.

Route handlers stay thin and delegate here, matching the pattern used for
upload/list in `uploaded_file_service.py`.
"""

from uuid import UUID

from sqlmodel import Session

from monitoring.api.repositories.service_log_repository import (
    get_all_service_log_groups,
    get_service_log_group,
)
from monitoring.api.repositories.uploaded_file_repository import (
    get_uploaded_file_by_guid,
)
from monitoring.exceptions.definitions.upload_exceptions import (
    UploadedFileNotFoundException,
)
from monitoring.schemas.service_log_schemas import (
    FileLogsResponse,
    ServiceLogListQueryParams,
)


def get_file_logs(
    *, session: Session, guid: UUID, query: ServiceLogListQueryParams
) -> FileLogsResponse:
    """
    With no `service_id`, return every service in the file (total count +
    first batch each) -- the accordion's initial load. With a `service_id`,
    return just that service's next batch at `query.offset` -- its
    "Show more" click.
    """
    uploaded_file = get_uploaded_file_by_guid(session=session, guid=guid)
    if uploaded_file is None:
        raise UploadedFileNotFoundException()

    if query.service_id is None:
        groups = get_all_service_log_groups(session=session, upload_id=uploaded_file.id)
    else:
        groups = [
            get_service_log_group(
                session=session,
                upload_id=uploaded_file.id,
                service_id=query.service_id,
                offset=query.offset,
            )
        ]

    return FileLogsResponse(services=groups)
