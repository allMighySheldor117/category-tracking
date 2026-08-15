# Phase 9 Streamlit Cloud Deployment Contract

Status: Approved — Phase 9 Streamlit Cloud Deployment Contract and narrow dependency-boundary test mutation approved by the user

Canonical repository:

`C:\Users\hatem\OneDrive\Desktop\Project for uri\visualize code\category-tracking`

Authoritative Blueprint:

`plans/phase-9-streamlit-community-cloud-deployment.md`

## 1. Purpose and authority

Phase 9 prepares the accepted Streamlit application for Streamlit Community Cloud deployment.

This contract governs only deployment readiness for the current accepted Streamlit frontend. It does not authorize scientific changes, backend/API changes, job changes, Next.js promotion, university-server deployment, infrastructure work, dependency edits, or Streamlit Cloud app creation by itself.

Authoritative user-facing frontend:

- Primary accepted frontend: `category_tracking_web.py`
- Launch command: `python -m streamlit run category_tracking_web.py`
- Next.js workspace: deferred / experimental / non-primary

Scientific authority remains unchanged:

- `engine/` remains the single source of truth for biological definitions, exact and sampled simulation, summaries, comparisons, and scientific outputs.
- Exact probability remains the authoritative deterministic scientific path.
- Sampled modes retain their existing experimental/compatibility meanings.
- Streamlit rendering must not duplicate scientific algorithms or biological tables.

## 2. Deployment target

Phase 9 targets Streamlit Community Cloud as the first public sharing path.

Proposed Cloud deployment settings:

| Setting | Proposed value | Status |
| --- | --- | --- |
| Host | Streamlit Community Cloud | Proposed — awaiting approval |
| Repository | `https://github.com/allMighySheldor117/category-tracking.git` | Proposed — awaiting approval |
| Branch | `master` | Proposed — awaiting approval |
| Entrypoint file | `category_tracking_web.py` | Proposed — awaiting approval |
| App type | Public demo / research sharing app | Proposed — awaiting approval |
| University server | Deferred to later phase | Proposed — awaiting approval |

Step 6 must revalidate the local `origin` remote before any deployment setup uses the repository value above.

## 3. Compatibility and preservation contract

Phase 9 must preserve:

- accepted Phase 8 Streamlit UI;
- exact chart types;
- chart meanings;
- chart axes;
- chart legends;
- chart ordering;
- chart data;
- table contents;
- table columns;
- section order;
- control order;
- one-button workflow;
- fullscreen behavior;
- exact probability outputs;
- sampled RNG behavior;
- aggregated sampled contract;
- Streamlit primary frontend decision;
- FastAPI behavior;
- Phase 5 job behavior;
- engine APIs;
- frozen diagnostics;
- frozen fixtures;
- compatibility APIs;
- Tkinter compatibility.

Phase 9 deployment-readiness changes may not make scientific or UI behavior “lighter” merely to fit a free tier. If workload/resource limits are observed, record them and request approval before changing defaults, limits, charts, tables, or scientific display.

## 4. File organization contract

The accepted app entrypoint is at repository root:

```text
category_tracking_web.py
```

The root `requirements.txt` is the dependency file currently in scope for Streamlit Community Cloud dependency installation.

The root `.streamlit/config.toml`, if present, remains the only approved Streamlit configuration file.

Phase 9 must not add duplicate dependency/configuration files unless a later approved contract mutation authorizes them.

## 5. Dependency policy

The current `requirements.txt` contains:

```text
fastapi>=0.139,<0.141
uvicorn[standard]>=0.51,<0.52
httpx>=0.28,<0.29
```

This is backend-oriented and may not be sufficient for Streamlit Community Cloud to run the accepted Streamlit app.

Expected dependency gap to audit in Step 3:

- `category_tracking_web.py` imports Streamlit/Plotly/Pandas-facing runtime packages.
- Streamlit Community Cloud provides Streamlit by default, but the project should still explicitly record app runtime dependencies when needed to reduce missing-package and version-drift risk.
- Likely packages to audit include `streamlit`, `pandas`, and `plotly`.

Dependency change rules:

1. Step 2 does not edit `requirements.txt`.
2. Step 3 must audit actual imports before proposing dependency changes.
3. Any `requirements.txt` edit requires explicit user approval before editing.
4. Approved backend dependencies must not be removed without explicit approval.
5. No unrelated packages may be added.
6. No assets, frontend framework packages, deployment packages, database clients, worker packages, auth packages, or external-service SDKs may be added in Phase 9.
7. Dependency ranges should be constrained enough to reduce Cloud drift while staying compatible with the local tested environment.

Approved Phase 9 dependency-boundary mutation:

- The user approved a narrow Phase 9 test/contract mutation so dependency-boundary tests allow Streamlit deployment runtime dependencies in `requirements.txt`.
- The approved dependency manifest contains the existing Phase 4/5 backend dependencies plus the audited Phase 9 Streamlit runtime dependencies:

```text
fastapi>=0.139,<0.141
uvicorn[standard]>=0.51,<0.52
httpx>=0.28,<0.29
streamlit>=1.60,<1.61
pandas>=2.2,<2.3
plotly>=6.8,<6.9
```

- This mutation does not authorize app behavior changes, engine changes, API/job changes, fixture changes, secrets, runtime pin files, deployment setup, assets, or unrelated dependencies.

## 6. Python runtime policy

Default proposal:

- Select Python version in the Streamlit Community Cloud dashboard Advanced settings.
- Prefer Python 3.12 unless Step 3 audit evidence supports another released, Cloud-supported version.

Repository runtime files:

- Do not add `runtime.txt`, `.python-version`, or another runtime-selection file in Step 2.
- Repository runtime selection remains prohibited unless a later approved contract mutation identifies the exact file, value, validation method, and rollback plan.

## 7. Secrets policy

Current Phase 9 expectation:

- No secrets are required.
- No `.streamlit/secrets.toml` may be committed.
- No credentials, API keys, tokens, passwords, private paths, or university-server details may be added to the repository.

If a future deployment path needs secrets:

1. stop;
2. record the need;
3. request explicit approval;
4. use Streamlit Cloud app settings or another approved secret-management mechanism;
5. never commit secrets to Git.

## 8. Resource and multi-user limitations

Streamlit Community Cloud is suitable for:

- public demo use;
- teaching/research sharing;
- low-to-moderate exploratory use;
- early community feedback.

It is not proven by this contract as:

- high-concurrency production hosting;
- long-running heavy compute hosting;
- durable multi-user storage;
- a replacement for a university server or dedicated compute node.

Phase 9 must document any observed cold-start, runtime, memory, or concurrency limitations honestly. If the accepted workload is too slow or unstable on the free tier, record evidence and ask for approval before changing limits, defaults, or scientific display.

## 9. Cloud deployment responsibilities

The user remains the deployment approver.

Possible deployment ownership models:

| Model | Meaning | Status |
| --- | --- | --- |
| User performs dashboard connection | User connects GitHub and creates the app in Streamlit Cloud; agent provides exact settings and later QA checklist | Proposed — awaiting approval |
| Agent assists with dashboard if tools/access are available | Agent helps only after explicit approval and only within Streamlit Cloud setup scope | Proposed — awaiting approval |

If dashboard access is unavailable to the agent:

- do not fake deployment;
- provide exact manual instructions;
- stop at the manual-connect gate;
- ask the user for the deployed public URL before Step 7 browser QA.

## 10. Local verification before deployment

Before Cloud setup, Phase 9 must prove the app can launch locally from repository root.

Required verification baseline:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s tests -p "test_streamlit_surface.py" -v
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -m unittest discover -s tests -p "test_*.py"
python -m unittest discover -s tests -p "test_api_job*.py" -v
python -m unittest discover -s tests -p "test_api_*.py" -v
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules); print('engine-ui-independence-ok')"
```

Required local Streamlit launch command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m streamlit run category_tracking_web.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
```

If port `8501` is occupied:

- do not kill unrelated processes without approval;
- use a recorded alternate local port for QA.

## 11. Deployed browser QA contract

After a public Streamlit URL exists, Step 7 must inspect the deployed app and verify:

- cold-start behavior;
- app loads;
- no missing dependency errors;
- Phase 8 UI appears;
- one-button workflow remains clear;
- Codon focus works;
- Whole population works;
- Compare both works;
- charts render;
- tables render;
- fullscreen controls remain;
- invalid input produces a concise user-facing error;
- no traceback is visible;
- no sensitive information leaks;
- free-tier/resource limitations are documented if observed.

If no deployed URL is available:

- record the exact blocker;
- provide the manual connection instructions;
- do not claim deployed QA passed.

## 12. Accessibility, security, and resource review contract

Phase 9 Step 8 must review:

- keyboard reachability for deployed app controls;
- visible focus;
- readable labels and guidance;
- chart/table context preserved;
- no committed secrets;
- no stack traces or private paths in deployed UI;
- no unexpected external service dependency;
- no database/worker/storage requirement;
- no changed engine/API/frontend boundaries;
- no broad CORS/auth/deployment assumptions;
- observed resource limitations and user guidance.

No missing authentication/CORS/rate limiting should be treated as a Phase 9 defect because Phase 9 is a public Streamlit demo deployment-readiness phase unless a later approved plan mutation says otherwise.

## 13. README deployment instructions policy

README edits are not authorized by Step 2 alone unless the user approves this contract and explicitly permits Step 4 README deployment instructions.

If approved in Step 4, README may document:

- Streamlit Community Cloud target;
- repository/branch/entrypoint;
- local launch command;
- dependency notes;
- Cloud Python version guidance;
- resource-limit warning;
- university-server deployment deferred.

README edits may not change scientific claims or implementation behavior.

## 14. Rollback and revert protocol

For every Phase 9 implementation step:

1. record touched files;
2. record pre-change byte counts and SHA-256;
3. back up existing touched files to a unique OS-temporary directory;
4. edit only approved files;
5. rerun required verification;
6. if rollback is needed, restore only manifest-listed files from backup;
7. remove only exact newly created files after validating resolved paths are inside the canonical repository;
8. never use Git as a backup system;
9. never recursively delete a broad directory;
10. record rollback evidence.

For Cloud deployment rollback:

- If the app was created manually in Streamlit Cloud, disable/delete/reconfigure it through the Streamlit Cloud dashboard only after user approval.
- If repository files were changed and committed later, use a normal reviewed revert commit after approval.

## 15. Prohibited changes

Phase 9 prohibits:

- scientific behavior changes;
- engine changes;
- FastAPI route or job behavior changes;
- Next.js rebuild or promotion;
- university server deployment;
- Docker or Kubernetes;
- authentication or authorization;
- database work;
- Redis, Celery, RQ, or PostgreSQL;
- paid infrastructure;
- asset/image/GIF/icon additions;
- fixture regeneration;
- diagnostic edits;
- chart-data changes;
- chart-type changes;
- table-data changes;
- hidden automatic mode switching;
- committed secrets;
- deployment setup before explicit approval;
- Phase 10 work.

## 16. Approval gates

| Gate | Required approval |
| --- | --- |
| Gate 1 | Approve this Phase 9 deployment contract before Step 3 |
| Gate 2 | Approve any `requirements.txt` dependency edit before Step 3 writes |
| Gate 3 | Approve README deployment-doc edits before Step 4 writes |
| Gate 4 | Approve Streamlit Cloud dashboard connection/deployment before Step 6 |
| Gate 5 | Provide or approve deployed public URL before Step 7 QA |
| Gate 6 | Approve Step 9 delivery gate before Step 10 |
| Gate 7 | Approve commit/push after Step 10 |

## 17. Explicit decisions awaiting approval

| Decision | Recommended option | Status |
| --- | --- | --- |
| Deployment target | Streamlit Community Cloud first | Proposed — awaiting approval |
| Repository | `https://github.com/allMighySheldor117/category-tracking.git` | Proposed — awaiting approval |
| Branch | `master` | Proposed — awaiting approval |
| Entrypoint | `category_tracking_web.py` | Proposed — awaiting approval |
| Primary frontend | Streamlit | Proposed — awaiting approval |
| Next.js status | Deferred / experimental / non-primary | Proposed — awaiting approval |
| Secrets | No secrets required; do not commit secrets | Proposed — awaiting approval |
| Database/storage/workers | None for Phase 9 | Proposed — awaiting approval |
| Python runtime | Select in Streamlit Cloud dashboard, preferably Python 3.12 unless audit says otherwise | Proposed — awaiting approval |
| Repository runtime file | Do not add unless separately approved | Proposed — awaiting approval |
| Step 3 dependency audit | Allow audit; user approved narrow dependency-boundary test mutation and minimal runtime dependency edit | Approved |
| Runtime dependencies | `streamlit>=1.60,<1.61`, `pandas>=2.2,<2.3`, `plotly>=6.8,<6.9` after audit | Approved |
| README deployment section | Edit only if contract approval or separate approval authorizes Step 4 | Proposed — awaiting approval |
| Cloud dashboard ownership | User performs manual connection unless agent access is explicitly approved and available | Proposed — awaiting approval |
| University server | Deferred to later phase | Proposed — awaiting approval |

## 18. Plan-mutation protocol

If a requested or discovered deployment need requires any prohibited or uncertain change:

1. stop;
2. record the conflict in `plans/phase-9-execution-log.md`;
3. identify affected files and user-visible behavior;
4. propose the smallest contract/Blueprint mutation;
5. explain compatibility, verification, and rollback impact;
6. request explicit user approval;
7. do not implement until approval is given.

Mutation triggers include:

- changing scientific calculations;
- changing charts/tables/data;
- adding deployment infrastructure;
- adding paid services;
- adding secrets;
- adding a database or storage provider;
- making Next.js primary;
- changing engine/API/job behavior;
- editing frozen fixtures or diagnostics;
- adding dependency files beyond `requirements.txt`;
- adding a repository runtime pin file;
- changing Streamlit entrypoint.

## 19. Completion checklist

- [x] Primary frontend named.
- [x] Deferred Next.js status named.
- [x] Deployment target named.
- [x] Repository, branch, and entrypoint proposed.
- [x] Dependency policy defined.
- [x] Expected dependency gap documented.
- [x] Python runtime policy defined.
- [x] Secrets policy defined.
- [x] Resource/multi-user limitations documented.
- [x] Local verification requirements listed.
- [x] Deployed browser QA requirements listed.
- [x] Accessibility/security/resource review requirements listed.
- [x] Rollback protocol defined.
- [x] Prohibited changes listed.
- [x] Approval gates listed.
- [x] Plan-mutation protocol listed.
- [x] User approved this deployment contract and the narrow dependency-boundary test mutation.
