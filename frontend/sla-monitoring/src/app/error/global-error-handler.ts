import { ErrorHandler } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { TimeoutError } from 'rxjs';
import { ApiErrorResponse } from '../types/interfaces/api';

/**
 * Centralized handler for every uncaught error in the app (thrown template/
 * component code, rejected promises, and any HttpErrorResponse that a
 * caller didn't already handle).
 *
 * Categorization order matters here: a `status: 0` HttpErrorResponse means
 * the browser never got a response at all (offline, DNS failure, connection
 * refused, a CORS rejection, ...) — it is never something the backend
 * produced, so it must be checked before treating the error as a server
 * response. Skipping that check is what causes network failures to get
 * mislabeled as generic server/unexpected errors.
 */
export class GlobalErrorHandler implements ErrorHandler {
  handleError(error: unknown): void {
    if (error instanceof TimeoutError) {
      console.error('Request timed out before the server responded.', error);
      return;
    }

    if (error instanceof HttpErrorResponse) {
      this.handleHttpError(error);
      return;
    }

    console.error('Unexpected error occurred:', error);
  }

  private handleHttpError(error: HttpErrorResponse): void {
    if (error.status === 0) {
      console.error('Network error: unable to reach the server.', error);
      return;
    }

    const body = error.error as Partial<ApiErrorResponse<unknown>> | null;
    const message = body?.message ?? error.message;

    if (error.status >= 500) {
      console.error(`Server error (${error.status}): ${message}`, error);
      return;
    }

    console.error(`Request error (${error.status}): ${message}`, error);
  }
}
