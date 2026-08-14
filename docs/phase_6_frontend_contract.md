# Phase 6 Frontend Contract — Streamlit Primary Frontend and Deferred Next.js Workspace

## Status

Approved with Phase 6 frontend acceptance mutation.

This document is the authoritative Phase 6 frontend contract as amended by explicit user approval after live frontend inspection. Phase 6 implementation and handoff evidence must follow this contract; implementation evidence must not silently rewrite it after coding.

Approved acceptance mutation:

- Streamlit remains the primary accepted user-facing frontend for Phase 6.
- The Next.js workspace under `frontend/` is deferred, experimental, and non-primary until a later approved phase or contract mutation fixes its layout, controls, and chart parity enough for acceptance.
- This mutation does not change scientific behavior, engine behavior, FastAPI behavior, Phase 5 jobs, Streamlit behavior, frozen fixtures, diagnostics, or compatibility APIs.

## 1. Purpose and authority

Phase 6 originally added a first working Next.js + TypeScript analysis workspace over the existing FastAPI backend. After live user inspection, that workspace did not meet frontend acceptance because its layout, controls, and chart presentation did not match the trusted Streamlit experience closely enough.

The accepted Phase 6 release frontend is therefore the existing Streamlit app:

- primary UI entry point: `category_tracking_web.py`;
- trusted visual and interaction exemplar: `category_tracking_web.py`;
- launch command: `python -m streamlit run category_tracking_web.py`.

The deferred Next.js workspace remains a non-primary browser consumer of the Phase 4 synchronous API and Phase 5 in-process background-job API. It is not a scientific provider and is not the accepted Phase 6 release UI.

Locked scientific authority:

- exact probability remains the authoritative deterministic scientific path;
- aggregated sampled mode remains explicit and experimental;
- detailed sampled per-copy results remain unavailable over HTTP;
- the browser never recalculates biology, mutation probabilities, denominators, convergence, comparisons, or sampled paths.

Ownership:

| Role | Owner |
| --- | --- |
| Primary accepted frontend provider | `category_tracking_web.py` Streamlit application |
| Deferred experimental frontend provider | `frontend/` Next.js application |
| Backend provider | FastAPI app under `api/` |
| Scientific provider | Python engine under `engine/` |
| Compatibility consumers | Streamlit and Tkinter adapters |
| Contract approver | User |

## 2. Compatibility and versioning

- Existing Phase 4 synchronous API routes remain API version `phase4-api-v1`.
- Existing Phase 5 job routes remain unchanged.
- Phase 6 preserves the Streamlit primary frontend as the accepted UI.
- Phase 6 also contains a deferred experimental browser consumer under `frontend/`.
- Phase 6 may add Next.js same-origin proxy routes, but those proxy routes must not redefine backend response shapes.
- Breaking API, job, scientific, Streamlit, or Tkinter changes require a Blueprint/contract mutation and explicit user approval.
- Frozen diagnostics and fixtures remain immutable.
- Promoting the Next.js workspace back to primary UI requires a later approved phase or contract mutation with explicit visual/control/chart parity acceptance criteria.

## 3. Proposed dependency and project decisions

The original Next.js decisions remain implementation evidence for the deferred workspace only. They do not override the approved Streamlit-primary acceptance mutation.

| Decision | Recommended option | Status |
| --- | --- | --- |
| Primary release UI | Existing Streamlit app, `category_tracking_web.py` | Approved by frontend acceptance mutation |
| Deferred workspace directory | `frontend/` | Deferred / experimental / non-primary |
| Deferred framework | Next.js + React + TypeScript | Deferred / experimental / non-primary |
| Deferred router | Next.js App Router | Deferred / experimental / non-primary |
| Deferred package manager | npm with `package-lock.json` | Deferred / experimental / non-primary |
| Deferred styling | Plain CSS or CSS modules first | Deferred / experimental / non-primary |
| Deferred charting | Plotly dependency was approved for fidelity attempt, but Next.js chart parity was not accepted | Deferred / experimental / non-primary |
| Type source | Handwritten TypeScript interfaces checked against FastAPI OpenAPI in Phase 6; generated clients deferred unless approved | Deferred / experimental / non-primary |
| Backend access | Next.js same-origin route-handler proxy to the FastAPI backend | Deferred / experimental / non-primary |
| Backend URL config | Server-side `FRONTEND_API_BASE_URL`, defaulting to `http://127.0.0.1:8000` for local development | Deferred / experimental / non-primary |
| CORS | No backend CORS broadening in Phase 6 | Approved preservation rule |
| Mock/static frontend fixtures | Compact UI/API mocks under `frontend/tests/fixtures/**` only if needed; hashes recorded; never replacements for scientific/API golden fixtures | Deferred / experimental / non-primary |
| Retry/cancel UI | Expose only for approved Phase 5 job actions; hide if not implemented safely | Deferred / experimental / non-primary |

## 4. Non-goals

Phase 6 excludes:

- scientific engine rewrites;
- FastAPI route changes, except proxy consumption through Next.js;
- Streamlit or Tkinter behavior changes;
- detailed sampled per-copy HTTP exposure;
- exports, reports, PDFs, CSV downloads, screenshots, or notebooks;
- deployment, hosting, Docker, Kubernetes, Redis, Celery, RQ, PostgreSQL, durable jobs, authentication, authorization, accounts, or production CORS;
- Phase 7 visual polish;
- Phase 8 scientific wording overhaul;
- new chart/UI libraries unless separately approved.

## 5. Consumed backend routes

The frontend may consume only these backend routes through the approved client/proxy.

| Purpose | Method | Backend route | Phase |
| --- | --- | --- | --- |
| Health | `GET` | `/health` | Phase 4 |
| Metadata | `GET` | `/api/v1/metadata` | Phase 4 |
| Exact simulation | `POST` | `/api/v1/simulations/exact` | Phase 4 |
| Aggregated simulation | `POST` | `/api/v1/simulations/aggregated` | Phase 4 |
| Exact comparison | `POST` | `/api/v1/comparisons/exact` | Phase 4 |
| Exact-vs-sampled calibration | `POST` | `/api/v1/comparisons/exact-vs-sampled` | Phase 4 |
| Exact job submit | `POST` | `/api/v1/jobs/exact` | Phase 5 |
| Aggregated job submit | `POST` | `/api/v1/jobs/aggregated` | Phase 5 |
| Exact comparison job submit | `POST` | `/api/v1/jobs/comparisons/exact` | Phase 5 |
| Exact-vs-sampled job submit | `POST` | `/api/v1/jobs/comparisons/exact-vs-sampled` | Phase 5 |
| Job status | `GET` | `/api/v1/jobs/{job_id}` | Phase 5 |
| Job result | `GET` | `/api/v1/jobs/{job_id}/result` | Phase 5 |
| Job retry | `POST` | `/api/v1/jobs/{job_id}/retry` | Phase 5 |
| Job delete/cancel | `DELETE` | `/api/v1/jobs/{job_id}` | Phase 5 |

The frontend must not consume or expose a detailed sampled per-copy route.

## 6. Frontend proxy contract

The approved default is a same-origin Next.js proxy/route-handler layer.

Rules:

- Browser code calls local `frontend/app/api/**` route handlers or an equivalent approved proxy location.
- Proxy handlers forward requests to `FRONTEND_API_BASE_URL`.
- `FRONTEND_API_BASE_URL` is read server-side only.
- Proxy handlers preserve backend status codes and JSON envelope shapes.
- Proxy handlers must not rewrite scientific payloads.
- Proxy handlers may translate network/backend-unavailable failures into a concise frontend error envelope.
- Proxy handlers must not add CORS requirements to the FastAPI backend.
- Proxy handlers must not persist data, write files, or log secrets.

## 7. Response envelope contract

The frontend must support the Phase 4/5 envelopes exactly as serialized by FastAPI.

Success envelope:

```json
{
  "data": {}
}
```

Error envelope:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": null
  }
}
```

Frontend rules:

- Render `data` only when the HTTP status is successful and `data` exists.
- Render `error.message` concisely for expected backend errors.
- Preserve `error.code` for debugging/test assertions.
- Never display Python stack traces.
- Treat malformed or network-level failures as frontend transport errors, not scientific results.

## 8. Required UI states

Every Phase 6 feature slice must define and test:

- idle state;
- loading state;
- success state;
- empty state;
- validation-blocked state for incomplete UI inputs;
- backend error state;
- network/proxy error state.

Dynamic job flows must additionally define:

- queued;
- running;
- completed;
- failed;
- cancel_requested;
- cancelled;
- expired;
- result not ready.

## 9. First analysis workspace views

The opening route must be a working analysis workspace, not a marketing page.

Approved first-view scope:

- backend connection indicator;
- metadata-driven controls;
- codon focus;
- whole-population analysis;
- exact simulation;
- aggregated sampled simulation;
- exact comparison;
- exact-vs-sampled comparison;
- background job submission/status/result retrieval;
- trait drilldown panels;
- summary tables.

Deferred:

- export/report actions;
- advanced chart polish;
- sticky/fullscreen/responsive refinement beyond a functional baseline;
- scientific wording overhaul.

## 10. Input and validation contract

Frontend validation is for usability only.

Rules:

- Backend validation remains authoritative.
- The frontend may block obviously incomplete requests.
- The frontend must not invent new scientific validation rules.
- Aggregated sampled requests must require an explicit integer seed.
- UI controls must not silently route oversized synchronous requests into jobs.
- Job mode must be explicitly selected or explicitly invoked by job controls.
- No automatic sync-to-job switching is allowed.

## 11. Job polling contract

The frontend may poll job status only with bounded behavior.

Rules:

- Poll only after a job has been accepted.
- Use a bounded interval approved in implementation, with no tight loop.
- Stop polling at terminal statuses:
  - completed;
  - failed;
  - cancelled;
  - expired.
- Stop polling if the component/page no longer needs the job.
- Do not spawn duplicate polling loops for the same visible job.
- Show result retrieval separately from status when appropriate.

## 12. Type and schema parity contract

Step 4 must prove frontend types match the approved backend contract.

Required parity evidence:

- every approved consumed route has a typed frontend client function;
- every client function uses the approved HTTP method and path;
- success and error envelopes are represented;
- required fields are present in frontend types;
- nullable/optional fields are explicit;
- job statuses match the Phase 5 contract;
- no detailed sampled route appears;
- frontend tests compare route/type coverage against the approved Phase 4/5 contracts or generated FastAPI OpenAPI output.

The frontend must not keep a hidden competing schema source.

## 13. Frontend mock and fixture policy

Frontend fixtures, if needed, are UI/API mocks only.

Rules:

- Store them under `frontend/tests/fixtures/**`.
- Record hashes in `plans/phase-6-execution-log.md`.
- Keep fixtures compact.
- Do not generate or rewrite them automatically.
- Do not use them to replace Phase 1–5 scientific/API fixtures.
- Do not weaken backend fixture or diagnostic requirements.

## 14. Accessibility contract

Phase 6 must meet a functional accessibility baseline:

- semantic landmarks for header, main content, controls, and results;
- keyboard-reachable controls;
- visible focus states;
- labels for form controls;
- concise error text connected to relevant controls where practical;
- status/loading updates visible in text;
- no color-only status meaning;
- table headers for result tables;
- chart summaries must have text/table equivalents.

Full visual polish remains Phase 7, but basic accessibility blockers must be resolved before Step 11 approval.

## 15. Browser QA contract

Step 9 must verify, if local servers can start safely:

- home/workspace route loads;
- backend health/connection state appears;
- metadata loads;
- exact simulation flow works;
- aggregated simulation flow works;
- job submit/status/result flow works;
- exact comparison flow works;
- exact-vs-sampled comparison flow works;
- error state is reachable without crashing;
- no unexpected routes or detailed sampled route are visible.

If browser tooling or local server startup is unavailable, record that explicitly and rely on frontend tests plus API verification only if the Blueprint permits proceeding.

## 16. Security and boundary contract

Frontend code must not:

- contain secrets, tokens, passwords, or private URLs;
- use `dangerouslySetInnerHTML` unless separately approved and sanitized;
- broaden backend CORS;
- claim authentication exists;
- add deployment assumptions;
- write files;
- persist scientific results beyond browser state;
- duplicate biological tables, mutation matrices, algorithms, denominators, category mappings, or scientific formulas;
- call Python files directly;
- expose detailed sampled per-copy records;
- import root research files.

Backend and engine boundaries must remain:

- `engine/` does not import frontend, FastAPI, Streamlit, Tkinter, Plotly, PyQt, CSS, HTML, or UI colors;
- `api/` does not import frontend code, Streamlit, Tkinter, Plotly, PyQt, UI colors, or root research files;
- Phase 4 and Phase 5 route contracts remain unchanged.

## 17. Dependency and artifact contract

Approved proposed dependencies for Step 3:

- Next.js;
- React;
- React DOM;
- TypeScript;
- ESLint tooling generated/required by the approved Next.js setup.

No chart, UI component, state-management, OpenAPI-generator, accessibility-test, browser-test, or styling dependency may be added without being listed and approved first.

Generated/local artifacts must not be committed:

- `frontend/node_modules/`;
- `frontend/.next/`;
- frontend coverage output;
- temporary browser artifacts;
- environment files containing secrets.

## 18. Verification matrix

| Consumer/provider | Contract proof |
| --- | --- |
| Frontend app shell | Build/lint/test and browser smoke. |
| Typed API client | Schema parity tests against contracts/OpenAPI. |
| Frontend proxy | Route/status/envelope preservation tests. |
| Metadata controls | Tests using backend-compatible metadata shape. |
| Simulation views | Tests proving values are rendered from API responses only. |
| Job workflow | Polling/lifecycle tests and API job smoke. |
| Browser QA | Step 9 local route/flow evidence. |
| Accessibility | Step 9 keyboard/labels/focus/landmark evidence. |
| Security | Step 9 frontend/API boundary review. |
| Existing Python backend | Universal Python verification baseline after every step. |

## 19. Change protocol

If implementation evidence conflicts with this contract:

1. Stop.
2. Record evidence in `plans/phase-6-execution-log.md`.
3. Identify affected consumer/provider and owning step.
4. Propose the smallest contract mutation.
5. Record touched files and compatibility impact.
6. Obtain explicit user approval.
7. Update this contract first.
8. Add failing tests.
9. Implement only the approved mutation.
10. Rerun frontend and universal Python verification.

No implementation-first contract changes are allowed.

## 20. Completion checklist

- [x] Provider and consumers identified.
- [x] One authoritative frontend contract named.
- [x] Consumed routes listed.
- [x] Proxy/no-CORS approach proposed.
- [x] Dependency decisions listed.
- [x] Frontend state requirements listed.
- [x] Job polling behavior listed.
- [x] Accessibility expectations listed.
- [x] Browser QA expectations listed.
- [x] Security boundaries listed.
- [x] Fixture policy listed.
- [x] Step 3 can scaffold without guessing after approval.
- [x] All human decisions remain proposed pending approval.
