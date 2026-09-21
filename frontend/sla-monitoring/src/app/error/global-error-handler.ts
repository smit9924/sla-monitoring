import { ErrorHandler, inject } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { TimeoutError } from 'rxjs';
import { ApiErrorResponse } from '../types/interfaces/api';
import { Dialog } from '../services/dialog';

/**
 * Centralized handler for every uncaught error in the app (thrown template/
 * component code, rejected promises, and any HttpErrorResponse that a
 * caller didn't already handle). Logs full details to the console and
 * surfaces a categorized, user-facing dialog via `Dialog`.
 *
 * Categorization order matters here: a `status: 0` HttpErrorResponse means
 * the browser never got a response at all (offline, DNS failure, connection
 * refused, a CORS rejection, ...) — it is never something the backend
 * produced, so it must be checked before treating the error as a server
 * response. Skipping that check is what causes network failures to get
 * mislabeled as generic server/unexpected errors.
 */
export class GlobalErrorHandler implements ErrorHandler {
  private readonly dialog = inject(Dialog);

  handleError(error: unknown): void {
    if (error instanceof TimeoutError) {
      this.report(
        'Request Timeout',
        'The request took too long to complete. Please check your internet connection and try again.',
        error,
      );
      return;
    }

    if (error instanceof HttpErrorResponse) {
      this.handleHttpError(error);
      return;
    }

    this.report(
      'Unexpected Error',
      'Something went wrong. Please refresh the page and try again. If the problem persists, contact support.',
      error,
    );
  }

  private handleHttpError(error: HttpErrorResponse): void {
    if (error.status === 0) {
      this.report(
        'Network Error',
        'A network error occurred. Please check your internet connection and try again.',
        error,
      );
      return;
    }

    const body = error.error as Partial<ApiErrorResponse<unknown>> | null;
    const message = body?.message;

    if (error.status >= 500) {
      this.report(
        'Server Error',
        message ?? 'The server encountered an error. Please try again later.',
        error,
      );
      return;
    }

    this.report('Request Error', message ?? 'The request could not be completed.', error);
  }

  private report(title: string, message: string, error: unknown): void {
    console.error(`${title}: ${message}`, error);
    this.dialog.openOkDialog(title, message);
  }
}
