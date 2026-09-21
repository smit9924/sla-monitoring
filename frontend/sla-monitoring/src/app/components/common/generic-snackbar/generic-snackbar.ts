import { Component, inject } from '@angular/core';
import { MAT_SNACK_BAR_DATA, MatSnackBarRef } from '@angular/material/snack-bar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { GenericSnackbarType } from '../../../types/enums/common';
import { GenericSnackbarConfigData } from '../../../types/models/common/generic-snackbar/generic-snackbar-config-data';

interface SnackbarMeta {
  icon: string;
}

const TYPE_META: Record<GenericSnackbarType, SnackbarMeta> = {
  [GenericSnackbarType.DEFAULT]: { icon: 'info' },
  [GenericSnackbarType.SUCCESS]: { icon: 'success' },
  [GenericSnackbarType.WARNING]: { icon: 'warning' },
  [GenericSnackbarType.INFO]: { icon: 'info' },
  [GenericSnackbarType.ERROR]: { icon: 'error' },
};

@Component({
  selector: 'app-generic-snackbar',
  imports: [MatButtonModule, MatIconModule, MatTooltipModule],
  templateUrl: './generic-snackbar.html',
  styleUrl: './generic-snackbar.scss',
})
export class GenericSnackbar {
  protected readonly TYPE_META = TYPE_META;
  protected readonly data = inject<GenericSnackbarConfigData>(MAT_SNACK_BAR_DATA);
  private readonly snackbarRef = inject(MatSnackBarRef<GenericSnackbar>);

  protected dismiss(): void {
    this.snackbarRef.dismiss();
  }
}
