import { TestBed } from '@angular/core/testing';
import { Loader } from './loader';

describe('Loader', () => {
  let loader: Loader;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    loader = TestBed.inject(Loader);
  });

  it('should create', () => {
    expect(loader).toBeTruthy();
  });

  it('should start with loading false', async () => {
    expect(await firstValue(loader.loading$)).toBe(false);
  });

  it('should show the loader while a request is in flight', async () => {
    loader.showLoader();
    expect(await firstValue(loader.loading$)).toBe(true);
  });

  it('should keep the loader visible until every concurrent request completes', async () => {
    loader.showLoader();
    loader.showLoader();

    loader.hideLoader();
    expect(await firstValue(loader.loading$)).toBe(true);

    loader.hideLoader();
    expect(await firstValue(loader.loading$)).toBe(false);
  });

  it('should not go negative when hideLoader is called without a matching showLoader', async () => {
    loader.hideLoader();
    loader.showLoader();
    expect(await firstValue(loader.loading$)).toBe(true);
  });
});

function firstValue<T>(source: { subscribe: (cb: (value: T) => void) => void }): Promise<T> {
  return new Promise((resolve) => {
    source.subscribe((value) => resolve(value));
  });
}
