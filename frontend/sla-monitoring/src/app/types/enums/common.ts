export enum GenericDialogButtonType {
  FILLED = 'filled',
  OUTLINED = 'outlined',
  LINK = 'link',
  TONAL = 'tonal',
  ICON = 'icon',
}

export enum GenericSnackbarType {
  DEFAULT = 'default',
  SUCCESS = 'success',
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info',
}

export enum GenericSnackbarDuration {
  /** Snackbar duration in milliseconds. */
  SHORT = 3000,
  MEDIUM = 5000,
  LONG = 10000,
  /** Special value indicating the snackbar stays open until dismissed. */
  INFINITE = 0,
}
