from monitoring.exceptions.definitions.base import BaseException
from monitoring.types.error_codes import ErrorCodes


class ServiceUnavailableException(BaseException):
    """Raised when the service fails its own health check."""

    def __init__(
        self,
        message: str = "The service is currently unavailable. Please try again later."
    ) -> None:
        super().__init__(ErrorCodes.SERVICE_UNAVAILABLE, message)
