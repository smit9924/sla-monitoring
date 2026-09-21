import { HttpContextToken, HttpInterceptorFn } from '@angular/common/http';
import { timeout } from 'rxjs';
import { HttpRequestTimeout } from '../../types/enums/http';

export const REQUEST_TIMEOUT = new HttpContextToken<HttpRequestTimeout>(
  () => HttpRequestTimeout.DISABLED,
);

export const httpConfigInterceptor: HttpInterceptorFn = (req, next) => {
  const timeoutValue = req.context.get(REQUEST_TIMEOUT);

  if (timeoutValue === HttpRequestTimeout.DISABLED) {
    return next(req);
  }

  // RxJS `timeout` throws a `TimeoutError` if the request exceeds the given
  // duration. It propagates through the stream and is handled centrally by
  // `GlobalErrorHandler`.
  return next(req).pipe(timeout(timeoutValue));
};
