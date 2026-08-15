# Phase 9 Blueprint: Streamlit Community Cloud Deployment Readiness

Status: Proposed — awaiting Phase 9 Blueprint approval

Created: 2026-08-14

Canonical repository: `C:\Users\hatem\OneDrive\Desktop\Project for uri\visualize code\category-tracking`

Latest approved baseline: `6cd410e feat: improve Streamlit guided UX for Phase 8`

## 1. Objective

Prepare the accepted Streamlit application for deployment to Streamlit Community Cloud so users can open it from a public `streamlit.app` link.

Phase 9 is a deployment-readiness phase only. It must preserve the accepted Phase 8 Streamlit application exactly as a scientific user experience:

- Streamlit remains the primary accepted user-facing frontend.
- Next.js remains deferred, experimental, and non-primary.
- University-server deployment is deferred to a later phase.
- Scientific outputs, chart data, table data, chart types, section order, control order, fullscreen behavior, and one-button workflow remain preserved.

The accepted Streamlit entry point is:

```powershell
python -m streamlit run category_tracking_web.py
```

Streamlit Community Cloud deployment should be configured from GitHub using `category_tracking_web.py` as the app entrypoint.

Current GitHub remote to revalidate before deployment:

```text
https://github.com/allMighySheldor117/category-tracking.git
```

## 2. Non-goals

Phase 9 explicitly excludes:

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
- broad performance optimization;
- Phase 10 work.

If any implementation step appears to require one of these, stop and request a plan mutation before editing.

## 3. Deployment-readiness contract

Phase 9 should create and approve a formal deployment contract before editing deployment files.

The contract must freeze these expectations:

- Streamlit entry point: `category_tracking_web.py`.
- Local launch command: `python -m streamlit run category_tracking_web.py`.
- Community Cloud deployment source: GitHub repository `https://github.com/allMighySheldor117/category-tracking.git`, branch `master`, entrypoint `category_tracking_web.py`.
- Step 6 must revalidate the local `origin` remote before using that repository value.
- The app must not require local-only absolute paths.
- The app must not require secrets.
- The app must not require external databases, object storage, background workers, or external services.
- The app must preserve Phase 8 UI, charts, tables, and science.
- The deployment is suitable for demo/small-team use on a free tier, not proven high-concurrency production.
- University-server deployment is a later phase.
- Streamlit Cloud Python runtime selection is dashboard-only unless the approved contract explicitly adds a repository runtime file.

The contract must not mark itself approved. It must stop for user approval.

## 4. Dependency policy

Streamlit Community Cloud builds a new remote Python environment. The deployment must include all runtime Python packages needed by the Streamlit app.

Current Phase 8 `requirements.txt` is backend-oriented:

```text
fastapi>=0.139,<0.141
uvicorn[standard]>=0.51,<0.52
httpx>=0.28,<0.29
```

Phase 9 must audit the actual imports used by the accepted Streamlit app and engine before editing dependency files.

Expected dependency gap:

- `category_tracking_web.py` currently uses Streamlit/Plotly/Pandas-facing runtime packages.
- The current `requirements.txt` does not list the accepted Streamlit app runtime dependencies.
- Streamlit Community Cloud may provide Streamlit by default, but the deployment should still explicitly record the app's runtime dependencies to reduce drift and missing-package failures.

Likely Streamlit runtime dependencies to evaluate and, if approved, add or constrain include:

- `streamlit`
- `pandas`
- `plotly`

Dependency rules:

- Do not remove approved Phase 4/5 backend dependencies unless explicitly justified and approved.
- Do not add unrelated packages.
- Do not add assets or frontend framework dependencies.
- Pin or constrain dependencies enough to reduce Cloud drift.
- Pick a Streamlit Community Cloud Python version compatible with the selected packages, preferably a stable released version such as Python 3.12 unless local evidence supports another version.
- Prefer selecting the Python version in the Streamlit Community Cloud dashboard Advanced settings.
- Do not add a repository runtime-pin file unless the deployment contract explicitly approves the exact file and validation method.
- Dependency edits require an explicit dependency-change approval gate.

## 5. Runtime and resource policy

Streamlit Community Cloud is free but resource-limited. Phase 9 must document this honestly.

The app should be presented as:

- a public demo;
- a research/teaching tool;
- a small-team sharing path;
- not a proven high-concurrency production deployment.

Phase 9 must not silently reduce scientific limits, chart data, or result fidelity to fit the free tier.

If the accepted default workload is too slow or memory-heavy on Streamlit Community Cloud, Phase 9 should:

1. record the evidence;
2. document safe workload guidance;
3. request approval before changing limits or defaults.

## 6. Strict preservation requirements

Every Phase 9 step must preserve:

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

## 7. Authoritative context for all implementation steps

Each implementation step must read the relevant subset of these files before editing:

Governing project files:

- `CLAUDE.md`
- `.ai-style-rules.md`
- `README.md`
- `future_enhancement_explained.plan.md`

Phase plans/logs:

- `plans/phase-1-extract-ui-independent-engine.md`
- `plans/phase-1-execution-log.md`
- `plans/phase-2-strengthen-computation.md`
- `plans/phase-2-execution-log.md`
- `plans/phase-3-optimize-computation.md`
- `plans/phase-3-execution-log.md`
- `plans/phase-4-fastapi-backend.md`
- `plans/phase-4-execution-log.md`
- `plans/phase-5-in-process-background-jobs.md`
- `plans/phase-5-execution-log.md`
- `plans/phase-6-nextjs-analysis-workspace.md`
- `plans/phase-6-execution-log.md`
- `plans/phase-7-streamlit-product-polish.md`
- `plans/phase-7-execution-log.md`
- `plans/phase-8-streamlit-assets-guided-ux.md`
- `plans/phase-8-execution-log.md`
- `plans/phase-9-streamlit-community-cloud-deployment.md`

Contracts/docs:

- `docs/phase_2_scientific_contract.md`
- `docs/phase_4_api_contract.md`
- `docs/phase_5_job_contract.md`
- `docs/phase_6_frontend_contract.md`
- `docs/phase_7_streamlit_visual_contract.md`
- `docs/phase_8_streamlit_guided_ux_contract.md`
- `docs/phase_9_streamlit_cloud_deployment_contract.md`, after Step 2 creates it
- `engine/README.md`
- `frontend/README.md`

Application and compatibility files:

- `category_tracking_web.py`
- `category_tracking.py`
- `diagnose_category_tracking_web.py`
- `tests/test_streamlit_surface.py`
- `tests/test_streamlit_engine_boundary.py`
- `tests/fixtures/phase1_streamlit_surface.json`
- `tests/fixtures/phase1_scientific_baseline.json`
- `tests/fixtures/phase2_scientific_contract.json`
- `tests/fixtures/phase5_openapi.json`
- `tests/compat/diagnose_category_tracking_web_phase1_baseline.py`
- `engine/**`
- `api/**`
- `requirements.txt`
- `frontend/`

## 8. Touched-file boundaries

Likely allowed files:

- `plans/phase-9-execution-log.md`
- `docs/phase_9_streamlit_cloud_deployment_contract.md`
- `requirements.txt`, only after dependency audit and user approval
- `README.md`, for deployment instructions
- `.streamlit/config.toml`, only if explicitly justified and approved for Cloud compatibility
- `runtime.txt` or another Cloud runtime-selection file, only if the Step 2 deployment contract explicitly approves repository-based runtime selection instead of dashboard-only selection

Possible but discouraged:

- `category_tracking_web.py`, only if deployment compatibility requires a tiny non-scientific launch fix and the user approves it.
- `.streamlit/config.toml`, because Streamlit Community Cloud overrides some settings; edit only if an observed Cloud compatibility issue proves it is necessary.

Prohibited unless an approved plan mutation changes scope:

- `engine/**`
- `api/**`, except read-only verification or documentation-only references
- `frontend/**`
- `tests/fixtures/**`
- `diagnose_category_tracking_web.py`
- `tests/compat/diagnose_category_tracking_web_phase1_baseline.py`
- `category_tracking.py`
- prior phase contracts except read-only references
- `assets/**`
- package files outside Python deployment needs
- Git metadata

## 9. Repository mode and safety rules

- Use direct mode.
- Git may be inspected read-only until final commit approval.
- Do not create branches, tags, pushes, PRs, or commits without explicit approval.
- Do not use Git as a backup system.
- Use `PYTHONDONTWRITEBYTECODE=1` during Python verification.
- Run verification serially.
- No concurrent writers or concurrent verification processes.
- Use `apply_patch` for file edits.
- Back up touched files to a unique OS-temporary backup directory before edits.
- Record byte counts and SHA-256 hashes before and after edits.
- Remove only exact generated files/directories after validating their resolved paths are inside the repository.

## 10. Verification baseline

Every implementation step must preserve this baseline from repository root:

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

Also verify:

- frozen fixture hashes unchanged;
- diagnostic hashes unchanged;
- accepted Streamlit UI markers unchanged;
- no root runtime imports;
- no forbidden engine imports;
- no `__pycache__`;
- no unexpected generated files;
- No Git writes until commit approval: no branch, tag, commit, push, or PR.
- Working-tree changes must be limited to approved touched files for the active step.

## 11. Local launch QA baseline

Phase 9 must include local Streamlit launch QA:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m streamlit run category_tracking_web.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
```

If port `8501` is occupied:

- do not kill unrelated processes;
- use a recorded alternate local port.

Verify:

- app loads;
- Phase 8 UI appears;
- one-button workflow remains clear;
- codon focus works;
- whole population works;
- compare both works;
- charts render;
- tables render;
- fullscreen controls remain;
- no traceback.

## 12. Streamlit Community Cloud QA baseline

If public deployment is available during Phase 9, inspect the deployed URL and verify:

- app cold-start behavior;
- app loads;
- no missing dependency errors;
- Phase 8 UI appears;
- charts render;
- tables render;
- codon focus works;
- whole population works;
- compare both works;
- invalid input produces concise user-facing error;
- no public stack trace or sensitive leakage;
- free-tier/resource limitations are documented.

If deployment is unavailable because the user must manually connect GitHub to Streamlit Community Cloud:

- record the exact blocker;
- provide exact user instructions;
- do not fake deployed QA;
- stop at the deployment/manual-connect gate.

## 13. Step-by-step implementation plan

### Step 1 — Revalidate Phase 8 and open Phase 9 execution log

Recommended skills:

1. `ecc:orch-add-feature`

Goal:

- Establish a clean Phase 9 baseline before any deployment-readiness edits.

Context brief:

- Phase 8 is complete and pushed at `6cd410e`.
- Streamlit is primary.
- Next.js is deferred.
- Phase 9 must not implement deployment changes yet beyond opening the execution log.

Tasks:

1. Confirm current branch, latest commit, remote, and clean working tree.
2. Confirm latest commit is `6cd410e` or later approved commit.
3. Confirm this Phase 9 Blueprint exists.
4. Create `plans/phase-9-execution-log.md`.
5. Record UTC timestamp.
6. Record byte counts and SHA-256 for required baseline files.
7. Run the full verification baseline.
8. Record diagnostic pass counts, hash evidence, boundary checks, no-Git-write evidence, and working-tree status.

Allowed touched files:

- `plans/phase-9-execution-log.md`

Prohibited files:

- all production, test, fixture, contract, dependency, engine, API, frontend, and app files.

Rollback:

- Delete only `plans/phase-9-execution-log.md` if Step 1 fails before approval, after validating the path.

Exit criteria:

- Phase 9 log exists.
- Phase 8 baseline is green.
- No implementation code exists.
- No Git write action occurred.

### Step 2 — Freeze Streamlit Cloud deployment contract

Recommended skills:

1. `ecc:contract-first`

Goal:

- Create the formal deployment contract before editing dependency/docs/deployment files.

Tasks:

1. Create `docs/phase_9_streamlit_cloud_deployment_contract.md`.
2. Mark status: `Proposed — awaiting Streamlit Cloud Deployment Contract approval`.
3. Define entrypoint, launch command, GitHub/branch/file assumptions, no-secrets policy, dependency policy, resource policy, Cloud QA policy, and manual-connect gate.
4. Include a decision table:
   - Streamlit Community Cloud first.
   - GitHub repository `https://github.com/allMighySheldor117/category-tracking.git`.
   - Entrypoint `category_tracking_web.py`.
   - Branch `master`.
   - No secrets.
   - No database/storage.
   - No assets.
   - University deployment deferred.
   - Dependency changes require approval.
   - Python runtime selected in Streamlit Cloud dashboard by default.
   - Repository runtime file prohibited unless separately approved.
   - README deployment-doc edits authorized or not authorized by the contract.
5. Run focused verification.
6. Append evidence to `plans/phase-9-execution-log.md`.
7. Stop for explicit user approval.

Allowed touched files:

- `docs/phase_9_streamlit_cloud_deployment_contract.md`
- `plans/phase-9-execution-log.md`

Prohibited files:

- `requirements.txt`
- `README.md`
- `category_tracking_web.py`
- app/source/test/fixture files.

Rollback:

- Restore execution log from backup.
- Remove the contract file only if newly created and rollback is required.

Exit criteria:

- Contract exists.
- Contract is proposed, not approved by the agent.
- User approval is requested before Step 3.

Approval gate:

- User must approve the Phase 9 deployment contract before proceeding.

### Step 3 — Audit and update dependency manifest only if needed

Recommended skills:

1. `ecc:orch-refine-code`
2. `ecc:python-patterns`

Goal:

- Make `requirements.txt` sufficient for Streamlit Community Cloud only if the audit proves it is not currently sufficient.

Tasks:

1. Inspect imports used by `category_tracking_web.py`, `engine/**`, and app startup.
2. Compare required third-party runtime packages against `requirements.txt`.
3. Treat missing Streamlit app runtime dependencies as the expected audit result unless evidence proves otherwise.
4. Decide whether `requirements.txt` must add or constrain Streamlit runtime dependencies such as `streamlit`, `pandas`, and `plotly`.
5. If dependency edits are needed:
   - stop and request explicit dependency-change approval before editing.
6. If approved:
   - update `requirements.txt` minimally;
   - preserve approved backend dependencies;
   - avoid unneeded packages.
7. Run local import and full verification.
8. Append evidence to execution log.

Allowed touched files:

- `requirements.txt`, only after approval
- `plans/phase-9-execution-log.md`

Prohibited files:

- application code;
- fixtures;
- engine/API behavior;
- frontend files.

Rollback:

- Restore `requirements.txt` from backup.
- Rerun import verification and baseline.

Exit criteria:

- Dependency manifest is either confirmed sufficient or updated with approval.
- No dependency drift beyond the approved set.
- Full verification passes.

Approval gate:

- Required before editing `requirements.txt`.

### Step 4 — Add/update deployment README instructions

Recommended skills:

1. `ecc:orch-refine-code`

Goal:

- Document how to deploy and launch the app on Streamlit Community Cloud.

Tasks:

1. Update `README.md` with a concise deployment section.
   - This requires either Step 2 contract approval explicitly authorizing README deployment-doc edits, or a separate README/deployment-doc approval before editing.
2. Include:
   - Streamlit remains primary frontend.
   - GitHub repository/branch.
   - Entry point `category_tracking_web.py`.
   - Local command.
   - Streamlit Community Cloud manual steps.
   - Recommended Python version selected in Streamlit Cloud settings.
   - Resource-limit warning.
   - University-server deployment deferred.
3. Do not alter scientific or user-facing app behavior.
4. Run verification.
5. Append evidence.

Allowed touched files:

- `README.md`
- `plans/phase-9-execution-log.md`

Prohibited files:

- production app files;
- tests unless a documentation marker test is explicitly approved;
- fixtures;
- dependency files unless Step 3 approved changes.

Rollback:

- Restore `README.md` and log from backup.

Exit criteria:

- Deployment instructions are clear and accurate.
- Verification passes.

### Step 5 — Local clean-launch verification

Recommended skills:

1. `developing-with-streamlit`
2. `ecc:browser-qa`

Goal:

- Prove the app launches locally from repository root in the same way Streamlit Community Cloud will run it.

Tasks:

1. Confirm dependencies import locally.
2. Start Streamlit from repository root.
3. If port `8501` is occupied, use a recorded alternate port.
4. Browser QA:
   - app loads;
   - Phase 8 UI appears;
   - codon focus works;
   - whole population works;
   - compare both works;
   - charts/tables render;
   - fullscreen controls remain;
   - invalid input is concise;
   - no traceback.
5. Stop local Streamlit cleanly.
6. Run full verification.
7. Append evidence.

Allowed touched files:

- `plans/phase-9-execution-log.md`

Prohibited files:

- all app/source/test/fixture/dependency/docs files unless earlier approved steps already changed them.

Rollback:

- Stop started local server.
- Remove exact generated cache files only after path validation.

Exit criteria:

- Local launch passes.
- Browser QA passes or records a clear non-code blocker.
- Full verification passes.

### Step 6 — Deploy or prepare deployment to Streamlit Community Cloud

Recommended skills:

1. `ecc:deployment-patterns`

Goal:

- Prepare or perform the Streamlit Community Cloud deployment workflow.

Tasks:

1. Confirm user is ready to connect GitHub to Streamlit Community Cloud.
2. If agent cannot access the Streamlit Cloud dashboard:
   - provide exact manual user steps;
   - stop at manual-connect gate;
   - do not fake deployment.
3. If deployment access is available and explicitly approved:
   - configure repository `allMighySheldor117/category-tracking`;
   - branch `master`;
   - entrypoint `category_tracking_web.py`;
   - selected Python version per contract;
   - no secrets.
4. Record deployment URL if available.
5. Append evidence.

Allowed touched files:

- `plans/phase-9-execution-log.md`
- possibly `README.md` if the public URL is known and user approves recording it.

Prohibited files:

- source code;
- fixtures;
- dependency files unless Step 3 approved.

Rollback:

- If deployment was created incorrectly, document dashboard steps to delete/reconfigure.
- Do not delete remote resources without explicit approval.

Exit criteria:

- Deployment is available for QA, or exact manual-connect blocker/instructions are recorded.

Approval gate:

- User must approve/perform manual Streamlit Cloud connection when required.

### Step 7 — Browser QA on deployed public Streamlit link

Recommended skills:

1. `ecc:browser-qa`

Goal:

- Verify the deployed public app works for users.

Tasks:

1. Open deployed public Streamlit URL.
2. Verify:
   - cold start behavior;
   - app loads;
   - no missing dependency errors;
   - Phase 8 UI appears;
   - codon focus works;
   - whole population works;
   - compare both works;
   - charts/tables render;
   - invalid input is user-facing;
   - no stack trace or sensitive leakage.
3. Record resource/free-tier observations.
4. Append evidence.

Allowed touched files:

- `plans/phase-9-execution-log.md`

Prohibited files:

- all source/test/fixture/dependency files.

Rollback:

- If deployed QA fails due to dependencies, return to Step 3.
- If deployed QA fails due to manual Cloud configuration, return to Step 6.

Exit criteria:

- Public deployed link is verified, or exact blocker is documented.

### Step 8 — Accessibility/security/resource review for public demo readiness

Recommended skills:

1. `ecc:accessibility`
2. `ecc:security-review`

Goal:

- Review the public demo posture without adding auth/secrets/infrastructure.

Tasks:

1. Accessibility:
   - keyboard controls reachable;
   - focus visible;
   - labels preserved;
   - guided copy understandable;
   - chart/table headings remain clear.
2. Security/public-demo review:
   - no secrets required;
   - no committed secrets;
   - no local-only files required;
   - no upload/persistent storage assumption;
   - no public stack traces observed in normal error paths;
   - no deployment logs exposed to ordinary viewers;
   - public resource limitations documented.
3. Classify findings.
4. Do not add auth or infrastructure.
5. Append evidence.

Allowed touched files:

- `plans/phase-9-execution-log.md`
- `README.md`, only if documenting resource/security posture is required and approved.

Prohibited files:

- source behavior;
- engine/API/job changes;
- auth/database/deployment infrastructure.

Rollback:

- Restore README/log if needed.

Exit criteria:

- No unresolved CRITICAL/HIGH findings.
- Any LOW findings are explicitly deferred.

### Step 9 — Delivery gate / final compatibility approval

Recommended skills:

1. `ecc:delivery-gate`

Goal:

- Verify Phase 9 is ready for final handoff.

Tasks:

1. Confirm Steps 1-8 are complete or blocked with explicit evidence.
2. Run full verification baseline.
3. Verify:
   - dependency manifest status;
   - README deployment instructions;
   - local launch QA;
   - deployed QA or manual blocker;
   - accessibility/security/resource evidence;
   - immutable fixture hashes;
   - diagnostics;
   - no source/science regressions;
   - no unexpected files.
4. Append evidence.
5. Stop for user approval to proceed to Step 10.

Allowed touched files:

- `plans/phase-9-execution-log.md`

Prohibited files:

- all source/test/fixture/dependency/docs files unless already approved earlier.

Rollback:

- If delivery gate fails, identify owning step and request approval to reopen.

Exit criteria:

- Delivery gate passes.
- No unresolved CRITICAL/HIGH findings.

### Step 10 — Final handoff and commit/push gate

Recommended skills:

1. `ecc:delivery-gate`

Goal:

- Complete final Phase 9 handoff and stop before commit/push unless user approves.

Tasks:

1. Confirm Step 9 passed.
2. Run final verification baseline.
3. Record final Git status.
4. Record final touched-file manifest.
5. Record public URL if available.
6. Record manual deployment blocker if deployment requires user action.
7. Record deferred findings.
8. Recommend commit message.
9. Stop for explicit commit/push approval.

Allowed touched files:

- `plans/phase-9-execution-log.md`

Prohibited files:

- all implementation files unless earlier approved.

Rollback:

- Restore manifest-listed files from backup.
- Rerun verification.

Exit criteria:

- Phase 9 final handoff complete.
- No commit/push occurred without approval.
- Phase 10 not started.

Recommended commit message:

```text
docs: prepare Streamlit Community Cloud deployment
```

If dependency changes are included, consider:

```text
chore: prepare Streamlit Community Cloud deployment
```

## 14. Dependency graph

```text
Step 1
  -> Step 2
      -> Step 3
          -> Step 4
              -> Step 5
                  -> Step 6
                      -> Step 7
                          -> Step 8
                              -> Step 9
                                  -> Step 10
```

Parallelism:

- No implementation steps should run in parallel.
- Deployment-readiness changes touch shared docs/dependency/log state, so serial execution is safer.

## 15. Approval gates

Gate 1 — Blueprint approval:

- Approve this Phase 9 Blueprint before Step 1.

Gate 2 — Deployment contract approval:

- Required after Step 2 before dependency/docs/deployment work.
- Must explicitly decide whether README deployment-doc edits are authorized.

Gate 3 — Dependency-change approval:

- Required before editing `requirements.txt`.

Gate 4 — Manual Streamlit Cloud connection/deployment gate:

- Required before or during Step 6 if the user must connect GitHub/dashboard access.

Gate 5 — Delivery approval:

- Required after Step 9 before Step 10 final handoff.

Gate 6 — Commit/push approval:

- Required after Step 10.

## 16. Recommended ECC skill order

| Step | Skills | Purpose |
|---|---|---|
| 1 | `ecc:orch-add-feature` | Open Phase 9 safely and establish baseline. |
| 2 | `ecc:contract-first` | Freeze Streamlit Cloud deployment contract. |
| 3 | `ecc:orch-refine-code` + `ecc:python-patterns` | Audit/update dependencies only if approved. |
| 4 | `ecc:orch-refine-code` | Documentation-only deployment instructions. |
| 5 | `developing-with-streamlit` + `ecc:browser-qa` | Local Streamlit launch and browser smoke QA. |
| 6 | `ecc:deployment-patterns` | Streamlit Community Cloud deployment/manual setup gate. |
| 7 | `ecc:browser-qa` | Public deployed-link QA. |
| 8 | `ecc:accessibility` + `ecc:security-review` | Public demo readiness review. |
| 9 | `ecc:delivery-gate` | Final compatibility approval gate. |
| 10 | `ecc:delivery-gate` | Final handoff and commit gate. |

## 17. Risk classification

Overall risk: medium.

- Deployment risk: medium, because cloud runtime/dependency behavior can differ from local Windows development.
- Scientific risk: low if touched-file boundaries are honored.
- Availability/resource risk: medium, because Streamlit Community Cloud free resources may throttle, slow down, or fail under heavy workloads.
- Security risk: low if no secrets, auth, uploads, persistence, or external services are introduced.
- Acceptance risk: low-to-medium, because the app UI is already accepted but deployment cold starts/resource limits may affect perceived quality.

## 18. Anti-patterns

Do not:

- treat a local launch as proof of deployed Cloud readiness;
- fake deployed browser QA without a public URL;
- silently change generation/copy limits for Cloud performance;
- remove backend dependencies from `requirements.txt` without approval;
- assume current `requirements.txt` is Cloud-ready without auditing the accepted Streamlit app imports;
- add unneeded packages to `requirements.txt`;
- add secrets to the repository;
- add `.streamlit/secrets.toml`;
- use Windows-only paths in deployment docs;
- change chart/table output to reduce Cloud load;
- promote Next.js;
- start university-server work;
- start Phase 10.

## 19. Plan-mutation protocol

If any requested deployment improvement requires one of the following, stop and request explicit approval:

- changing chart type or data;
- changing scientific behavior;
- changing engine/API/job behavior;
- adding auth;
- adding a database;
- adding deployment infrastructure beyond Streamlit Community Cloud;
- adding external service secrets;
- adding paid resources;
- modifying fixtures;
- making Next.js primary;
- moving to university server deployment;
- changing Phase 9 step order materially.
- adding a repository runtime-pin file instead of dashboard-only Python selection.

Required mutation record:

1. reason for mutation;
2. affected files;
3. affected prior contracts;
4. compatibility impact;
5. rollback plan;
6. exact user approval;
7. updated verification requirements.

## 20. Rollback protocol

Before each editing step:

1. record touched-file manifest;
2. record byte counts and SHA-256 hashes;
3. create a unique OS-temporary backup directory;
4. back up every touched file;
5. append backup paths to `plans/phase-9-execution-log.md`.

If rollback is needed:

1. restore only manifest-listed files from backup;
2. remove only exact newly created files after validating resolved paths inside the repository;
3. never recursively delete broad directories;
4. rerun verification baseline;
5. record rollback evidence.

## 21. Unresolved decisions requiring user approval

- Approve this Phase 9 Blueprint.
- Approve the Step 2 deployment contract.
- Decide whether `requirements.txt` may be updated if dependency audit proves Streamlit Cloud needs app runtime packages.
- Choose a Streamlit Community Cloud Python version, likely Python 3.12 unless audit evidence recommends otherwise.
- Decide whether Python runtime selection is dashboard-only, or whether a repository runtime file is approved.
- Decide whether Step 2 contract approval authorizes README deployment-doc edits.
- Decide whether the user or agent will perform the Streamlit Cloud dashboard connection.
- Provide/approve the public deployed URL for Step 7 QA.
- Approve final commit/push after Step 10.

## 22. Completion checklist

Phase 9 is complete only when:

- Phase 9 execution log exists and is complete.
- Deployment contract is approved.
- Dependency manifest is verified or updated with approval.
- README deployment instructions are present if approved.
- Local launch QA passes.
- Streamlit Community Cloud deployment is either verified or the manual blocker is precisely documented.
- Public deployed-link QA passes if a public URL is available.
- Accessibility/security/resource review has no unresolved CRITICAL/HIGH findings.
- Full verification baseline passes.
- Immutable fixtures and diagnostics remain unchanged.
- Streamlit remains primary.
- Next.js remains non-primary.
- University-server deployment remains deferred.
- No Phase 10 work has started.
- Final handoff is complete.
- Commit/push occurs only after explicit user approval.
