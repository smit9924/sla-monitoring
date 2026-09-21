import { HttpErrorResponse } from '@angular/common/http';
import { TimeoutError } from 'rxjs';
import { GlobalErrorHandler } from './global-error-handler';

describe('GlobalErrorHandler', () => {
  let handler: GlobalErrorHandler;
  let consoleErrorSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    handler = new GlobalErrorHandler();
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
  });

  it('should report a status-0 HttpErrorResponse as a network error, not a server error', () => {
    const error = new HttpErrorResponse({ status: 0, statusText: 'Unknown Error' });

    handler.handleError(error);

    expect(consoleErrorSpy).toHaveBeenCalledWith(expect.stringContaining('Network error'), error);
  });

  it('should report a TimeoutError as a timeout, not a network or server error', () => {
    const error = new TimeoutError();

    handler.handleError(error);

    expect(consoleErrorSpy).toHaveBeenCalledWith(expect.stringContaining('timed out'), error);
  });

  it('should report a 5xx HttpErrorResponse as a server error', () => {
    const error = new HttpErrorResponse({
      status: 503,
      statusText: 'Service Unavailable',
      error: { message: 'Service is down', errorCode: 1001, metadata: null },
    });

    handler.handleError(error);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.stringMatching(/^Server error \(503\): Service is down$/),
      error,
    );
  });

  it('should report a 4xx HttpErrorResponse as a request error, distinct from a server error', () => {
    const error = new HttpErrorResponse({
      status: 404,
      statusText: 'Not Found',
      error: { message: 'Resource not found', errorCode: 1002, metadata: null },
    });

    handler.handleError(error);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.stringMatching(/^Request error \(404\): Resource not found$/),
      error,
    );
  });

  it('should fall back to the raw HttpErrorResponse message when no structured body is present', () => {
    const error = new HttpErrorResponse({ status: 500, statusText: 'Internal Server Error' });

    handler.handleError(error);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.stringContaining('Server error (500)'),
      error,
    );
  });

  it('should report anything else as an unexpected error', () => {
    const error = new Error('boom');

    handler.handleError(error);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.stringContaining('Unexpected error'),
      error,
    );
  });
});
