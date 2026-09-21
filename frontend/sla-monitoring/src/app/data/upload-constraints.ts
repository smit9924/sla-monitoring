/**
 * Client-side mirror of the backend's `core/constants.py` upload limits, so
 * an invalid file is rejected immediately on selection instead of only
 * after a round trip to the API.
 */
export const MAX_UPLOAD_FILE_SIZE_BYTES = 1 * 1024 * 1024 * 1024; // 1 GB

export const ALLOWED_UPLOAD_EXTENSIONS = ['csv'] as const;
