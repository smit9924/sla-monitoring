import { HttpContextToken, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { finalize } from 'rxjs';
import { Loader } from '../../services/loader';

/**
 * Set on a request's `HttpContext` to opt that request out of the global
 * loader (e.g. silent background polling).
 */
export const SkipLoading = new HttpContextToken<boolean>(() => false);

export const loaderInterceptor: HttpInterceptorFn = (req, next) => {
  const loader = inject(Loader);

  if (req.context.get(SkipLoading)) {
    return next(req);
  }

  loader.showLoader();

  return next(req).pipe(finalize(() => loader.hideLoader()));
};
