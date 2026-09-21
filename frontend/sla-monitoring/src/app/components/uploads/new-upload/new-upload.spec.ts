import { HttpEventType } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';
import { NewUpload } from './new-upload';
import { MAX_UPLOAD_FILE_SIZE_BYTES } from '../../../data/upload-constraints';
import { Dialog } from '../../../services/dialog';
import { Upload } from '../../../services/upload';

interface TestableNewUpload {
  selectedFile: () => File | null;
  validationError: () => string | null;
  isValid: () => boolean;
  onFileInputChange: (event: Event) => void;
  onSubmit: () => void;
}

function asTestable(component: NewUpload): TestableNewUpload {
  return component as unknown as TestableNewUpload;
}

function fileInputChangeEvent(file: File): Event {
  return { target: { files: [file], value: '' } } as unknown as Event;
}

describe('NewUpload', () => {
  let uploadService: { uploadFile: ReturnType<typeof vi.fn> };
  let dialog: { openOkDialog: ReturnType<typeof vi.fn> };
  let router: { navigateByUrl: ReturnType<typeof vi.fn> };

  function createComponent(): NewUpload {
    uploadService = { uploadFile: vi.fn() };
    dialog = { openOkDialog: vi.fn().mockReturnValue({ afterClosed: () => of(undefined) }) };
    router = { navigateByUrl: vi.fn() };

    TestBed.configureTestingModule({
      providers: [
        { provide: Upload, useValue: uploadService },
        { provide: Dialog, useValue: dialog },
        { provide: Router, useValue: router },
      ],
    });

    return TestBed.createComponent(NewUpload).componentInstance;
  }

  it('should reject a non-CSV file and keep submit disabled', () => {
    const testable = asTestable(createComponent());
    const file = new File(['data'], 'notes.txt', { type: 'text/plain' });

    testable.onFileInputChange(fileInputChangeEvent(file));

    expect(testable.validationError()).toContain('.csv');
    expect(testable.isValid()).toBe(false);
  });

  it('should reject an empty file', () => {
    const testable = asTestable(createComponent());
    const file = new File([], 'logs.csv', { type: 'text/csv' });

    testable.onFileInputChange(fileInputChangeEvent(file));

    expect(testable.validationError()).toContain('empty');
    expect(testable.isValid()).toBe(false);
  });

  it('should reject a file larger than the max upload size', () => {
    const testable = asTestable(createComponent());
    const file = new File(['data'], 'logs.csv', { type: 'text/csv' });
    Object.defineProperty(file, 'size', { value: MAX_UPLOAD_FILE_SIZE_BYTES + 1 });

    testable.onFileInputChange(fileInputChangeEvent(file));

    expect(testable.validationError()).toContain('too large');
    expect(testable.isValid()).toBe(false);
  });

  it('should accept a valid CSV file and enable submit', () => {
    const testable = asTestable(createComponent());
    const file = new File(['a,b\n1,2'], 'logs.csv', { type: 'text/csv' });

    testable.onFileInputChange(fileInputChangeEvent(file));

    expect(testable.validationError()).toBeNull();
    expect(testable.isValid()).toBe(true);
  });

  it('should upload the selected file, show a success dialog, and redirect to the history page', () => {
    const component = createComponent();
    const testable = asTestable(component);
    const file = new File(['a,b\n1,2'], 'logs.csv', { type: 'text/csv' });

    uploadService.uploadFile.mockReturnValue(
      of({
        type: HttpEventType.Response,
        body: { guid: 'abc' },
      }),
    );

    testable.onFileInputChange(fileInputChangeEvent(file));
    testable.onSubmit();

    expect(uploadService.uploadFile).toHaveBeenCalledWith(file);
    expect(dialog.openOkDialog).toHaveBeenCalledWith(
      'Upload successful',
      expect.stringContaining('upload history page'),
    );
    expect(router.navigateByUrl).toHaveBeenCalledWith('/');
  });

  it('should not upload when no file has been selected', () => {
    const testable = asTestable(createComponent());

    testable.onSubmit();

    expect(uploadService.uploadFile).not.toHaveBeenCalled();
  });
});
