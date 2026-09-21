"""
CSV parser cloud function.

Triggered by Cloud Storage whenever an object finishes uploading to the
configured bucket. For every file that belongs to this application (i.e. one
with a matching `uploaded_files` row already created by the upload API), it:

  1. Marks the file "in progress" in Postgres.
  2. Checks the file is actually a .csv file.
  3. Downloads it and loads it into a pandas DataFrame.
  4. Checks all required columns are present.
  5. Cleans the data: converts timestamps to UTC, converts latency to
     milliseconds, drops unusable rows and exact duplicates, and sorts
     everything by time.
  6. Saves the cleaned rows to the `service_logs` table, linked back to the
     file via `upload_id`.
  7. Marks the file "success" (with a row count) or "error" (with a specific
     error code) in Postgres, so the frontend can show what happened.

Every step that can fail raises `CsvProcessingError` with a specific
`FileProcessingErrorCode` (see enums.py), which is what ends up stored on the
`uploaded_files` row and shown to the user.
"""

import io
import logging
from datetime import UTC, datetime
from pathlib import Path

import functions_framework
import pandas as pd
from google.cloud import storage
from google.cloud.exceptions import NotFound
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select

import db
from csv_cleaning import clean_dataframe, validate_columns
from enums import FileProcessingErrorCode, FileProcessingStatus
from exceptions import CsvProcessingError
from models import ServiceLog, UploadedFile

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def _validate_extension(object_name: str) -> None:
    """Raise INVALID_EXTENSION unless the uploaded object is a .csv file."""
    extension = Path(object_name).suffix.lower().lstrip(".")
    if extension != "csv":
        raise CsvProcessingError(
            FileProcessingErrorCode.INVALID_EXTENSION,
            f"Expected a .csv file but got '.{extension or 'unknown'}'.",
        )


def _download_csv_bytes(bucket_name: str, object_name: str) -> bytes:
    """Download the uploaded object's raw bytes from Cloud Storage."""
    try:
        client = storage.Client()
        blob = client.bucket(bucket_name).blob(object_name)
        return blob.download_as_bytes()
    except NotFound as e:
        raise CsvProcessingError(
            FileProcessingErrorCode.STORAGE_DOWNLOAD_FAILED,
            "The uploaded file could not be found in cloud storage.",
        ) from e
    except Exception as e:
        log.exception("Failed to download '%s' from bucket '%s'", object_name, bucket_name)
        raise CsvProcessingError(
            FileProcessingErrorCode.STORAGE_DOWNLOAD_FAILED,
            "The uploaded file could not be downloaded from cloud storage.",
        ) from e


def _load_csv(raw_bytes: bytes) -> pd.DataFrame:
    """
    Load the raw CSV bytes into a DataFrame with every column read as text.

    Columns are kept as plain strings (instead of letting pandas guess a
    type for each one) so the cleaning step gets full control over how each
    value is validated and converted. Left to itself, pandas would silently
    turn a malformed number into NaN before we get a chance to flag the row
    as invalid.
    """
    if len(raw_bytes) == 0:
        raise CsvProcessingError(
            FileProcessingErrorCode.EMPTY_FILE,
            "The uploaded file is empty.",
        )

    try:
        df = pd.read_csv(
            io.BytesIO(raw_bytes),
            dtype=str,
            keep_default_na=False,
            encoding="utf-8",
        )
    except pd.errors.EmptyDataError as e:
        raise CsvProcessingError(
            FileProcessingErrorCode.EMPTY_FILE,
            "The uploaded file has no header or data rows.",
        ) from e
    except (pd.errors.ParserError, UnicodeDecodeError) as e:
        raise CsvProcessingError(
            FileProcessingErrorCode.INVALID_CSV_FORMAT,
            "The uploaded file could not be parsed as a CSV.",
        ) from e

    if df.empty:
        raise CsvProcessingError(
            FileProcessingErrorCode.EMPTY_FILE,
            "The uploaded file has a header but no data rows.",
        )

    return df


def _persist_logs(session: Session, upload_id: int, df: pd.DataFrame) -> None:
    """Insert every cleaned row as a ServiceLog, all in a single transaction."""
    logs = [
        ServiceLog(
            upload_id=upload_id,
            service_id=row.service_id,
            service_name=row.service_name,
            recorded_at=row.recorded_at.to_pydatetime(),
            status_code=int(row.status_code),
            latency_ms=float(row.latency_ms),
            agent=row.agent,
            region=row.region,
        )
        for row in df.itertuples()
    ]

    try:
        session.add_all(logs)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        log.exception("Failed to write %d service log rows for upload %d", len(logs), upload_id)
        raise CsvProcessingError(
            FileProcessingErrorCode.DATABASE_WRITE_FAILED,
            "Cleaned rows could not be saved to the database.",
        ) from e


def _mark_status(
    session: Session,
    upload_row: UploadedFile,
    status: FileProcessingStatus,
    *,
    error_code: FileProcessingErrorCode | None = None,
    error_message: str | None = None,
    row_count: int | None = None,
) -> None:
    """Update the uploaded_files row's status (and related fields) and commit immediately."""
    upload_row.status = status
    upload_row.error_code = error_code
    upload_row.error_message = error_message
    if row_count is not None:
        upload_row.row_count = row_count
    if status in (FileProcessingStatus.SUCCESS, FileProcessingStatus.ERROR):
        upload_row.processed_at = datetime.now(UTC)

    session.add(upload_row)
    session.commit()


@functions_framework.cloud_event
def parse_csv(cloud_event):
    """
    Cloud Storage-triggered function: fires whenever a new object finishes
    uploading to the configured bucket.

    The trigger fires for *every* uploaded object, not just the ones this
    application cares about — Eventarc can't filter by filename. Only
    objects with a matching `uploaded_files` row (created by the upload API
    before the file lands in storage) are processed; everything else is
    ignored.
    """
    data = cloud_event.data
    bucket_name = data["bucket"]
    object_name = data["name"]

    # Step 1: establish the database connection up front. If the database
    # itself is unreachable, there is no `uploaded_files` row to mark as
    # ERROR either, so the only thing we can do is log loudly and stop.
    try:
        db.check_connection()
    except SQLAlchemyError:
        log.critical("Could not connect to the database while processing '%s'", object_name)
        return

    with Session(db.get_engine()) as session:
        upload_row = session.exec(
            select(UploadedFile).where(UploadedFile.storage_object_name == object_name)
        ).first()

        if upload_row is None:
            log.warning("No uploaded_files record for object '%s'; ignoring.", object_name)
            return

        if upload_row.status == FileProcessingStatus.SUCCESS:
            # Cloud Storage/Eventarc delivers events at-least-once, so the
            # same upload can trigger this function more than once. Without
            # this guard, a redelivered event would insert every log row a
            # second time.
            log.info("Object '%s' was already processed successfully; skipping.", object_name)
            return

        # Step 2: mark the file as being worked on before anything else, so
        # anyone looking at the dashboard sees it move out of "queued"
        # immediately, even if parsing takes a while.
        _mark_status(session, upload_row, FileProcessingStatus.IN_PROGRESS)

        try:
            # Step 3: reject anything that isn't a .csv file.
            _validate_extension(object_name)

            # Step 4 (part 1): fetch the file and load it into a DataFrame.
            raw_bytes = _download_csv_bytes(bucket_name, object_name)
            df = _load_csv(raw_bytes)

            # Step 4 (part 2): make sure every required column is present.
            validate_columns(df)

            # Steps 5-7: convert timestamps to UTC, convert latency to ms,
            # drop unusable/duplicate rows, and sort by time ascending.
            cleaned_df = clean_dataframe(df)

            # Step 8: save the cleaned rows, linked back to this file.
            _persist_logs(session, upload_row.id, cleaned_df)
        except CsvProcessingError as e:
            # A known, specific failure: record its error code so the
            # frontend can show a precise message.
            log.error("Processing failed for '%s': %s", object_name, e.message)
            _mark_status(
                session,
                upload_row,
                FileProcessingStatus.ERROR,
                error_code=e.error_code,
                error_message=e.message,
            )
        except Exception as e:
            # Anything not already covered above. Logged in full for
            # debugging, but only a generic code is stored on the row.
            log.exception("Unexpected error processing '%s'", object_name)
            _mark_status(
                session,
                upload_row,
                FileProcessingStatus.ERROR,
                error_code=FileProcessingErrorCode.UNKNOWN_ERROR,
                error_message=str(e)[:1000],
            )
        else:
            # Step 9: everything succeeded.
            _mark_status(
                session,
                upload_row,
                FileProcessingStatus.SUCCESS,
                row_count=len(cleaned_df),
            )
            log.info("Successfully processed '%s': %d rows persisted.", object_name, len(cleaned_df))
