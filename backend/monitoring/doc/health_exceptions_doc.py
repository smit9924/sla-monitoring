from monitoring.schemas.common_schemas import ApiErrorResponse
from monitoring.types.error_codes import ErrorCodes

HEALTH_EXCEPTIONS_DOC = {
    "ServiceUnavailableException": {
        503: {
            "description": "The service failed its own health check.",
            "model": ApiErrorResponse[None],
            "content": {
                "application/json": {
                    "example": {
                        "metadata": "None",
                        "message": "The service is currently unavailable. Please try again later.",
                        "errorCode": ErrorCodes.SERVICE_UNAVAILABLE
                    }
                }
            },
        }
    },
}
