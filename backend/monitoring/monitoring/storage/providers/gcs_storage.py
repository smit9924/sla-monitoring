import logging
from datetime import timedelta
from typing import BinaryIO

from google.api_core.exceptions import GoogleAPIError
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage
from google.cloud.exceptions import NotFound

from monitoring.exceptions.definitions.storage_exceptions import (
    StorageObjectNotFoundException,
    StorageOperationFailedException,
)
from monitoring.schemas.storage_schemas import StorageSettings
from monitoring.storage.base import BaseStorage

log = logging.getLogger(__name__)


class GCSStorage(BaseStorage):
    """
    Google Cloud Storage implementation of `BaseStorage`.

    Every method delegates to the `google-cloud-storage` SDK against a single
    configured bucket. SDK-level failures are logged in full here and then
    re-raised as the application's own storage exceptions, so callers (and the
    exception handlers registered for them) never see provider-specific detail.
    """

    def __init__(self, settings: StorageSettings) -> None:
        try:
            if settings.gcs_credentials_path:
                self._client = storage.Client.from_service_account_json(
                    str(settings.gcs_credentials_path)
                )
            else:
                # Falls back to Application Default Credentials, which itself
                # honours the standard GOOGLE_APPLICATION_CREDENTIALS env var.
                self._client = storage.Client()
        except DefaultCredentialsError as e:
            log.exception("GCS client construction failed: no credentials found")
            raise StorageOperationFailedException from e

        self._bucket = self._client.bucket(settings.gcs_bucket_name)
        self._default_url_expiration_seconds = settings.gcs_signed_url_expiration_seconds

    def upload(
        self,
        *,
        file: bytes | BinaryIO,
        destination_path: str,
        content_type: str | None = None,
    ) -> str:
        """Upload via `Blob.upload_from_string` (bytes) or `Blob.upload_from_file` (stream)."""
        blob = self._bucket.blob(destination_path)
        try:
            if isinstance(file, bytes):
                blob.upload_from_string(file, content_type=content_type)
            else:
                blob.upload_from_file(file, content_type=content_type)
        except GoogleAPIError as e:
            log.exception("GCS upload failed for %s", destination_path)
            raise StorageOperationFailedException from e

        return destination_path

    def download(self, *, source_path: str) -> bytes:
        """Download via `Blob.download_as_bytes`."""
        blob = self._bucket.blob(source_path)
        try:
            return blob.download_as_bytes()
        except NotFound as e:
            raise StorageObjectNotFoundException from e
        except GoogleAPIError as e:
            log.exception("GCS download failed for %s", source_path)
            raise StorageOperationFailedException from e

    def delete(self, *, file_path: str) -> None:
        """Delete via `Blob.delete`."""
        blob = self._bucket.blob(file_path)
        try:
            blob.delete()
        except NotFound as e:
            raise StorageObjectNotFoundException from e
        except GoogleAPIError as e:
            log.exception("GCS delete failed for %s", file_path)
            raise StorageOperationFailedException from e

    def list_files(self, *, prefix: str | None = None) -> list[str]:
        """List via `Client.list_blobs`."""
        try:
            return [blob.name for blob in self._client.list_blobs(self._bucket, prefix=prefix)]
        except GoogleAPIError as e:
            log.exception("GCS list_blobs failed for prefix %s", prefix)
            raise StorageOperationFailedException from e

    def exists(self, *, file_path: str) -> bool:
        """Check via `Blob.exists`."""
        blob = self._bucket.blob(file_path)
        try:
            return blob.exists()
        except GoogleAPIError as e:
            log.exception("GCS exists check failed for %s", file_path)
            raise StorageOperationFailedException from e

    def get_url(self, *, file_path: str, expires_in_seconds: int | None = None) -> str:
        """Generate a v4 signed URL via `Blob.generate_signed_url`."""
        blob = self._bucket.blob(file_path)
        expiration = timedelta(
            seconds=expires_in_seconds or self._default_url_expiration_seconds
        )
        try:
            return blob.generate_signed_url(version="v4", expiration=expiration)
        except GoogleAPIError as e:
            log.exception("GCS signed URL generation failed for %s", file_path)
            raise StorageOperationFailedException from e
