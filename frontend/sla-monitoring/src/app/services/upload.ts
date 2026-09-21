import { HttpClient, HttpContext, HttpEvent } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { apiRoutes } from '../data/api-routes';
import { SkipLoading } from '../interceptors/loader/loader-interceptor';
import {
  UploadedFileResponse,
  UploadHistoryQuery,
  UploadHistoryResponse,
} from '../types/interfaces/upload';

@Injectable({
  providedIn: 'root',
})
export class Upload {
  private readonly http = inject(HttpClient);

  /** Returns a paginated, sortable, searchable page of the upload history. */
  listHistory(query: UploadHistoryQuery): Observable<UploadHistoryResponse> {
    return this.http.get<UploadHistoryResponse>(apiRoutes.files.list, {
      params: {
        pageSize: query.pageSize,
        sortBy: query.sortBy,
        sortDirection: query.sortDirection,
        pageNumber: query.pageNumber,
        searchTerm: query.searchTerm ?? '',
      },
    });
  }

  /**
   * Uploads `file` and streams back progress + the final response as HTTP events, so the
   * caller can drive a determinate progress bar for large files.
   *
   * Opts out of the global loader (`SkipLoading`) since the upload has its own, more useful,
   * inline progress indicator.
   */
  uploadFile(file: File): Observable<HttpEvent<UploadedFileResponse>> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<UploadedFileResponse>(apiRoutes.files.upload, formData, {
      reportProgress: true,
      observe: 'events',
      context: new HttpContext().set(SkipLoading, true),
    });
  }
}
