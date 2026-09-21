from abc import ABC, abstractmethod
from typing import BinaryIO


class BaseStorage(ABC):
    """
    Abstract base class for file-storage backends.

    Concrete providers (Google Cloud Storage, and any added later) implement
    every method here. Application code must depend on this type -- never on
    a concrete provider class -- obtained via `storage.factory.get_storage_client`,
    so the backend can be swapped later via configuration alone.
    """

    @abstractmethod
    def upload(
        self,
        *,
        file: bytes | BinaryIO,
        destination_path: str,
        content_type: str | None = None,
    ) -> str:
        """
        Upload file content to `destination_path` in the backing store.

        `file` is raw bytes or a readable binary stream -- never a local
        filesystem path or a web-framework upload type -- to keep this module
        decoupled from its callers (e.g. FastAPI route code should read an
        `UploadFile` into bytes/stream before calling this).

        Returns the stored object's path/key.
        """

    @abstractmethod
    def download(self, *, source_path: str) -> bytes:
        """
        Download and return the raw bytes stored at `source_path`.

        Raises `monitoring.exceptions.definitions.storage_exceptions.StorageObjectNotFoundException`
        if no object exists at `source_path`.
        """

    @abstractmethod
    def delete(self, *, file_path: str) -> None:
        """
        Delete the object at `file_path`.

        Raises `monitoring.exceptions.definitions.storage_exceptions.StorageObjectNotFoundException`
        if no object exists at `file_path`.
        """

    @abstractmethod
    def list_files(self, *, prefix: str | None = None) -> list[str]:
        """
        Return the paths/keys of all objects under `prefix`.

        If `prefix` is None, returns every object in the backing store.
        """

    @abstractmethod
    def exists(self, *, file_path: str) -> bool:
        """Return True if an object exists at `file_path`, else False."""

    @abstractmethod
    def get_url(self, *, file_path: str, expires_in_seconds: int | None = None) -> str:
        """
        Return a URL for retrieving the object at `file_path`.

        The URL is time-limited (signed); `expires_in_seconds` overrides the
        provider's configured default expiration when given.
        """
