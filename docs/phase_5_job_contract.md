# Phase 5 Background Job Contract

Status: Proposed — awaiting Background Job Contract approval.

Version: `phase5-job-v1-proposed`

Contract owner: user-approved project contract.

Provider owner: FastAPI background-job adapter under `api/`.

Scientific provider owner: existing public APIs under `engine/`.

Approver: user.

Authoritative Blueprint: `plans/phase-5-in-process-background-jobs.md`.

## 1. Purpose and authority

Phase 5 adds an optional asynchronous background-job layer over the existing Phase 4 FastAPI backend. It is additive: every Phase 4 synchronous endpoint remains available, unchanged, and governed by `docs/phase_4_api_contract.md`.

Exact probability remains the authoritative deterministic scientific path. Aggregated sampled mode remains explicit and experimental. Detailed sampled per-copy paths remain absent from HTTP.

The Phase 5 provider is in-process, process-memory, and standard-library-only unless a later approved Blueprint mutation changes this contract first.

Implementation must follow this contract. If implementation evidence contradicts the contract, the contract must be amended and approved before code changes continue.

## 2. Compatibility and versioning

Existing Phase 4 routes and response contracts remain API version `phase4-api-v1`.

Phase 5 job routes are additive under `/api/v1/jobs/...`. They reuse the Phase 4 success and error envelope style where applicable:

- success responses include `api_version`, `mode`, `scientific_authority`, `data`, and `schema`;
- error responses include `api_version`, `mode`, `scientific_authority`, `errors`, and `schema`;
- table serialization remains identical to Phase 4 when a completed job returns a scientific result.

Existing synchronous response payloads, error codes, request-size behavior, and OpenAPI surface must not change as a side effect of Phase 5.

Breaking changes require the Phase 5 Blueprint mutation protocol and user approval.

## 3. Non-goals

Phase 5 explicitly excludes:

- Redis;
- Celery;
- RQ;
- PostgreSQL;
- durable shared storage;
- Docker, Kubernetes, or deployment work;
- authentication or authorization;
- CORS changes;
- Next.js frontend work;
- Streamlit or Tkinter changes;
- scientific engine rewrites;
- detailed sampled per-copy HTTP endpoints;
- automatic sync-to-job switching.

## 4. Dependency decision

Phase 5 adds no new third-party dependency.

The job provider must use only Python standard-library concurrency and data structures.

Existing Phase 4 dependencies remain:

- `fastapi>=0.139,<0.141`
- `uvicorn[standard]>=0.51,<0.52`
- `httpx>=0.28,<0.29`

Any new dependency requires contract mutation and user approval before implementation.

## 5. Job route contract

All job route responses use JSON. Job IDs are path parameters named `job_id`. All route paths are lowercase and kebab-free because the existing API uses compact scientific nouns.

### POST `/api/v1/jobs/exact`

Purpose: enqueue an authoritative exact-probability simulation job.

Request body: same scientific request body accepted by `POST /api/v1/simulations/exact`.

Starts engine work: yes, asynchronously after admission.

Mutates job state: creates a new queued job.

Idempotency: non-idempotent. Repeating the same request creates a new job with a new `job_id`.

Success status: `202 Accepted`.

Success envelope:

```json
{
  "api_version": "phase4-api-v1",
  "mode": "job_accepted",
  "scientific_authority": "exact_probability",
  "data": {
    "job": {},
    "links": {
      "status": "/api/v1/jobs/{job_id}",
      "result": "/api/v1/jobs/{job_id}/result"
    }
  },
  "schema": {"name": "JobAcceptedEnvelope", "version": "phase5-job-v1"}
}
```

Error envelope: Phase 4 error envelope shape with Phase 5 job-specific codes where relevant.

Owner: API job adapter; scientific execution delegates to Phase 4 exact adapter helpers or the same public engine calls used by synchronous exact endpoint.

### POST `/api/v1/jobs/aggregated`

Purpose: enqueue an explicit experimental aggregated sampled job.

Request body: same scientific request body accepted by `POST /api/v1/simulations/aggregated`, including required integer `seed`.

Starts engine work: yes, asynchronously after admission.

Mutates job state: creates a new queued job.

Idempotency: non-idempotent. Repeating the same request creates a new job with a new `job_id`.

Success status: `202 Accepted`.

Success envelope: `JobAcceptedEnvelope` with `scientific_authority: "experimental_sampled"`.

Errors: missing seed returns `422 validation_error`; queue full returns `503 queue_full`.

Owner: API job adapter; scientific execution delegates to the same aggregated path used by the synchronous aggregated endpoint.

### POST `/api/v1/jobs/comparisons/exact`

Purpose: enqueue an exact-vs-exact comparison job.

Request body: same body accepted by `POST /api/v1/comparisons/exact`.

Starts engine work: yes.

Mutates job state: creates a new queued job.

Idempotency: non-idempotent.

Success status: `202 Accepted`.

Success envelope: `JobAcceptedEnvelope` with `scientific_authority: "exact_probability"`.

Owner: API job adapter; comparison execution delegates to the Phase 4 comparison adapter path.

### POST `/api/v1/jobs/comparisons/exact-vs-sampled`

Purpose: enqueue an exact deterministic reference versus aggregated sampled calibration job.

Request body: same body accepted by `POST /api/v1/comparisons/exact-vs-sampled`.

Starts engine work: yes.

Mutates job state: creates a new queued job.

Idempotency: non-idempotent.

Success status: `202 Accepted`.

Success envelope: `JobAcceptedEnvelope` with `scientific_authority: "exact_probability"`.

Owner: API job adapter; comparison execution delegates to the Phase 4 exact-vs-sampled adapter path.

### GET `/api/v1/jobs/{job_id}`

Purpose: retrieve job metadata and lifecycle state.

Request body: none.

Starts engine work: no.

Mutates job state: no, except bounded cleanup may expire old retained jobs before lookup.

Idempotency: idempotent.

Success status: `200 OK`.

Success envelope:

```json
{
  "api_version": "phase4-api-v1",
  "mode": "job_status",
  "scientific_authority": "none",
  "data": {"job": {}},
  "schema": {"name": "JobStatusEnvelope", "version": "phase5-job-v1"}
}
```

Errors: `404 job_not_found`, `410 job_expired`.

Owner: API job adapter.

### GET `/api/v1/jobs/{job_id}/result`

Purpose: retrieve the completed job result.

Request body: none.

Starts engine work: no.

Mutates job state: no, except bounded cleanup may expire old retained jobs before lookup.

Idempotency: idempotent.

Success status: `200 OK` only when the job status is `completed`.

Success envelope: embeds the same payload shape as the corresponding Phase 4 synchronous endpoint success envelope inside `data.result`.

Result-not-ready behavior: `409 job_result_not_ready`.

Failed behavior: `409 internal_job_error` or the retained expected error code if the job failed from a documented engine/API error.

Cancelled behavior: `409 job_cancelled`.

Expired behavior: `410 job_expired`.

Owner: API job adapter.

### POST `/api/v1/jobs/{job_id}/retry`

Purpose: retry a retained failed, cancelled, or expired job using the original request.

Request body: none.

Starts engine work: yes, if retry is accepted.

Mutates job state: increments `attempt`, clears transient running/result fields for the new attempt, and returns the job to `queued`.

Idempotency: non-idempotent for allowed states. Repeating a successful retry request may consume another attempt if the job reaches another retryable terminal state later.

Success status: `202 Accepted`.

Errors: `404 job_not_found`, `409 job_retry_not_allowed`, `410 job_expired` when original request data is no longer retained.

Owner: API job adapter.

### DELETE `/api/v1/jobs/{job_id}`

Purpose: request cancellation or remove a retained terminal job from the in-memory store.

Request body: none.

Starts engine work: no.

Mutates job state: yes.

Idempotency: idempotent.

Success status:

- `202 Accepted` when a running job moves to `cancel_requested`;
- `200 OK` when a queued job is cancelled or a terminal retained job is removed;
- repeating deletion of a cancelled retained job returns `200 OK` until cleanup removes it.

Errors: `404 job_not_found`, `410 job_expired`.

Owner: API job adapter.

### Route examples

Exact job submission:

```json
POST /api/v1/jobs/exact
{
  "n_generations": 5,
  "probabilities": {"a_to_t": 0.2, "a_to_g": 0.5, "a_to_c": 0.3},
  "start_weights": {"TGG": 1.0}
}
```

Aggregated job submission:

```json
POST /api/v1/jobs/aggregated
{
  "n_generations": 5,
  "probabilities": {"a_to_t": 0.2, "a_to_g": 0.5, "a_to_c": 0.3},
  "start_weights": {"TGG": 100},
  "seed": 8675309
}
```

Exact comparison job submission:

```json
POST /api/v1/jobs/comparisons/exact
{
  "metric": "survivor_fraction",
  "scope": {"start_scope": "population", "start_key": "all"},
  "baseline": {"label": "baseline", "simulation": {}},
  "candidate": {"label": "candidate", "simulation": {}}
}
```

Exact-vs-sampled job submission:

```json
POST /api/v1/jobs/comparisons/exact-vs-sampled
{
  "metric": "survivor_fraction",
  "denominator_scope": "population_initial",
  "exact": {},
  "sampled": {"seed": 8675309}
}
```

Status polling:

```json
GET /api/v1/jobs/8b6c1ab0-d8cb-4fb0-bbd2-1f9d5b7397b5
```

Result retrieval:

```json
GET /api/v1/jobs/8b6c1ab0-d8cb-4fb0-bbd2-1f9d5b7397b5/result
```

Retry:

```json
POST /api/v1/jobs/8b6c1ab0-d8cb-4fb0-bbd2-1f9d5b7397b5/retry
```

Cancel or remove:

```json
DELETE /api/v1/jobs/8b6c1ab0-d8cb-4fb0-bbd2-1f9d5b7397b5
```

## 6. Job statuses and state transitions

Allowed statuses:

- `queued`
- `running`
- `completed`
- `failed`
- `cancel_requested`
- `cancelled`
- `expired`

Allowed transitions:

| From | To | Rule |
| --- | --- | --- |
| none | `queued` | job accepted |
| `queued` | `running` | worker starts job |
| `queued` | `cancelled` | cancellation before worker starts |
| `queued` | `expired` | cleanup expires a retained queued job before running |
| `running` | `completed` | engine/API work succeeds |
| `running` | `failed` | expected or unexpected job execution failure |
| `running` | `cancel_requested` | cancellation requested while work is running |
| `cancel_requested` | `cancelled` | worker reaches a safe cancellation checkpoint |
| `cancel_requested` | `completed` | work finishes before cancellation takes effect |
| `cancel_requested` | `failed` | work fails before cancellation takes effect |
| `completed` | `expired` | TTL cleanup |
| `failed` | `expired` | TTL cleanup |
| `cancelled` | `expired` | TTL cleanup |
| `failed` | `queued` | retry accepted while retained and attempts remain |
| `cancelled` | `queued` | retry accepted while retained and attempts remain |
| `expired` | `queued` | retry accepted only if original request is still retained |

Forbidden transitions:

- `completed` to `running`;
- `completed` to `queued`;
- `failed` to `running` without passing through `queued`;
- `cancelled` to `running` without passing through `queued`;
- any transition that decreases `attempt`;
- any transition that changes `job_type` or `job_id`.

Terminal states for an attempt: `completed`, `failed`, `cancelled`, and `expired`.

Result availability:

- only `completed` jobs have successful results;
- `failed` jobs have error information;
- `cancelled` jobs have cancellation error information;
- `expired` jobs do not expose scientific results.

Timestamp rules:

- all timestamps are UTC RFC 3339 strings ending in `Z`;
- `created_at` is set once;
- `started_at` is set when a worker starts an attempt;
- `completed_at` is set for `completed`, `failed`, `cancelled`, and `expired`;
- `updated_at` changes on every status, progress, result, error, retry, cancel, or expiry update.

## 7. Job metadata model

Fields appear in this order:

| Field | JSON type | Nullable | Default | Meaning | Compatibility rule |
| --- | --- | --- | --- | --- | --- |
| `job_id` | string | no | generated UUID4 | opaque job identifier | never parse semantically |
| `job_type` | string enum | no | request route | `exact`, `aggregated`, `exact_comparison`, or `exact_vs_sampled` | additive enum values require approval |
| `status` | string enum | no | `queued` | current lifecycle status | values listed in this contract only |
| `created_at` | string | no | current UTC | job creation timestamp | RFC 3339 UTC |
| `started_at` | string | yes | null | current attempt start timestamp | null until running |
| `completed_at` | string | yes | null | attempt terminal timestamp | null until terminal |
| `updated_at` | string | no | current UTC | last state update | RFC 3339 UTC |
| `progress` | number | no | `0.0` | coarse lifecycle progress in `[0.0, 1.0]` | no false precision |
| `attempt` | integer | no | `1` | current attempt number | starts at one |
| `max_attempts` | integer | no | `2` | maximum attempts retained for this job | default may change only by approval |
| `expires_at` | string | yes | null | scheduled expiry timestamp after terminal result | null before terminal retention begins |
| `cancel_supported` | boolean | no | true | whether cancellation can be requested | running cancellation is best-effort |
| `retry_supported` | boolean | no | derived | true for retryable retained failed/cancelled/expired jobs with attempts remaining | derived from state |

## 8. Job result contract

`GET /api/v1/jobs/{job_id}/result` returns a completed result only when `status == "completed"`.

Completed result retrieval embeds the same payload as the corresponding Phase 4 synchronous endpoint success envelope in `data.result`. Scientific table serialization, null handling, row order, column order, dtype names, index metadata, value kinds, and warning/error fields remain identical to Phase 4.

Result-not-ready behavior:

- `queued`, `running`, and `cancel_requested` return HTTP `409` with code `job_result_not_ready`;
- the status endpoint remains the safe polling route.

Failed behavior:

- failed jobs expose the retained error envelope under `data.error` on the status route;
- result retrieval returns an error envelope with the retained code and a concise message.

Cancelled behavior:

- cancelled jobs return `409 job_cancelled` from the result route.

Expired behavior:

- expired jobs return `410 job_expired`;
- expired jobs do not expose scientific result payloads.

## 9. Job ID contract

Job IDs are UUID4 opaque strings.

The server generates job IDs. Clients cannot provide or choose job IDs.

Job IDs are:

- not sequential;
- not meaningful;
- not paths;
- not filenames;
- not database keys;
- not cryptographic authorization.

Future authentication may restrict job visibility, but Phase 5 does not add auth.

## 10. Execution provider contract

The Phase 5 job provider is:

- in-process;
- process-memory only;
- standard-library-only;
- bounded by configured queue capacity and retained-job count;
- hosted inside the FastAPI process.

Jobs are lost on process restart. There is no cross-process coordination and no durable storage.

The provider must not:

- write job state to the filesystem;
- use Redis, Celery, RQ, PostgreSQL, SQLite, or external queues;
- spawn an unmanaged background process outside the FastAPI process;
- redefine engine scientific contracts;
- duplicate Phase 4 adapter calculations.

## 11. Concurrency and capacity contract

Proposed values awaiting approval:

| Setting | Proposed value | Rationale |
| --- | ---: | --- |
| worker count | `1` | deterministic, simple, safe in-process behavior |
| queue capacity | `20` | bounded admission control without new infrastructure |
| maximum retained jobs | `100` | bounded memory for status/result retention |
| terminal TTL | `30 minutes` | enough for polling while avoiding unbounded retention |
| running job timeout | none in Phase 5 | existing request-size limits bound work; unsafe thread termination is prohibited |
| queue-full status | `503 Service Unavailable` | queue exhaustion is service capacity overload, not per-client rate limiting |

`queue_full` responses should include a concise message and may include `Retry-After` when available. Queue capacity and retained-job cleanup are correctness requirements; wall-clock latency is not.

## 12. Job-size limits

Async/job limits are separate from synchronous Phase 4 limits, but Phase 5 proposes keeping them equal at first. Jobs improve request responsiveness and polling, not scientific scale.

| Limit | Proposed Phase 5 value | Error |
| --- | ---: | --- |
| exact job max `n_generations` | `2000` | `oversized_job_request` |
| aggregated job max `n_generations` | `500` | `oversized_job_request` |
| aggregated max normalized start count | `100_000` | `oversized_job_request` |
| exact comparison max family rows | `10_000` | `oversized_job_request` |
| exact-vs-sampled comparison max family rows | `10_000` | `oversized_job_request` |
| request body size | `1 MiB` | `oversized_job_request` |

Oversized synchronous requests must not be silently routed to jobs. A client must explicitly choose a job route.

## 13. Cancellation contract

Queued jobs can be cancelled before running.

Running jobs move to `cancel_requested`. Running exact and aggregated computations may not stop immediately unless safe checkpoints exist. Phase 5 must not kill Python threads unsafely.

Cancellation is best-effort:

- if a queued job is cancelled before worker pickup, it becomes `cancelled`;
- if a running job reaches a safe checkpoint after cancellation request, it becomes `cancelled`;
- if computation completes before observing cancellation, it may become `completed`;
- if computation fails before observing cancellation, it may become `failed`.

Cancellation request responses:

- `202 Accepted` for running jobs moved to `cancel_requested`;
- `200 OK` for queued jobs moved to `cancelled`;
- `200 OK` for already terminal retained jobs where deletion/removal succeeds;
- `404 job_not_found` or `410 job_expired` for unavailable jobs.

Cancelled result retrieval returns `409 job_cancelled`.

## 14. Retry contract

Retry is allowed only for retained jobs in these statuses:

- `failed`;
- `cancelled`;
- `expired`, only when the original request data is still retained.

Retry increments `attempt` on the same `job_id`. It does not create a new job ID.

`max_attempts` defaults to `2`. A job with `attempt >= max_attempts` returns `409 job_retry_not_allowed`.

The original request is reused. The previous error is retained in job history only if the implementation can do so without unbounded retention; otherwise the latest error is retained.

Successful retry response: `202 Accepted` with updated metadata.

## 15. Expiry and cleanup contract

Completed, failed, and cancelled jobs receive `expires_at = completed_at + 30 minutes`.

Cleanup may run:

- before job submission;
- before status lookup;
- before result lookup;
- before retry;
- before cancellation;
- after job completion.

Cleanup must enforce:

- maximum retained jobs `100`;
- no unbounded result retention;
- no unbounded error retention;
- no unbounded completed-job list.

Expired jobs return `410 job_expired` while a tombstone remains. Once fully removed, lookup returns `404 job_not_found`.

## 16. Progress contract

`progress` is a JSON number in `[0.0, 1.0]`.

Progress is coarse lifecycle information only:

- `queued`: `0.0`;
- `running`: implementation may set `0.1` or another coarse value below `1.0`;
- `completed`: `1.0`;
- `failed`: last known progress, defaulting to `0.0` if work never started;
- `cancel_requested`: last known running progress;
- `cancelled`: last known progress;
- `expired`: last known progress.

Phase 5 must not claim fine-grained scientific progress unless engine checkpoints are added through an approved mutation.

## 17. Error contract

Job-specific errors:

| Condition | HTTP status | Code | Message | Details |
| --- | ---: | --- | --- | --- |
| job missing | 404 | `job_not_found` | `Job not found.` | null or omitted |
| result not ready | 409 | `job_result_not_ready` | `Job result is not ready.` | may include current status |
| expired retained job | 410 | `job_expired` | `Job has expired.` | null or omitted |
| cancelled result | 409 | `job_cancelled` | `Job was cancelled.` | may include current status |
| retry not allowed | 409 | `job_retry_not_allowed` | `Job cannot be retried.` | may include status and attempts |
| queue full | 503 | `queue_full` | `Job queue is full. Try again later.` | may include capacity |
| job validation failure | 422 | `job_validation_error` | `Job request validation failed.` | field-level details where available |
| oversized job request | 413 | `oversized_job_request` | `Job request exceeds Phase 5 limits.` | limit details |
| internal job failure | 500 | `internal_job_error` | `Job failed unexpectedly.` | no stack trace |

The engine never displays Streamlit messages. The API never returns stack traces, filesystem paths, secrets, or raw exception reprs. No expected failure becomes a silent empty result.

Phase 5 must not add incidental probability-range or finite-number validation beyond already approved Phase 4 behavior unless this contract is amended.

## 18. Scientific preservation contract

Job workers call the same Phase 4 adapter paths or shared helpers used by synchronous endpoints.

Exact jobs call authoritative exact analysis and must not call legacy `run_simulation` separately.

Aggregated jobs require explicit integer `seed` and preserve local RNG isolation.

Comparison jobs preserve Phase 4 comparison semantics, denominator rules, alignment rules, statistical methodology, and error mapping.

Detailed sampled HTTP remains absent.

The job layer must not duplicate:

- biological definitions;
- codon tables;
- mutation matrices;
- exact propagation loops;
- sampled algorithms;
- denominator formulas;
- comparison formulas;
- statistical formulas.

## 19. OpenAPI contract

All job routes must appear in OpenAPI after implementation.

Required tags:

- `jobs`

Operation names should be stable and descriptive:

- `createExactJob`;
- `createAggregatedJob`;
- `createExactComparisonJob`;
- `createExactVsSampledJob`;
- `getJobStatus`;
- `getJobResult`;
- `retryJob`;
- `deleteJob`.

No unexpected job routes may appear.

Static OpenAPI fixture decision: create and review a Phase 5 static OpenAPI fixture after job routes exist, not during Step 2. The fixture becomes immutable only after user approval.

## 20. Security contract

Phase 5 adds no authentication. Job IDs are not authorization.

Phase 5 adds no CORS change.

The job provider must not:

- write files;
- read user-supplied paths;
- expose secrets;
- expose stack traces;
- accept user-chosen job IDs;
- create deployment artifacts;
- add Redis, databases, workers, queues, or external services;
- retain unbounded jobs, results, or errors.

Queue capacity and retained-job bounds are the Phase 5 denial-of-service protection. Future auth/deployment may restrict job visibility later.

## 21. Benchmark and load contract

Phase 5 benchmark/load evidence is advisory unless the Blueprint names a deterministic structural gate.

Required methodology:

- measure job submission latency for compact exact and aggregated requests;
- measure polling status transitions;
- measure completed result retrieval;
- exercise queue-full behavior with the approved queue capacity;
- exercise retained-job cardinality with the approved maximum;
- exercise failed-job retention;
- exercise retry behavior;
- confirm retained collection cardinality remains bounded by queue capacity, retained-job count, generations, and finite biological dimensions.

No wall-clock SLA is created in Step 2. Any future performance threshold requires approval.

## 22. Consumer/provider verification matrix

| Provider or consumer | Fields produced or consumed | Verification method | Compatibility requirement | Owner |
| --- | --- | --- | --- | --- |
| Job provider | job metadata, status transitions, queue capacity, retained results | lifecycle unit/API tests | bounded memory and approved transitions | API |
| Exact job endpoint | exact request, job metadata, exact result envelope | API tests plus exact endpoint parity | identical scientific payload to synchronous exact result | API + engine |
| Aggregated job endpoint | aggregated request, explicit seed, sampled result envelope | API tests plus RNG isolation checks | same scientific payload as synchronous aggregated result | API + engine |
| Exact comparison job endpoint | exact comparison request/result | API tests plus synchronous parity | same comparison semantics as Phase 4 | API + engine |
| Exact-vs-sampled job endpoint | calibration request/result | API tests plus synchronous parity | same statistical methodology as Phase 4 | API + engine |
| Status endpoint | job metadata model | lifecycle and OpenAPI tests | stable metadata fields and nullability | API |
| Result endpoint | completed result, not-ready/error states | lifecycle and error-envelope tests | no silent empty result; same Phase 4 payload when completed | API |
| FastAPI synchronous endpoints | existing Phase 4 routes | full Phase 4 API suite | unchanged | API |
| Engine | exact/aggregated/comparison public APIs | full scientific suite and import-boundary tests | no scientific behavior change | engine |
| Future Next.js frontend | job submission/status/result shapes | future contract fixtures | additive consumer over approved contract | future frontend |
| Tests | all routes, states, errors, limits | standard-library `unittest` | no generated drift without approval | tests |

## 23. Change protocol

1. Update `docs/phase_5_job_contract.md` first.
2. Record affected files and compatibility impact in `plans/phase-5-execution-log.md`.
3. Obtain user approval.
4. Write focused failing tests.
5. Implement the provider or consumer change.
6. Run focused and universal verification.
7. Update the execution log.
8. Stop at the next approval gate.

No implementation-first contract updates are allowed.

## 24. Explicit approval decisions

| Decision | Recommended option | Status |
| --- | --- | --- |
| Job provider | in-process standard-library provider | Proposed — awaiting Background Job Contract approval |
| Storage | process-memory only | Proposed — awaiting Background Job Contract approval |
| Dependencies | no new dependency | Proposed — awaiting Background Job Contract approval |
| Job IDs | server-generated UUID4 strings | Proposed — awaiting Background Job Contract approval |
| Worker count | `1` | Proposed — awaiting Background Job Contract approval |
| Queue capacity | `20` | Proposed — awaiting Background Job Contract approval |
| Maximum retained jobs | `100` | Proposed — awaiting Background Job Contract approval |
| Terminal TTL | `30 minutes` | Proposed — awaiting Background Job Contract approval |
| Running timeout | no hard timeout in Phase 5 | Proposed — awaiting Background Job Contract approval |
| Queue-full status | `503 Service Unavailable` | Proposed — awaiting Background Job Contract approval |
| Retry statuses | failed, cancelled, expired while retained | Proposed — awaiting Background Job Contract approval |
| Retry behavior | increment attempt on same job | Proposed — awaiting Background Job Contract approval |
| Max attempts | `2` | Proposed — awaiting Background Job Contract approval |
| Cancellation | best-effort; never kill threads unsafely | Proposed — awaiting Background Job Contract approval |
| Sync-to-job switching | none; clients choose job routes explicitly | Proposed — awaiting Background Job Contract approval |
| Detailed sampled HTTP | absent | Proposed — awaiting Background Job Contract approval |
| Redis/Celery/RQ/PostgreSQL | excluded | Proposed — awaiting Background Job Contract approval |
| Static OpenAPI fixture | create after job routes exist | Proposed — awaiting Background Job Contract approval |

## 25. Completion checklist

- [x] Provider and consumers identified.
- [x] Routes explicit.
- [x] Statuses and transitions explicit.
- [x] Metadata fields explicit.
- [x] Result behavior explicit.
- [x] Errors explicit.
- [x] Cancellation, retry, and expiry explicit.
- [x] Capacity limits explicit.
- [x] Dependency decision explicit.
- [x] Security boundaries explicit.
- [x] Benchmark methodology explicit.
- [x] Phase 1–4 preservation protected.
- [x] Step 3 can implement without guessing after approval.
- [x] Human approval decisions listed.
