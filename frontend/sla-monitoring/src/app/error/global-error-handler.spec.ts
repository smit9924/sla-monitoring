import { HttpErrorResponse } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { TimeoutError } from 'rxjs';
import { GlobalErrorHandler } from './global-error-handler';
import { Dialog } from '../services/dialog';

describe('GlobalErrorHandler', () => {
  let handler: GlobalErrorHandler;
  let dialog: { openOkDialog: ReturnType<typeof vi.fn> };
  let consoleErrorSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    dialog = { openOkDialog: vi.fn() };
    TestBed.configureTestingModule({
      providers: [GlobalErrorHandler, { provide: Dialog, useValue: dialog }],
    });
    handler = TestBed.inject(GlobalErrorHandler);
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
  });

  it('should report a status-0 HttpErrorResponse as a network error, not a server error', () => {
    const error = new HttpErrorResponse({ status: 0, statusText: 'Unknown Error' });

    handler.handleError(error);

    expect(consoleErrorSpy).toHaveBeenCalledWith(expect.stringContaining('Network Error'), error);
    expect(dialog.openOkDialog).toHaveBeenCalledWith(
      'Network Error',
      expect.stringContaining('internet connection'),
    );
  });

  it('should report a TimeoutError as a timeout, not a network or server error', () => {
    const error = new TimeoutError();

    handler.handleError(error);

    expect(consoleErrorSpy).toHaveBeenCalledWith(expect.stringContaining('Request Timeout'), error);
    expect(dialog.openOkDialog).toHaveBeenCalledWith(
      'Request Timeout',
      expect.stringContaining('too long'),
    );
  });

  it('should report a 5xx HttpErrorResponse as a server error, using the backend message', () => {
    const error = new HttpErrorResponse({
      status: 503,
      statusText: 'Service Unavailable',
      error: { message: 'Service is down', errorCode: 1001, metadata: null },
    });

    handler.handleError(error);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.stringMatching(/^Server Error: Service is down$/),
      error,
    );
    expect(dialog.openOkDialog).toHaveBeenCalledWith('Server Error', 'Service is down');
  });

  it('should report a 4xx HttpErrorResponse as a request error, distinct from a server error', () => {
    const error = new HttpErrorResponse({
      status: 404,
      statusText: 'Not Found',
      error: { message: 'Resource not found', errorCode: 1002, metadata: null },
    });

    handler.handleError(error);

    expect(dialog.openOkDialog).toHaveBeenCalledWith('Request Error', 'Resource not found');
  });

  it('should fall back to a generic message when no structured body is present', () => {
    const error = new HttpErrorResponse({ status: 500, statusText: 'Internal Server Error' });

    handler.handleError(error);

    expect(dialog.openOkDialog).toHaveBeenCalledWith(
      'Server Error',
      'The server encountered an error. Please try again later.',
    );
  });

  it('should report anything else as an unexpected error', () => {
    const error = new Error('boom');

    handler.handleError(error);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.stringContaining('Unexpected Error'),
      error,
    );
    expect(dialog.openOkDialog).toHaveBeenCalledWith(
      'Unexpected Error',
      expect.stringContaining('refresh the page'),
    );
  });
});
