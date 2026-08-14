import {
  BACKEND_ROUTES,
  resolveBackendRoute,
  toFrontendProxyPath,
  type BackendRoute,
} from "./routes";
import type {
  AggregatedSimulationRequest,
  AggregatedSimulationResult,
  ApiEnvelope,
  ExactComparisonRequest,
  ExactComparisonResult,
  ExactSimulationRequest,
  ExactSimulationResult,
  ExactVsSampledComparisonRequest,
  ExactVsSampledComparisonResult,
  JobAccepted,
  JobResult,
  JobStatusResponse,
  JsonValue,
  MetadataResponse,
} from "../../types/api";

export class ApiClientError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: JsonValue | null;

  constructor(message: string, status: number, code: string, details: JsonValue | null) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function parseEnvelope<TData>(response: Response): Promise<TData> {
  const body = (await response.json()) as ApiEnvelope<TData>;
  if ("error" in body) {
    throw new ApiClientError(
      body.error.message,
      response.status,
      body.error.code,
      body.error.details,
    );
  }
  if ("errors" in body && Array.isArray(body.errors) && body.errors.length > 0) {
    const firstError = body.errors[0];
    throw new ApiClientError(
      firstError.message,
      response.status,
      firstError.code,
      firstError.details,
    );
  }
  if ("data" in body) {
    return body.data;
  }
  throw new ApiClientError("Malformed API response.", response.status, "malformed_response", null);
}

async function request<TData, TBody = undefined>(
  route: BackendRoute,
  body?: TBody,
): Promise<TData> {
  const response = await fetch(toFrontendProxyPath(route.path), {
    method: route.method,
    headers:
      body === undefined
        ? undefined
        : {
            "Content-Type": "application/json",
          },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  return parseEnvelope<TData>(response);
}

export async function getHealth(): Promise<JsonValue> {
  return request<JsonValue>(BACKEND_ROUTES.health);
}

export async function getMetadata(): Promise<MetadataResponse> {
  return request<MetadataResponse>(BACKEND_ROUTES.metadata);
}

export async function runExactSimulation(
  body: ExactSimulationRequest,
): Promise<ExactSimulationResult> {
  return request<ExactSimulationResult, ExactSimulationRequest>(
    BACKEND_ROUTES.exactSimulation,
    body,
  );
}

export async function runAggregatedSimulation(
  body: AggregatedSimulationRequest,
): Promise<AggregatedSimulationResult> {
  return request<AggregatedSimulationResult, AggregatedSimulationRequest>(
    BACKEND_ROUTES.aggregatedSimulation,
    body,
  );
}

export async function compareExact(
  body: ExactComparisonRequest,
): Promise<ExactComparisonResult> {
  return request<ExactComparisonResult, ExactComparisonRequest>(
    BACKEND_ROUTES.exactComparison,
    body,
  );
}

export async function compareExactVsSampled(
  body: ExactVsSampledComparisonRequest,
): Promise<ExactVsSampledComparisonResult> {
  return request<ExactVsSampledComparisonResult, ExactVsSampledComparisonRequest>(
    BACKEND_ROUTES.exactVsSampledComparison,
    body,
  );
}

export async function submitExactJob(
  body: ExactSimulationRequest,
): Promise<JobAccepted> {
  return request<JobAccepted, ExactSimulationRequest>(BACKEND_ROUTES.exactJob, body);
}

export async function submitAggregatedJob(
  body: AggregatedSimulationRequest,
): Promise<JobAccepted> {
  return request<JobAccepted, AggregatedSimulationRequest>(
    BACKEND_ROUTES.aggregatedJob,
    body,
  );
}

export async function submitExactComparisonJob(
  body: ExactComparisonRequest,
): Promise<JobAccepted> {
  return request<JobAccepted, ExactComparisonRequest>(
    BACKEND_ROUTES.exactComparisonJob,
    body,
  );
}

export async function submitExactVsSampledJob(
  body: ExactVsSampledComparisonRequest,
): Promise<JobAccepted> {
  return request<JobAccepted, ExactVsSampledComparisonRequest>(
    BACKEND_ROUTES.exactVsSampledJob,
    body,
  );
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  return request<JobStatusResponse>(
    resolveBackendRoute(BACKEND_ROUTES.jobStatus, { job_id: jobId }),
  );
}

export async function getJobResult(jobId: string): Promise<JobResult> {
  return request<JobResult>(
    resolveBackendRoute(BACKEND_ROUTES.jobResult, { job_id: jobId }),
  );
}

export async function retryJob(jobId: string): Promise<JobAccepted> {
  return request<JobAccepted>(
    resolveBackendRoute(BACKEND_ROUTES.jobRetry, { job_id: jobId }),
  );
}

export async function deleteJob(jobId: string): Promise<JobStatusResponse> {
  return request<JobStatusResponse>(
    resolveBackendRoute(BACKEND_ROUTES.jobDelete, { job_id: jobId }),
  );
}
