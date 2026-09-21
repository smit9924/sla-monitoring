from datetime import UTC, datetime

from sqlmodel import Field

from .base import SQLModel


class ServiceLog(SQLModel, table=True):
    """
    Database model for a single service log entry parsed from an uploaded CSV.

    Each row corresponds to one data row of the source CSV, which is expected
    to provide: service_id, service_name, timestamp, status_code, latency,
    latency_unit, agent, region. `latency` and `latency_unit` are normalized
    into a single `latency_ms` column at parse time, and `timestamp` is
    normalized to UTC and stored as `recorded_at`. `service_id` is not stored
    yet, since the source system does not provide one at this time.

    Attributes
    ----------
    id : int | None
        Primary key identifier for the log entry (internal use only).
    upload_id : int
        Foreign key reference to the source file (`uploaded_files.id`).
        Preserves lineage back to the CSV a row was parsed from, which is
        needed for auditing, debugging bad data, and re-processing.
    service_name : str
        Human-readable name of the monitored service, as provided in the CSV.
    recorded_at : datetime
        UTC timestamp of when the logged event occurred (converted from the
        CSV's `timestamp` column, which may arrive in any timezone). Indexed
        to support time-range queries used in SLA window calculations.
    status_code : int
        Status code recorded for the request (e.g. HTTP status). Indexed to
        support filtering/aggregating error rates.
    latency_ms : float
        Latency of the request in milliseconds. Normalized at parse time from
        the CSV's `latency` + `latency_unit` columns; `latency_unit` itself is
        not stored since every row is converted to a common unit.
    agent : str | None, optional
        Agent/probe that captured the log entry, as provided in the CSV.
    region : str | None, optional
        Geographic region associated with the request, as provided in the CSV.
    created_at : datetime
        UTC timestamp of when this row was inserted into the database.
        Distinct from `recorded_at`, which is the event's own timestamp; this
        column is useful for auditing ingestion lag.

    Notes
    -----
    - All timestamps are stored in UTC.
    """

    __tablename__ = "service_logs"  # type: ignore

    id: int | None = Field(default=None, primary_key=True, index=True)

    upload_id: int = Field(
        foreign_key="uploaded_files.id",
        nullable=False,
        index=True,
    )

    service_name: str = Field(nullable=False, max_length=255, index=True)

    recorded_at: datetime = Field(nullable=False, index=True)

    status_code: int = Field(nullable=False, index=True)

    latency_ms: float = Field(nullable=False)

    agent: str | None = Field(default=None, max_length=255)

    region: str | None = Field(default=None, max_length=100)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )


__all__ = [
    "ServiceLog",
]
