# Phase 4 API Contract — FastAPI Backend

Status: Proposed — awaiting Phase 4 API Contract approval.

Version: `phase4-api-v1-proposed`

Owner/provider: Python FastAPI service under the future `api/` package.

Authoritative scientific provider: existing Python engine under `engine/`.

Approver: user.

## 1. Purpose and authority

Phase 4 creates a FastAPI HTTP boundary over the existing Codon Category Tracking engine. The API is a transport adapter: it validates HTTP input, calls named engine APIs, serializes approved scientific outputs to JSON, and translates expected engine errors into documented JSON error responses.

The Python engine remains the single source of truth for:

- biological definitions;
- mutation matrix construction;
- exact probability propagation and analysis;
- detailed sampled compatibility behavior;
- aggregated sampled execution;
- denominators, zero behavior, comparisons, convergence, and invariants.

Exact probability remains the authoritative deterministic scientific path. Aggregated sampled mode remains explicit and experimental. Detailed sampled per-copy mode remains a Python compatibility API and is not exposed over HTTP in Phase 4 unless this contract is amended and approved before implementation.

Current consumers:

- existing Streamlit UI, unchanged;
- existing Tkinter compatibility adapter, unchanged;
- Python/notebook callers using `engine`;
- future Next.js frontend, not implemented in Phase 4;
- future service/API clients consuming this HTTP contract.

Change protocol: implementation must follow this contract. A contract change must be proposed and approved before provider code, tests, fixtures, or dependencies change.

## 2. Scope and non-goals

Phase 4 includes synchronous FastAPI backend contracts only.

In scope:

- `GET /health`;
- `GET /api/v1/metadata`;
- `POST /api/v1/simulations/exact`;
- `POST /api/v1/simulations/aggregated`;
- `POST /api/v1/comparisons/exact`;
- `POST /api/v1/comparisons/exact-vs-sampled`;
- JSON request/response contracts;
- OpenAPI generation and contract-conformance tests;
- API error translation;
- local development run instructions.

Out of scope:

- Phase 5 jobs, Redis, workers, retry states, queues, progress polling, job IDs, and result storage;
- Phase 6 Next.js frontend;
- deployment, Docker, cloud hosting, production configuration, auth, user accounts, CORS broadening, database, persistence, exports, PDF/CSV/report generation;
- engine optimization, vectorization, NumPy/SciPy transition rewrite, or scientific behavior changes.

## 3. Dependency decision

Proposed dependency file: `requirements.txt`.

Reason: this repository is currently a small Python app without a dependency file. A minimal `requirements.txt` is the lowest-ceremony dependency artifact for Phase 4. A later packaging phase may migrate to `pyproject.toml` if distribution/build tooling becomes necessary.

Proposed packages, pending human approval:

| Package | Proposed range | Purpose |
| --- | --- | --- |
| `fastapi` | `>=0.139,<0.141` | HTTP API framework and Pydantic integration |
| `uvicorn[standard]` | `>=0.51,<0.52` | local ASGI server |
| `httpx` | `>=0.28,<0.29` | FastAPI `TestClient`/transport testing support |

Rationale:

- FastAPI and Uvicorn current PyPI release streams in July/August 2026 are in the `0.139/0.140` and `0.51` families respectively.
- `httpx` stable release remains in the `0.28` family.
- Ranges are narrow enough for reproducibility while allowing patch releases.

Dependency files are created in Step 3, not Step 2.

Required Step 3 import verification:

```powershell
python -c "import fastapi; from fastapi.testclient import TestClient; import uvicorn; import httpx; print('phase4-api-dependencies-ok')"
```

## 4. API versioning

Base path: `/api/v1`.

API version string: `phase4-api-v1`.

Every success and error response includes:

```json
"api_version": "phase4-api-v1"
```

Compatibility policy:

- Additive fields are allowed only when old clients can ignore them.
- Removing or renaming fields, changing field types, changing endpoint paths, changing denominator semantics, changing error codes, or changing null behavior is breaking.
- Breaking changes require Blueprint mutation, contract amendment, human approval, tests, and explicit migration notes.

## 5. Common request model

Field names use JSON `snake_case` to match the Python scientific domain and avoid browser-side scientific renaming.

| Field | JSON type | Required | Default | Range/nullability | Engine mapping |
| --- | --- | --- | --- | --- | --- |
| `n_generations` | integer | endpoint-specific | none | `0 <= n <= 2000` proposed | exact/aggregated generation count |
| `probabilities` | object | yes for simulation requests | none | keys `a_to_t`, `a_to_g`, `a_to_c`; finite numbers, each `0 <= p <= 1`; sum must match existing engine matrix expectations | `build_substitution_matrix` |
| `start_weights` | object | optional for exact, required for aggregated | exact default `null` means engine all-valid-codon default; aggregated no default | keys valid sense codons; exact values number; aggregated values normalized with `max(0, int(weight))` by engine | engine start weights |
| `selected_codon` | string | endpoint-specific | none | valid sense codon | codon-specific exact/summary query |
| `compare_codon` | string | endpoint-specific | none | valid sense codon | future comparison convenience, if used |
| `start_scope` | string | endpoint-specific | `population` where applicable | enum `population`, `codon`, `amino_acid`, `trait` | scoped exact/aggregated query |
| `start_key` | string | endpoint-specific | `all` for population | valid for scope | scoped query key |
| `metric` | string | comparison endpoints | none | approved metric enum | comparison metric |
| `basis` | string | convergence endpoint/query | contract default `category_fraction` | approved convergence basis | convergence query |
| `alpha` | number | optional | `0.01` | `0 < alpha < 1` | statistical familywise alpha where applicable |
| `tolerance` | number | optional | `0.01` for convergence unless endpoint specifies otherwise | finite non-negative number | convergence tolerance |
| `seed` | integer | aggregated endpoint | none | required integer | `run_aggregated_experiment` local seed |
| `familywise_alpha` | number | exact-vs-sampled | `0.01` | `0 < alpha < 1` | `compare_exact_to_sampled` |

No request field may be silently ignored. Unknown top-level fields produce a documented validation error.

## 6. Common response envelope

Success response fields appear in this conceptual order:

| Field | JSON type | Nullable | Meaning |
| --- | --- | --- | --- |
| `api_version` | string | no | API version string |
| `mode` | string | no | `exact`, `aggregated_sampled`, `comparison`, `metadata`, or `health` |
| `scientific_authority` | string | no | `authoritative_exact`, `experimental_sampled`, or `service_metadata` |
| `request` | object | no | normalized request echo after validation |
| `result` | object | no | endpoint-specific scalar/status result metadata |
| `tables` | object | no | named serialized tables |
| `metadata` | object | no | endpoint-specific metadata and labels |
| `warnings` | array | no | non-fatal warnings; empty array if none |
| `errors` | array | no | empty array on success |
| `schema` | object | no | response/table schema identifiers and versions |

Health endpoint may return a compact envelope with `status`, but still includes `api_version`.

## 7. DataFrame/table serialization contract

Every serialized pandas DataFrame is represented as:

```json
{
  "columns": ["generation", "category", "value"],
  "dtypes": {"generation": "int64", "category": "object", "value": "float64"},
  "records": [
    {"generation": 1, "category": "Hydrophobic", "value": 0.25}
  ],
  "index_kind": "RangeIndex",
  "row_count": 1,
  "value_kind": "probability_weight"
}
```

Rules:

- `columns` preserves engine column order.
- `dtypes` stores stringified pandas dtypes.
- `records` preserves row order.
- `index_kind` is `RangeIndex` for canonical tables.
- `row_count` equals `len(records)`.
- `generation` is 1-based post-mutation generation for time-series tables.
- JSON `null` represents pandas `pd.NA`, `NaN`, or nullable missing values.
- Fractions are returned as fractions in `[0, 1]`; presentation percentages are not returned unless explicitly named as presentation-only metadata.
- Exact probability weights are never called integer counts.
- Sampled integer counts are never called probability weights.
- Same-process tests compare engine outputs before JSON serialization. JSON tests compare stable fields and exact numeric values where JSON permits; tolerance is allowed only for serialization round-trip cases explicitly documented by a focused test.

## 8. Endpoint contracts

### `GET /health`

Purpose: service liveness smoke check.

Request: none.

Response `200`:

```json
{
  "api_version": "phase4-api-v1",
  "status": "ok",
  "service": "codon-category-tracking-api"
}
```

No engine simulation is run.

### `GET /api/v1/metadata`

Purpose: expose valid options and labels for clients.

Engine sources:

- `engine.genetic_code`;
- `engine.mutation_matrix`;
- `engine.comparisons`;
- public `engine.__all__` where useful.

Response tables/fields:

- `valid_codons`: ordered sense codons;
- `stop_codons`: canonical `TAA`, `TAG`, `TGA`;
- `category_labels`: ordered category labels;
- `probability_presets`: existing presets;
- `supported_modes`: `exact`, `aggregated_sampled`, `exact_comparison`, `exact_vs_sampled`;
- `supported_metrics`: approved comparison metrics;
- `engine_contracts`: references to Phase 2/3 docs.

Metadata must be sourced from engine modules, not duplicated in `api/`.

### `POST /api/v1/simulations/exact`

Purpose: run authoritative exact analysis and return chart/table-ready JSON.

Request:

```json
{
  "n_generations": 20,
  "probabilities": {"a_to_t": 0.3333333333, "a_to_g": 0.3333333333, "a_to_c": 0.3333333333},
  "start_weights": {"TGG": 1.0},
  "scopes": [{"start_scope": "population", "start_key": "all"}],
  "codon_outcomes": [{"start_codon": "TGG", "generation": 20}],
  "convergence": [{"start_scope": "population", "start_key": "all", "basis": "category_fraction", "tolerance": 0.01}]
}
```

Required engine calls:

- `build_substitution_matrix`;
- `run_exact_analysis`;
- exact query functions for requested scopes.

Tables returned:

- `category_metrics`;
- `survivor_fractions`;
- `survival_by_start`;
- `stop_outcomes`;
- `codon_outcomes`;
- `convergence`.

The endpoint must call `run_exact_analysis` once per simulation request. It must not call `run_simulation` separately unless this contract is amended and approved.

### `POST /api/v1/simulations/aggregated`

Purpose: run explicit experimental aggregated sampled simulation and return bounded counters/tables.

Request:

```json
{
  "n_generations": 20,
  "probabilities": {"a_to_t": 0.3333333333, "a_to_g": 0.3333333333, "a_to_c": 0.3333333333},
  "start_weights": {"TGG": 100},
  "seed": 7,
  "scopes": [{"start_scope": "population", "start_key": "all"}],
  "codon_outcomes": [{"start_codon": "TGG", "generation": 20}]
}
```

Required engine calls:

- `build_substitution_matrix`;
- `run_aggregated_experiment`;
- aggregated query functions.

Tables returned:

- `generation_counts`;
- `category_metrics`;
- `survivor_fractions`;
- `survival_by_start`;
- `stop_outcomes`;
- `codon_outcomes`;
- `convergence`.

Must not expose:

- individual copy IDs;
- individual records;
- mutation paths;
- per-copy final records;
- individual stop-generation records;
- module-global detailed sampled RNG state.

`scientific_authority` is `experimental_sampled`.

### `POST /api/v1/comparisons/exact`

Purpose: compare two exact settings using approved directed comparison semantics.

Request:

```json
{
  "metric": "category_fraction",
  "baseline": {"label": "baseline", "simulation": {"n_generations": 5, "probabilities": {"a_to_t": 0.2, "a_to_g": 0.5, "a_to_c": 0.3}, "start_weights": {"TGG": 1.0}}},
  "candidate": {"label": "candidate", "simulation": {"n_generations": 5, "probabilities": {"a_to_t": 0.1, "a_to_g": 0.7, "a_to_c": 0.2}, "start_weights": {"TGG": 1.0}}},
  "scope": {"start_scope": "population", "start_key": "all"}
}
```

Required engine calls:

- exact analysis/query APIs for baseline and candidate;
- `compare_numeric_metric` or `compare_convergence`.

Semantics:

- `signed_delta = candidate_value - baseline_value`;
- `absolute_delta = abs(signed_delta)`;
- `relative_delta = null` when baseline value is zero;
- only `signed_delta` changes sign if baseline/candidate are swapped.

### `POST /api/v1/comparisons/exact-vs-sampled`

Purpose: compare experimental aggregated sampled estimates to authoritative exact fractions.

Request:

```json
{
  "metric": "survivor_fraction",
  "denominator_scope": "population_initial",
  "familywise_alpha": 0.01,
  "exact": {"n_generations": 5, "probabilities": {"a_to_t": 0.2, "a_to_g": 0.5, "a_to_c": 0.3}, "start_weights": {"TGG": 1.0}},
  "sampled": {"n_generations": 5, "probabilities": {"a_to_t": 0.2, "a_to_g": 0.5, "a_to_c": 0.3}, "start_weights": {"TGG": 100}, "seed": 8675309}
}
```

Required engine calls:

- exact analysis/query APIs;
- `run_aggregated_experiment`;
- aggregated query APIs;
- `compare_exact_to_sampled`.

Wilson/Bonferroni methodology, `familywise_alpha` default, nullable interval fields, and `sample_size == 0` behavior must match Phase 2.

## 9. Exact endpoint contract

`POST /api/v1/simulations/exact` is the authoritative scientific endpoint.

It must:

- call `run_exact_analysis`;
- call exact scoped query functions;
- return probability weights/fractions with explicit value kinds;
- preserve engine schemas, ordering, empty behavior, denominators, and zero rules;
- reject oversize synchronous requests with a documented API error;
- avoid scientific calculations in `api/`.

It must not:

- duplicate exact propagation loops;
- call `run_simulation` separately;
- convert exact output into presentation percentages without contract fields;
- change existing Streamlit/Tkinter behavior.

## 10. Aggregated sampled endpoint contract

`POST /api/v1/simulations/aggregated` is experimental.

It must:

- require explicit integer `seed`;
- call `run_aggregated_experiment`;
- preserve local RNG isolation;
- preserve count conservation;
- expose only bounded counters and derived aggregate tables;
- include `mode: "aggregated_sampled"`;
- include `scientific_authority: "experimental_sampled"`.

Maximum proposed synchronous aggregated sample size:

- total normalized starting count: `100_000`;
- `n_generations`: `500`;
- request body size: `1 MiB`.

The endpoint must reject requests exceeding limits with `oversized_request`.

## 11. Detailed sampled HTTP decision

Decision: detailed per-copy sampled paths are not exposed over HTTP in Phase 4.

Rationale:

- detailed sampled mode retains individual paths and is not memory-safe for large HTTP responses;
- Phase 2 explicitly created aggregated sampled mode as the engine-only large-run API;
- detailed `run_experiment` remains available for Python compatibility and frozen tests;
- exposing detailed sampled output later requires Blueprint mutation or a later phase.

## 12. Comparison endpoint contracts

Supported exact numeric metrics:

- `category_live_value`;
- `category_fraction`;
- `survivor_fraction`;
- `stop_fraction`;
- `new_stop_value`;
- `cumulative_stop_value`;
- `cumulative_stop_fraction`;
- `codon_live_value`;
- `codon_new_stop_value`;
- `codon_cumulative_stop_value`.

Supported convergence comparison:

- exact convergence table only;
- status comparison separate from numeric deltas.

Exact-vs-sampled metrics:

- `category_fraction`;
- `survivor_fraction`;
- `stop_fraction`;
- `cumulative_stop_fraction`.

All comparison rows align by scientific keys, not positional row order.

## 13. Metadata endpoint contract

`GET /api/v1/metadata` response includes:

- ordered `valid_codons`;
- ordered `stop_codons`;
- ordered `category_labels`;
- `probability_presets`;
- supported exact scopes;
- supported comparison metrics;
- supported modes;
- `api_version`;
- references to `docs/phase_2_scientific_contract.md`, `docs/phase_4_api_contract.md`, and `engine/README.md`.

No biological table is copied into static API constants. The metadata serializer reads from `engine`.

## 14. Error contract

Error response shape:

```json
{
  "api_version": "phase4-api-v1",
  "mode": "error",
  "scientific_authority": "none",
  "request": {},
  "result": {},
  "tables": {},
  "metadata": {},
  "warnings": [],
  "errors": [
    {
      "code": "validation_error",
      "message": "Request validation failed.",
      "details": [{"field": "n_generations", "message": "Must be between 0 and 2000."}],
      "request_id": null,
      "status_code": 422
    }
  ],
  "schema": {"name": "ApiErrorEnvelope", "version": "phase4-api-v1"}
}
```

Error mapping:

| Condition | HTTP status | Code |
| --- | ---: | --- |
| malformed JSON | 400 | `malformed_json` |
| request validation | 422 | `validation_error` |
| invalid scientific scope | 422 | `invalid_scientific_scope` |
| unsupported comparison | 422 | `unsupported_comparison` |
| metric schema mismatch | 422 | `metric_schema_mismatch` |
| exact provenance error | 422 | `exact_provenance_error` |
| scientific invariant error | 500 | `scientific_invariant_error` |
| oversized synchronous request | 413 | `oversized_request` |
| unexpected internal error | 500 | `internal_error` |

`request_id` policy: absent from Phase 4 runtime behavior; represented as `null` only if a common error model requires the field. No request-id middleware is added in Phase 4.

No expected failure becomes a silent empty result. No Streamlit message appears in API responses.

## 15. Synchronous request-size limits

Proposed Phase 4 limits:

| Limit | Proposed value | Error |
| --- | ---: | --- |
| max exact `n_generations` | `2000` | `oversized_request` |
| max aggregated `n_generations` | `500` | `oversized_request` |
| max exact nonzero starting codons | `61` | `oversized_request` if exceeded/impossible |
| max aggregated normalized start count | `100_000` | `oversized_request` |
| max comparison family rows | `10_000` | `oversized_request` |
| max request body size | `1 MiB` | `oversized_request` |

These limits protect the synchronous API until Phase 5 jobs exist. They are not scientific constraints. Implementation must test accepted boundary values and rejected oversize values.

## 16. OpenAPI/static fixture decision

Decision: do not create `tests/fixtures/phase4_api_contract_openapi.json` in Step 2.

Reason: there is no FastAPI app skeleton yet, so a complete OpenAPI artifact would be handwritten twice: once as prose and once as JSON. That would create drift risk before implementation exists.

Requirement:

- Step 3 generates a first OpenAPI schema from the app skeleton.
- Step 7 freezes a reviewed static OpenAPI fixture after routes, schemas, and error handlers exist.
- Step 7 must stop for approval before treating the fixture as immutable.
- Steps 8–9 compare implemented routes, methods, request schemas, response schemas, error shapes, and version fields against this contract and the approved fixture.

## 17. Security and boundary contract

Required boundaries:

- `engine/` must not import FastAPI, Starlette, Uvicorn, httpx, Streamlit, Tkinter, Plotly, PyQt, UI colors, CSS, or HTML.
- `api/` must not import Streamlit, Tkinter, Plotly, PyQt, UI colors, or workspace-root research files.
- `api/` must not duplicate codon tables, property tables, presets, mutation matrices, simulation loops, denominators, comparison formulas, or statistical formulas.
- Request handlers perform no filesystem writes.
- Phase 4 adds no auth.
- Phase 4 adds no deployment secrets.
- CORS policy: no CORS middleware in Phase 4 unless Step 2 approval is amended. Future frontend work may add a narrow localhost/dev origin policy in Phase 6.
- No background jobs.

## 18. Testing contract

Use standard-library `unittest`.

Required Step 3–9 test families:

- app import and app factory;
- health endpoint;
- metadata endpoint;
- exact endpoint;
- aggregated endpoint;
- exact comparison endpoint;
- exact-vs-sampled endpoint;
- error translation;
- request-size limits;
- OpenAPI generation;
- contract conformance;
- engine/API/UI independence;
- root import locality;
- frozen diagnostics and fixtures.

Tests must not regenerate frozen Phase 1/2 fixtures. Any Phase 4 fixture must be reviewed and immutable after approval.

## 19. Verification matrix

| Provider/endpoint | Engine functions used | Contract artifact | Focused tests | Universal verification | Compatibility risk | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| Health | none | this document | `test_api_app.py` | full suite | low | API |
| Metadata | `engine.genetic_code`, `engine.mutation_matrix`, public exports | this document | `test_api_app.py` | full suite | medium: duplicated definitions | API |
| Exact simulation | `build_substitution_matrix`, `run_exact_analysis`, exact query APIs | this document | `test_api_exact.py` | full suite + diagnostics | high: scientific drift | API + engine contract |
| Aggregated simulation | `run_aggregated_experiment`, aggregated query APIs | this document | `test_api_aggregated.py` | full suite + diagnostics | high: RNG/count/memory drift | API + engine contract |
| Exact comparison | exact analysis/query APIs, `compare_numeric_metric`, `compare_convergence` | this document | `test_api_comparisons.py` | full suite | high: direction/schema drift | API + engine contract |
| Exact-vs-sampled | exact/aggregated APIs, `compare_exact_to_sampled` | this document | `test_api_comparisons.py` | full suite | high: statistical drift | API + engine contract |
| Errors | engine exception types | this document | `test_api_errors.py` | full suite | medium: bad HTTP semantics | API |
| Boundaries | import graph | this document + future fixture | `test_api_boundaries.py` | full suite | medium: dependency leakage | API |

## 20. Change protocol

1. Propose the consumer/scientific/API need.
2. Update `docs/phase_4_api_contract.md` first.
3. Record touched files and compatibility impact in `plans/phase-4-execution-log.md`.
4. Obtain human approval.
5. Update Phase 4 static fixture if one exists.
6. Write focused failing tests.
7. Implement provider changes.
8. Rerun focused and universal verification.
9. Stop at the next approval gate if compatibility or scope changes.

No implementation-first contract updates are allowed.

## 21. Explicit approval decisions

| Decision | Proposed value | Status |
| --- | --- | --- |
| Dependency file format | `requirements.txt` | Proposed — awaiting human approval |
| FastAPI dependency | `fastapi>=0.139,<0.141` | Proposed — awaiting human approval |
| ASGI server dependency | `uvicorn[standard]>=0.51,<0.52` | Proposed — awaiting human approval |
| Test client dependency | `httpx>=0.28,<0.29` | Proposed — awaiting human approval |
| Detailed sampled HTTP endpoint | not exposed in Phase 4 | Proposed — awaiting human approval |
| Aggregated sampled endpoint | exposed as explicit experimental endpoint | Proposed — awaiting human approval |
| Exact max generations | `2000` | Proposed — awaiting human approval |
| Aggregated max generations | `500` | Proposed — awaiting human approval |
| Aggregated max normalized start count | `100_000` | Proposed — awaiting human approval |
| Comparison family row limit | `10_000` | Proposed — awaiting human approval |
| Request body size | `1 MiB` | Proposed — awaiting human approval |
| JSON table orientation | `columns`, `dtypes`, `records`, `index_kind`, `row_count`, `value_kind` | Proposed — awaiting human approval |
| Missing value representation | JSON `null` | Proposed — awaiting human approval |
| Static OpenAPI fixture timing | create/review after app skeleton, not in Step 2 | Proposed — awaiting human approval |
| CORS policy | no CORS middleware in Phase 4 | Proposed — awaiting human approval |
| Request ID policy | no runtime request-id middleware in Phase 4 | Proposed — awaiting human approval |
| API version string | `phase4-api-v1` | Proposed — awaiting human approval |

## 22. Completion checklist

- [x] Provider and consumers identified.
- [x] All Phase 4 endpoints explicit.
- [x] Request schemas explicit.
- [x] Response envelope explicit.
- [x] Table serialization explicit.
- [x] Error shape and status-code mapping explicit.
- [x] Dependencies and version ranges explicit.
- [x] Request limits explicit.
- [x] Non-goals explicit.
- [x] Phase 1–3 preservation explicit.
- [x] OpenAPI fixture timing explicit.
- [x] Implementation can start Step 3 without guessing after approval.
- [x] Unresolved decisions listed for human approval.
