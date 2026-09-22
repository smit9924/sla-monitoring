import { environment } from '../../environments/environment';

export const apiRoutes = {
  health: {
    check: `${environment.apiBaseUrl}/health`,
  },
  files: {
    upload: `${environment.apiBaseUrl}/files`,
    list: `${environment.apiBaseUrl}/files`,
    stats: (guid: string) => `${environment.apiBaseUrl}/files/${guid}/stats`,
    logs: (guid: string) => `${environment.apiBaseUrl}/files/${guid}/logs`,
  },
} as const;
