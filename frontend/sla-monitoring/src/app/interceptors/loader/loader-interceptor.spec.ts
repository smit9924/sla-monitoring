import { HttpContext, HttpEvent, HttpHandlerFn, HttpRequest } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { firstValueFrom, of, throwError } from 'rxjs';
import { loaderInterceptor, SkipLoading } from './loader-interceptor';
import { Loader } from '../../services/loader';

function stubHandler(): HttpHandlerFn {
  return vi.fn(() => of({} as HttpEvent<unknown>));
}

describe('loaderInterceptor', () => {
  let loader: Loader;
  const req = new HttpRequest('GET', '/api/v1/health');

  beforeEach(() => {
    TestBed.configureTestingModule({});
    loader = TestBed.inject(Loader);
  });

  it('should show and then hide the loader around a successful request', async () => {
    const showSpy = vi.spyOn(loader, 'showLoader');
    const hideSpy = vi.spyOn(loader, 'hideLoader');
    const next = stubHandler();

    await firstValueFrom(TestBed.runInInjectionContext(() => loaderInterceptor(req, next)));

    expect(showSpy).toHaveBeenCalledTimes(1);
    expect(hideSpy).toHaveBeenCalledTimes(1);
  });

  it('should still hide the loader when the request errors', async () => {
    const hideSpy = vi.spyOn(loader, 'hideLoader');
    const next: HttpHandlerFn = vi.fn(() => throwError(() => new Error('boom')));

    await expect(
      firstValueFrom(TestBed.runInInjectionContext(() => loaderInterceptor(req, next))),
    ).rejects.toThrow('boom');

    expect(hideSpy).toHaveBeenCalledTimes(1);
  });

  it('should skip the loader entirely when SkipLoading is set', async () => {
    const showSpy = vi.spyOn(loader, 'showLoader');
    const skipReq = new HttpRequest('GET', '/api/v1/health', {
      context: new HttpContext().set(SkipLoading, true),
    });
    const next = stubHandler();

    await firstValueFrom(TestBed.runInInjectionContext(() => loaderInterceptor(skipReq, next)));

    expect(showSpy).not.toHaveBeenCalled();
  });
});
