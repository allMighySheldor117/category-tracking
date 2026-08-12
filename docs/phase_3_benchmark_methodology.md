# Phase 3 Benchmark Methodology

## Status

Proposed — awaiting Benchmark Methodology approval.

## 1. Purpose and authority

Phase 3 optimizes computation behind the approved Phase 2 contracts. Benchmarks provide comparable engineering evidence, but they do not redefine scientific correctness.

Scientific correctness is proven by:

- Phase 2 regression tests;
- frozen diagnostics and fixtures;
- exact output equivalence;
- canonical schema, dtype, index, and ordering equality;
- detailed sampled RNG preservation;
- aggregated sampled reducer equivalence;
- conservation invariants;
- UI-independent engine import checks.

Timing and advisory memory observations may guide optimization priorities. They are not acceptance criteria unless a later approved contract explicitly promotes a structural condition into a gate.

No hard runtime threshold is approved by this methodology. Step 3 captures the baseline first.

## 2. Environment recording

Every benchmark report must record:

| Field | Required value |
| --- | --- |
| UTC timestamp | ISO-8601 UTC timestamp at benchmark start and finish |
| Repository path | Absolute clean-repo path |
| Git branch | Current branch |
| Git commit | Current commit hash and subject |
| Working tree state | `git status --short` before and after |
| OS/platform | `platform.platform()` |
| CPU | `platform.processor()` when available |
| Python | `sys.version` |
| pandas | `pandas.__version__` |
| Streamlit | `streamlit.__version__` |
| Shell | PowerShell command invocation |
| Bytecode policy | `PYTHONDONTWRITEBYTECODE=1` |
| Dependency changes | Must be `none` unless separately approved |

Environment observed while proposing this methodology:

| Field | Observed value |
| --- | --- |
| Python | `3.13.0 (tags/v3.13.0:60403a5, Oct 7 2024, 09:38:07) [MSC v.1941 64 bit (AMD64)]` |
| Platform | `Windows-11-10.0.26200-SP0` |
| Processor | `Intel64 Family 6 Model 140 Stepping 1, GenuineIntel` |
| pandas | `2.2.3` |
| Streamlit | `1.60.0` |

Step 3 must re-record these values at measurement time rather than relying on this proposal-time snapshot.

## 3. Deterministic benchmark workloads

Use a fixed substitution matrix for every benchmark family unless a benchmark explicitly states otherwise. The default fixed matrix should be produced by the existing `build_substitution_matrix` API with one documented probability set. Step 3 must record the exact probabilities used.

### 3.1 Exact single-codon runs

| Size | Start weights | Generations | Purpose |
| --- | --- | ---: | --- |
| Small | `{"TGG": 1.0}` | 5 | quick correctness and overhead signal |
| Medium | `{"TGG": 1.0}` | 25 | exact propagation and table construction signal |
| Larger safe | `{"TGG": 1.0}` | 75 | larger-generation exact behavior without unsafe runtime |

### 3.2 Exact all-codon population runs

| Size | Start weights | Generations | Purpose |
| --- | --- | ---: | --- |
| Small | default all sense codons | 5 | full canonical ordering signal |
| Medium | default all sense codons | 15 | population table construction signal |
| Larger safe | default all sense codons | 35 | all-codon scaling signal |

### 3.3 Repeated exact table construction

For one already-built `ExactAnalysisResult`, repeatedly query:

- category metrics;
- survivor fractions;
- survival by start;
- stop outcomes;
- codon outcomes;
- convergence.

Use repeat families of 1, 10, and 50 query cycles. This isolates derived-table/query overhead from exact propagation.

### 3.4 Large generation exact runs

Use sparse starts only to keep runtime safe:

| Size | Start weights | Generations |
| --- | --- | ---: |
| Medium | `{"AAA": 1.0, "TGG": 1.0}` | 100 |
| Larger safe | `{"AAA": 1.0, "TGG": 1.0}` | 250 |

If a run exceeds the approved timeout safety policy, record it as skipped with the observed reason rather than raising thresholds mid-run.

### 3.5 Aggregated sampled runs

Use explicit local seeds. Suggested seed panel:

- `2718`
- `314159`
- `8675309`

| Size | Start weights | Generations | Purpose |
| --- | --- | ---: | --- |
| Small | `{"AAA": 100, "TGG": 100}` | 10 | reducer-equivalence and low-cost timing |
| Medium | `{"AAA": 1_000, "TGG": 1_000}` | 10 | copy-count scaling |
| Larger safe | `{"AAA": 10_000, "TGG": 10_000}` | 10 | structural memory and advisory runtime |
| Generation scaling | `{"AAA": 1_000, "TGG": 1_000}` | 50 | generation-count scaling |

Step 3 may lower the larger safe copy count if the environment risks exhaustion. Any reduction must be recorded before measuring.

### 3.6 Comparison and calibration workloads

Benchmark:

- directed numeric comparisons for category fraction, survivor fraction, stop fraction, and codon live value;
- convergence comparisons for stable, no-convergence, and all-stopped cases;
- exact-versus-sampled calibration using the approved Phase 2 fixed seed panel and predeclared sample sizes.

No benchmark may search for favorable seeds or weaken confidence parameters.

## 4. Measurement policy

### Warm-up

Run one warm-up call for each benchmark case when the case is safe and completes within timeout. Do not include warm-up observations in reported median/min/max values.

### Repeats

Default repeat count:

- 5 repeats for small and medium workloads;
- 3 repeats for larger safe workloads;
- 1 repeat for a workload explicitly marked expensive after methodology approval.

Any repeat-count reduction must be recorded with the reason before measuring.

### Timing

Use `time.perf_counter()` around the smallest meaningful operation:

- exact propagation only;
- exact analysis construction;
- scoped table query cycle;
- aggregated sampled call;
- comparison call;
- full calibration panel.

Report seconds with enough precision to compare runs, usually six decimal places.

For every case report:

- median;
- minimum;
- maximum;
- repeat count;
- warm-up count;
- skipped/timeout status if applicable.

### Advisory memory

Use `tracemalloc` where practical. Run memory measurements separately from timing measurements to avoid mixing instrumentation overhead with timing.

Report:

- current memory after operation;
- peak memory during operation;
- input size;
- retained result cardinality when applicable.

Memory figures are advisory and environment-dependent.

### Structural memory checks

Structural checks are authoritative for aggregated sampled memory safety:

- `AggregatedSampledResult` must not retain records, paths, copy IDs, per-copy final records, or individual stop-generation records.
- Snapshot count may grow only with generation count.
- Counter key cardinality may grow only with finite biological dimensions.
- Integer magnitudes may grow with copy count.
- Retained collection cardinality must not grow with copy count except where generations or biological state dimensions grow.

### Timeout safety

Each individual benchmark case should have a predeclared timeout budget. A suggested default is:

- 30 seconds for small/medium cases;
- 120 seconds for larger safe cases.

Timeouts do not fail scientific correctness. They mark a case as too expensive for the current environment and should guide scope decisions.

## 5. Correctness gates

Every benchmarked optimization must preserve:

- `python -m unittest discover -s tests -p "test_*.py"`;
- `python diagnose_category_tracking_web.py`;
- `python -m tests.compat.diagnose_category_tracking_web_phase1_baseline`;
- fresh-process engine import without `streamlit`, `tkinter`, `plotly`, or `PyQt5`;
- frozen diagnostic hashes;
- frozen fixture hashes;
- exact `float.hex()` equality where Phase 2 tests require it;
- DataFrame column, dtype, index, row, key, and empty-result equality;
- denominator and zero-case behavior;
- detailed sampled module-global RNG behavior;
- aggregated sampled local-seed repeatability and global-RNG isolation;
- detailed-reducer equivalence for compact reviewed aggregate cases;
- conservation of exact probability mass and sampled integer counts.

Correctness must pass before benchmark observations are interpreted.

## 6. Exact benchmark methodology

Exact benchmarks must separate:

1. `run_simulation` propagation cost;
2. `run_exact_analysis` total cost;
3. `build_exact_analysis` derivation cost from an existing simulation;
4. scoped exact query cost;
5. repeated table construction cost.

Every exact optimization benchmark must compare against the Phase 2 reference behavior using:

- same-process value equality;
- `float.hex()` equality for covered exact outputs;
- schema/dtype/index/order equality for DataFrames;
- provenance validation behavior;
- zero-generation and sparse-start behavior;
- all-codon population behavior.

Do not rewrite exact propagation first. Do not introduce matrix or NumPy/SciPy behavior without the Step 6 dependency/contract gate.

## 7. Aggregated sampled benchmark methodology

Aggregated sampled benchmarks must record:

- requested start weights;
- normalized sampled start counts using `max(0, int(weight))`;
- seed;
- generation count;
- total start count;
- snapshot count;
- retained top-level collection cardinality;
- retained nested counter cardinality;
- total live plus cumulative stopped conservation by generation;
- advisory elapsed time;
- advisory peak memory.

For compact cases, compare aggregate output against the canonical detailed-record reducer for:

- every generation;
- live codon counters;
- live amino-acid counters;
- live category counters;
- start-codon counters;
- start-trait counters;
- current codon by starting codon;
- new stops by stop codon;
- new stops by starting codon;
- new stops by starting trait;
- `new_stop_codon_by_start_codon`;
- final counters;
- totals;
- ordering.

Aggregated benchmarks must prove:

- same seed gives identical aggregate results;
- different seeds are allowed to differ;
- global module-level random state is unchanged;
- no per-copy records, paths, or identifiers are retained.

Do not use generation-major random draws, vectorized random-count algorithms, or automatic mode switching as replacements for the Phase 2 aggregate API.

## 8. Comparison and calibration benchmark methodology

Comparison benchmarks must keep statistical correctness separate from runtime.

Measure:

- `compare_numeric_metric`;
- `compare_convergence`;
- `compare_exact_to_sampled`;
- full approved calibration panel.

Correctness must preserve:

- Wilson score interval formula;
- Bonferroni-adjusted familywise alpha;
- nullable behavior when sample size is zero;
- `p=0` and `p=1` behavior;
- family-size handling;
- directed signed-delta semantics;
- relative-delta `pd.NA` behavior at zero baseline;
- no seed searching;
- no tolerance weakening.

Calibration benchmark output may report pooled RMSE and interval coverage, but a legitimate statistical rejection must pause for human scientific review rather than changing seeds or thresholds.

## 9. Reporting format

Step 3 benchmark reports should use this table format:

| Field | Meaning |
| --- | --- |
| benchmark_name | Stable identifier |
| benchmark_family | `exact`, `aggregated`, `comparison`, or `calibration` |
| input_case | Human-readable input description |
| generations | Number of post-mutation generations |
| copies_or_weights | Start weights or sampled copy counts |
| seed | Seed or `not_applicable` |
| warmups | Warm-up count |
| repeats | Measured repeat count |
| median_seconds | Median elapsed seconds |
| min_seconds | Minimum elapsed seconds |
| max_seconds | Maximum elapsed seconds |
| advisory_peak_bytes | `tracemalloc` peak when measured |
| structural_cardinality | Retained collection/cardinality summary |
| correctness_command | Verification command proving scientific safety |
| status | `measured`, `skipped`, or `timeout` |
| notes | Constraints, environment caveats, or skip reason |

Benchmark reports must include a narrative summary that says what can and cannot be concluded. Avoid a single composite performance score.

## 10. Approval gate

This methodology is proposed only.

Before Step 3 starts, the user must explicitly approve:

- benchmark workload families;
- warm-up and repeat policy;
- advisory memory policy;
- absence of hard runtime thresholds before baseline capture;
- reporting format;
- any reduced larger-safe workload needed for the local machine.

Do not mark this methodology approved until the user explicitly approves it.

