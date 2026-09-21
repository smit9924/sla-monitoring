/** Preset request timeouts, in milliseconds, usable via the `REQUEST_TIMEOUT` http context token. */
export enum HttpRequestTimeout {
  DISABLED = -1,
  TIMEOUT_10S = 10000,
  TIMEOUT_20S = 20000,
  TIMEOUT_30S = 30000,
  TIMEOUT_60S = 60000,
}
