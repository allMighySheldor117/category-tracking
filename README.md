# Codon Category Tracking Lab

This directory is the canonical, self-contained application produced by Phase 2. It contains the UI-independent scientific engine, the existing Streamlit and Tkinter interfaces, compatibility tests, frozen fixtures, and Streamlit configuration.

## Run

Run commands from this directory:

```powershell
streamlit run category_tracking_web.py
python category_tracking.py
```

The Streamlit app imports scientific behavior directly from `engine/`. The Tkinter entry point remains a compatibility adapter: its historical public functions and tuple results are preserved while their implementations delegate to the engine.

Exact probability is the authoritative deterministic scientific path. New scientific callers should use `run_exact_analysis` and the named exact query APIs exported from `engine`. The Streamlit UI still preserves its frozen labels, including `Sampled copies` and `Exact probability`, for compatibility.

Detailed sampled simulation remains the frozen legacy experimental path through `run_experiment`. Phase 2 also adds `run_aggregated_experiment` as an explicit engine-only experimental API for memory-safe sampled summaries. It is not exposed through a Streamlit widget and there is no automatic sampled-mode threshold.

## Verify

```powershell
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"
```

The JSON files in `tests/fixtures/` and both diagnostic scripts are frozen compatibility oracles. Tests never regenerate them. Same-process exact comparisons require identical structure, insertion order, concrete containers, and `float.hex()` values. Sampled comparisons require identical records, paths, draw order, and final `random.getstate()`.

## Structure

```text
engine/
  genetic_code.py       biological definitions and grouping helpers
  mutation_matrix.py    probability presets and substitution mappings
  models.py             named exact and sampled result dataclasses
  exact_tracking.py     exact probability propagation
  sampled_tracking.py   sampled per-copy paths using module-level random
  aggregated_tracking.py
                         sampled per-generation counters with local RNG
  exact_analysis.py     authoritative exact analysis and scoped tables
  comparisons.py        directed exact/sample comparison contracts
  invariants.py         scientific invariant reports and errors
  category_analysis.py  category, trait, fraction, and denominator tables
  summaries.py          stop, convergence, outcome, and population summaries
category_tracking.py    legacy Tkinter and tuple compatibility boundary
category_tracking_web.py
                         Streamlit UI and Plotly presentation
tests/                   focused, compatibility, boundary, and UI tests
.streamlit/config.toml   visual theme
```

See `engine/README.md` for the engine API and scientific contracts.

## Phase 2 scientific surface

- `run_exact_analysis` calls the unchanged exact propagation once and returns named probability-weight tables for category metrics, survivor fractions, survival, stop outcomes, codon outcomes, convergence, and comparisons.
- `build_exact_analysis` derives the same authoritative surface from an existing exact result plus explicit starting weights after provenance validation.
- `run_aggregated_experiment` keeps bounded integer counters by generation, not individual histories. It uses an explicit local seed and leaves the detailed sampled module-global RNG contract untouched.
- `compare_numeric_metric`, `compare_convergence`, and `compare_exact_to_sampled` provide typed comparison outputs. Exact-vs-sampled calibration uses Wilson intervals with Bonferroni family correction and treats sampled values as experimental estimates.
- Denominators and zero behavior are documented in `engine/README.md` and `docs/phase_2_scientific_contract.md`. Exact values are probability weights; sampled values are integer copy counts; displayed percentages are presentation only.

## Boundary rules

- `engine/` never imports Streamlit, Tkinter, Plotly, PyQt, CSS, HTML, or UI colors.
- Biological tables and simulation loops have one production definition under `engine/`.
- New consumers use `ExactSimulationResult` and `SampledSimulationResult`; positional tuples exist only at explicit legacy/cache boundaries.
- New Phase 2 consumers use named result dataclasses and public `engine` exports. Positional tuple indexes are not used in new APIs.
- Engine functions raise errors directly. UI adapters own user-facing validation messages.
- Every application/runtime artifact stays under this directory. Root application files are read-only research references.

## Deferred work

Phase 2 intentionally does not change probability validation, optimize/vectorize the exact algorithm, redesign caching, expose aggregated sampling in Streamlit, or add the planned API, frontend, job queue, persistence, exports, authentication, or deployment architecture. Phase 3 may optimize only behind the approved exact and sampled contracts and must prove equivalence independently.

## Phase 4 local API

Install the approved Phase 4 API dependencies, then run the local FastAPI adapter:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn api.main:app --reload
```

The initial service exposes `GET /health` and `GET /api/v1/metadata`. Simulation and comparison endpoints are added by later Phase 4 implementation steps.
