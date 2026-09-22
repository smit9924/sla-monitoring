/** One service's SLA summary for a file; mirrors the backend's `ServiceSlaStat` schema. */
export interface ServiceSlaStat {
  serviceId: string;
  serviceName: string;
  totalChecks: number;
  failedChecks: number;
  uptimePercentage: number;
  slaFulfilled: boolean;
}

/** One point of the per-day, per-service failure line chart; mirrors `DailyFailureCount`. */
export interface DailyFailureCount {
  /** ISO date string (`YYYY-MM-DD`). */
  day: string;
  serviceId: string;
  serviceName: string;
  failureCount: number;
}

/** Returned by `GET /files/{guid}/stats`; mirrors the backend's `FileStatsResponse` schema. */
export interface FileStatsResponse {
  fileGuid: string;
  slaThresholdPercentage: number;
  overallSlaFulfilled: boolean;
  overallUptimePercentage: number;
  services: ServiceSlaStat[];
  dailyFailures: DailyFailureCount[];
}
