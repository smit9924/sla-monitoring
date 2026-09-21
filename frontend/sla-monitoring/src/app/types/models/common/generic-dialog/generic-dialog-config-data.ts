import { GenericDialogButtonMetadata } from '../../../interfaces/common';

export class GenericDialogConfigData {
  buttons: GenericDialogButtonMetadata[] = [];
  title = '';
  contentText = '';

  constructor(config?: Partial<GenericDialogConfigData>) {
    if (config) {
      Object.assign(this, config);
    }
  }
}
