import { HttpContext, HttpEvent, HttpHandlerFn, HttpRequest } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { firstValueFrom, NEVER, of, TimeoutError } from 'rxjs';
import { httpConfigInterceptor, REQUEST_TIMEOUT } from './http-config-interceptor';
import { HttpRequestTimeout } from '../../types/enums/http';

function stubHandler(response: HttpEvent<unknown>): HttpHandlerFn {
  return vi.fn(() => of(response));
}

describe('httpConfigInterceptor', () => {
  const req = new HttpRequest('GET', '/api/v1/health');

  it('should forward the request untouched when the timeout is disabled', () => {
    const next = stubHandler({} as HttpEvent<unknown>);

    TestBed.runInInjectionContext(() => httpConfigInterceptor(req, next));

    expect(next).toHaveBeenCalledWith(req);
  });

  it('should let a request that responds in time pass through unchanged', async () => {
    const response = { ok: true } as unknown as HttpEvent<unknown>;
    const reqWithTimeout = new HttpRequest('GET', '/api/v1/health', {
      context: new HttpContext().set(REQUEST_TIMEOUT, HttpRequestTimeout.TIMEOUT_10S),
    });
    const next = stubHandler(response);

    const result$ = TestBed.runInInjectionContext(() =>
      httpConfigInterceptor(reqWithTimeout, next),
    );

    await expect(firstValueFrom(result$)).resolves.toBe(response);
  });

  it('should surface a TimeoutError once a request exceeds its configured timeout', async () => {
    const reqWithTimeout = new HttpRequest('GET', '/api/v1/health', {
      context: new HttpContext().set(REQUEST_TIMEOUT, HttpRequestTimeout.TIMEOUT_10S),
    });
    // NEVER never emits, so the interceptor's timeout operator is the only
    // thing that can cause this observable to terminate.
    const next: HttpHandlerFn = vi.fn(() => NEVER);

    vi.useFakeTimers();
    try {
      const result$ = TestBed.runInInjectionContext(() =>
        httpConfigInterceptor(reqWithTimeout, next),
      );
      const assertion = expect(firstValueFrom(result$)).rejects.toBeInstanceOf(TimeoutError);
      await vi.advanceTimersByTimeAsync(HttpRequestTimeout.TIMEOUT_10S);
      await assertion;
    } finally {
      vi.useRealTimers();
    }
  });
});
