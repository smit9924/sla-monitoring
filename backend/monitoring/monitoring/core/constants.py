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

# Cloud-provider SLA convention referenced in the assignment's own framing
# ("if availability drops below 99.9%, the customer gets a billing credit").
# Used as the pass/fail cutoff for the per-service and overall uptime badges.
SLA_UPTIME_THRESHOLD_PERCENTAGE = 99.9

# A response is only ever classified success/failure by its HTTP status
# class: 2xx/3xx are success, everything else (4xx, 5xx, and any
# out-of-range sentinel like the dataset's `999`) counts as a failure. This
# mirrors the assignment's instruction to treat 4xx/5xx as failure, and
# conservatively folds non-HTTP sentinel codes into "failure" too rather than
# silently treating them as healthy.
FAILURE_STATUS_CODE_THRESHOLD = 400

# Logs view (upload stats page, second accordion) is paginated per service in
# fixed-size batches rather than a client-chosen page size, so "Show more"
# always fetches predictably-sized chunks.
SERVICE_LOGS_BATCH_SIZE = 200
