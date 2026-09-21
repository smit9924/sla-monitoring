from fastapi import Request, status
from fastapi.responses import JSONResponse

from monitoring.exceptions.definitions.storage_exceptions import (
    StorageObjectNotFoundException,
    StorageOperationFailedException,
)
from monitoring.schemas.common_schemas import ApiErrorResponse
from monitoring.types.error_codes import ErrorCodes


def storage_object_not_found_exception_handler(
    _request: Request,
    exc: StorageObjectNotFoundException,
) -> JSONResponse:
    """
    Handle storage object not found exceptions.

    Description
    -----------
    Generates a standardized API error response when a requested file
    does not exist in the configured storage backend.

    Parameters
    ----------
    _request : Request
        The incoming FastAPI request object.
    exc : StorageObjectNotFoundException
        Exception containing details about the missing object, including
        the error code and user-facing message.

    Returns
    -------
    JSONResponse
        HTTP 404 Not Found response with a structured error payload.
    """

    response = ApiErrorResponse(
        metadata=None,
        errorCode=exc.errorCode,
        message=exc.message,
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=response.model_dump(),
    )


def storage_operation_failed_exception_handler(
    _request: Request,
    _exc: StorageOperationFailedException,
) -> JSONResponse:
    """
    Handle storage backend operation failures.

    Description
    -----------
    Generates a standardized API error response when a storage backend
    operation fails for an internal/technical reason (credentials, network,
    quota, SDK-level errors, and similar). The response is always a fixed,
    generic message and never surfaces provider or infrastructure details
    to the client; the real cause is logged server-side at the point of
    failure inside the storage provider implementation.

    Parameters
    ----------
    _request : Request
        The incoming FastAPI request object.
    _exc : StorageOperationFailedException
        The exception raised by the storage layer. Intentionally unused here
        so that whatever detail it carries can never leak into the response.

    Returns
    -------
    JSONResponse
        HTTP 500 Internal Server Error response with a structured, non-exposing
        error payload.
    """

    response = ApiErrorResponse(
        metadata=None,
        errorCode=ErrorCodes.STORAGE_OPERATION_FAILED,
        message="Unable to complete the storage operation. Please try again later.",
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(),
    )
