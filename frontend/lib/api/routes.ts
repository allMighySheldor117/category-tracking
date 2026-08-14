export interface BackendRoute {
  method: "GET" | "POST" | "DELETE";
  path: string;
}

export const BACKEND_ROUTES = {
  health: { method: "GET", path: "/health" },
  metadata: { method: "GET", path: "/api/v1/metadata" },
  exactSimulation: { method: "POST", path: "/api/v1/simulations/exact" },
  aggregatedSimulation: {
    method: "POST",
    path: "/api/v1/simulations/aggregated",
  },
  exactComparison: { method: "POST", path: "/api/v1/comparisons/exact" },
  exactVsSampledComparison: {
    method: "POST",
    path: "/api/v1/comparisons/exact-vs-sampled",
  },
  exactJob: { method: "POST", path: "/api/v1/jobs/exact" },
  aggregatedJob: { method: "POST", path: "/api/v1/jobs/aggregated" },
  exactComparisonJob: {
    method: "POST",
    path: "/api/v1/jobs/comparisons/exact",
  },
  exactVsSampledJob: {
    method: "POST",
    path: "/api/v1/jobs/comparisons/exact-vs-sampled",
  },
  jobStatus: { method: "GET", path: "/api/v1/jobs/{job_id}" },
  jobResult: { method: "GET", path: "/api/v1/jobs/{job_id}/result" },
  jobRetry: { method: "POST", path: "/api/v1/jobs/{job_id}/retry" },
  jobDelete: { method: "DELETE", path: "/api/v1/jobs/{job_id}" },
} as const satisfies Record<string, BackendRoute>;

export function resolveBackendRoute(
  route: BackendRoute,
  params: Record<string, string> = {},
): BackendRoute {
  let path = route.path;
  for (const [key, value] of Object.entries(params)) {
    path = path.replace(`{${key}}`, encodeURIComponent(value));
  }
  return { ...route, path };
}

export function toFrontendProxyPath(path: string): string {
  if (path === "/health") {
    return "/api/health";
  }
  return `/api/backend${path}`;
}

