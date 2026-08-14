import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { test } from "node:test";

const root = process.cwd();

function read(relativePath) {
  return readFileSync(join(root, relativePath), "utf8");
}

const approvedRoutes = [
  ["GET", "/health", "getHealth"],
  ["GET", "/api/v1/metadata", "getMetadata"],
  ["POST", "/api/v1/simulations/exact", "runExactSimulation"],
  ["POST", "/api/v1/simulations/aggregated", "runAggregatedSimulation"],
  ["POST", "/api/v1/comparisons/exact", "compareExact"],
  ["POST", "/api/v1/comparisons/exact-vs-sampled", "compareExactVsSampled"],
  ["POST", "/api/v1/jobs/exact", "submitExactJob"],
  ["POST", "/api/v1/jobs/aggregated", "submitAggregatedJob"],
  ["POST", "/api/v1/jobs/comparisons/exact", "submitExactComparisonJob"],
  [
    "POST",
    "/api/v1/jobs/comparisons/exact-vs-sampled",
    "submitExactVsSampledJob",
  ],
  ["GET", "/api/v1/jobs/{job_id}", "getJobStatus"],
  ["GET", "/api/v1/jobs/{job_id}/result", "getJobResult"],
  ["POST", "/api/v1/jobs/{job_id}/retry", "retryJob"],
  ["DELETE", "/api/v1/jobs/{job_id}", "deleteJob"],
];

test("typed client covers every approved backend route and no detailed sampled route", () => {
  const routes = read("lib/api/routes.ts");
  const client = read("lib/api/client.ts");

  for (const [method, path, functionName] of approvedRoutes) {
    assert.match(routes, new RegExp(method));
    assert.match(routes, new RegExp(path.replace(/[{}]/g, "\\$&")));
    assert.match(client, new RegExp(`export async function ${functionName}\\b`));
  }

  assert.doesNotMatch(routes, /detailed|per-copy|paths/i);
  assert.doesNotMatch(client, /detailed|per-copy|paths/i);
});

test("frontend types declare envelopes, job statuses, and required request/result names", () => {
  const types = read("types/api.ts");

  for (const requiredType of [
    "ApiSuccess",
    "ApiErrorEnvelope",
    "MetadataResponse",
    "ExactSimulationRequest",
    "ExactSimulationResult",
    "AggregatedSimulationRequest",
    "AggregatedSimulationResult",
    "ExactComparisonRequest",
    "ExactComparisonResult",
    "ExactVsSampledComparisonRequest",
    "ExactVsSampledComparisonResult",
    "JobAccepted",
    "JobStatus",
    "JobResult",
    "JobStatusValue",
  ]) {
    assert.match(types, new RegExp(`\\b${requiredType}\\b`));
  }

  for (const status of [
    "queued",
    "running",
    "completed",
    "failed",
    "cancel_requested",
    "cancelled",
    "expired",
  ]) {
    assert.match(types, new RegExp(`"${status}"`));
  }
});

test("proxy route handlers preserve backend paths without adding CORS or scientific logic", () => {
  const proxy = read("lib/api/proxy.ts");
  const routeFiles = [
    "app/api/health/route.ts",
    "app/api/backend/[...path]/route.ts",
  ].map(read).join("\n");

  assert.match(proxy, /FRONTEND_API_BASE_URL/);
  assert.match(routeFiles, /proxyBackendRequest/);
  assert.doesNotMatch(proxy + routeFiles, /Access-Control-Allow-Origin/i);
  assert.doesNotMatch(proxy + routeFiles, /VALID_CODONS|STOP_CODONS|mutation|denominator|runSimulation/i);
});

