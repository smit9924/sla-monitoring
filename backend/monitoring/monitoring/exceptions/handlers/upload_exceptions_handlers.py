from fastapi import Request, status
from fastapi.responses import JSONResponse

from monitoring.exceptions.definitions.upload_exceptions import (
    EmptyFileUploadException,
    FileTooLargeException,
    InvalidFileTypeException,
)
from monitoring.schemas.common_schemas import ApiErrorResponse


def invalid_file_type_exception_handler(
    _request: Request,
    exc: InvalidFileTypeException,
) -> JSONResponse:
    """
    Handle invalid file type exceptions.

    Description
    -----------
    Generates a standardized API error response when an uploaded file's
    extension is not one of the accepted upload types.

    Parameters
    ----------
    _request : Request
        The incoming FastAPI request object.
    exc : InvalidFileTypeException
        Exception containing details about the rejected file, including
        the error code and user-facing message.

    Returns
    -------
    JSONResponse
        HTTP 400 Bad Request response with a structured error payload.
    """

    response = ApiErrorResponse(
        metadata=None,
        errorCode=exc.errorCode,
        message=exc.message,
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=response.model_dump(),
    )


def file_too_large_exception_handler(
    _request: Request,
    exc: FileTooLargeException,
) -> JSONResponse:
    """
    Handle file too large exceptions.

    Description
    -----------
    Generates a standardized API error response when an uploaded file
    exceeds the maximum allowed upload size.

    Parameters
    ----------
    _request : Request
        The incoming FastAPI request object.
    exc : FileTooLargeException
        Exception containing details about the rejected file, including
        the error code and user-facing message.

    Returns
    -------
    JSONResponse
        HTTP 400 Bad Request response with a structured error payload.
    """

    response = ApiErrorResponse(
        metadata=None,
        errorCode=exc.errorCode,
        message=exc.message,
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=response.model_dump(),
    )


def empty_file_upload_exception_handler(
    _request: Request,
    exc: EmptyFileUploadException,
) -> JSONResponse:
    """
    Handle empty file upload exceptions.

    Description
    -----------
    Generates a standardized API error response when an uploaded file has
    no content.

    Parameters
    ----------
    _request : Request
        The incoming FastAPI request object.
    exc : EmptyFileUploadException
        Exception containing details about the rejected file, including
        the error code and user-facing message.

    Returns
    -------
    JSONResponse
        HTTP 400 Bad Request response with a structured error payload.
    """

    response = ApiErrorResponse(
        metadata=None,
        errorCode=exc.errorCode,
        message=exc.message,
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=response.model_dump(),
    )
