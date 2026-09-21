import { environment } from '../../environments/environment';

export const apiRoutes = {
  health: {
    check: `${environment.apiBaseUrl}/health`,
  },
  files: {
    upload: `${environment.apiBaseUrl}/files`,
    list: `${environment.apiBaseUrl}/files`,
  },
} as const;
