import { Routes } from '@angular/router';
import { FileDashboard } from './components/dashboard/file-dashboard/file-dashboard';
import { NewUpload } from './components/uploads/new-upload/new-upload';
import { UploadHistory } from './components/uploads/upload-history/upload-history';

export const routes: Routes = [
  {
    path: '',
    component: UploadHistory,
  },
  {
    path: 'upload',
    component: NewUpload,
  },
  {
    path: 'files/:guid',
    component: FileDashboard,
  },
  {
    path: '**',
    redirectTo: '',
  },
];
