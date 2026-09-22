/** One `service_logs` row shown in the logs accordion; mirrors `ServiceLogEntry`. */
export interface ServiceLogEntry {
  id: number;
  /** ISO datetime string. */
  recordedAt: string;
  statusCode: number;
  isFailure: boolean;
  latencyMs: number | null;
  agent: string | null;
  region: string | null;
}

/** One service's section of the logs accordion; mirrors the backend's `ServiceLogGroup` schema. */
export interface ServiceLogGroup {
  serviceId: string;
  serviceName: string;
  /** Total log count for this service across the whole file, not just the current batch. */
  totalCount: number;
  logs: ServiceLogEntry[];
  /** Whether a "Show more" click would return additional logs for this service. */
  hasMore: boolean;
}

/** Returned by `GET /files/{guid}/logs`; mirrors the backend's `FileLogsResponse` schema. */
export interface FileLogsResponse {
  services: ServiceLogGroup[];
}

/** Query for a single service's next batch of logs ("Show more"). */
export interface ServiceLogQuery {
  serviceId: string;
  offset: number;
}
