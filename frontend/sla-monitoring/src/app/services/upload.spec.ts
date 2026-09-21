import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { apiRoutes } from '../data/api-routes';
import { SkipLoading } from '../interceptors/loader/loader-interceptor';
import { Upload } from './upload';

describe('Upload', () => {
  let service: Upload;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(Upload);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should request the upload history with the given query params', () => {
    service
      .listHistory({
        searchTerm: 'invoice',
        pageSize: 25,
        sortBy: 'uploadedAt',
        sortDirection: 'desc',
        pageNumber: 2,
      })
      .subscribe();

    const req = httpMock.expectOne(
      (request) =>
        request.url === apiRoutes.files.list &&
        request.params.get('searchTerm') === 'invoice' &&
        request.params.get('pageSize') === '25' &&
        request.params.get('sortBy') === 'uploadedAt' &&
        request.params.get('sortDirection') === 'desc' &&
        request.params.get('pageNumber') === '2',
    );
    expect(req.request.method).toBe('GET');
    req.flush({ items: [], totalCount: 0, pageNumber: 2, pageSize: 25 });
  });

  it('should default an empty search term when none is given', () => {
    service
      .listHistory({ pageSize: 10, sortBy: 'uploadedAt', sortDirection: 'desc', pageNumber: 1 })
      .subscribe();

    const req = httpMock.expectOne((request) => request.url === apiRoutes.files.list);
    expect(req.request.params.get('searchTerm')).toBe('');
    req.flush({ items: [], totalCount: 0, pageNumber: 1, pageSize: 10 });
  });

  it('should upload the file as multipart form data and skip the global loader', () => {
    const file = new File(['a,b\n1,2'], 'logs.csv', { type: 'text/csv' });

    service.uploadFile(file).subscribe();

    const req = httpMock.expectOne(apiRoutes.files.upload);
    expect(req.request.method).toBe('POST');
    expect(req.request.reportProgress).toBe(true);
    expect(req.request.context.get(SkipLoading)).toBe(true);
    expect(req.request.body).toBeInstanceOf(FormData);
    expect((req.request.body as FormData).get('file')).toBe(file);

    req.flush({
      guid: 'abc',
      originalFilename: 'logs.csv',
      status: 'queued',
      fileSizeBytes: file.size,
      uploadedAt: new Date().toISOString(),
    });
  });
});
