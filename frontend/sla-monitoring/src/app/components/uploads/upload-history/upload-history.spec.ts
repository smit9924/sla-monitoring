import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';
import { UploadHistory } from './upload-history';
import { Upload } from '../../../services/upload';
import { FileProcessingStatus } from '../../../types/enums/upload';
import { UploadHistoryResponse } from '../../../types/interfaces/upload';

interface TestableUploadHistory {
  totalCount: () => number;
  isInitialLoad: () => boolean;
  isRefreshing: () => boolean;
  sortBy: () => string;
  sortDirection: () => string;
  onSearch: (term: string) => void;
  onSortChange: (sort: { active: string; direction: string }) => void;
  onRefresh: () => void;
  goToUpload: () => Promise<void>;
}

function asTestable(component: UploadHistory): TestableUploadHistory {
  return component as unknown as TestableUploadHistory;
}

const SAMPLE_RESPONSE: UploadHistoryResponse = {
  items: [
    {
      guid: '1',
      originalFilename: 'logs.csv',
      status: FileProcessingStatus.SUCCESS,
      errorCode: null,
      errorMessage: null,
      rowCount: 10,
      fileSizeBytes: 100,
      uploadedAt: new Date().toISOString(),
      processedAt: new Date().toISOString(),
    },
  ],
  totalCount: 1,
  pageNumber: 1,
  pageSize: 10,
};

describe('UploadHistory', () => {
  let uploadService: { listHistory: ReturnType<typeof vi.fn> };
  let router: { navigateByUrl: ReturnType<typeof vi.fn> };

  function createComponent(): UploadHistory {
    uploadService = { listHistory: vi.fn().mockReturnValue(of(SAMPLE_RESPONSE)) };
    router = { navigateByUrl: vi.fn() };

    TestBed.configureTestingModule({
      providers: [
        { provide: Upload, useValue: uploadService },
        { provide: Router, useValue: router },
      ],
    });

    const fixture = TestBed.createComponent(UploadHistory);
    fixture.detectChanges();
    return fixture.componentInstance;
  }

  it('should load the first page of upload history on init', () => {
    const testable = asTestable(createComponent());

    expect(uploadService.listHistory).toHaveBeenCalledWith({
      searchTerm: '',
      pageSize: 10,
      sortBy: 'uploadedAt',
      sortDirection: 'desc',
      pageNumber: 1,
    });
    expect(testable.totalCount()).toBe(1);
    expect(testable.isInitialLoad()).toBe(false);
  });

  it('should reset to the first page and re-request when searching', () => {
    const testable = asTestable(createComponent());
    uploadService.listHistory.mockClear();

    testable.onSearch('invoice');

    expect(uploadService.listHistory).toHaveBeenCalledWith(
      expect.objectContaining({ searchTerm: 'invoice', pageNumber: 1 }),
    );
  });

  it('should update sort state and re-request when the sort changes', () => {
    const testable = asTestable(createComponent());
    uploadService.listHistory.mockClear();

    testable.onSortChange({ active: 'originalFilename', direction: 'asc' });

    expect(testable.sortBy()).toBe('originalFilename');
    expect(testable.sortDirection()).toBe('asc');
    expect(uploadService.listHistory).toHaveBeenCalledWith(
      expect.objectContaining({
        sortBy: 'originalFilename',
        sortDirection: 'asc',
        pageNumber: 1,
      }),
    );
  });

  it('should turn off the refreshing flag once the refresh request completes', () => {
    const testable = asTestable(createComponent());

    testable.onRefresh();

    expect(testable.isRefreshing()).toBe(false);
  });

  it('should navigate to the upload page', async () => {
    const testable = asTestable(createComponent());

    await testable.goToUpload();

    expect(router.navigateByUrl).toHaveBeenCalledWith('/upload');
  });
});
