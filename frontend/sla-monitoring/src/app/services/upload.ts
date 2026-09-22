import { HttpClient, HttpContext, HttpEvent } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { apiRoutes } from '../data/api-routes';
import { SkipLoading } from '../interceptors/loader/loader-interceptor';
import { FileLogsResponse, ServiceLogQuery } from '../types/interfaces/service-log';
import { FileStatsResponse } from '../types/interfaces/stats';
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

  /** Returns the SLA stats accordion's data (overall + per-service uptime, daily failure chart). */
  getFileStats(guid: string): Observable<FileStatsResponse> {
    return this.http.get<FileStatsResponse>(apiRoutes.files.stats(guid));
  }

  /**
   * Returns the logs accordion's data. With no `query`, fetches every service's initial
   * batch (the accordion's first-expand load). With `query`, fetches just that one
   * service's next batch at `query.offset` (a "Show more" click).
   */
  getFileLogs(guid: string, query?: ServiceLogQuery): Observable<FileLogsResponse> {
    return this.http.get<FileLogsResponse>(apiRoutes.files.logs(guid), {
      params: query ? { serviceId: query.serviceId, offset: query.offset } : {},
    });
  }
}
