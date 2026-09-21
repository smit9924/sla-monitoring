from typing import Any

from monitoring.exceptions.definitions.health_exceptions import (
    ServiceUnavailableException,
)
from monitoring.exceptions.definitions.storage_exceptions import (
    StorageObjectNotFoundException,
    StorageOperationFailedException,
)
from monitoring.exceptions.definitions.upload_exceptions import (
    EmptyFileUploadException,
    FileTooLargeException,
    InvalidFileTypeException,
)
from monitoring.exceptions.handlers.health_exceptions_handlers import (
    service_unavailable_exception_handler,
)
from monitoring.exceptions.handlers.storage_exceptions_handlers import (
    storage_object_not_found_exception_handler,
    storage_operation_failed_exception_handler,
)
from monitoring.exceptions.handlers.upload_exceptions_handlers import (
    empty_file_upload_exception_handler,
    file_too_large_exception_handler,
    invalid_file_type_exception_handler,
)


def get_exception_handlers() -> dict[Any, Any]:
    """
    Returns a mapping of custom exception types to their corresponding
    FastAPI exception handler callables.
    """
    return {
        # Register HEALTH EXCEPTION handlers
        ServiceUnavailableException: service_unavailable_exception_handler,
        # Register STORAGE EXCEPTION handlers
        StorageObjectNotFoundException: storage_object_not_found_exception_handler,
        StorageOperationFailedException: storage_operation_failed_exception_handler,
        # Register UPLOAD EXCEPTION handlers
        InvalidFileTypeException: invalid_file_type_exception_handler,
        FileTooLargeException: file_too_large_exception_handler,
        EmptyFileUploadException: empty_file_upload_exception_handler,
    }
