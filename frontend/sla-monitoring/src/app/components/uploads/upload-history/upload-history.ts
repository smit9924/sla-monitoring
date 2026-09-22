import { DatePipe } from '@angular/common';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Router } from '@angular/router';
import { finalize } from 'rxjs';
import { Searchbar } from '../../common/searchbar/searchbar';
import { appRoutes, buildFileDashboardRoute } from '../../../data/app-routes';
import { Upload } from '../../../services/upload';
import { FileProcessingStatus } from '../../../types/enums/upload';
import { UploadedFileListItem, UploadHistorySortBy } from '../../../types/interfaces/upload';

/**
 * Landing page: a paginated, sortable, searchable history of every file
 * uploaded for SLA log ingestion. State is entirely server-side, mirroring
 * every other listing page's pattern -- `[dataSource]` is bound directly to
 * the array the API returns, and every search/sort/page change re-requests
 * the backend rather than filtering/sorting/paging client-side.
 */
@Component({
  selector: 'app-upload-history',
  imports: [
    DatePipe,
    Searchbar,
    MatTableModule,
    MatSortModule,
    MatPaginatorModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
  ],
  templateUrl: './upload-history.html',
  styleUrl: './upload-history.scss',
})
export class UploadHistory implements OnInit {
  private readonly uploadService = inject(Upload);
  private readonly router = inject(Router);

  protected readonly FileProcessingStatus = FileProcessingStatus;
  protected readonly displayedColumns = ['originalFilename', 'uploadedAt', 'status', 'rowCount'];
  protected readonly pageSizeOptions = [10, 25, 50];

  protected readonly files = signal<UploadedFileListItem[]>([]);
  protected readonly totalCount = signal(0);
  protected readonly pageIndex = signal(0);
  protected readonly pageSize = signal(10);
  protected readonly sortBy = signal<UploadHistorySortBy>('uploadedAt');
  protected readonly sortDirection = signal<'asc' | 'desc'>('desc');
  protected readonly searchTerm = signal('');
  protected readonly isInitialLoad = signal(true);
  protected readonly isRefreshing = signal(false);

  protected readonly hasFiles = computed(() => this.totalCount() > 0);
  protected readonly isEmptySearch = computed(() => !this.hasFiles() && !!this.searchTerm());

  ngOnInit(): void {
    this.loadFiles();
  }

  protected onSearch(term: string): void {
    this.searchTerm.set(term);
    this.pageIndex.set(0);
    this.loadFiles();
  }

  protected onSortChange(sort: Sort): void {
    this.sortBy.set((sort.active as UploadHistorySortBy) || 'uploadedAt');
    this.sortDirection.set(sort.direction === 'asc' ? 'asc' : 'desc');
    this.pageIndex.set(0);
    this.loadFiles();
  }

  protected onPageChange(event: PageEvent): void {
    this.pageIndex.set(event.pageIndex);
    this.pageSize.set(event.pageSize);
    this.loadFiles();
  }

  /** Re-requests the current page/search/sort from the backend, e.g. to pick up newly processed files. */
  protected onRefresh(): void {
    this.isRefreshing.set(true);
    this.loadFiles(() => this.isRefreshing.set(false));
  }

  protected async goToUpload(): Promise<void> {
    await this.router.navigateByUrl(appRoutes.newUpload);
  }

  /** Only successfully-processed files have statistics/logs to show; the filename link is gated on that. */
  protected async viewFileStats(file: UploadedFileListItem): Promise<void> {
    if (file.status !== FileProcessingStatus.SUCCESS) {
      return;
    }
    await this.router.navigateByUrl(buildFileDashboardRoute(file.guid));
  }

  protected statusLabel(status: FileProcessingStatus): string {
    switch (status) {
      case FileProcessingStatus.QUEUED:
        return 'Queued';
      case FileProcessingStatus.IN_PROGRESS:
        return 'Processing';
      case FileProcessingStatus.SUCCESS:
        return 'Success';
      case FileProcessingStatus.ERROR:
        return 'Error';
    }
  }

  private loadFiles(onDone?: () => void): void {
    this.uploadService
      .listHistory({
        searchTerm: this.searchTerm() || '',
        pageSize: this.pageSize(),
        sortBy: this.sortBy(),
        sortDirection: this.sortDirection(),
        pageNumber: this.pageIndex() + 1,
      })
      .pipe(
        finalize(() => {
          this.isInitialLoad.set(false);
          onDone?.();
        }),
      )
      .subscribe((response) => {
        this.files.set(response.items);
        this.totalCount.set(response.totalCount);
      });
  }
}
