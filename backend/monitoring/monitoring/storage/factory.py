from functools import lru_cache

from monitoring.core.config import settings
from monitoring.storage.base import BaseStorage
from monitoring.storage.providers.gcs_storage import GCSStorage
from monitoring.types.enums import StorageProviderName

_PROVIDERS: dict[StorageProviderName, type[BaseStorage]] = {
    StorageProviderName.GCS: GCSStorage,
}


@lru_cache
def get_storage_client() -> BaseStorage:
    """
    Return the process-wide singleton `BaseStorage` instance for `STORAGE_PROVIDER`.

    Memoised via `functools.lru_cache` on this zero-argument function, so the
    concrete provider is constructed exactly once per process and every caller
    receives the same instance, typed as `BaseStorage` -- never the concrete
    provider class -- so the backend can be swapped via configuration alone.
    """
    storage_settings = settings.storage_settings()
    provider_cls = _PROVIDERS[storage_settings.provider]
    return provider_cls(storage_settings)
