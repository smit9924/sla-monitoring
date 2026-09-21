from monitoring.exceptions.definitions.base import BaseException
from monitoring.types.error_codes import ErrorCodes


class StorageObjectNotFoundException(BaseException):
    """Raised when a requested object does not exist in the storage backend."""

    def __init__(self, message: str = "The requested file was not found.") -> None:
        super().__init__(ErrorCodes.STORAGE_OBJECT_NOT_FOUND, message)


class StorageOperationFailedException(BaseException):
    """Raised when a storage backend operation (upload/download/delete/list) fails unexpectedly."""

    def __init__(
        self,
        message: str = "Unable to complete the storage operation. Please try again later.",
    ) -> None:
        super().__init__(ErrorCodes.STORAGE_OPERATION_FAILED, message)
