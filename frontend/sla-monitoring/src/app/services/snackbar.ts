import { inject, Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { GenericSnackbar } from '../components/common/generic-snackbar/generic-snackbar';
import { GenericSnackbarType, GenericSnackbarDuration } from '../types/enums/common';
import { GenericSnackbarConfig } from '../types/models/common/generic-snackbar/generic-snackbar-config';
import { GenericSnackbarConfigData } from '../types/models/common/generic-snackbar/generic-snackbar-config-data';

@Injectable({
  providedIn: 'root',
})
export class Snackbar {
  private readonly snackBar = inject(MatSnackBar);

  open(config: GenericSnackbarConfig): void {
    config.politeness = config.ariaPoliteness;
    config.panelClass = config.snackbarPanelClass;
    this.snackBar.openFromComponent(GenericSnackbar, config);
  }

  show(
    text: string,
    type: GenericSnackbarType = GenericSnackbarType.DEFAULT,
    options?: { duration?: GenericSnackbarDuration; showCloseButton?: boolean },
  ): void {
    this.open(
      new GenericSnackbarConfig({
        duration: options?.duration ?? GenericSnackbarDuration.MEDIUM,
        data: new GenericSnackbarConfigData({
          text,
          type,
          showCloseButton: options?.showCloseButton ?? false,
        }),
      }),
    );
  }
}
