from pathlib import Path

from pydantic import model_validator

from monitoring.schemas.base_schemas import BaseSchema
from monitoring.types.enums import StorageProviderName


class StorageSettings(BaseSchema):
    """Storage backend configuration passed to `storage.factory.get_storage_client`."""

    provider: StorageProviderName
    gcs_bucket_name: str | None = None
    gcs_credentials_path: Path | None = None
    gcs_signed_url_expiration_seconds: int = 3600

    @model_validator(mode="after")
    def _require_provider_fields(self) -> "StorageSettings":
        """Fail loudly if the selected provider's required fields are missing."""
        if self.provider is StorageProviderName.GCS and not self.gcs_bucket_name:
            raise ValueError("GCS_BUCKET_NAME is required when STORAGE_PROVIDER=gcs")
        return self
