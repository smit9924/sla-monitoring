/** Mirrors the backend's `FileProcessingStatus` enum on `UploadedFile.status`. */
export enum FileProcessingStatus {
  QUEUED = 'queued',
  IN_PROGRESS = 'in_progress',
  SUCCESS = 'success',
  ERROR = 'error',
}
