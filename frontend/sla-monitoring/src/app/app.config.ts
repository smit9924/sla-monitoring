import {
  ApplicationConfig,
  ErrorHandler,
  inject,
  provideAppInitializer,
  provideBrowserGlobalErrorListeners,
} from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';

import { routes } from './app.routes';
import { GlobalErrorHandler } from './error/global-error-handler';
import { httpConfigInterceptor } from './interceptors/http-config/http-config-interceptor';
import { loaderInterceptor } from './interceptors/loader/loader-interceptor';
import { Icon } from './services/icon';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    {
      provide: ErrorHandler,
      useClass: GlobalErrorHandler,
    },
    provideRouter(routes),
    provideHttpClient(withInterceptors([loaderInterceptor, httpConfigInterceptor])),
    provideAppInitializer(() => {
      // Eagerly registers every icon in IconList before the app renders.
      inject(Icon);
    }),
  ],
};
