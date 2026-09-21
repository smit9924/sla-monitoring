"""
Pure data-cleaning helpers for the CSV parser cloud function.

None of the functions here talk to the network or the database — they only
take a pandas DataFrame in and hand a cleaned one back (or raise
`CsvProcessingError`). Keeping them separate from main.py makes the cleaning
rules easy to read and test on their own.
"""

import logging

import pandas as pd

from enums import FileProcessingErrorCode
from exceptions import CsvProcessingError

log = logging.getLogger(__name__)

# Columns every uploaded CSV must have, matching the sample files provided
# with the assignment. Extra columns beyond these are ignored rather than
# rejected, so an unrelated extra column won't break an otherwise valid file.
REQUIRED_COLUMNS = [
    "service_id",
    "service_name",
    "timestamp",
    "status_code",
    "latency",
    "latency_unit",
    "agent",
    "region",
]

# Plain-text columns that just need surrounding whitespace removed.
TEXT_COLUMNS = ["service_id", "service_name", "agent", "region"]

# Multiplier to convert a supported latency_unit into milliseconds.
LATENCY_UNIT_TO_MS = {
    "ms": 1,
    "s": 1000,
}


def validate_columns(df: pd.DataFrame) -> None:
    """Raise SCHEMA_MISMATCH if any required column is missing from the header."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise CsvProcessingError(
            FileProcessingErrorCode.SCHEMA_MISMATCH,
            f"CSV is missing required column(s): {', '.join(missing_columns)}",
        )


def _parse_timestamp_to_utc(raw_value: str) -> pd.Timestamp | None:
    """
    Parse one `timestamp` cell into a timezone-aware UTC pandas Timestamp.

    The sample data mixes three formats for the same kind of value:
      - ISO 8601 in UTC, e.g. "2025-04-11T17:30:00Z"
      - ISO 8601 with a timezone offset, e.g. "2025-04-11T23:00:00+05:30"
      - Unix epoch seconds as a plain number, e.g. "1748729700"
    All three describe a real point in time, just written differently, so all
    three are converted to the same UTC representation. Returns None if the
    value doesn't match any known format, so the caller can drop that one row
    instead of failing the whole file over a single bad timestamp.
    """
    raw_value = raw_value.strip()
    try:
        if raw_value.isdigit():
            return pd.to_datetime(int(raw_value), unit="s", utc=True)
        return pd.to_datetime(raw_value, utc=True)
    except (ValueError, TypeError):
        return None


def _parse_latency_ms(raw_latency: str, raw_unit: str) -> float | None:
    """
    Parse one `latency` + `latency_unit` pair into a single latency-in-milliseconds value.

    Returns None (instead of raising) for values that can't represent a real
    measurement, so the caller can drop just that row:
      - blank/missing latency
      - latency that isn't a number
      - a negative latency (impossible for a real measurement; a handful of
        rows in the sample data have small negative numbers, which looks
        like a sensor/agent glitch rather than a genuine reading)
      - a latency_unit other than the two the monitoring agents use ("ms"/"s")
    """
    unit = raw_unit.strip().lower()
    if unit not in LATENCY_UNIT_TO_MS:
        return None

    try:
        value = float(raw_latency.strip())
    except ValueError:
        return None

    if value < 0:
        return None

    return value * LATENCY_UNIT_TO_MS[unit]


def _parse_status_code(raw_value: str) -> int | None:
    """Parse a `status_code` cell into an int, or None if it isn't a whole number."""
    try:
        return int(raw_value.strip())
    except ValueError:
        return None


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Turn a raw, string-typed DataFrame (as read straight from the CSV) into a
    clean one ready to persist, applying every rule from the assignment:

      1. Drop exact duplicate rows (the sample files each contain a handful
         of rows repeated byte-for-byte, most likely from a retried upload
         upstream of this pipeline).
      2. Convert every timestamp to UTC.
      3. Convert every latency into milliseconds.
      4. Sort the remaining rows by time, ascending.

    A row with a value that can't be trusted (bad timestamp, bad latency,
    bad status code) is dropped individually rather than failing the whole
    file, since a handful of corrupt readings should not block every other
    valid row in the file from being ingested. If nothing is left once
    cleaning is done, the whole file is treated as an error.
    """
    total_rows = len(df)

    df = df.drop_duplicates(subset=REQUIRED_COLUMNS, keep="first").copy()
    duplicate_rows_dropped = total_rows - len(df)

    df["recorded_at"] = df["timestamp"].map(_parse_timestamp_to_utc)
    df["latency_ms"] = [
        _parse_latency_ms(latency, unit)
        for latency, unit in zip(df["latency"], df["latency_unit"], strict=True)
    ]
    df["status_code"] = df["status_code"].map(_parse_status_code)

    for column in TEXT_COLUMNS:
        df[column] = df[column].str.strip()

    rows_before_validity_filter = len(df)
    df = df[
        df["recorded_at"].notna()
        & df["latency_ms"].notna()
        & df["status_code"].notna()
        # A row that doesn't say which service it's about is not usable,
        # even if every other column on it looks fine.
        & (df["service_id"] != "")
        & (df["service_name"] != "")
    ].copy()
    invalid_rows_dropped = rows_before_validity_filter - len(df)

    if df.empty:
        raise CsvProcessingError(
            FileProcessingErrorCode.DATA_CLEANING_FAILED,
            "No valid rows remained after cleaning (every row had a bad "
            "timestamp, latency, or status code, or was a duplicate).",
        )

    df["status_code"] = df["status_code"].astype(int)

    # agent/region are optional in the database; store a genuine missing
    # value as NULL rather than as an empty string.
    df["agent"] = df["agent"].replace("", None)
    df["region"] = df["region"].replace("", None)

    df = df.sort_values("recorded_at", ascending=True).reset_index(drop=True)

    log.info(
        "Cleaned CSV: %d rows in, %d exact duplicates dropped, %d rows dropped "
        "for an invalid timestamp/latency/status code, %d rows kept.",
        total_rows,
        duplicate_rows_dropped,
        invalid_rows_dropped,
        len(df),
    )

    return df
