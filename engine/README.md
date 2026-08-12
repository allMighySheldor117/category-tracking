# Scientific Engine

`engine` is the UI-independent scientific core for Codon Category Tracking Lab. Phase 2 registers the public scientific surface through `engine.__all__` while keeping implementation helpers module-scoped.

## Modules and APIs

- `genetic_code`: `BASES`, `STOP_CODONS`, `CODON_TABLE`, `AA_FULL`, `VALID_CODONS`, `ALL_AAS`, `AA_PROPERTIES`, `PROPERTY_LABELS`, `AA_AROMATIC`, `AA_SMALL`, codon-count mappings, and typed grouping/count helpers.
- `mutation_matrix`: `PRESET_AT`, `PRESET_AG`, `PRESET_AC`, and `build_substitution_matrix`.
- `exact_tracking`: `run_simulation(...) -> ExactSimulationResult`; this is the unchanged exact propagation primitive.
- `exact_analysis`: `run_exact_analysis(...) -> ExactAnalysisResult`, `build_exact_analysis(...) -> ExactAnalysisResult`, and scoped exact queries for category metrics, survivor fractions, survival, stop outcomes, codon outcomes, and convergence.
- `sampled_tracking`: `run_experiment(...) -> SampledSimulationResult`; this is the frozen detailed sampled compatibility primitive.
- `aggregated_tracking`: `run_aggregated_experiment(...) -> AggregatedSampledResult` using explicit local seeding and bounded per-generation counters.
- `category_analysis`: sampled/exact category, all-population, starting-trait, trait-codon, trait-amino-acid, surviving-fraction, survival-balance, and trait-summary tables.
- `summaries`: stop series, named convergence/no-more-change results, all-codon status, explicit sampled/exact codon outcome tables, property stop totals, and named starting/final population metrics.
- `comparisons`: `compare_numeric_metric`, `compare_convergence`, and `compare_exact_to_sampled`.
- `invariants`: biological, mutation-matrix, and exact-analysis invariant reports.

`ExactSimulationResult` names the historical exact result fields: `enc_codon`, `enc_aa`, `enc_codon_cnt`, `enc_aa_cnt`, `fin_codon`, `fin_aa`, `per_gen_aa`, `start_to_fin`, `stats`, `stop_data`, and `track_data`.

`SampledSimulationResult` names `records`, `sample_fin_codon`, `sample_fin_aa`, and `sample_start_to_fin`.

`ExactAnalysisResult` owns the authoritative Phase 2 exact surface. It carries the unchanged `ExactSimulationResult`, the canonical starting weights, and eager population tables. Scoped exact query functions return canonical DataFrames for codon, amino-acid, trait, stop, outcome, convergence, and comparison work.

`AggregatedSampledResult` owns the explicit sampled aggregate surface. It retains `AggregatedGenerationCounts` snapshots, normalized start counts, final live counters, stop counters, the required seed, generation count, and total starting count. No per-copy records, paths, copy identifiers, per-copy final objects, or individual stop-generation records are retained. The joint `new_stop_codon_by_start_codon` counter is bounded by valid starting codons and the three canonical stops.

`ComparisonResult`, `ConvergenceComparisonResult`, and `ExactSampledComparisonResult` name the approved comparison outputs. `compare_exact_to_sampled` uses Wilson score intervals with Bonferroni family correction; exact probability is the deterministic reference and sampled output is an experimental estimate.

`ConvergenceResult` names `generation` and `max_delta`. `NoMoreChangeResult` names the generation label and status. Their legacy tuple conversions are used only by compatibility adapters.

`to_legacy_tuple()` and `from_legacy_tuple()` are compatibility boundaries. New scientific and UI code uses named fields.

## Preservation policy

The exact algorithm intentionally retains its historical loop and accumulation order. Same-process comparisons require exact nested container order and identical `float.hex()` values; tolerances are reserved for explicitly reviewed external fixtures. `run_exact_analysis` calls that primitive once and derives authoritative tables from the named result without rewriting the propagation loop.

The detailed sampled algorithm intentionally uses Python's module-level `random` generator. It preserves start-codon order, `randint` then `choices` draw order, early-stop behavior, per-copy paths, copy numbering, consecutive-call behavior, and final `random.getstate()`.

The aggregated sampled algorithm is separate. It requires an explicit integer seed, constructs a local `random.Random(seed)`, preserves detailed-compatible copy-major draw order for reducer-equivalence tests, and never mutates module-global random state. It summarizes integer counts by generation rather than retaining detailed histories.

## Denominators

| Output | Basis | Zero behavior |
|---|---|---|
| Surviving category fraction | Category survivors divided by all non-stop survivors at that generation | `0.0` when no survivors remain |
| Starting-trait stop percentage | Cumulative stops from a starting trait divided by initial copies/weight in that trait | `0.0` when the starting total is zero |
| Survival balance | Surviving count/weight; stopped is `max(0, start - surviving)` | Existing clipping is preserved |
| Trait-codon stop fraction | Starting copies per codon minus final survivors, divided by copies per codon | `0.0` when copies per codon is zero |
| Trait codon/AA survival | Absolute survivors originating from the selected starting trait/codon/AA | Stable empty schemas are preserved |
| No-more-change count basis | Current and every later category-count vector within tolerance `1.0` | Preserves `all stopped` status |
| No-more-change fraction basis | Current and every later surviving-category fraction vector within `alpha` | Preserves the zero-survivor vector |
| Exact category metrics | Live probability weight from the explicit starting weights | Zero-valued categories remain present where the canonical table contract requires them |
| Exact stop outcomes | New and cumulative stop probability weight divided by the actual positive starting weight for the scope | `0.0` fractions when the eligible starting weight is zero |
| Aggregated sampled survival | Live and stopped integer counts divided by normalized sampled start counts, `max(0, int(weight))` | `0.0` fractions when no eligible sampled copies exist |
| Exact-vs-sampled calibration | Exact and sampled fractions aligned to the same denominator scope | Nullable sampled/error/interval fields when `sample_size == 0` |

## Canonical tables

Phase 2 canonical tables use a zero-based `RangeIndex`, 1-based post-mutation generations, documented column order, and explicit pandas dtypes. Exact tables store probability weight with `value_kind="probability_weight"`. Aggregated tables store integer copy counts with `value_kind="copy_count"`. Presentation layers may format percentages, but engine tables keep fractions in `[0, 1]`.

The authoritative table families are category metrics, survivor fractions, survival by start, stop outcomes, codon outcomes, convergence, directed numeric comparison, convergence/status comparison, and exact-vs-sampled calibration. See `../docs/phase_2_scientific_contract.md` for the complete schema and error contract.

## Dependency boundary

Pandas is allowed in analysis and summary modules. Engine modules must not import Streamlit, Tkinter, Plotly, PyQt, HTML/CSS, or presentation colors. Errors stay explicit in the engine; UI adapters translate expected errors into concise messages.

## Verification

From `final code/`:

```powershell
python -m unittest discover -s tests -p "test_*.py"
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"
```

Frozen fixtures and diagnostics are reviewed inputs and must never be regenerated or weakened to accept a refactor.
