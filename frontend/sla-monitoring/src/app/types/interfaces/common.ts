import { GenericDialogButtonType } from '../enums/common';

export interface GenericDialogButtonMetadata<R = unknown> {
  label: string;
  type: GenericDialogButtonType;
  /** Whether clicking this button closes the dialog. */
  closeOnClick: boolean;
  /** Result the dialog resolves with when `closeOnClick` is true. */
  closeValue?: R;
  iconName?: string;
  callback?: () => void;
}
