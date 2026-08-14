"use client";

import { useEffect, useState } from "react";

import {
  ApiClientError,
  deleteJob,
  getJobResult,
  getJobStatus,
  retryJob,
  submitAggregatedJob,
  submitExactComparisonJob,
  submitExactJob,
  submitExactVsSampledJob,
} from "../../lib/api/client";
import {
  buildAggregatedSimulationRequest,
  buildExactComparisonRequest,
  buildExactSimulationRequest,
  buildExactVsSampledComparisonRequest,
  validateAnalysisInputs,
  type AnalysisInputs,
} from "../../lib/state/analysis-state";
import type {
  JobAccepted,
  JobResult,
  JobStatus,
  JobStatusValue,
  JsonValue,
  MetadataResponse,
} from "../../types/api";

interface JobWorkflowProps {
  inputs: AnalysisInputs;
  metadata: MetadataResponse | null;
}

export const TERMINAL_JOB_STATUSES: JobStatusValue[] = [
  "completed",
  "failed",
  "cancelled",
  "expired",
];

const JOB_STATUS_LEGEND: JobStatusValue[] = [
  "queued",
  "running",
  "completed",
  "failed",
  "cancel_requested",
  "cancelled",
  "expired",
];

const POLLING_INTERVAL_MS = 1500;

function isTerminal(status: JobStatusValue): boolean {
  return TERMINAL_JOB_STATUSES.includes(status);
}

function displayPayload(value: JsonValue | null): string {
  if (value === null) {
    return "No result payload returned yet.";
  }
  return JSON.stringify(value, null, 2);
}

export function JobWorkflow({ inputs, metadata }: JobWorkflowProps) {
  const [job, setJob] = useState<JobStatus | null>(null);
  const [accepted, setAccepted] = useState<JobAccepted | null>(null);
  const [result, setResult] = useState<JobResult | null>(null);
  const [message, setMessage] = useState("Submit a background job to begin.");
  const [polling, setPolling] = useState(false);

  async function submitJob(kind: "exact" | "aggregated" | "comparison" | "calibration") {
    const validationMessages = validateAnalysisInputs(inputs, metadata);
    if (validationMessages.length > 0) {
      setMessage(validationMessages[0]);
      return;
    }

    setMessage("Submitting background job.");
    setResult(null);

    try {
      let response: JobAccepted;
      if (kind === "exact") {
        response = await submitExactJob(buildExactSimulationRequest(inputs, metadata));
      } else if (kind === "aggregated") {
        response = await submitAggregatedJob(
          buildAggregatedSimulationRequest(inputs, metadata),
        );
      } else if (kind === "comparison") {
        response = await submitExactComparisonJob(
          buildExactComparisonRequest(inputs, metadata),
        );
      } else {
        response = await submitExactVsSampledJob(
          buildExactVsSampledComparisonRequest(inputs, metadata),
        );
      }
      setAccepted(response);
      setJob(response.job);
      setPolling(!isTerminal(response.job.status));
      setMessage(`Job accepted with status ${response.job.status}.`);
    } catch (error) {
      setMessage(
        error instanceof ApiClientError
          ? error.message
          : "The job submission could not reach the backend.",
      );
    }
  }

  useEffect(() => {
    if (!polling || !job || isTerminal(job.status)) {
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      void getJobStatus(job.job_id)
        .then((payload) => {
          setJob(payload.job);
          if (isTerminal(payload.job.status)) {
            setPolling(false);
          }
        })
        .catch((error) => {
          setPolling(false);
          setMessage(
            error instanceof ApiClientError
              ? error.message
              : "The job status request could not reach the backend.",
          );
        });
    }, POLLING_INTERVAL_MS);

    return () => window.clearInterval(intervalId);
  }, [job, polling]);

  async function loadResult() {
    if (!job) {
      setMessage("Submit a job before retrieving a result.");
      return;
    }

    try {
      const payload = await getJobResult(job.job_id);
      setResult(payload);
      setJob(payload.job);
      setMessage("Job result loaded.");
    } catch (error) {
      setMessage(
        error instanceof ApiClientError
          ? error.message
          : "The job result request could not reach the backend.",
      );
    }
  }

  async function retryCurrentJob() {
    if (!job) {
      setMessage("Submit a job before retrying.");
      return;
    }

    try {
      const payload = await retryJob(job.job_id);
      setAccepted(payload);
      setJob(payload.job);
      setResult(null);
      setPolling(!isTerminal(payload.job.status));
      setMessage(`Retry job accepted with status ${payload.job.status}.`);
    } catch (error) {
      setMessage(
        error instanceof ApiClientError
          ? error.message
          : "The retry request could not reach the backend.",
      );
    }
  }

  async function cancelOrDeleteCurrentJob() {
    if (!job) {
      setMessage("Submit a job before cancelling or deleting.");
      return;
    }

    try {
      const payload = await deleteJob(job.job_id);
      setJob(payload.job);
      setPolling(false);
      setMessage(`Cancel or delete job returned status ${payload.job.status}.`);
    } catch (error) {
      setMessage(
        error instanceof ApiClientError
          ? error.message
          : "The cancel/delete request could not reach the backend.",
      );
    }
  }

  return (
    <section className="workspace__results" aria-labelledby="jobs-title">
      <div className="panel-heading">
        <div>
          <h2 id="jobs-title">Background jobs</h2>
          <p>
            Submit approved Phase 5 jobs, poll with a bounded interval, and stop
            automatically at terminal states.
          </p>
        </div>
      </div>

      <div className="button-row" aria-label="Background job actions">
        <button type="button" onClick={() => submitJob("exact")}>
          Submit exact job
        </button>
        <button type="button" onClick={() => submitJob("aggregated")}>
          Submit aggregated job
        </button>
        <button type="button" onClick={() => submitJob("comparison")}>
          Submit exact comparison job
        </button>
        <button type="button" onClick={() => submitJob("calibration")}>
          Submit exact-vs-sampled job
        </button>
      </div>

      <p className="status-note" aria-live="polite">
        {message}
      </p>

      <ul className="pill-list" aria-label="Supported job statuses">
        {JOB_STATUS_LEGEND.map((status) => (
          <li key={status}>{status}</li>
        ))}
      </ul>

      <div className="button-row" aria-label="Selected job controls">
        <button type="button" onClick={loadResult} disabled={!job}>
          Get result
        </button>
        <button type="button" onClick={retryCurrentJob} disabled={!job?.retry_supported}>
          Retry job
        </button>
        <button type="button" onClick={cancelOrDeleteCurrentJob} disabled={!job}>
          Cancel or delete job
        </button>
      </div>

      <div className="result-grid">
        <article className="result-card">
          <h3>Job status</h3>
          {job ? (
            <dl className="definition-list">
              <div>
                <dt>Job ID</dt>
                <dd>{job.job_id}</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>{job.status}</dd>
              </div>
              <div>
                <dt>Progress</dt>
                <dd>{job.progress}</dd>
              </div>
              <div>
                <dt>Attempt</dt>
                <dd>
                  {job.attempt} / {job.max_attempts}
                </dd>
              </div>
            </dl>
          ) : (
            <p className="empty-state">No job has been submitted yet.</p>
          )}
        </article>

        <article className="result-card">
          <h3>Job links and result</h3>
          {accepted ? (
            <dl className="definition-list">
              <div>
                <dt>Status link</dt>
                <dd>{accepted.links.status}</dd>
              </div>
              <div>
                <dt>Result link</dt>
                <dd>{accepted.links.result}</dd>
              </div>
            </dl>
          ) : null}
          <pre className="payload-preview">{displayPayload(result?.result ?? null)}</pre>
        </article>
      </div>
    </section>
  );
}
