"""File-upload constraints for the `POST /files` endpoint.

Kept as plain constants (rather than `.env`-configurable settings) since
they describe a fixed product constraint from the assignment spec, not an
environment-specific value.
"""

# Only CSV files are accepted for SLA log ingestion. Checked against the
# uploaded file's extension, matching the `csv-parser` cloud function's own
# `_validate_extension` check.
ALLOWED_UPLOAD_EXTENSIONS = frozenset({"csv"})

# 1 GiB, per the assignment's upload size constraint.
MAX_UPLOAD_FILE_SIZE_BYTES = 1 * 1024 * 1024 * 1024
