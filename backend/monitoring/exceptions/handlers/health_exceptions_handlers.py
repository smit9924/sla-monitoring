from fastapi import Request, status
from fastapi.responses import JSONResponse

from monitoring.exceptions.definitions.health_exceptions import (
    ServiceUnavailableException,
)
from monitoring.schemas.common_schemas import ApiErrorResponse


def service_unavailable_exception_handler(
    _request: Request,
    exc: ServiceUnavailableException,
) -> JSONResponse:
    """
    Handle service unavailable exceptions.

    Description
    -----------
    Generates a standardized API error response when the service fails
    its own health check.

    Parameters
    ----------
    _request : Request
        The incoming FastAPI request object.
    exc : ServiceUnavailableException
        Exception containing details about the health check failure, including
        the error code and user-facing message.

    Returns
    -------
    JSONResponse
        HTTP 503 Service Unavailable response with a structured error payload.
    """

    response = ApiErrorResponse(
        metadata=None,
        errorCode=exc.errorCode,
        message=exc.message,
    )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=response.model_dump(),
    )
