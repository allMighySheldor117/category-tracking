# Phase 5 Blueprint — In-Process Background Jobs

## Status

Proposed — awaiting human review and approval.

This Blueprint is for Phase 5 only. It does not implement Phase 5 code.

Canonical repository:

- `C:\Users\hatem\OneDrive\Desktop\Project for uri\visualize code\category-tracking`
- Current completed Phase 4 commit at planning time: `8ce9277 feat: add phase 4 FastAPI backend`

## Chosen Phase 5 scope

Phase 5 should add the first background-execution layer for long-running API simulations while keeping the deployment simple:

- add explicit asynchronous job endpoints to the existing FastAPI backend;
- run jobs in-process with Python standard-library concurrency;
- keep job state in bounded process memory;
- expose job submission, status/progress, result retrieval, failure details, cancellation where safe, and safe retry;
- preserve all Phase 4 synchronous endpoints unchanged;
- do not add Redis, Celery, RQ, PostgreSQL, external workers, deployment infrastructure, authentication, or a frontend.

This is the smallest coherent Phase 5 because `future_enhancement_explained.plan.md` says Phase 5 should “add background jobs when necessary,” and also says infrastructure such as Redis, workers, and PostgreSQL should appear only when measured workloads require them.

Phase 4 already established synchronous limits to protect the API. Phase 5 should add an opt-in asynchronous path for larger but still local workloads without prematurely committing the project to distributed infrastructure.

## Scoping decision

Chosen option: **A. remain local/in-process and standard-library only**, with a clear contract boundary that can later be replaced by Redis/workers if Phase 11 deployment measurements justify it.

| Option | Decision | Reason |
| --- | --- | --- |
| A. local/in-process, standard-library only | Chosen | Smallest useful background-job slice; no new infrastructure risk; enough to support a future frontend loading/progress flow. |
| B. lightweight durable local job state | Defer | Durability needs are not proven; local files introduce cleanup, corruption, and deployment-path questions. |
| C. queue/worker dependency | Defer | Adds dependency and operational semantics before measured need. |
| D. Redis/RQ/Celery | Defer | Explicitly belongs to a later scaling/deployment decision unless workloads prove it. |
| E. design only | Not enough | Phase 4 already has a contract; Phase 5 should deliver the first job execution capability, not only a document. |

Tradeoff: in-process jobs are not durable across server restarts and are not multi-process safe. That limitation is acceptable for Phase 5 if it is explicit in the API contract and documentation. Later phases can replace the provider behind the same job API.

## Size and risk classification

Phase 5 is a large, high-risk backend feature.

It is high-risk because it introduces:

- asynchronous request lifecycle and status transitions;
- shared mutable job state;
- cancellation/retry semantics;
- background execution of scientific computations;
- new API endpoints and response contracts;
- denial-of-service and memory-pressure risks;
- error retention and result lifecycle rules.

The scientific engine must not be rewritten.

## Work type

Phase 5 is a mix of:

- new backend feature work;
- API contract work;
- job/background-processing work;
- safety and security-boundary work;
- benchmark/load-methodology work;
- documentation and final delivery work.

It is not:

- Phase 6 frontend work;
- Redis/Celery/RQ infrastructure;
- PostgreSQL persistence;
- deployment work;
- authentication/authorization work;
- scientific engine refactoring;
- Streamlit or Tkinter UI work.

## Non-negotiable preservation rules

Preserve all Phase 1–4 behavior unless a separately approved contract mutation says otherwise.

Do not change:

- exact probability outputs, `float.hex()` expectations, schemas, dtypes, ordering, denominators, or zero behavior;
- detailed sampled RNG behavior, paths, records, copy numbering, early stops, module-global random state, or final `random.getstate()`;
- aggregated sampled explicit seed behavior, copy-major draw order, structural memory bounds, and reducer equivalence;
- Streamlit widget order, labels, query/cache behavior, charts, tables, errors, accessibility, and visual identity;
- Tkinter compatibility;
- frozen diagnostic scripts or fixtures;
- biological definitions, mutation matrices, category labels, codon ordering, or stop ordering;
- Phase 4 synchronous API routes, request contracts, response envelopes, error envelopes, and limits.

Background job adapters may coordinate work and translate errors. They must not duplicate scientific formulas, mutation loops, category mappings, denominators, or simulation algorithms.

## Proposed Phase 5 API shape

The exact endpoint names and response schemas must be frozen in a Phase 5 contract before implementation.

Recommended additive routes:

- `POST /api/v1/jobs/exact`
- `POST /api/v1/jobs/aggregated`
- `POST /api/v1/jobs/comparisons/exact`
- `POST /api/v1/jobs/comparisons/exact-vs-sampled`
- `GET /api/v1/jobs/{job_id}`
- `GET /api/v1/jobs/{job_id}/result`
- `POST /api/v1/jobs/{job_id}/retry`
- `DELETE /api/v1/jobs/{job_id}`

Recommended statuses:

- `queued`
- `running`
- `completed`
- `failed`
- `cancel_requested`
- `cancelled`
- `expired`

Recommended job response fields:

- `api_version`
- `mode`
- `scientific_authority`
- `job`
- `request`
- `result`
- `tables`
- `metadata`
- `warnings`
- `errors`
- `schema`

Recommended job metadata fields:

- `job_id`
- `job_type`
- `status`
- `created_at`
- `started_at`
- `completed_at`
- `updated_at`
- `progress`
- `attempt`
- `max_attempts`
- `expires_at`
- `cancel_supported`
- `retry_supported`

## Job semantics to freeze in Step 2

The contract must explicitly decide:

- job ID format;
- whether job IDs are random UUIDs or deterministic test IDs behind injection;
- job state transition rules;
- maximum retained jobs;
- completed/failed job time-to-live;
- result size retention rules;
- error retention rules;
- cancellation guarantee: best-effort only unless the engine exposes checkpoints;
- retry eligibility;
- whether retry creates a new job ID or increments an attempt on the existing job;
- whether jobs run one-at-a-time or with a bounded thread pool;
- default worker count before implementation begins — recommended default is `1` worker until focused tests prove every approved job type is state-isolated and deterministic under concurrent execution;
- whether exact and aggregated jobs share the same concurrency limit;
- what happens when the queue is full;
- whether job endpoints accept requests larger than synchronous limits and what their separate maximums are;
- whether request body size remains `1 MiB`;
- whether job results reuse Phase 4 synchronous response payloads exactly.

## Direct-mode safety

Use direct mode unless the user explicitly authorizes branch/PR workflow.

Every implementation step must:

1. run from the canonical repo root;
2. use `PYTHONDONTWRITEBYTECODE=1`;
3. record UTC start and completion times in `plans/phase-5-execution-log.md`;
4. record touched-file manifests with pre/post byte counts and SHA-256 hashes;
5. back up existing touched files to a unique OS-temp directory before editing;
6. use serialized writes and serialized verification;
7. avoid broad recursive destructive commands;
8. preserve unrelated user changes;
9. not commit until the final user-approved handoff gate.

## Universal verification baseline

Every implementation step must preserve:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s tests -p "test_api_*.py" -v
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules); print('engine-ui-independence-ok')"
```

Every step must also verify:

- no unexpected Phase 4 route changes;
- new job routes only after the approved Phase 5 contract;
- no forbidden imports into `engine/`;
- no root runtime imports;
- frozen fixture hashes unchanged;
- diagnostic hashes unchanged;
- no `__pycache__` directories;
- Git only changes during explicit commit approval.

## Dependency graph

```text
Step 1 Revalidate Phase 4 and open Phase 5 log
  -> Step 2 Freeze Phase 5 job API contract
    -> Step 3 Add job models and in-process job store contract
      -> Step 4 Add job runner lifecycle and unit tests
        -> Step 5 Add exact and aggregated job submission/result endpoints
          -> Step 6 Add comparison job endpoints
            -> Step 7 Add cancellation, retry, expiry, and queue-full behavior
              -> Step 8 Benchmark/load methodology and advisory load check
                -> Step 9 Security/service-boundary review
                  -> Step 10 Council go/no-go
                    -> Step 11 Compatibility/API approval gate
                      -> Step 12 Final delivery gate and handoff
```

Logical parallelism:

- After Step 2, read-only review of job-state contracts and endpoint schemas may happen in parallel.
- Steps 5 and 6 can be researched independently, but writes should remain serialized because they share `api/` and test helpers.
- Security review and Council are read-only and may use subagents where the relevant ECC skill requires them.

## Step 1 — Revalidate Phase 4 and open Phase 5 execution log

### Cold-start context

Phase 4 is complete, committed, and pushed. Phase 5 must begin by proving that the current FastAPI, engine, Streamlit, Tkinter, and diagnostic baselines still pass before any job work starts.

### Touched files

- `plans/phase-5-execution-log.md`

### Preconditions

- User approved this Phase 5 Blueprint.
- Phase 4 commit `8ce9277` or a later approved Phase 4 commit is present.
- Working tree is inspected.

### Tasks

1. Record current branch, latest commit, remote, and working-tree status.
2. Verify the Phase 4 runtime/test dependencies are importable:
   - `fastapi`;
   - `fastapi.testclient.TestClient`;
   - `uvicorn`;
   - `httpx`.
3. If dependencies are missing, stop for explicit dependency-install approval rather than treating the repository as broken.
4. Record hashes for governing docs, Phase 1–5 plans/logs, API files, engine files, diagnostics, fixtures, and tests.
5. Run the universal verification baseline.
6. Create `plans/phase-5-execution-log.md`.
7. Stop if baseline fails.

### Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -c "import fastapi, httpx, uvicorn; from fastapi.testclient import TestClient; print('phase4-api-dependencies-ok')"
```

Then use the universal verification baseline.

### Exit criteria

- Universal verification passes.
- Phase 5 execution log exists.
- No application behavior changed.

### Rollback

- Delete only `plans/phase-5-execution-log.md` if rolling back the unopened Phase 5 log.
- Rerun universal verification.

### Handoff

Proceed to Step 2 contract-first job API design.

## Step 2 — Freeze the Phase 5 background-job contract

### Cold-start context

Phase 5 introduces asynchronous behavior. The job API contract must be approved before code, tests, or dependency changes are added.

### Touched files

- `docs/phase_5_job_contract.md`
- `plans/phase-5-execution-log.md`

### Preconditions

- Step 1 complete.
- No Phase 5 production code has been added.

### Tasks

1. Use `ecc:contract-first` with `ecc:api-design`.
2. Define job routes, request/response envelopes, statuses, error codes, cancellation semantics, retry semantics, expiry semantics, queue-full behavior, progress fields, and result retention.
3. Define whether Phase 5 remains standard-library in-process only.
4. Define job-size limits distinct from synchronous Phase 4 limits.
5. Define how job results reuse Phase 4 response payloads.
6. Define OpenAPI/static fixture timing for job routes.
7. List all human approval decisions.
8. Stop for explicit user approval.

### Verification

- Confirm only allowed files changed.
- Run universal verification baseline.
- Confirm no job code, tests, dependencies, fixtures, Redis/Celery/RQ/PostgreSQL/deployment/auth/frontend files were created.

### Exit criteria

- `docs/phase_5_job_contract.md` exists.
- Status is `Proposed — awaiting Background Job Contract approval`.
- User approval is required before Step 3.

### Rollback

- Restore `plans/phase-5-execution-log.md` from backup.
- Remove `docs/phase_5_job_contract.md` only if newly created and its exact path is verified.

### Handoff

After user approval, implement models/store contracts in Step 3.

## Step 3 — Add job models and in-process job store contract

### Cold-start context

The approved contract defines job statuses and metadata. This step adds typed models and a bounded in-process store without starting background execution yet.

### Touched files

- `api/jobs.py`
- `api/models.py`
- `api/__init__.py` only if needed for package registration
- `tests/test_api_jobs.py`
- `plans/phase-5-execution-log.md`

### Preconditions

- Step 2 contract is explicitly approved.
- No queue/worker dependency is approved.

### Tasks

1. Use `ecc:orch-add-feature`.
2. Use TDD: write failing job model/store tests first.
3. Add typed job dataclasses or Pydantic-compatible response helpers consistent with the contract.
4. Add bounded in-memory job store with explicit capacity and expiry metadata.
5. Ensure store state is isolated in API layer, not `engine/`.
6. Ensure no simulation execution starts in this step.

### Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s tests -p "test_api_jobs.py" -v
```

Then run universal verification baseline.

### Exit criteria

- Job models and store pass focused tests.
- No background worker starts.
- `engine/` remains UI/API independent.
- Phase 4 routes unchanged.

### Rollback

- Restore touched files from Step 3 backup.
- Remove newly created `api/jobs.py` and `tests/test_api_jobs.py` only after exact path validation.
- Rerun universal verification.

### Handoff

Proceed to Step 4 job runner lifecycle.

## Step 4 — Add job runner lifecycle

### Cold-start context

The job store exists but does not execute work. This step adds the standard-library runner with bounded concurrency, lifecycle transitions, progress metadata, failure capture, and safe shutdown behavior.

### Touched files

- `api/jobs.py`
- `tests/test_api_jobs.py`
- `tests/test_api_job_runner.py`
- `plans/phase-5-execution-log.md`

### Preconditions

- Step 3 complete.
- Contract-approved concurrency and queue-capacity values exist.

### Tasks

1. Use TDD.
2. Implement a small in-process runner using standard-library concurrency.
3. Use the Step 2 approved default worker count. Recommended default is `1` worker unless the approved contract and focused tests prove safe deterministic concurrency for every job type.
4. Preserve deterministic tests by allowing a test executor or synchronous test mode only if contract-approved.
5. Record lifecycle transitions:
   - `queued`
   - `running`
   - `completed`
   - `failed`
   - `cancel_requested`
   - `cancelled`
   - `expired`
6. Capture error envelopes without stack traces.
7. Avoid killing Python threads unsafely; cancellation is best-effort unless a job has not started.

### Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s tests -p "test_api_job_runner.py" -v
python -m unittest discover -s tests -p "test_api_jobs.py" -v
```

Then run universal verification baseline.

### Exit criteria

- Lifecycle transitions are tested.
- Queue full behavior is tested.
- Failure capture is tested.
- No scientific calculation behavior changed.

### Rollback

- Restore touched files from Step 4 backup.
- Remove newly created `tests/test_api_job_runner.py` only after exact path validation.
- Rerun universal verification.

### Handoff

Proceed to Step 5 exact/aggregated job endpoints.

## Step 5 — Add exact and aggregated simulation job endpoints

### Cold-start context

The runner can execute generic work. This step wires exact and aggregated simulation requests into async job endpoints while preserving existing synchronous Phase 4 routes.

### Touched files

- `api/main.py`
- `api/jobs.py`
- `api/models.py`
- `tests/test_api_jobs.py`
- `tests/test_api_job_endpoints.py`
- `plans/phase-5-execution-log.md`

### Preconditions

- Step 4 complete.
- Step 2 contract approved exact/aggregated job route names and limits.

### Tasks

1. Use TDD.
2. Add `POST /api/v1/jobs/exact`.
3. Add `POST /api/v1/jobs/aggregated`.
4. Add `GET /api/v1/jobs/{job_id}`.
5. Add `GET /api/v1/jobs/{job_id}/result`.
6. Reuse Phase 4 request parsing, validation, size-limit checks, and response serializers.
7. Ensure exact job work calls authoritative exact analysis.
8. Ensure aggregated job work uses explicit seed and does not mutate module-global random.
9. Ensure synchronous Phase 4 endpoints remain unchanged.

### Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s tests -p "test_api_job_endpoints.py" -v
python -m unittest discover -s tests -p "test_api_*.py" -v
```

Then run universal verification baseline.

### Exit criteria

- Exact and aggregated jobs can be submitted, monitored, and retrieved.
- Completed job results match Phase 4 synchronous response payloads for compact cases.
- Missing/invalid/oversized job requests return approved errors.
- Phase 4 synchronous routes remain stable.

### Rollback

- Restore touched files from Step 5 backup.
- Remove newly created `tests/test_api_job_endpoints.py` only after exact path validation.
- Rerun universal verification.

### Handoff

Proceed to Step 6 comparison job endpoints.

## Step 6 — Add comparison job endpoints

### Cold-start context

Exact and aggregated jobs work. This step adds asynchronous comparison jobs while preserving Phase 4 comparison routes.

### Touched files

- `api/main.py`
- `api/jobs.py`
- `tests/test_api_job_endpoints.py`
- `tests/test_api_job_comparisons.py`
- `plans/phase-5-execution-log.md`

### Preconditions

- Step 5 complete.
- Contract-approved comparison job route names and limits exist.

### Tasks

1. Use TDD.
2. Add `POST /api/v1/jobs/comparisons/exact`.
3. Add `POST /api/v1/jobs/comparisons/exact-vs-sampled`.
4. Reuse Phase 4 comparison validation and serializers.
5. Preserve nested oversize limit enforcement.
6. Ensure completed job result payloads match synchronous comparison responses for compact cases.

### Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s tests -p "test_api_job_comparisons.py" -v
python -m unittest discover -s tests -p "test_api_comparisons.py" -v
python -m unittest discover -s tests -p "test_api_*.py" -v
```

Then run universal verification baseline.

### Exit criteria

- Comparison jobs submit, run, fail, and return results according to contract.
- Existing comparison endpoints remain unchanged.
- No scientific formulas are duplicated in `api/`.

### Rollback

- Restore touched files from Step 6 backup.
- Remove newly created `tests/test_api_job_comparisons.py` only after exact path validation.
- Rerun universal verification.

### Handoff

Proceed to Step 7 cancellation, retry, expiry, and cleanup.

## Step 7 — Add cancellation, retry, expiry, and cleanup behavior

### Cold-start context

Job submission and retrieval work. This step completes operational lifecycle behavior before review.

### Touched files

- `api/main.py`
- `api/jobs.py`
- `api/models.py`
- `tests/test_api_jobs.py`
- `tests/test_api_job_runner.py`
- `tests/test_api_job_endpoints.py`
- `tests/test_api_job_comparisons.py`
- `plans/phase-5-execution-log.md`

### Preconditions

- Step 6 complete.
- Contract specifies cancellation, retry, expiry, and capacity semantics.

### Tasks

1. Use TDD.
2. Add contract-approved `DELETE /api/v1/jobs/{job_id}` cancellation endpoint behavior.
3. Add contract-approved `POST /api/v1/jobs/{job_id}/retry` retry endpoint behavior.
4. Add expiry cleanup behavior that is deterministic in tests.
5. Add queue-full behavior.
6. Add result-not-ready and job-not-found envelopes.
7. Verify route methods, status codes, state transitions, and error envelopes match the approved contract for cancellation, retry, expiry, not-ready, not-found, and queue-full cases.
8. Confirm no filesystem writes are performed by job handlers.

### Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s tests -p "test_api_jobs.py" -v
python -m unittest discover -s tests -p "test_api_job_runner.py" -v
python -m unittest discover -s tests -p "test_api_job_endpoints.py" -v
python -m unittest discover -s tests -p "test_api_job_comparisons.py" -v
```

Then run universal verification baseline.

### Exit criteria

- Cancellation, retry, expiry, not-found, not-ready, and queue-full behavior matches the approved contract.
- No CRITICAL/HIGH lifecycle ambiguity remains.
- Phase 4 synchronous APIs remain stable.

### Rollback

- Restore touched files from Step 7 backup.
- Rerun universal verification.

### Handoff

Proceed to Step 8 benchmark/load methodology.

## Step 8 — Benchmark/load methodology and advisory load check

### Cold-start context

The job layer works. This step measures whether the in-process design behaves acceptably for its intended local scope and records scaling limits without creating new performance promises.

### Touched files

- `docs/phase_5_job_benchmark_methodology.md`
- `plans/phase-5-execution-log.md`
- `tests/test_api_job_load_boundaries.py` is approved for Step 8 only if it contains deterministic structural/load-boundary tests and does not encode wall-clock SLAs.

### Preconditions

- Step 7 complete.
- No external queue dependency is approved.

### Tasks

1. Use `ecc:benchmark-methodology`, then `ecc:benchmark`.
2. Define deterministic load methodology:
   - compact exact job;
   - compact aggregated job;
   - queue-full case;
   - multiple completed job retention case;
   - failure and retry case.
3. Record advisory timings and memory observations.
4. Confirm retained job collection grows with configured retained jobs, not per-copy sampled paths.
5. Confirm no wall-clock SLA is created unless separately approved.
6. Identify thresholds that would justify Redis/workers in a later phase.

### Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s tests -p "test_api_job*.py" -v
python -m unittest discover -s tests -p "test_api_*.py" -v
```

Then run universal verification baseline.

### Exit criteria

- Advisory benchmark report exists.
- No performance threshold is treated as a correctness gate unless contract-approved.
- No Phase 11 deployment or Redis decision is implemented.

### Rollback

- Restore docs/log/test files from Step 8 backup.
- Rerun universal verification.

### Handoff

Proceed to Step 9 security/service-boundary review.

## Step 9 — Security and service-boundary review

### Cold-start context

The job API handles user input, shared mutable state, background execution, retained results, and error reporting. It needs a dedicated security review before approval.

### Touched files

- `tests/test_api_job_boundaries.py`
- `plans/phase-5-execution-log.md`

### Preconditions

- Step 8 complete.
- No writers or verification commands are running.

### Tasks

1. Use `ecc:security-review`.
2. Review:
   - malformed JSON;
   - invalid job requests;
   - unsupported job types;
   - unknown job IDs;
   - result-not-ready behavior;
   - cancellation/retry abuse;
   - queue-full behavior;
   - error leakage;
   - retained-result memory pressure;
   - no secrets/auth/deployment scope creep;
   - no filesystem writes unless separately approved;
   - no engine import of API/job modules.
3. Add boundary tests only if missing from prior steps.
4. Record findings with severity, evidence, owner, consequence, and disposition.

### Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s tests -p "test_api_job_boundaries.py" -v
python -m unittest discover -s tests -p "test_api_*.py" -v
```

Then run universal verification baseline.

### Exit criteria

- No unresolved CRITICAL/HIGH security finding remains.
- All findings are recorded.
- Step 10 Council may convene.

### Rollback

- Restore `tests/test_api_job_boundaries.py` and the execution log from backup.
- Rerun universal verification.

### Handoff

Proceed to Step 10 Council go/no-go.

## Step 10 — Council go/no-go

### Cold-start context

Security review and benchmark evidence are complete. A structured decision is needed before presenting Phase 5 for API compatibility approval.

### Touched files

- `plans/phase-5-execution-log.md`

### Preconditions

- Step 9 complete.
- Security findings include severity, evidence, owner, consequence, and disposition.
- No unresolved CRITICAL/HIGH finding remains unless the expected verdict is `REOPEN` or `BLOCK`.

### Tasks

1. Use `ecc:council`.
2. Convene Architect, Skeptic, Pragmatist, and Critic.
3. Decide:
   - `PROCEED` to Compatibility/API Approval Gate;
   - `REOPEN` an owning Step 3–8;
   - `BLOCK FOR CONTRACT DECISION`.
4. Append Council verdict and findings to the execution log.

### Verification

- Confirm Council prerequisites exist.
- Confirm no files other than execution log changed.

### Exit criteria

- Council verdict is recorded.
- If `PROCEED`, Step 11 may start only after user approval.
- If `REOPEN` or `BLOCK`, stop for explicit user direction.

### Rollback

- Restore execution log from backup if the Council entry is malformed.

### Handoff

Proceed according to Council verdict.

## Step 11 — Compatibility/API approval gate

### Cold-start context

Council has approved proceeding. This step proves Phase 5 is ready for final handoff and resolves approval-gate decisions.

### Touched files

- `plans/phase-5-execution-log.md`

### Preconditions

- Step 10 Council verdict is `PROCEED`.
- User approved starting Step 11.

### Tasks

1. Use `ecc:delivery-gate`.
2. Run universal verification baseline.
3. Verify Phase 4 synchronous endpoints remain unchanged.
4. Verify Phase 5 job endpoints match the approved contract.
5. Verify no unexpected routes exist.
6. Verify boundary/security rules.
7. Verify benchmark/load evidence is recorded.
8. Resolve deferred LOW findings by recommendation only.
9. Stop for explicit user approval before Step 12.

### Verification

Use universal verification baseline and focused job API suites:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s tests -p "test_api_job*.py" -v
python -m unittest discover -s tests -p "test_api_*.py" -v
python -m unittest discover -s tests -p "test_*.py"
```

### Exit criteria

- No unresolved CRITICAL/HIGH/MEDIUM finding remains unless explicitly deferred by user approval.
- User is asked to approve final Step 12 handoff.

### Rollback

- Restore execution log from backup.

### Handoff

Proceed to final delivery gate after user approval.

## Step 12 — Final delivery gate and handoff

### Cold-start context

Implementation, security review, Council, benchmark/load checks, and compatibility approval have passed. This final step records evidence and prepares the commit handoff.

### Touched files

- `plans/phase-5-execution-log.md`
- Optional documentation file if explicitly named by the approved contract/Blueprint

### Preconditions

- Step 11 approved by user.

### Tasks

1. Use `ecc:delivery-gate`.
2. Run final verification.
3. Run final boundary and hash audit.
4. Confirm Phase 6 was not started.
5. Confirm no unapproved dependency/infrastructure was added.
6. Record final evidence, backup locations, deferred findings, and recommended commit message.
7. Stop before commit.

### Verification

Use universal verification baseline and focused job API suites.

### Exit criteria

- Final handoff is complete.
- No unresolved blocker remains.
- User is asked to approve commit.

### Rollback

- Restore only manifest-listed files from recorded backups.
- Rerun universal verification.

### Handoff

Recommended commit message:

```text
feat: add phase 5 background job API
```

## Approval gates

| Gate | After step | Required approval |
| --- | ---: | --- |
| Blueprint approval | Blueprint | Approve Phase 5 plan before Step 1. |
| Background Job Contract approval | Step 2 | Approve job API/status/lifecycle semantics before code. |
| Security review gate | Step 9 | Resolve CRITICAL/HIGH findings before Council. |
| Council go/no-go | Step 10 | Decide PROCEED, REOPEN, or BLOCK. |
| Compatibility/API approval gate | Step 11 | User approves final compatibility state before handoff. |
| Final delivery/commit gate | Step 12 | User approves commit. |

## Recommended ECC skill order

1. `ecc:orch-add-feature` — Step 1 baseline/log setup only; no feature implementation.
2. `ecc:contract-first` + `ecc:api-design` — Step 2 job API/lifecycle contract.
3. `ecc:orch-add-feature` — Steps 3–7 TDD implementation.
4. `ecc:benchmark-methodology` — Step 8 methodology.
5. `ecc:benchmark` — Step 8 advisory load check.
6. `ecc:security-review` — Step 9 service-boundary/security review.
7. `ecc:council` — Step 10 go/no-go.
8. `ecc:delivery-gate` — Step 11 compatibility/API approval gate.
9. `ecc:delivery-gate` — Step 12 final handoff.

Do not use `ecc:browser-qa` unless a real browser-visible frontend or docs page must be manually inspected. Do not use `ecc:accessibility` in Phase 5 unless a user-facing UI changes.

## Benchmark/load methodology requirements

Phase 5 benchmark work is advisory and structural unless a later contract freezes hard thresholds.

Measure:

- job submission latency;
- status polling behavior;
- exact compact job completion;
- aggregated compact job completion;
- concurrent queueing with bounded worker count;
- queue-full rejection;
- completed result retention count;
- failed job retention;
- retry behavior;
- memory cardinality as retained jobs increase.

Do not:

- create a production SLA;
- optimize scientific algorithms;
- change Phase 3 optimized internals;
- introduce Redis/Celery/RQ as a benchmark “fix” without contract mutation.

## Security review gates

Security review must inspect:

- user input validation;
- queue-full and oversize request handling;
- job ID guessing/enumeration risk;
- result retention and error leakage;
- cancellation/retry abuse;
- background exception handling;
- global state isolation;
- no filesystem writes unless approved;
- no secrets;
- no auth claims;
- no CORS unless approved;
- no root runtime imports;
- no engine dependency on API/job modules.

## Anti-pattern catalog

- Do not add Redis, Celery, RQ, PostgreSQL, Docker, Kubernetes, deployment files, auth, or frontend code in Phase 5 unless the approved contract mutates scope.
- Do not make job results durable while claiming standard-library in-process semantics.
- Do not expose detailed sampled per-copy paths over HTTP.
- Do not silently route oversized synchronous requests to background jobs.
- Do not automatically switch between synchronous and background execution.
- Do not duplicate Phase 4 endpoint code instead of reusing handlers/serializers safely.
- Do not store per-copy sampled records in job state.
- Do not retain unbounded job results.
- Do not leak stack traces through job failure responses.
- Do not kill running Python threads unsafely for cancellation.
- Do not weaken Phase 1–4 tests, fixtures, diagnostics, tolerances, hashes, contracts, or security checks.
- Do not modify Streamlit/Tkinter behavior.
- Do not start Phase 6 frontend.

## Formal plan-mutation protocol

If evidence shows this Blueprint is wrong:

1. Record the evidence and affected step in `plans/phase-5-execution-log.md`.
2. Identify whether the issue is scientific, API-contract, security, dependency, infrastructure, or implementation scope.
3. Propose the smallest contract/Blueprint mutation.
4. Record touched-file impact and rollback impact.
5. Stop for explicit user approval.
6. After approval, update the authoritative contract/Blueprint first.
7. Add failing tests.
8. Implement only the approved mutation.
9. Rerun focused and universal verification.
10. Resume from the affected step.

No implementation-first contract changes are allowed.

## Unresolved decisions requiring user approval

These must be resolved in Step 2 before implementation:

| Decision | Recommended option | Status |
| --- | --- | --- |
| Job provider | In-process standard-library provider | Proposed — awaiting approval |
| Job durability | Process-memory only; jobs lost on restart | Proposed — awaiting approval |
| Maximum retained jobs | Choose small bounded value, e.g. 100 | Proposed — awaiting approval |
| Worker concurrency | Choose bounded value, e.g. 1 or 2 | Proposed — awaiting approval |
| Queue capacity | Choose bounded value, e.g. 20 queued jobs | Proposed — awaiting approval |
| Job TTL | Choose explicit TTL for completed/failed jobs | Proposed — awaiting approval |
| Job ID format | UUID4 opaque string | Proposed — awaiting approval |
| Retry semantics | Retry failed/cancelled jobs explicitly | Proposed — awaiting approval |
| Cancellation semantics | Best-effort; queued jobs cancellable, running jobs cancel only at safe boundaries | Proposed — awaiting approval |
| Job size limits | Larger than synchronous but still bounded | Proposed — awaiting approval |
| Automatic sync-to-job switching | Do not add automatic switching | Proposed — awaiting approval |
| Static OpenAPI fixture | Decide whether to create Phase 5 fixture after job routes exist | Proposed — awaiting approval |

## Deferred work

- Redis, Celery, RQ, external workers, or distributed queues.
- PostgreSQL or durable shared result storage.
- Authentication and authorization.
- CORS policy for a frontend.
- Deployment infrastructure.
- Next.js frontend.
- Export/report generation.
- Phase 6+ browser workflows.
- Scientific engine rewrites or optimizations.
- New probability-validation behavior unrelated to job boundaries.

## Completion checklist

- [x] Phase 5 scope chosen.
- [x] Smallest coherent infrastructure option selected.
- [x] Phase 1–4 preservation rules included.
- [x] Contract-first gate included.
- [x] Job lifecycle semantics identified.
- [x] Dependency/infrastructure decision matrix included.
- [x] Step-by-step implementation plan included.
- [x] Dependency graph included.
- [x] Touched files and verification commands included for each step.
- [x] Security review gate included.
- [x] Benchmark/load methodology included.
- [x] Compatibility/API approval gate included.
- [x] Final delivery/commit gate included.
- [x] Anti-pattern catalog included.
- [x] Plan mutation protocol included.
- [x] Unresolved decisions listed.
- [x] No Phase 5 implementation code included.

## Adversarial review record

Blueprint review completed with no CRITICAL or HIGH findings.

Resolved MEDIUM review findings:

- Clarified that Step 2 must approve the default worker count before Step 4; recommended default is `1` worker until deterministic concurrency is proven.
- Explicitly named `DELETE /api/v1/jobs/{job_id}` and `POST /api/v1/jobs/{job_id}/retry` in Step 7.
- Added Step 1 dependency preflight for FastAPI, TestClient, Uvicorn, and httpx.

Resolved LOW review findings:

- Clarified that `tests/test_api_job_load_boundaries.py` is approved in Step 8 only for deterministic structural/load-boundary tests with no wall-clock SLA.
- Clarified the recommended skill order entry for Step 1 as baseline/log setup only.
