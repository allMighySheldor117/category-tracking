# Phase 3 Blueprint — Optimize Computation

## Status

Proposed — awaiting human review and approval.

Generated for the clean private repository:

- Repository: `https://github.com/allMighySheldor117/category-tracking`
- Canonical local repo: `C:\Users\hatem\OneDrive\Desktop\Project for uri\visualize code\category-tracking`
- Current branch observed during planning: `master`
- Current commit observed during planning: `54b2c1d feat: add codon category tracking web app`

This Blueprint is for Phase 3 only. It does not implement Phase 3 code.

## Size and risk classification

Phase 3 is a large, high-risk scientific optimization project.

Risk is high because optimization can accidentally change:

- exact floating-point accumulation order;
- canonical DataFrame schemas and ordering;
- detailed sampled RNG side effects;
- aggregated sampled reducer equivalence;
- denominator and zero-case behavior;
- Streamlit or Tkinter compatibility through seemingly internal changes.

The safest Phase 3 posture is: benchmark first, optimize behind Phase 2 contracts, compare against Phase 2 reference behavior, then expose nothing new unless a contract gate approves it.

## Planning observations

The clean repo is now the canonical application repository. It contains the Phase 2 engine, tests, fixtures, docs, Streamlit app, and Tkinter compatibility adapter.

Observed public Phase 2 engine surface includes:

- `run_exact_analysis`, `build_exact_analysis`;
- exact query APIs for category metrics, survivor fractions, survival by start, stop outcomes, codon outcomes, and convergence;
- `run_aggregated_experiment`;
- aggregated query APIs for category metrics, survivor fractions, survival by start, stop outcomes, codon outcomes, and convergence;
- `compare_numeric_metric`, `compare_convergence`, `compare_exact_to_sampled`;
- Phase 2 dataclasses and explicit engine exceptions exported from `engine.__init__`.

Observed compatibility baseline:

- `python diagnose_category_tracking_web.py` passed all 17 checks.
- `python -m tests.compat.diagnose_category_tracking_web_phase1_baseline` passed all 17 checks.
- Fresh engine UI-independence import passed.
- `python -m unittest discover -s tests -p "test_*.py"` currently reports one clean-repo packaging failure: `tests/test_phase2_boundaries.py` expects `CLAUDE.md`, but the clean repo intentionally excludes that file. Phase 3 Step 1 must resolve or re-scope this repository-boundary test before optimization begins.
- The attachment referenced `tests/test_exact_invariants.py`; the clean repo instead contains `tests/test_scientific_invariants.py`.

## Non-negotiable preservation rules

Phase 3 optimizations are allowed only behind the approved Phase 2 contracts.

Preserve exactly:

- Phase 2 public dataclass fields, field order, ownership, and result contracts;
- exact result schemas, columns, dtypes, indexes, row order, key order, labels, denominators, zero behavior, and empty behavior;
- exact same-process output equality for existing APIs, including `float.hex()` where Phase 2 requires it;
- `engine.exact_tracking.run_simulation` behavior unless a separately approved reference/optimized dual-path contract is created;
- detailed sampled `run_experiment` records, paths, copy numbering, random draw order, module-global RNG behavior, consecutive-call behavior, and final `random.getstate()`;
- aggregated sampled local-seed behavior, copy-major draw order, reducer equivalence, no per-copy retention, structural memory bounds, and count conservation;
- Streamlit widget order, labels, query/cache behavior, charts, tables, error wording, accessibility behavior, and visual identity;
- Tkinter compatibility through `category_tracking.py`;
- frozen diagnostics and fixtures.

Phase 3 must not change Phase 2 scientific meaning merely to make code faster.

## Canonical verification baseline

Every implementation step must run from the clean repo root with `PYTHONDONTWRITEBYTECODE=1`:

```powershell
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"
```

Until Step 1 resolves the clean-repo `CLAUDE.md` test expectation, that specific suite failure is a known pre-optimization blocker and must not be ignored.

## Repository and execution mode

Use Git for read-only inspection and user-approved commits only. Do not commit during any approval gate unless the user explicitly authorizes it.

Each implementation step must:

- start from a clean or explicitly documented working tree;
- record UTC timestamps, touched files, pre/post SHA-256 hashes, and verification evidence;
- use focused tests before production edits;
- keep writes serialized;
- avoid concurrent verification commands in the same workspace;
- preserve unrelated user changes;
- update a Phase 3 execution log at `plans/phase-3-execution-log.md`.

## Recommended ECC skill order

Use this order after the Blueprint is approved:

1. `ecc:orch-refine-code` — run Step 1 only to fix/re-scope the clean-repo boundary baseline without changing scientific behavior.
2. `ecc:benchmark-methodology` — create and approve the Phase 3 benchmark methodology before measuring or optimizing.
3. `ecc:benchmark` — capture read-only baseline runtime, memory, and cardinality observations.
4. `ecc:orch-refine-code` — implement safe internal optimizations step by step under TDD.
5. `ecc:contract-first` — only if a dependency, matrix representation, new optimized API, or UI option is proposed.
6. `ecc:council` — use at optimization equivalence and final go/no-go gates.
7. `ecc:browser-qa` and `ecc:accessibility` — only if Phase 3 touches or exposes any UI behavior.
8. `ecc:delivery-gate` — final Phase 3 handoff after all approved steps pass.

## Dependency graph

```text
Step 1 Phase 2 revalidation and clean-repo boundary repair
  -> Step 2 Benchmark methodology contract
    -> Step 3 Baseline benchmark harness and measurements
      -> Step 4 Exact hot-path profiling
        -> Step 5 Exact derived-table optimization
        -> Step 6 Exact propagation optimization research gate
      -> Step 7 Aggregated sampled profiling
        -> Step 8 Aggregated sampled internal optimization
      -> Step 9 Comparison and calibration workload optimization
        -> Step 10 Optimization equivalence council
          -> Step 11 Compatibility/UI approval gate
            -> Step 12 Final documentation and delivery gate
```

Logical parallelism:

- Step 4 and Step 7 can be researched in parallel after Step 3 because both are read-only profiling tracks.
- Step 5, Step 8, and Step 9 touch different logical areas but should still be implemented serially in this repo to keep benchmark and regression evidence clear.
- Any dependency or public-contract change discovered in Step 6 pauses the plan and routes through the mutation protocol before implementation.

## Step 1 — Revalidate Phase 2 and repair clean-repo boundary assumptions

### Purpose

Establish a green Phase 2 baseline inside the clean repo before optimization work starts.

### Cold-start context

The clean repo intentionally excludes `CLAUDE.md` and `.ai-style-rules.md`, but `tests/test_phase2_boundaries.py` currently expects `CLAUDE.md`. This is a packaging-boundary issue, not an observed scientific failure. Diagnostics and engine UI-independence checks pass.

### Touched files

- `tests/test_phase2_boundaries.py`
- `README.md` only if the test requires a documented clean-repo boundary statement
- `plans/phase-3-execution-log.md`

### Preconditions

- Blueprint approved by the user.
- Working tree inspected and unrelated changes preserved.
- No Phase 3 optimization code has been written.

### Tasks

1. Record the Phase 3 start manifest and baseline hashes.
2. Add a focused failing test that expresses the clean repo boundary correctly: runtime app files must not require root research files or excluded agent-instruction files.
3. Update only the stale boundary assertion that assumes `CLAUDE.md` is present.
4. Preserve all scientific, Streamlit, Tkinter, fixture, and diagnostic assertions.
5. Run the full Phase 2 verification baseline.

### Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s tests -p "test_phase2_boundaries.py" -v
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"
```

### Exit criteria

- Full suite is green in the clean repo.
- Diagnostics still pass all 17 checks.
- No app behavior, scientific output, or public API changes occurred.
- Execution log records the clean-repo packaging rationale.

### Rollback

Restore only the touched files from the Step 1 backup and rerun the observed pre-step diagnostics.

### Handoff

Step 2 may start only after this baseline is green.

## Step 2 — Define and approve benchmark methodology

### Purpose

Freeze how Phase 3 measures runtime, memory, cardinality, and equivalence before any optimization.

### Cold-start context

Phase 2 explicitly says aggregated sampling reduced retained memory, not CPU complexity. Phase 3 must not turn advisory timing into a scientific acceptance rule.

### Touched files

- `docs/phase_3_benchmark_methodology.md`
- `plans/phase-3-execution-log.md`

### Preconditions

- Step 1 full baseline is green.

### Tasks

1. Record hardware, OS, Python, pandas, Streamlit, and dependency versions.
2. Define deterministic benchmark workloads:
   - exact single-codon small/medium/larger generation runs;
   - exact all-codon population runs;
   - repeated exact table construction;
   - aggregated sampled small/medium/larger copy-count runs;
   - comparison/calibration workloads.
3. Define warm-up, repeat count, median/min/max reporting, and timeout safety.
4. Define advisory memory measurement with `tracemalloc` plus structural memory checks.
5. Define correctness gates separately from timing observations.
6. Stop for human benchmark-methodology approval.

### Verification

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

### Exit criteria

- Methodology is explicit enough that two runs can be compared without guessing.
- No benchmark thresholds are invented before baseline capture.
- Human approval is recorded before Step 3.

### Rollback

Remove only the new methodology file if newly created, restore the execution log, and rerun Step 1 baseline.

### Handoff

Step 3 uses this methodology unchanged unless a plan mutation is approved.

## Step 3 — Add baseline benchmark harness and capture reference measurements

### Purpose

Create repeatable, non-production benchmark tooling and capture Phase 2 reference behavior.

### Cold-start context

Benchmark output is advisory unless the methodology marks a structural condition as an acceptance gate. No production optimization occurs in this step.

### Touched files

- `tests/test_phase3_benchmark_baseline.py`
- `tools/benchmark_phase3.py` or `tests/phase3_benchmark_support.py`
- `docs/phase_3_benchmark_results.md`
- `plans/phase-3-execution-log.md`

### Preconditions

- Step 2 methodology approved.
- Full Phase 2 baseline green.

### Tasks

1. Add tests proving benchmark workloads are deterministic and safe.
2. Add a small standard-library benchmark harness.
3. Capture baseline timing and advisory memory observations.
4. Record structural memory/cardinality data for aggregated sampled results.
5. Store results as documentation, not as brittle pass/fail thresholds.

### Verification

```powershell
python -m unittest discover -s tests -p "test_phase3_benchmark_baseline.py" -v
python tools/benchmark_phase3.py
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
```

### Exit criteria

- Baseline measurements exist.
- Benchmark harness does not import UI frameworks.
- Benchmark tests do not depend on wall-clock speed.

### Rollback

Remove only new benchmark artifacts and restore the execution log.

### Handoff

Steps 4, 7, and 9 use these baseline measurements.

## Step 4 — Profile exact-probability hot paths

### Purpose

Find exact computation bottlenecks without changing code.

### Cold-start context

`run_simulation` is the Phase 1-compatible exact primitive. `run_exact_analysis` calls it once, then builds canonical Phase 2 tables. Optimization must not change exact propagation order unless a separately approved dual-reference strategy exists.

### Touched files

- `docs/phase_3_exact_profile.md`
- `plans/phase-3-execution-log.md`

### Preconditions

- Step 3 benchmark baseline exists.

### Tasks

1. Profile exact workloads using the approved benchmark cases.
2. Separate propagation time from derived-table construction time.
3. Identify repeated table derivation, sorting, grouping, Counter use, DataFrame construction, and provenance-validation costs.
4. Recommend safe optimization targets for Step 5.
5. Route any algorithm rewrite or matrix idea to Step 6 instead of implementing it here.

### Verification

```powershell
python tools/benchmark_phase3.py --exact-profile
python -m unittest discover -s tests -p "test_*.py"
```

### Exit criteria

- Profile report names specific hot paths and expected safety constraints.
- No production code changes occurred.

### Rollback

Remove the profile document if needed and restore execution-log changes.

### Handoff

Step 5 implements only low-risk optimizations justified by this profile.

## Step 5 — Optimize exact derived-table construction

### Purpose

Reduce repeated exact table construction overhead while preserving exact propagation and Phase 2 table contracts.

### Cold-start context

The safest first optimization target is derived-table construction around `ExactAnalysisResult`, not the underlying propagation algorithm.

### Touched files

- `engine/exact_analysis.py`
- `engine/category_analysis.py` only if exact table reuse requires it
- `tests/test_exact_analysis.py`
- `tests/test_scientific_invariants.py`
- `tests/test_phase3_exact_optimization.py`
- `docs/phase_3_benchmark_results.md`
- `plans/phase-3-execution-log.md`

### Preconditions

- Step 4 identifies table construction as a meaningful cost.
- Step 1 baseline remains green.

### Tasks

1. Write failing equivalence tests comparing optimized outputs to Phase 2 reference outputs.
2. Add safe internal caching or shared derived-table helpers only where inputs are immutable or copied defensively.
3. Ensure `run_simulation` is still called at most once by `run_exact_analysis`.
4. Preserve DataFrame schema, dtype, index, row order, and `float.hex()` where required.
5. Re-run benchmarks and record before/after observations.

### Verification

```powershell
python -m unittest discover -s tests -p "test_phase3_exact_optimization.py" -v
python -m unittest discover -s tests -p "test_exact_analysis.py" -v
python -m unittest discover -s tests -p "test_scientific_invariants.py" -v
python tools/benchmark_phase3.py --exact
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
```

### Exit criteria

- Exact outputs are byte/hex/schema equivalent to Phase 2 reference expectations.
- Benchmarks show measured effect, positive or neutral.
- No public contract changes occurred.

### Rollback

Restore touched engine/tests/docs/log files from backups and rerun Step 4 baseline.

### Handoff

Step 6 decides whether deeper exact algorithm work is justified.

## Step 6 — Exact matrix/transition-model research and dependency gate

### Purpose

Evaluate whether NumPy/SciPy, transition matrices, or a new optimized exact algorithm are worth a formal contract/dependency mutation.

### Cold-start context

The Phase 2 contract deferred matrices, vectorization, NumPy/SciPy, and optimization to Phase 3. This step may research and propose, but must not silently add dependencies or replace exact APIs.

### Touched files

- `docs/phase_3_exact_matrix_research.md`
- `plans/phase-3-execution-log.md`
- If approved later: `docs/phase_3_exact_optimization_contract.md`

### Preconditions

- Step 5 benchmark results are available.

### Tasks

1. Compare candidate designs:
   - keep current exact algorithm;
   - optimize pure-Python internals only;
   - add optional transition matrix reference implementation;
   - add NumPy/SciPy-backed experimental path.
2. Document dependency impact, install impact, fallback plan, and equivalence strategy.
3. Define whether a new API is needed or whether optimization remains internal.
4. Stop for dependency/contract approval before any implementation.

### Verification

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

### Exit criteria

- Recommendation is evidence-backed.
- No dependency is added.
- No production algorithm is changed.
- Human approval gate decision is recorded.

### Rollback

Remove research/contract proposal documents only if requested, restore execution-log entry.

### Handoff

If rejected, continue with pure-Python/internal-only optimization. If approved, insert new implementation steps through the plan-mutation protocol.

## Step 7 — Profile aggregated sampled execution

### Purpose

Measure where aggregated sampled runtime is spent while preserving Phase 2 memory and RNG contracts.

### Cold-start context

Phase 2 aggregated sampling is explicit, local-seeded, copy-major, reducer-equivalent, and structurally memory-bounded. CPU improvements must not break that unless a new experimental API is approved.

### Touched files

- `docs/phase_3_aggregated_profile.md`
- `docs/phase_3_benchmark_results.md`
- `plans/phase-3-execution-log.md`

### Preconditions

- Step 3 baseline exists.

### Tasks

1. Profile aggregated workloads at approved safe copy counts.
2. Measure counter-update overhead, transition lookup overhead, loop overhead, and result freezing overhead.
3. Confirm retained collection cardinality remains bounded as copy counts grow.
4. Identify low-risk internal optimizations for Step 8.
5. Route generation-major/vectorized/random-count algorithms to a separate contract gate.

### Verification

```powershell
python tools/benchmark_phase3.py --aggregated-profile
python -m unittest discover -s tests -p "test_aggregated_tracking.py" -v
python -m unittest discover -s tests -p "test_*.py"
```

### Exit criteria

- Profile report separates CPU cost from retained-memory behavior.
- No production code changes occurred.

### Rollback

Restore docs/log only.

### Handoff

Step 8 implements only contract-preserving internal improvements.

## Step 8 — Optimize aggregated sampled internals without changing reducer equivalence

### Purpose

Reduce overhead in `run_aggregated_experiment` while preserving the Phase 2 sampled aggregate contract exactly.

### Cold-start context

Any optimized path that cannot preserve detailed-reducer equivalence is not a replacement for `run_aggregated_experiment`.

### Touched files

- `engine/aggregated_tracking.py`
- `tests/test_aggregated_tracking.py`
- `tests/test_aggregated_analysis.py`
- `tests/test_phase3_aggregated_optimization.py`
- `docs/phase_3_benchmark_results.md`
- `plans/phase-3-execution-log.md`

### Preconditions

- Step 7 identifies safe internal overhead.
- Full baseline is green.

### Tasks

1. Write failing equivalence and structural-memory tests for the specific optimization.
2. Optimize only internal data access, counter updates, or freezing where draw order and retained fields remain unchanged.
3. Preserve local `random.Random(seed)`, copy-major order, `randint` then `choices`, early-stop behavior, and canonical key ordering.
4. Prove exact detailed-reducer equality for reviewed compact seeds.
5. Re-run benchmark observations.

### Verification

```powershell
python -m unittest discover -s tests -p "test_phase3_aggregated_optimization.py" -v
python -m unittest discover -s tests -p "test_aggregated_tracking.py" -v
python -m unittest discover -s tests -p "test_aggregated_analysis.py" -v
python tools/benchmark_phase3.py --aggregated
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
```

### Exit criteria

- Reducer equivalence and count conservation are exact.
- Global RNG remains untouched.
- Retained collection cardinality does not grow with copy count.
- Detailed sampled API remains byte-identical unless a separate approved change exists.

### Rollback

Restore touched engine/tests/docs/log files and rerun Step 7 baseline.

### Handoff

Step 9 may optimize comparison/calibration workload construction.

## Step 9 — Optimize comparison and calibration workloads

### Purpose

Reduce repeated exact/sampled table work in comparison and calibration flows while preserving Phase 2 statistical methodology.

### Cold-start context

`compare_exact_to_sampled` uses Wilson score intervals with Bonferroni family correction. Exact probability is deterministic reference; sampled output is experimental estimate.

### Touched files

- `engine/comparisons.py`
- `engine/exact_analysis.py` only if shared exact table reuse is needed
- `tests/test_comparisons.py`
- `tests/test_statistical_convergence.py`
- `tests/test_phase3_comparison_optimization.py`
- `docs/phase_3_benchmark_results.md`
- `plans/phase-3-execution-log.md`

### Preconditions

- Steps 5 and 8 complete or explicitly deferred.

### Tasks

1. Add tests proving comparison tables match Phase 2 exactly.
2. Avoid recomputing table schemas, row maps, or aligned key structures when a safe internal cache or helper can be used.
3. Preserve Wilson/Bonferroni formulas, nullable behavior, family-size handling, and calibration seed panel.
4. Re-run statistical calibration tests and benchmark observations.

### Verification

```powershell
python -m unittest discover -s tests -p "test_phase3_comparison_optimization.py" -v
python -m unittest discover -s tests -p "test_comparisons.py" -v
python -m unittest discover -s tests -p "test_statistical_convergence.py" -v
python tools/benchmark_phase3.py --comparisons
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
```

### Exit criteria

- Statistical outputs are contract-equivalent.
- Calibration panel remains preregistered; no seed searching.
- Benchmarks report measured effect.

### Rollback

Restore touched files and rerun previous full baseline.

### Handoff

Step 10 reviews all optimization evidence together.

## Step 10 — Optimization equivalence council

### Purpose

Decide whether Phase 3 optimized internals are scientifically equivalent and safe to move to compatibility approval.

### Cold-start context

This is a decision gate, not implementation. It must use strongest-model adversarial review before the council verdict.

### Touched files

- `plans/phase-3-execution-log.md`
- `docs/phase_3_benchmark_results.md` only for final evidence append

### Preconditions

- Steps 5, 8, and 9 either complete or are explicitly deferred with evidence.
- Full regression and benchmark evidence exists.

### Tasks

1. Run a strongest-model read-only technical review covering:
   - exact float/order equivalence;
   - schemas/dtypes/indexes/key order;
   - denominator and zero behavior;
   - detailed sampled RNG preservation;
   - aggregated reducer equivalence and structural memory;
   - statistical methodology;
   - import/UI boundaries;
   - dependency and Phase 3 scope boundaries.
2. Convene `ecc:council` for PROCEED, REOPEN, or BLOCK FOR CONTRACT DECISION.
3. Resolve or explicitly defer only non-blocking MEDIUM/LOW findings.

### Verification

```powershell
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"
python tools/benchmark_phase3.py --all
```

### Exit criteria

- No unresolved CRITICAL/HIGH finding remains.
- Any contract conflict routes through plan mutation instead of being hidden.
- Council verdict is recorded.

### Rollback

No code edits occur in this step. If the council requires reopening, restore only the owning step’s files through that step’s rollback plan.

### Handoff

If PROCEED, Step 11 performs compatibility/UI approval.

## Step 11 — Compatibility and UI approval gate

### Purpose

Confirm optimized internals did not alter Streamlit, Tkinter, diagnostics, or frozen compatibility.

### Cold-start context

Phase 3 defaults to no UI changes. Browser QA and accessibility are required only if UI files changed or performance options were exposed.

### Touched files

- `plans/phase-3-execution-log.md`
- `docs/phase_3_benchmark_results.md`
- UI fixtures only if a separately approved UI mutation exists

### Preconditions

- Step 10 council verdict is PROCEED.

### Tasks

1. Run full regression baseline and both diagnostics.
2. Verify frozen fixture hashes.
3. Verify root research files are not imported at runtime.
4. If UI touched: run `ecc:browser-qa`, then `ecc:accessibility`, create/update UI fixture only under approved mutation, and stop for human approval.
5. If UI untouched: record that browser/accessibility gates are not required and preserve frozen Streamlit behavior.

### Verification

```powershell
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"
```

Optional UI verification only if UI changed:

```powershell
streamlit run category_tracking_web.py --server.headless true
```

### Exit criteria

- Human compatibility/UI approval is recorded if required.
- Otherwise explicit evidence shows UI was untouched and frozen UI tests pass.

### Rollback

Restore only files touched by the optimization steps that caused compatibility drift.

### Handoff

Step 12 performs final documentation and delivery.

## Step 12 — Final documentation, registration, and delivery gate

### Purpose

Package Phase 3 evidence for final review and optional commit authorization.

### Cold-start context

This step does not introduce optimization logic. It records what changed, why it is safe, and how to verify it.

### Touched files

- `README.md`
- `engine/README.md`
- `docs/phase_3_benchmark_results.md`
- `plans/phase-3-execution-log.md`

### Preconditions

- Step 11 approval complete.

### Tasks

1. Document approved Phase 3 optimization behavior and benchmark interpretation.
2. Confirm no public contract changed unless approved.
3. Record final touched-file manifest and hashes.
4. Run final full verification.
5. Use `ecc:delivery-gate` for final readiness review.
6. Present proposed commit messages, but do not commit unless the user authorizes it.

### Verification

```powershell
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"
python tools/benchmark_phase3.py --all
git status --short
```

### Exit criteria

- Final delivery report is complete.
- No unresolved CRITICAL/HIGH findings remain.
- User is asked whether to commit and push.

### Rollback

Use each owning implementation step’s rollback instructions. Documentation-only rollback restores docs/log/README files.

### Handoff

Recommended conventional commit if approved:

```text
perf: optimize codon computation behind Phase 2 contracts
```

If Step 1 only fixed clean-repo packaging tests, use a separate commit:

```text
test: align boundary tests with clean application repository
```

## Approval gates

1. Phase 2 revalidation gate — before any optimization.
2. Benchmark methodology approval gate — after Step 2.
3. Dependency/contract approval gate — before NumPy/SciPy, transition matrices, new optimized APIs, automatic mode switching, or UI exposure.
4. Optimization equivalence gate — Step 10 strongest-model review and council.
5. Compatibility/UI gate — Step 11, including browser QA/accessibility only if UI changes.
6. Final delivery/Gate 2 — Step 12.

## Anti-pattern catalog

Do not:

- optimize before a green Phase 2 baseline;
- use timing as proof of scientific correctness;
- weaken tests, tolerances, seeds, fixtures, or diagnostics after a failure;
- change exact floating-point iteration order accidentally;
- change detailed sampled RNG or final module-global random state;
- replace detailed sampled or aggregated sampled APIs silently;
- call probability weights integer counts;
- duplicate codon tables, mutation matrices, property mappings, or simulation loops;
- add NumPy/SciPy without dependency approval;
- use generation-major or vectorized sampled draws as a replacement for reducer-equivalent aggregate sampling;
- expose optimized or aggregated modes in Streamlit without a separate UI contract;
- add FastAPI, Next.js, workers, queues, databases, deployment, authentication, or export infrastructure;
- modify original root research files;
- commit or push without explicit authorization.

## Plan-mutation protocol

Use this protocol for any required change to this Blueprint:

1. State the evidence that makes the current plan insufficient.
2. Identify affected contracts, public APIs, files, fixtures, and tests.
3. Classify the mutation as split, insert, reorder, scope expansion, scope reduction, dependency change, contract change, or abandonment.
4. Propose the smallest safe amendment.
5. Run read-only impact analysis.
6. Request explicit human approval.
7. Update this Blueprint and the Phase 3 execution log before implementation.
8. Add or update focused failing tests.
9. Implement only after approval.
10. Run full verification and record evidence.

No implementation-first contract changes are allowed.

## Adversarial review requirements

Step 10 must include a strongest-model read-only review. The reviewer must inspect:

- exact scientific equivalence;
- float/order preservation;
- Phase 2 table schemas and dataclass contracts;
- denominator and zero-case behavior;
- detailed sampled RNG behavior;
- aggregated reducer equivalence;
- structural memory bounds;
- benchmark methodology and interpretation;
- statistical calibration methodology;
- UI and adapter compatibility;
- dependency and scope boundaries.

Every finding must include severity, evidence, affected file/contract, owning step, consequence, and required disposition. CRITICAL and HIGH findings block progress.

## Unresolved decisions requiring human approval

| Decision | Recommended default | Approval point |
| --- | --- | --- |
| Clean-repo boundary test repair | Update the test to reflect that `CLAUDE.md` is intentionally excluded from the deployable app repo | Step 1 |
| Benchmark result storage | Store concise Markdown results in `docs/phase_3_benchmark_results.md`; avoid large generated artifacts | Step 2 |
| Performance thresholds | Do not set hard thresholds until after baseline measurements | Step 2 |
| NumPy/SciPy dependency | Do not add by default; evaluate only through dependency gate | Step 6 |
| Matrix/transition model | Research only first; implement only if contract/dependency gate approves | Step 6 |
| New optimized sampled algorithm | Do not replace `run_aggregated_experiment`; add only as a separately contracted experimental API if approved | Step 8 or mutation gate |
| UI exposure of performance options | Default no UI changes | Step 11 or mutation gate |
| Commit/push | Do not commit or push until user authorizes | Step 12 |

## Completion checklist for this Blueprint

- [x] Phase 3 limited to optimization, scalability, and maintainability.
- [x] Phase 2 contracts remain authoritative.
- [x] Clean repo is canonical.
- [x] Current clean-repo baseline issue is recorded.
- [x] Benchmark methodology precedes implementation.
- [x] Exact optimization starts with profiling and derived-table work, not algorithm rewrite.
- [x] Matrix/NumPy/SciPy work requires approval.
- [x] Aggregated sampled optimization preserves reducer equivalence by default.
- [x] UI changes are excluded by default.
- [x] Every step includes touched files, preconditions, tasks, verification, exit criteria, rollback, and handoff.
- [x] Dependency graph, anti-pattern catalog, mutation protocol, adversarial review, approval gates, and unresolved decisions are included.
- [x] No Phase 3 code is implemented by this Blueprint.
