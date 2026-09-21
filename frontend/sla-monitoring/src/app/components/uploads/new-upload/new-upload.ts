import { HttpEventType } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { Router } from '@angular/router';
import { finalize } from 'rxjs';
import { appRoutes } from '../../../data/app-routes';
import {
  ALLOWED_UPLOAD_EXTENSIONS,
  MAX_UPLOAD_FILE_SIZE_BYTES,
} from '../../../data/upload-constraints';
import { Dialog } from '../../../services/dialog';
import { Upload } from '../../../services/upload';

/**
 * Upload page: a custom file picker (drag-drop + browse) that validates
 * type and size on selection, before the Submit button is even enabled, so
 * an invalid file never reaches the API. Errors returned by the API itself
 * (e.g. a storage failure) are left unhandled here and surface through the
 * app's `GlobalErrorHandler`, same as every other unhandled HTTP failure.
 */
@Component({
  selector: 'app-new-upload',
  imports: [MatButtonModule, MatIconModule, MatProgressBarModule],
  templateUrl: './new-upload.html',
  styleUrl: './new-upload.scss',
})
export class NewUpload {
  private readonly uploadService = inject(Upload);
  private readonly dialog = inject(Dialog);
  private readonly router = inject(Router);

  protected readonly maxFileSizeLabel = this.formatBytes(MAX_UPLOAD_FILE_SIZE_BYTES);

  protected readonly selectedFile = signal<File | null>(null);
  protected readonly validationError = signal<string | null>(null);
  protected readonly isDragging = signal(false);
  protected readonly isUploading = signal(false);
  protected readonly uploadProgress = signal(0);

  protected readonly isValid = computed(
    () => this.selectedFile() !== null && this.validationError() === null,
  );

  protected onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragging.set(true);
  }

  protected onDragLeave(): void {
    this.isDragging.set(false);
  }

  protected onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragging.set(false);

    const file = event.dataTransfer?.files?.[0];
    if (file) {
      this.setFile(file);
    }
  }

  protected onFileInputChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      this.setFile(file);
    }
    // Reset so selecting the same file again still fires a `change` event.
    input.value = '';
  }

  protected removeFile(): void {
    this.selectedFile.set(null);
    this.validationError.set(null);
  }

  protected onSubmit(): void {
    const file = this.selectedFile();
    if (!file || !this.isValid()) {
      return;
    }

    this.isUploading.set(true);
    this.uploadProgress.set(0);

    this.uploadService
      .uploadFile(file)
      .pipe(finalize(() => this.isUploading.set(false)))
      .subscribe((event) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          this.uploadProgress.set(Math.round((100 * event.loaded) / event.total));
        } else if (event.type === HttpEventType.Response) {
          this.onUploadSuccess();
        }
      });
  }

  protected formatBytes(bytes: number): string {
    if (bytes <= 0) {
      return '0 B';
    }

    const units = ['B', 'KB', 'MB', 'GB'];
    const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
    const value = bytes / 1024 ** exponent;

    return `${exponent === 0 ? value : value.toFixed(1)} ${units[exponent]}`;
  }

  private setFile(file: File): void {
    this.selectedFile.set(file);
    this.validationError.set(this.validateFile(file));
  }

  private validateFile(file: File): string | null {
    const extension = file.name.split('.').pop()?.toLowerCase() ?? '';
    if (!(ALLOWED_UPLOAD_EXTENSIONS as readonly string[]).includes(extension)) {
      const allowed = ALLOWED_UPLOAD_EXTENSIONS.map((ext) => `.${ext}`).join(', ');
      return `Unsupported file type ".${extension || 'unknown'}". Only ${allowed} files are accepted.`;
    }

    if (file.size === 0) {
      return 'The selected file is empty.';
    }

    if (file.size > MAX_UPLOAD_FILE_SIZE_BYTES) {
      return `The file is too large. Maximum allowed size is ${this.maxFileSizeLabel}.`;
    }

    return null;
  }

  private onUploadSuccess(): void {
    this.dialog
      .openOkDialog(
        'Upload successful',
        'Your file has been uploaded successfully. You will be able to see the result on the upload history page.',
      )
      .afterClosed()
      .subscribe(() => this.router.navigateByUrl(appRoutes.uploadHistory));
  }
}
