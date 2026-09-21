import { MatDialogConfig } from '@angular/material/dialog';

export class GenericDialogConfig<T> extends MatDialogConfig<T> {
  override width = '480px';
  override maxWidth = '95vw';
  override maxHeight = '90vh';
  override panelClass = 'generic-popup-panel';
  override hasBackdrop = true;
  override disableClose = false;
  override autoFocus = 'first-tabbable';
  override restoreFocus = true;
  override enterAnimationDuration = '200ms';
  override exitAnimationDuration = '150ms';

  constructor(config?: Partial<GenericDialogConfig<T>>) {
    super();
    if (config) {
      Object.assign(this, config);
    }
  }
}
