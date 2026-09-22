export const appRoutes = {
  uploadHistory: '/',
  newUpload: '/upload',
  fileDashboard: 'files/:guid',
} as const;

/** Builds a concrete `/files/:guid` link for navigation (see `fileDashboard` above for the route definition). */
export function buildFileDashboardRoute(guid: string): string {
  return `/files/${guid}`;
}
