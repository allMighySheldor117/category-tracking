# Phase 4 Blueprint — FastAPI Backend

## Status

Proposed — awaiting human review and approval.

This Blueprint is for Phase 4 only. It does not implement Phase 4 code.

Canonical repository:

- `C:\Users\hatem\OneDrive\Desktop\Project for uri\visualize code\category-tracking`
- Current completed Phase 3 commit at planning time: `e5894c5 refactor: optimize phase 3 computation internals`

## Chosen Phase 4 scope

Phase 4 should build the first service-layer slice: a small, synchronous FastAPI backend that exposes the existing Python engine through stable, typed JSON request and response contracts.

This is the smallest coherent Phase 4 because `future_enhancement_explained.plan.md` defines Stage 2 as:

- Phase 4: build the FastAPI backend;
- Phase 5: add background jobs when necessary;
- Phase 6: build the Next.js frontend.

Therefore Phase 4 must stop at a tested backend gateway. It must not start workers, Redis, PostgreSQL, deployment, authentication, or a Next.js interface.

## Size and risk classification

Phase 4 is a large, high-risk service-boundary feature.

It is high-risk because it introduces:

- a new HTTP/API contract;
- new runtime dependencies;
- JSON serialization of scientific DataFrames and typed results;
- request validation and error translation around existing scientific exceptions;
- a second programmatic interface that future frontend and notebook callers may rely on.

The scientific engine itself should not be rewritten. Phase 4 is a service adapter over the Phase 2/3 engine.

## Work type

Phase 4 is a mix of:

- new feature work: FastAPI service package and endpoints;
- scientific/API contract work: stable JSON request and response schemas;
- testing work: API contract and integration tests;
- documentation work: backend README/API docs;
- light repository work: dependency file and local run instructions.

It is not:

- a behavior-preserving engine refactor;
- a Streamlit redesign;
- a Next.js frontend;
- a job queue/background worker phase;
- a deployment phase.

## Non-negotiable preservation rules

Preserve all Phase 1–3 behavior unless a separately approved contract mutation says otherwise.

Do not change:

- exact probability outputs, `float.hex()` expectations, schemas, dtypes, ordering, denominators, or zero behavior;
- detailed sampled RNG behavior, paths, records, copy numbering, early stops, module-global random state, or final `random.getstate()`;
- aggregated sampled explicit seed behavior, copy-major draw order, structural memory bounds, and reducer equivalence;
- Streamlit widget order, labels, query/cache behavior, charts, tables, errors, accessibility, and visual identity;
- Tkinter compatibility;
- frozen diagnostic scripts or fixtures;
- biological definitions, mutation matrices, category labels, codon ordering, or stop ordering.

FastAPI adapters may validate HTTP request shape and translate known engine errors, but they must not add new scientific calculation rules or duplicate engine algorithms.

## Direct-mode safety

Use direct mode unless the user explicitly authorizes a branch/PR workflow.

Every implementation step must:

1. run from the canonical repo root;
2. use `PYTHONDONTWRITEBYTECODE=1`;
3. record UTC start and completion times in `plans/phase-4-execution-log.md`;
4. record touched-file manifests with pre/post byte counts and SHA-256 hashes;
5. back up existing touched files to a unique OS-temp directory before editing;
6. use serialized writes and serialized verification;
7. avoid broad recursive destructive commands;
8. preserve unrelated user changes;
9. not commit until the final user-approved handoff gate.

## Universal verification baseline

Every implementation step must preserve:

```powershell
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"
```

After the API dependency step, also run the focused API tests defined by that step.

## Proposed API shape

The exact endpoint names are proposed and must be frozen in the Phase 4 contract before implementation:

- `GET /health`
- `GET /api/metadata`
- `POST /api/simulate/exact`
- `POST /api/simulate/aggregated`
- `POST /api/compare/exact`
- `POST /api/compare/exact-vs-sampled`

Recommended Phase 4 response posture:

- return JSON records derived from existing engine DataFrames;
- include schema/version metadata in responses;
- include explicit value meanings: `probability_weight`, `copy_count`, `fraction`, `status`;
- expose exact probability as the authoritative deterministic mode;
- expose aggregated sampled as an explicit experimental mode;
- do not expose detailed per-copy sampled paths over HTTP in Phase 4 unless the contract gate explicitly approves it.

## Dependency graph

```text
Step 1 Phase 3 revalidation and execution log
  -> Step 2 API contract and dependency approval
    -> Step 3 FastAPI dependency and app skeleton
      -> Step 4 Exact simulation endpoint
      -> Step 5 Aggregated sampled endpoint
      -> Step 6 Comparison endpoints
        -> Step 7 Error handling, metadata, and OpenAPI documentation
          -> Step 8 Service boundary and security review
            -> Step 9 Compatibility/API approval gate
              -> Step 10 Final documentation, registration, and handoff
```

Logical parallelism:

- Steps 4, 5, and 6 can be researched independently after Step 3, but implementation writes should remain serialized.
- Review work in Step 8 may be read-only and parallel if no writers or verification commands are running.

## Step 1 — Revalidate Phase 3 and open Phase 4 execution log

### Cold-start context

Phase 3 is complete, committed, and pushed. Phase 4 must start from a clean repository and prove that all Phase 1–3 behavior still passes before introducing a service layer.

### Touched files

- `plans/phase-4-execution-log.md`

### Preconditions

- User approved this Phase 4 Blueprint.
- Working tree is inspected.
- No Phase 4 code exists.

### Tasks

1. Record current commit, branch, remote, and working-tree status.
2. Record hashes for governing docs, engine files, diagnostics, fixtures, and Phase 3 benchmark docs.
3. Run the universal verification baseline.
4. Create `plans/phase-4-execution-log.md`.
5. Stop if the baseline fails.

### Verification

```powershell
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"
```

### Exit criteria

- Universal verification passes.
- Phase 4 execution log exists.
- No application behavior changed.

### Rollback

- Delete only `plans/phase-4-execution-log.md` if rolling back the unopened Phase 4 log.
- Rerun the universal verification baseline.

### Handoff

Proceed to Step 2 contract-first API design.

## Step 2 — Freeze the Phase 4 API contract and dependency decision

### Cold-start context

Phase 4 introduces a new HTTP boundary. The API contract must be approved before code, tests, or dependency files are added.

### Touched files

- `docs/phase_4_api_contract.md`
- `plans/phase-4-execution-log.md`

### Preconditions

- Step 1 completed.
- No FastAPI code or dependency file has been added.

### Tasks

1. Use `ecc:contract-first`.
2. Define request and response schemas for all Phase 4 endpoints.
3. Define JSON table orientation, field ordering, nullability, status labels, error shapes, version fields, and scientific meanings.
4. Decide whether Phase 4 exposes aggregated sampled only, or also a capped detailed sampled endpoint.
5. Decide dependency strategy:
   - recommended: `fastapi[standard]` or `fastapi`, `uvicorn`, and whatever test-client dependency is required;
   - document exact packages and why.
6. Freeze package names plus approved version pins or version ranges, and define whether Phase 4 uses a simple `requirements.txt` or another dependency/lock strategy.
7. Decide whether to create a reviewed static API schema fixture:
   - recommended: `tests/fixtures/phase4_api_contract_openapi.json`;
   - if approved, the fixture becomes immutable implementation evidence and Step 7–9 must compare generated OpenAPI/schema/error shapes against it.
8. Define error translation from engine exceptions to HTTP status codes.
9. Mark the contract `Proposed — awaiting API Contract approval`.
10. Stop for explicit user approval.

### Verification

- Confirm only allowed files changed.
- Confirm no production API code, tests, dependency files, or fixtures were created.
- If a static API fixture is approved for creation during Step 2, confirm it is listed in the manifest and marked proposed, not silently generated from implementation.
- Run the universal verification baseline.

### Exit criteria

- `docs/phase_4_api_contract.md` exists and is explicit enough for implementation without guessing.
- All unresolved decisions are listed.
- User approval is required before Step 3.

### Rollback

- Restore `plans/phase-4-execution-log.md` from backup.
- Remove `docs/phase_4_api_contract.md` only if it was newly created and rollback is approved.

### Handoff

After user approval, proceed to Step 3.

## Step 3 — Add FastAPI dependency and service skeleton

### Cold-start context

The approved API contract exists. This step adds the smallest runnable FastAPI app without scientific endpoint behavior beyond health/metadata.

### Touched files

- `requirements.txt` or approved dependency file
- `api/__init__.py`
- `api/main.py`
- `api/models.py`
- `api/serializers.py`
- `tests/test_api_app.py`
- `tests/fixtures/phase4_api_contract_openapi.json` if approved in Step 2
- `README.md`
- `plans/phase-4-execution-log.md`

### Preconditions

- Step 2 contract and dependency choice approved.
- Working tree inspected and backed up.

### Tasks

1. Add approved dependency file.
2. Add `api/` package with a FastAPI app factory or `app`.
3. Add `GET /health`.
4. Add `GET /api/metadata` with codon/category/version metadata sourced from engine, not duplicated tables.
5. Add serializers for DataFrames and scalar metadata, but no endpoint-specific scientific calculations.
6. Add focused `unittest` API skeleton tests.
7. Add a fresh-environment/import check proving the approved FastAPI/TestClient dependency set imports from the dependency file strategy.
8. If a static OpenAPI fixture was approved, compare generated route names, methods, operation IDs, request schemas, response schemas, error schemas, and version fields against it.
9. Document local run command.

### Verification

```powershell
python -m unittest discover -s tests -p "test_api_app.py" -v
python -c "import fastapi; from fastapi.testclient import TestClient; print('fastapi-testclient-ok')"
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"
```

### Exit criteria

- API app imports without importing UI frameworks into `engine`.
- Health and metadata endpoints pass.
- Existing Streamlit/Tkinter behavior is unchanged.

### Rollback

- Restore modified files from Step 3 backup.
- Restore an existing dependency file from backup if one existed before Step 3.
- Remove a newly created dependency file only after validating its exact path and pre-change nonexistence.
- Remove only new `api/`, fixture, and focused test files after validating exact paths.

### Handoff

Proceed to exact endpoint implementation.

## Step 4 — Implement exact simulation endpoint

### Cold-start context

Exact probability is the authoritative deterministic scientific path. The HTTP endpoint must call `run_exact_analysis` once and serialize approved exact tables.

### Touched files

- `api/main.py`
- `api/models.py`
- `api/serializers.py`
- `tests/test_api_exact.py`
- `plans/phase-4-execution-log.md`

### Preconditions

- Step 3 skeleton green.
- API contract approved.

### Tasks

1. Write failing API tests for `POST /api/simulate/exact`.
2. Validate request fields according to the API contract.
3. Build substitution matrix through `engine.mutation_matrix`.
4. Call `run_exact_analysis`.
5. Serialize category metrics, survivor fractions, survival by start, stop outcomes, codon outcomes, and convergence according to the approved contract.
6. Preserve empty/zero-generation behavior.
7. Prove response values match same-process engine outputs exactly where JSON permits.
8. Test approved synchronous request-size limits for exact generations and starting-weight payloads.

### Verification

```powershell
python -m unittest discover -s tests -p "test_api_exact.py" -v
python -m unittest discover -s tests -p "test_exact_analysis.py" -v
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
```

### Exit criteria

- Exact endpoint passes contract tests.
- Engine output remains unchanged.
- No scientific calculations are duplicated in `api/`.

### Rollback

- Restore touched files from Step 4 backup.
- Remove newly created focused test only if Step 4 is rolled back.

### Handoff

Proceed to aggregated sampled endpoint.

## Step 5 — Implement aggregated sampled endpoint

### Cold-start context

Aggregated sampled mode is explicit and experimental. It uses local seed and bounded counters. Detailed sampled compatibility must not be changed or silently replaced.

### Touched files

- `api/main.py`
- `api/models.py`
- `api/serializers.py`
- `tests/test_api_aggregated.py`
- `plans/phase-4-execution-log.md`

### Preconditions

- Step 4 exact endpoint green.
- Contract approved whether aggregated is exposed in Phase 4.

### Tasks

1. Write failing API tests for `POST /api/simulate/aggregated`.
2. Require explicit integer seed.
3. Call `run_aggregated_experiment`.
4. Serialize retained generation counters and final counters only.
5. Do not expose individual copy records, paths, copy IDs, or legacy global RNG state.
6. Prove global `random.getstate()` isolation and count conservation.
7. Confirm response cardinality is bounded by generation count and finite biological state.
8. Test approved synchronous request-size limits for sampled copies, generations, and payload size.

### Verification

```powershell
python -m unittest discover -s tests -p "test_api_aggregated.py" -v
python -m unittest discover -s tests -p "test_aggregated_tracking.py" -v
python -m unittest discover -s tests -p "test_aggregated_analysis.py" -v
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
```

### Exit criteria

- Aggregated endpoint is explicit and experimental.
- Detailed sampled API remains byte/behavior unchanged.
- No per-copy retention leaks into responses.

### Rollback

- Restore touched files from backup.
- Remove focused test only if newly created in this step.

### Handoff

Proceed to comparison endpoints.

## Step 6 — Implement comparison endpoints

### Cold-start context

Phase 2 added directed exact comparisons and exact-versus-sampled calibration. Phase 4 exposes these through JSON without changing formulas or statistical methodology.

### Touched files

- `api/main.py`
- `api/models.py`
- `api/serializers.py`
- `tests/test_api_comparisons.py`
- `plans/phase-4-execution-log.md`

### Preconditions

- Steps 4–5 green.
- API contract defines comparison request shapes and response schemas.

### Tasks

1. Add failing tests for `POST /api/compare/exact`.
2. Add failing tests for `POST /api/compare/exact-vs-sampled`.
3. Reuse engine comparison functions:
   - `compare_numeric_metric`;
   - `compare_convergence`;
   - `compare_exact_to_sampled`.
4. Preserve direction semantics and `pd.NA` JSON representation from the approved API contract.
5. Preserve Wilson/Bonferroni methodology and fixed meanings of sample size, interval, and verdict fields.
6. Test approved synchronous request-size limits for comparison families and nested request payloads.

### Verification

```powershell
python -m unittest discover -s tests -p "test_api_comparisons.py" -v
python -m unittest discover -s tests -p "test_comparisons.py" -v
python -m unittest discover -s tests -p "test_statistical_convergence.py" -v
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
```

### Exit criteria

- Comparison endpoints match engine outputs and approved schema contracts.
- No comparison formulas are copied into endpoint render/serialization code.

### Rollback

- Restore touched files from backup.
- Remove focused test only if newly created in this step.

### Handoff

Proceed to error handling and API documentation.

## Step 7 — Add error translation, OpenAPI metadata, and documentation

### Cold-start context

The API must translate expected engine errors into concise JSON errors while preserving explicit engine failures. The service must remain discoverable for future frontend work.

### Touched files

- `api/main.py`
- `api/models.py`
- `README.md`
- `docs/phase_4_api_contract.md`
- `tests/fixtures/phase4_api_contract_openapi.json` if approved
- `tests/test_api_errors.py`
- `plans/phase-4-execution-log.md`

### Preconditions

- Steps 3–6 green.

### Tasks

1. Add tests for malformed requests, invalid scopes, unsupported comparisons, schema mismatches, and invariant failures.
2. Map expected exceptions to documented HTTP status codes.
3. Ensure no expected engine error becomes a silent empty result.
4. Add OpenAPI title/version/tags matching the approved contract.
5. Add contract-conformance tests comparing implemented routes, request schemas, response schemas, error shapes, and documented version fields against `docs/phase_4_api_contract.md` and the static OpenAPI fixture if approved.
6. Document local run and verification commands.
7. Do not add authentication, rate limiting, deployment, or persistence.

### Verification

```powershell
python -m unittest discover -s tests -p "test_api_errors.py" -v
python -m unittest discover -s tests -p "test_api_*.py" -v
python -c "from api.main import app; schema=app.openapi(); assert schema['openapi']; assert schema['info']['version']"
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
```

### Exit criteria

- API errors are consistent, concise, and documented.
- Existing UI behavior remains unchanged.

### Rollback

- Restore touched files from backup.

### Handoff

Proceed to boundary and security review.

## Step 8 — Service boundary, dependency, and security review

### Cold-start context

The backend exists. Before approval, verify it is a thin service adapter and has not leaked UI, frontend, deployment, or scientific duplication into Phase 4.

### Touched files

- `tests/test_api_boundaries.py`
- `tests/test_api_contract_conformance.py` if not already created in Step 7
- `plans/phase-4-execution-log.md`

### Preconditions

- Steps 3–7 green.

### Tasks

1. Add or run boundary tests proving:
   - `engine/` does not import FastAPI;
   - `api/` does not import Streamlit, Tkinter, Plotly, or UI colors;
   - `api/` imports engine public APIs, not root research files;
   - biological tables and algorithms are not duplicated in `api/`;
   - dependency files contain only approved Phase 4 dependencies.
   - generated OpenAPI routes, methods, schema names, error shapes, and version fields match the approved contract or reviewed static fixture.
2. Run a read-only security review focused on request validation, error disclosure, dependency choice, file-system access, and denial-of-service risks from large synchronous requests.
3. Classify every finding by severity and owning step.
4. Resolve CRITICAL/HIGH findings through the owning step before Step 9.

### Verification

```powershell
python -m unittest discover -s tests -p "test_api_boundaries.py" -v
python -m unittest discover -s tests -p "test_api_contract_conformance.py" -v
python -m unittest discover -s tests -p "test_api_*.py" -v
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5','fastapi'}; assert not forbidden.intersection(sys.modules)"
```

### Exit criteria

- No CRITICAL/HIGH findings remain.
- Engine remains UI/API-framework independent.
- Phase 5/6/11 work has not leaked into Phase 4.

### Rollback

- Restore boundary tests/log from backup.
- Reopen owning step for any implementation rollback.

### Handoff

Proceed to compatibility/API approval gate.

## Step 9 — Compatibility and API approval gate

### Cold-start context

The FastAPI backend is implemented and reviewed. This step decides whether Phase 4 can be approved before final handoff.

### Touched files

- `plans/phase-4-execution-log.md`

### Preconditions

- Step 8 complete.
- All tests and diagnostics green.

### Tasks

1. Run the universal verification baseline.
2. Run all API tests.
3. Verify OpenAPI schema can be generated.
4. Verify generated OpenAPI and error shapes match the approved Phase 4 API contract and static fixture if approved.
5. Confirm Streamlit and Tkinter compatibility remain unchanged.
6. Confirm no browser/accessibility QA is required unless UI files changed.
7. Use `ecc:council` for go/no-go if evidence is ambiguous or any MEDIUM finding remains.
8. Stop for explicit user approval.

### Verification

```powershell
python -m unittest discover -s tests -p "test_api_*.py" -v
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "from api.main import app; assert app.openapi()['openapi']"
python -m unittest discover -s tests -p "test_api_contract_conformance.py" -v
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5','fastapi'}; assert not forbidden.intersection(sys.modules)"
```

### Exit criteria

- User explicitly approves Phase 4 compatibility/API gate.
- No Step 10 work begins before approval.

### Rollback

- No code rollback unless the gate finds a confirmed defect.
- Reopen the owning implementation step if needed.

### Handoff

After approval, proceed to final documentation and handoff.

## Step 10 — Final documentation, registration, and handoff

### Cold-start context

Phase 4 has been approved. Finalize docs and prepare a commit handoff without starting Phase 5.

### Touched files

- `README.md`
- `engine/README.md` only if API references require a cross-link
- `docs/phase_4_api_contract.md`
- `plans/phase-4-execution-log.md`

### Preconditions

- Step 9 approved by user.

### Tasks

1. Record final approval and verification evidence.
2. Ensure README documents:
   - Streamlit run command;
   - Tkinter run command;
   - FastAPI run command;
   - verification commands;
   - explicit non-goals for jobs/frontend/deployment.
3. Record final hashes.
4. Prepare conventional commit recommendation.
5. Stop before committing unless the user explicitly asks to commit.

### Verification

```powershell
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "from api.main import app; assert app.openapi()['openapi']"
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5','fastapi'}; assert not forbidden.intersection(sys.modules)"
```

### Exit criteria

- Phase 4 is fully documented and ready to commit.
- No Phase 5 jobs, Redis, persistence, frontend, deployment, or auth exists.

### Rollback

- Restore docs/log from backup.
- Do not roll back implementation files from a Step 10 docs-only rollback.

### Handoff

Recommended commit:

```text
feat: add phase 4 FastAPI backend
```

## Approval gates

1. Blueprint approval gate — before any Phase 4 work.
2. API Contract and dependency approval gate — after Step 2.
3. Security/boundary review gate — Step 8.
4. Compatibility/API approval gate — Step 9.
5. Final handoff/commit gate — Step 10.

## Recommended ECC skill order after Blueprint approval

1. `ecc:orch-add-feature` — Step 1 only, revalidate Phase 3 and open the Phase 4 execution log.
2. `ecc:contract-first` — Step 2 only, freeze API contract and dependency decision.
3. `ecc:api-design` or `ecc:fastapi-patterns` — optional read-only support for Step 2/3 if contract or FastAPI structure is unclear.
4. `ecc:orch-add-feature` — Steps 3–7 under TDD, serialized.
5. `ecc:security-review` — Step 8 security review.
6. `ecc:council` — Step 9 go/no-go if any ambiguity or non-blocking findings remain.
7. `ecc:browser-qa` and `ecc:accessibility` — only if Streamlit/UI files change, which Phase 4 should normally avoid.
8. `ecc:orch-refine-code` or `ecc:delivery-gate` — Step 10 final handoff only; do not use it for implementation.

## Anti-pattern catalog

- Building a Next.js frontend in Phase 4.
- Adding Redis, workers, PostgreSQL, queues, or job retry states before Phase 5.
- Adding deployment, Docker, cloud hosting, auth, or user accounts before a deployment phase.
- Copying codon tables, category maps, simulation loops, denominators, or comparison formulas into `api/`.
- Returning presentation-only percentages without numerator/denominator context.
- Exposing detailed sampled per-copy histories by default.
- Silently switching from exact to sampled or from detailed to aggregated mode.
- Changing Streamlit or Tkinter behavior while adding the API.
- Weakening diagnostics, fixtures, tolerances, seeds, or statistical confidence settings.
- Adding broad dependencies without contract approval.
- Treating OpenAPI generation as proof of scientific correctness.

## Plan mutation protocol

If implementation evidence conflicts with this Blueprint:

1. stop the affected step;
2. record the evidence in `plans/phase-4-execution-log.md`;
3. identify the owning contract, step, and touched files;
4. propose the smallest Blueprint mutation;
5. obtain explicit user approval;
6. update the API contract first if the HTTP boundary changes;
7. write focused failing tests;
8. implement only the approved mutation;
9. rerun focused and universal verification.

No implementation-first contract changes are allowed.

## Unresolved decisions requiring human approval

These must be resolved at Step 2:

1. Exact dependency set: `fastapi[standard]` vs separate `fastapi`, `uvicorn`, and test-client packages.
2. Whether Phase 4 exposes only aggregated sampled HTTP mode or also a capped detailed sampled endpoint.
3. JSON DataFrame orientation: recommended `records` plus explicit `columns`, `dtypes`, and `index_kind`.
4. Maximum synchronous request sizes for generations, starting codons, and sampled copies before Phase 5 jobs exist.
5. Error-code mapping for scientific validation versus malformed JSON.
6. Whether `GET /api/metadata` should include all codon/category definitions or only UI-friendly labels and valid options.
7. Whether the API contract gets a static reviewed JSON fixture during Step 2/3. Recommended path if approved: `tests/fixtures/phase4_api_contract_openapi.json`.

## Blueprint adversarial review record

Planning self-review findings:

- CRITICAL: none.
- HIGH: none.
- MEDIUM: The Phase 4 dependency decision is intentionally unresolved because the current repository has no dependency file. This is routed to the Step 2 API Contract and dependency approval gate, now with explicit version/lock strategy requirements.
- MEDIUM: The first review noted OpenAPI/API-contract conformance needed a machine gate. Steps 3, 7, 8, and 9 now require route/schema/error/version conformance checks against the approved contract and static fixture if approved.
- MEDIUM: The first review noted optional fixture paths were missing from touched-file lists. Conditional `tests/fixtures/phase4_api_contract_openapi.json` ownership is now listed.
- LOW: Browser/accessibility QA is conditional because Phase 4 should not modify UI files. If a later mutation touches Streamlit, the Step 9 gate must require those skills.
- LOW: The first review noted request-size/DoS limits needed implementation tests and dependency rollback needed clearer handling. Steps 3–7 now include explicit dependency rollback and request-size tests.

## Completion checklist

- [x] Phase 4 scoped to FastAPI backend only.
- [x] Phases 1–3 preserved.
- [x] Phase 5 jobs deferred.
- [x] Phase 6 frontend deferred.
- [x] API contract approval gate included.
- [x] Dependency approval gate included.
- [x] Verification baseline included for every step.
- [x] Touched-file boundaries included for every step.
- [x] Rollback instructions included for every step.
- [x] Anti-patterns and plan mutation protocol included.
- [x] Recommended ECC skill order included.
- [x] No Phase 4 code implemented.
