from monitoring.schemas.common_schemas import ApiErrorResponse
from monitoring.types.error_codes import ErrorCodes

UPLOAD_EXCEPTIONS_DOC = {
    "InvalidFileTypeException": {
        400: {
            "description": "The uploaded file's type is not supported.",
            "model": ApiErrorResponse[None],
            "content": {
                "application/json": {
                    "example": {
                        "metadata": "None",
                        "message": "Only CSV files are supported.",
                        "errorCode": ErrorCodes.INVALID_FILE_TYPE,
                    }
                }
            },
        }
    },
    "FileTooLargeException": {
        400: {
            "description": "The uploaded file exceeds the maximum allowed size.",
            "model": ApiErrorResponse[None],
            "content": {
                "application/json": {
                    "example": {
                        "metadata": "None",
                        "message": "The file exceeds the maximum allowed upload size.",
                        "errorCode": ErrorCodes.FILE_TOO_LARGE,
                    }
                }
            },
        }
    },
    "EmptyFileUploadException": {
        400: {
            "description": "The uploaded file has no content.",
            "model": ApiErrorResponse[None],
            "content": {
                "application/json": {
                    "example": {
                        "metadata": "None",
                        "message": "The uploaded file is empty.",
                        "errorCode": ErrorCodes.EMPTY_FILE_UPLOAD,
                    }
                }
            },
        }
    },
}
