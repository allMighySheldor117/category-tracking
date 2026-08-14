import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, it } from "node:test";

const root = process.cwd();

function readFrontend(relativePath) {
  return readFileSync(join(root, relativePath), "utf8");
}

describe("background job workflow", () => {
  it("models Phase 5 job envelopes and typed client functions correctly", () => {
    const typeSource = readFrontend("types/api.ts");
    const clientSource = readFrontend("lib/api/client.ts");

    assert.match(typeSource, /interface JobAccepted/);
    assert.match(typeSource, /job: JobStatus/);
    assert.match(typeSource, /links: JobLinks/);
    assert.match(typeSource, /interface JobStatusResponse/);
    assert.match(typeSource, /queued/);
    assert.match(typeSource, /cancel_requested/);
    assert.match(typeSource, /expired/);

    for (const fnName of [
      "submitExactJob",
      "submitAggregatedJob",
      "submitExactComparisonJob",
      "submitExactVsSampledJob",
      "getJobStatus",
      "getJobResult",
      "retryJob",
      "deleteJob",
    ]) {
      assert.match(clientSource, new RegExp(`function ${fnName}`));
    }
  });

  it("keeps bounded job workflow implemented without cluttering the Streamlit-like main UI", () => {
    const jobSource = readFrontend("components/jobs/job-workflow.tsx");
    const workspaceSource = readFrontend("components/analysis-workspace.tsx");

    assert.match(jobSource, /"use client"/);
    assert.match(jobSource, /setInterval/);
    assert.match(jobSource, /clearInterval/);
    assert.match(jobSource, /TERMINAL_JOB_STATUSES/);
    assert.match(jobSource, /queued/);
    assert.match(jobSource, /running/);
    assert.match(jobSource, /completed/);
    assert.match(jobSource, /failed/);
    assert.match(jobSource, /cancel_requested/);
    assert.match(jobSource, /cancelled/);
    assert.match(jobSource, /expired/);
    assert.match(jobSource, /Submit exact job/);
    assert.match(jobSource, /Submit aggregated job/);
    assert.match(jobSource, /Get result/);
    assert.match(jobSource, /Retry job/);
    assert.match(jobSource, /Cancel or delete job/);
    assert.doesNotMatch(workspaceSource, /<JobWorkflow/);
    assert.match(workspaceSource, /Run analysis/);

    assert.doesNotMatch(jobSource, /sampled\/details|detailed sampled|setInterval\([^,]+,\s*[0-9]{1,2}\)/);
  });
});
