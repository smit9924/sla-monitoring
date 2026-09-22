from datetime import datetime

from pydantic import Field

from .base_schemas import BaseSchema


class ServiceLogListQueryParams(BaseSchema):
    """
    Query parameters for `GET /files/{guid}/logs`.

    Leaving `service_id` unset drives the *initial* load: every service in
    the file is returned, each with its first batch of logs. Passing
    `service_id` (with `offset`) drives a single service's "Show more":
    only that service's next batch is fetched, so opening the accordion
    never has to re-fetch every other service's logs.
    """

    service_id: str | None = None
    offset: int = Field(default=0, ge=0)


class ServiceLogEntry(BaseSchema):
    """One `service_logs` row as shown in the logs accordion."""

    id: int
    recorded_at: datetime
    status_code: int
    is_failure: bool
    latency_ms: float | None
    agent: str | None
    region: str | None


class ServiceLogGroup(BaseSchema):
    """
    One service's section of the logs accordion: its total log count (across
    the whole file, not just this batch) and the current batch of entries.
    `has_more` tells the frontend whether to keep showing the "Show more"
    button for this service.
    """

    service_id: str
    service_name: str
    total_count: int
    logs: list[ServiceLogEntry]
    has_more: bool


class FileLogsResponse(BaseSchema):
    """
    Returned by `GET /files/{guid}/logs`. Contains one `ServiceLogGroup` per
    service on the initial (no `service_id`) call, or exactly one group when
    a specific service's next batch was requested.
    """

    services: list[ServiceLogGroup]


__all__ = [
    "FileLogsResponse",
    "ServiceLogEntry",
    "ServiceLogGroup",
    "ServiceLogListQueryParams",
]
