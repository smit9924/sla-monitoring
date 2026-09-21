import { environment } from '../../environments/environment';

export const apiRoutes = {
  health: {
    check: `${environment.apiBaseUrl}/health`,
  },
} as const;
