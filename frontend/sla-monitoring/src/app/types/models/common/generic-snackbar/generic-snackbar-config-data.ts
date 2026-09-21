import { GenericSnackbarType } from '../../../enums/common';

export class GenericSnackbarConfigData {
  text = '';
  showCloseButton = false;
  type: GenericSnackbarType = GenericSnackbarType.DEFAULT;

  constructor(data: Partial<GenericSnackbarConfigData>) {
    Object.assign(this, data);
  }
}
