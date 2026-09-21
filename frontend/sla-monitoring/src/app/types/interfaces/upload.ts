import { FileProcessingStatus } from '../enums/upload';
import { PaginatedQuery, PaginatedResponse } from './pagination';

/** Fields the upload history listing can be sorted by; mirrors the backend's `UploadedFileSortBy`. */
export type UploadHistorySortBy = 'originalFilename' | 'uploadedAt' | 'status' | 'fileSizeBytes';

export type UploadHistoryQuery = PaginatedQuery<UploadHistorySortBy>;

/** One row of the upload history table; mirrors the backend's `UploadedFileListItem` schema. */
export interface UploadedFileListItem {
  guid: string;
  originalFilename: string;
  status: FileProcessingStatus;
  errorCode: string | null;
  errorMessage: string | null;
  rowCount: number | null;
  fileSizeBytes: number | null;
  uploadedAt: string;
  processedAt: string | null;
}

export type UploadHistoryResponse = PaginatedResponse<UploadedFileListItem>;

/** Returned by the upload endpoint once a file has been accepted and stored. */
export interface UploadedFileResponse {
  guid: string;
  originalFilename: string;
  status: FileProcessingStatus;
  fileSizeBytes: number | null;
  uploadedAt: string;
}
