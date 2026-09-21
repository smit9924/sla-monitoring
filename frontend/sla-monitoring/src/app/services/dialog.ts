import { inject, Injectable } from '@angular/core';
import { MatDialog, MatDialogConfig, MatDialogRef } from '@angular/material/dialog';
import { GenericDialog } from '../components/common/generic-dialog/generic-dialog';
import { GenericDialogButtonMetadata } from '../types/interfaces/common';
import { GenericDialogButtonType } from '../types/enums/common';
import { GenericDialogConfig } from '../types/models/common/generic-dialog/generic-dialog-config';
import { GenericDialogConfigData } from '../types/models/common/generic-dialog/generic-dialog-config-data';

@Injectable({
  providedIn: 'root',
})
export class Dialog {
  private readonly dialog = inject(MatDialog);

  /**
   * Opens a generic dialog and returns a MatDialogRef.
   * Use this when you need full control over the config (e.g. custom buttons).
   */
  open<D = unknown, R = unknown>(config: MatDialogConfig<D>): MatDialogRef<GenericDialog, R> {
    return this.dialog.open<GenericDialog, D, R>(GenericDialog, config);
  }

  /** Opens a single-button dialog that just acknowledges a message. */
  openOkDialog(title: string, contentText: string): MatDialogRef<GenericDialog, void> {
    const buttons: GenericDialogButtonMetadata[] = [
      {
        label: 'Ok',
        type: GenericDialogButtonType.FILLED,
        closeOnClick: true,
      },
    ];

    return this.open<GenericDialogConfigData, void>(
      new GenericDialogConfig({
        data: new GenericDialogConfigData({ buttons, title, contentText }),
      }),
    );
  }

  /**
   * Opens a confirm dialog. The returned ref resolves `true` if Confirm was
   * clicked, `false` if Cancel was clicked, and `undefined` if dismissed
   * (e.g. backdrop click or Escape).
   */
  openConfirmDialog(title: string, contentText: string): MatDialogRef<GenericDialog, boolean> {
    const buttons: GenericDialogButtonMetadata<boolean>[] = [
      {
        label: 'Cancel',
        type: GenericDialogButtonType.OUTLINED,
        closeOnClick: true,
        closeValue: false,
      },
      {
        label: 'Confirm',
        type: GenericDialogButtonType.FILLED,
        closeOnClick: true,
        closeValue: true,
      },
    ];

    return this.open<GenericDialogConfigData, boolean>(
      new GenericDialogConfig({
        data: new GenericDialogConfigData({ buttons, title, contentText }),
      }),
    );
  }
}
