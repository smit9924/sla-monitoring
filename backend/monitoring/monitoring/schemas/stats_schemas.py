from datetime import date
from uuid import UUID

from .base_schemas import BaseSchema


class ServiceSlaStat(BaseSchema):
    """SLA summary for a single service, scoped to one uploaded file."""

    service_id: str
    service_name: str
    total_checks: int
    failed_checks: int
    uptime_percentage: float
    sla_fulfilled: bool


class DailyFailureCount(BaseSchema):
    """
    One point of the per-day, per-service failure line chart: the number of
    failed (4xx/5xx) checks recorded for `service_id` on `day`.
    """

    day: date
    service_id: str
    service_name: str
    failure_count: int


class FileStatsResponse(BaseSchema):
    """
    Returned by `GET /files/{guid}/stats`; backs the dashboard's first
    (SLA) accordion: the overall pass/fail banner, the per-service uptime
    breakdown, and the per-day-per-service failure line chart.
    """

    file_guid: UUID
    sla_threshold_percentage: float
    overall_sla_fulfilled: bool
    overall_uptime_percentage: float
    services: list[ServiceSlaStat]
    daily_failures: list[DailyFailureCount]


__all__ = [
    "DailyFailureCount",
    "FileStatsResponse",
    "ServiceSlaStat",
]
