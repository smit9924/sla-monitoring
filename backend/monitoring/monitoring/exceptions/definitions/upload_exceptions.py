from monitoring.exceptions.definitions.base import BaseException
from monitoring.types.error_codes import ErrorCodes


class InvalidFileTypeException(BaseException):
    """Raised when an uploaded file's extension is not one of `ALLOWED_UPLOAD_EXTENSIONS`."""

    def __init__(self, message: str = "Only CSV files are supported.") -> None:
        super().__init__(ErrorCodes.INVALID_FILE_TYPE, message)


class FileTooLargeException(BaseException):
    """Raised when an uploaded file exceeds `MAX_UPLOAD_FILE_SIZE_BYTES`."""

    def __init__(
        self,
        message: str = "The file exceeds the maximum allowed upload size.",
    ) -> None:
        super().__init__(ErrorCodes.FILE_TOO_LARGE, message)


class EmptyFileUploadException(BaseException):
    """Raised when an uploaded file has zero bytes."""

    def __init__(self, message: str = "The uploaded file is empty.") -> None:
        super().__init__(ErrorCodes.EMPTY_FILE_UPLOAD, message)
