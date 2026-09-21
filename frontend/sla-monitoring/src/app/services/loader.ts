import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class Loader {
  private readonly loadingSubject = new BehaviorSubject<boolean>(false);

  /** Number of in-flight requests currently holding the loader open. */
  private activeRequests = 0;

  readonly loading$ = this.loadingSubject.asObservable();

  showLoader(): void {
    this.activeRequests++;
    this.loadingSubject.next(true);
  }

  /**
   * Only hides the loader once every request that called `showLoader()` has
   * completed, so one fast request finishing early doesn't hide it while a
   * slower, concurrent request is still in flight.
   */
  hideLoader(): void {
    this.activeRequests = Math.max(0, this.activeRequests - 1);
    if (this.activeRequests === 0) {
      this.loadingSubject.next(false);
    }
  }
}
