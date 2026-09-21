/** Mirrors the backend's `ApiErrorResponse` schema returned on handled API failures. */
export interface ApiErrorResponse<T = unknown> {
  metadata: T;
  message: string;
  errorCode: number;
}
