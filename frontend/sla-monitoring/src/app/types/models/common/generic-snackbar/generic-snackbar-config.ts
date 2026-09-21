import {
  MatSnackBarConfig,
  MatSnackBarHorizontalPosition,
  MatSnackBarVerticalPosition,
} from '@angular/material/snack-bar';
import { GenericSnackbarDuration, GenericSnackbarType } from '../../../enums/common';
import { GenericSnackbarConfigData } from './generic-snackbar-config-data';

export const SNACKBAR_PANEL_CLASS: Record<GenericSnackbarType, string> = {
  [GenericSnackbarType.SUCCESS]: 'snackbar-success',
  [GenericSnackbarType.ERROR]: 'snackbar-error',
  [GenericSnackbarType.WARNING]: 'snackbar-warning',
  [GenericSnackbarType.INFO]: 'snackbar-info',
  [GenericSnackbarType.DEFAULT]: 'snackbar-default',
};

export class GenericSnackbarConfig extends MatSnackBarConfig<GenericSnackbarConfigData> {
  override verticalPosition: MatSnackBarVerticalPosition = 'top';
  override horizontalPosition: MatSnackBarHorizontalPosition = 'center';
  override duration: GenericSnackbarDuration = GenericSnackbarDuration.MEDIUM;

  constructor(config?: Partial<GenericSnackbarConfig>) {
    super();
    if (config) {
      Object.assign(this, config);
    }
  }

  get ariaPoliteness(): 'off' | 'polite' | 'assertive' {
    switch (this.data?.type) {
      case GenericSnackbarType.ERROR:
      case GenericSnackbarType.WARNING:
        return 'assertive';
      case GenericSnackbarType.SUCCESS:
      case GenericSnackbarType.INFO:
        return 'polite';
      default:
        return 'off';
    }
  }

  get snackbarPanelClass(): string {
    return SNACKBAR_PANEL_CLASS[this.data?.type ?? GenericSnackbarType.DEFAULT];
  }
}
