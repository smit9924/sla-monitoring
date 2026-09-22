"""Business logic for the SLA stats accordion on the file dashboard page.

Route handlers stay thin and delegate here, matching the pattern used for
upload/list in `uploaded_file_service.py`.
"""

from uuid import UUID

from sqlmodel import Session

from monitoring.api.repositories.service_log_repository import (
    get_daily_failure_counts,
    get_service_sla_stats,
)
from monitoring.api.repositories.uploaded_file_repository import (
    get_uploaded_file_by_guid,
)
from monitoring.core.constants import SLA_UPTIME_THRESHOLD_PERCENTAGE
from monitoring.exceptions.definitions.upload_exceptions import (
    UploadedFileNotFoundException,
)
from monitoring.schemas.stats_schemas import FileStatsResponse


def get_file_stats(*, session: Session, guid: UUID) -> FileStatsResponse:
    """
    Assemble the SLA accordion's data for one uploaded file: per-service
    uptime + pass/fail, the overall pass/fail banner, and the per-day
    per-service failure counts driving the line chart.
    """
    uploaded_file = get_uploaded_file_by_guid(session=session, guid=guid)
    if uploaded_file is None:
        raise UploadedFileNotFoundException()

    services = get_service_sla_stats(session=session, upload_id=uploaded_file.id)
    daily_failures = get_daily_failure_counts(session=session, upload_id=uploaded_file.id)

    total_checks = sum(service.total_checks for service in services)
    failed_checks = sum(service.failed_checks for service in services)
    overall_uptime_percentage = (
        round((total_checks - failed_checks) / total_checks * 100, 3)
        if total_checks
        else 0.0
    )

    # Overall pass/fail is the AND of every service's own SLA, not a
    # blended average -- one service breaching its SLA should still turn
    # the banner red even if the other services are comfortably above
    # threshold (matches the per-service badges shown alongside it).
    overall_sla_fulfilled = bool(services) and all(
        service.sla_fulfilled for service in services
    )

    return FileStatsResponse(
        file_guid=uploaded_file.guid,
        sla_threshold_percentage=SLA_UPTIME_THRESHOLD_PERCENTAGE,
        overall_sla_fulfilled=overall_sla_fulfilled,
        overall_uptime_percentage=overall_uptime_percentage,
        services=services,
        daily_failures=daily_failures,
    )
