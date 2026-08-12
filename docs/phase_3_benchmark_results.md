# Phase 3 Benchmark Results

Status: Baseline captured — advisory measurements only.

## Environment

- python: `3.13.0 (tags/v3.13.0:60403a5, Oct  7 2024, 09:38:07) [MSC v.1941 64 bit (AMD64)]`
- platform: `Windows-11-10.0.26200-SP0`
- processor: `Intel64 Family 6 Model 140 Stepping 1, GenuineIntel`
- pandas: `2.2.3`
- streamlit: `1.60.0`

## Baseline observations

| benchmark_name | benchmark_family | generations | copies_or_weights | seed | warmups | repeats | median_seconds | min_seconds | max_seconds | advisory_peak_bytes | structural_cardinality | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exact_single_codon_small | exact | 5 | {'TGG': 1.0} | not_applicable | 1 | 3 | 0.076449 | 0.069915 | 0.077887 | 169814 | not_applicable | measured |
| exact_single_codon_medium | exact | 25 | {'TGG': 1.0} | not_applicable | 1 | 3 | 0.349191 | 0.330077 | 0.421292 | 526000 | not_applicable | measured |
| exact_all_codon_small | exact | 5 | None | not_applicable | 1 | 3 | 3.165238 | 3.129468 | 3.168810 | 2782912 | not_applicable | measured |
| exact_repeated_queries | exact | 15 | {'AAA': 1.0, 'TGG': 1.0} | not_applicable | 1 | 3 | 0.515711 | 0.472216 | 0.519881 | 521477 | not_applicable | measured |
| aggregated_small | aggregated | 10 | {'AAA': 100, 'TGG': 100} | 2718 | 1 | 3 | 0.061056 | 0.057723 | 0.063954 | 392868 | snapshots=10; nested_counter_slots=41250; conservation_ok=True | measured |
| aggregated_medium | aggregated | 10 | {'AAA': 1000, 'TGG': 1000} | 314159 | 1 | 3 | 0.234351 | 0.231892 | 0.257279 | 436288 | snapshots=10; nested_counter_slots=41250; conservation_ok=True | measured |
| comparison_numeric | comparison | 5 | {'AAA': 1.0, 'TGG': 1.0} | not_applicable | 1 | 3 | 0.421541 | 0.396077 | 0.439597 | 457101 | not_applicable | measured |
| calibration_exact_sampled | calibration | 5 | {'AAA': 100, 'TGG': 100} | 8675309 | 1 | 3 | 0.212503 | 0.199417 | 0.215167 | 393451 | not_applicable | measured |

## Interpretation

These observations are a Phase 2 reference baseline for Phase 3. They do not define a runtime SLA and do not prove scientific correctness. Correctness remains owned by regression tests, diagnostics, exact equivalence, RNG preservation, reducer equivalence, and conservation checks.
