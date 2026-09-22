"""Database access for `ServiceLog` rows: the SLA stats accordion and the
paginated, per-service logs accordion on the file dashboard page.

Follows the same repository pattern as `uploaded_file_repository`: no raw
SQL string-formatting, aggregation expressed through SQLAlchemy's `func`/
`case`, and the module assembles response-shaped values directly rather than
handing raw rows back to the service layer.
"""

from sqlalchemy import case, func
from sqlmodel import Session, col, select

from monitoring.core.constants import (
    FAILURE_STATUS_CODE_THRESHOLD,
    SERVICE_LOGS_BATCH_SIZE,
    SLA_UPTIME_THRESHOLD_PERCENTAGE,
)
from monitoring.database.models.service_log import ServiceLog
from monitoring.schemas.service_log_schemas import ServiceLogEntry, ServiceLogGroup
from monitoring.schemas.stats_schemas import DailyFailureCount, ServiceSlaStat

_is_failure = col(ServiceLog.status_code) >= FAILURE_STATUS_CODE_THRESHOLD


def get_service_sla_stats(*, session: Session, upload_id: int) -> list[ServiceSlaStat]:
    """Per-service total/failed check counts and uptime %, for one uploaded file."""
    rows = session.exec(
        select(
            ServiceLog.service_id,
            ServiceLog.service_name,
            func.count().label("total_checks"),
            func.sum(case((_is_failure, 1), else_=0)).label("failed_checks"),
        )
        .where(col(ServiceLog.upload_id) == upload_id)
        .group_by(ServiceLog.service_id, ServiceLog.service_name)
        .order_by(ServiceLog.service_name)
    ).all()

    stats: list[ServiceSlaStat] = []
    for service_id, service_name, total_checks, failed_checks in rows:
        failed_checks = int(failed_checks or 0)
        uptime_percentage = (
            round((total_checks - failed_checks) / total_checks * 100, 3)
            if total_checks
            else 0.0
        )
        stats.append(
            ServiceSlaStat(
                service_id=service_id,
                service_name=service_name,
                total_checks=total_checks,
                failed_checks=failed_checks,
                uptime_percentage=uptime_percentage,
                sla_fulfilled=total_checks > 0
                and uptime_percentage >= SLA_UPTIME_THRESHOLD_PERCENTAGE,
            )
        )
    return stats


def get_daily_failure_counts(
    *, session: Session, upload_id: int
) -> list[DailyFailureCount]:
    """Per-day, per-service count of failed (4xx/5xx) checks, for the failure line chart."""
    day_column = func.date(ServiceLog.recorded_at)

    rows = session.exec(
        select(
            day_column.label("day"),
            ServiceLog.service_id,
            ServiceLog.service_name,
            func.count().label("failure_count"),
        )
        .where(
            col(ServiceLog.upload_id) == upload_id,
            _is_failure,
        )
        .group_by(day_column, ServiceLog.service_id, ServiceLog.service_name)
        .order_by(day_column, ServiceLog.service_name)
    ).all()

    return [
        DailyFailureCount(
            day=day,
            service_id=service_id,
            service_name=service_name,
            failure_count=failure_count,
        )
        for day, service_id, service_name, failure_count in rows
    ]


def _to_log_entry(log_row: ServiceLog) -> ServiceLogEntry:
    return ServiceLogEntry(
        id=log_row.id,  # type: ignore[arg-type]
        recorded_at=log_row.recorded_at,
        status_code=log_row.status_code,
        is_failure=log_row.status_code >= FAILURE_STATUS_CODE_THRESHOLD,
        latency_ms=log_row.latency_ms,
        agent=log_row.agent,
        region=log_row.region,
    )


def get_all_service_log_groups(*, session: Session, upload_id: int) -> list[ServiceLogGroup]:
    """
    Initial logs-accordion load: every service present in the file, each with
    its total log count and its first `SERVICE_LOGS_BATCH_SIZE` log rows.
    """
    service_rows = session.exec(
        select(
            ServiceLog.service_id,
            ServiceLog.service_name,
            func.count().label("total_count"),
        )
        .where(col(ServiceLog.upload_id) == upload_id)
        .group_by(ServiceLog.service_id, ServiceLog.service_name)
        .order_by(ServiceLog.service_name)
    ).all()

    groups: list[ServiceLogGroup] = []
    for service_id, service_name, total_count in service_rows:
        log_rows = session.exec(
            select(ServiceLog)
            .where(
                col(ServiceLog.upload_id) == upload_id,
                col(ServiceLog.service_id) == service_id,
            )
            .order_by(col(ServiceLog.recorded_at).asc(), col(ServiceLog.id).asc())
            .limit(SERVICE_LOGS_BATCH_SIZE)
        ).all()

        groups.append(
            ServiceLogGroup(
                service_id=service_id,
                service_name=service_name,
                total_count=total_count,
                logs=[_to_log_entry(log_row) for log_row in log_rows],
                has_more=total_count > len(log_rows),
            )
        )
    return groups


def get_service_log_group(
    *, session: Session, upload_id: int, service_id: str, offset: int
) -> ServiceLogGroup:
    """
    "Show more" for a single service: the next `SERVICE_LOGS_BATCH_SIZE` log
    rows starting at `offset`, plus that service's total count so the
    frontend knows whether to keep offering "Show more".
    """
    total_count = session.exec(
        select(func.count())
        .select_from(ServiceLog)
        .where(
            col(ServiceLog.upload_id) == upload_id,
            col(ServiceLog.service_id) == service_id,
        )
    ).one()

    log_rows = session.exec(
        select(ServiceLog)
        .where(
            col(ServiceLog.upload_id) == upload_id,
            col(ServiceLog.service_id) == service_id,
        )
        .order_by(col(ServiceLog.recorded_at).asc(), col(ServiceLog.id).asc())
        .offset(offset)
        .limit(SERVICE_LOGS_BATCH_SIZE)
    ).all()

    service_name = log_rows[0].service_name if log_rows else service_id

    return ServiceLogGroup(
        service_id=service_id,
        service_name=service_name,
        total_count=total_count,
        logs=[_to_log_entry(log_row) for log_row in log_rows],
        has_more=offset + len(log_rows) < total_count,
    )
