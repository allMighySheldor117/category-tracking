# Phase 3 Aggregated Sampled Profile

## Status

Complete — profile captured; no optimization implemented.

## Scope

This profile evaluates Phase 3 Step 7 only: aggregated sampled execution. It separates advisory runtime observations from the authoritative structural memory contract.

No production code changed. `engine.aggregated_tracking.run_aggregated_experiment` remains the Phase 2 explicit experimental aggregated sampled API.

## Benchmark harness observations

Command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python tools/benchmark_phase3.py
```

Aggregated rows from the harness:

| benchmark | generations | start weights | seed | median seconds | advisory peak bytes | structural cardinality |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| `aggregated_small` | 10 | `{"AAA": 100, "TGG": 100}` | 2718 | 0.077165 | 392868 | `snapshots=10; nested_counter_slots=41250; conservation_ok=True` |
| `aggregated_medium` | 10 | `{"AAA": 1000, "TGG": 1000}` | 314159 | 0.265019 | 436288 | `snapshots=10; nested_counter_slots=41250; conservation_ok=True` |

These are advisory local observations only. They are not a runtime SLA.

## Aggregated-only profiling probe

Command shape:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -c "<aggregated-only profiling probe>"
```

| case | generations | total start count | seed | elapsed seconds | advisory peak bytes | snapshots | nested counter slots | conservation | retains paths/records |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `copies_small` | 10 | 200 | 2718 | 0.049313 | 396706 | 10 | 41250 | true | false |
| `copies_medium` | 10 | 2000 | 314159 | 0.208108 | 436256 | 10 | 41250 | true | false |
| `copies_larger` | 10 | 10000 | 8675309 | 1.088537 | 442712 | 10 | 41250 | true | false |
| `generations_medium` | 25 | 2000 | 2718 | 0.363477 | 1103404 | 25 | 103125 | true | false |

The probe confirmed module-global RNG state was unchanged.

## Interpretation

Copy-count scaling:

- Runtime increases with copy count, as expected for copy-major streaming.
- Retained structural cardinality did not grow when total start count increased from 200 to 10,000 at the same generation count.
- Integer magnitudes grow with copy count, but retained collection shape remains bounded.

Generation-count scaling:

- Snapshot count grows with generation count.
- Bounded counter slots grow with generation count and finite biological state dimensions.
- This matches the Phase 2 structural memory contract.

CPU/runtime observations:

- The current algorithm remains copy-major.
- Runtime likely concentrates in per-copy generation loops, `randint`/`choices` calls, transition lookup, codon string reconstruction, counter updates, and generation result freezing.
- Step 7 does not prove which micro-operation dominates; it identifies safe areas for Step 8 investigation.

Structural memory verdict:

PASS.

The aggregated result does not retain:

- individual copy records;
- mutation paths;
- copy IDs;
- per-copy final records;
- individual stop-generation records.

## Safe Step 8 candidates

Step 8 may evaluate internal aggregated sampled optimization under TDD, but only while preserving reducer equivalence and RNG behavior.

Candidates:

1. Reduce repeated transition tuple lookups where key order remains identical.
2. Reduce repeated category/trait lookup overhead with local variables derived from existing single-source biological definitions.
3. Simplify counter-freezing loops without changing canonical ordering.
4. Avoid redundant summations during result freezing if exact nested counters remain the source of truth.
5. Keep copy-major iteration, `randint` then `choices`, local `random.Random(seed)`, and early-stop semantics unchanged.

Do not:

- introduce generation-major execution;
- vectorize random draws;
- add NumPy/SciPy;
- replace `run_aggregated_experiment`;
- add automatic sampled-mode thresholds;
- expose aggregated optimization in Streamlit.

