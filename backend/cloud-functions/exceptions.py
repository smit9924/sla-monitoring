"""Internal exception used to carry a specific `FileProcessingErrorCode` up to main.py."""

from enums import FileProcessingErrorCode


class CsvProcessingError(Exception):
    """
    Raised at any stage of the CSV pipeline (extension check, download,
    parsing, cleaning, or persistence) to signal exactly why it failed.

    `main.py` catches this one exception type and copies `error_code` and
    `message` straight onto the `uploaded_files` row, so every failure
    reason in the pipeline is recorded the same way.
    """

    def __init__(self, error_code: FileProcessingErrorCode, message: str) -> None:
        self.error_code = error_code
        self.message = message
        super().__init__(message)
