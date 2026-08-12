# Phase 3 Exact-Probability Hot-Path Profile

Status: Profile captured — no optimization implemented.

## Scope

This profile separates exact propagation, exact analysis construction, and repeated derived-table query work using the Phase 3 benchmark harness.

## Exact observations

| benchmark_name | benchmark_family | generations | copies_or_weights | seed | warmups | repeats | median_seconds | min_seconds | max_seconds | advisory_peak_bytes | structural_cardinality | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exact_all_codon_small | exact | 5 | None | not_applicable | 1 | 3 | 3.073141 | 2.990876 | 3.428010 | 2782912 | not_applicable | measured |
| exact_repeated_queries | exact | 15 | {'AAA': 1.0, 'TGG': 1.0} | not_applicable | 1 | 3 | 0.486996 | 0.486018 | 0.499331 | 521577 | not_applicable | measured |
| exact_single_codon_medium | exact | 25 | {'TGG': 1.0} | not_applicable | 1 | 3 | 0.442403 | 0.420007 | 0.455436 | 525908 | not_applicable | measured |
| exact_single_codon_small | exact | 5 | {'TGG': 1.0} | not_applicable | 1 | 3 | 0.111369 | 0.101590 | 0.161746 | 169118 | not_applicable | measured |

## Hot-path findings

- `run_exact_analysis` includes the unchanged exact propagation primitive plus eager population table construction.
- Repeated scoped queries exercise DataFrame construction, Counter/dict iteration, canonical ordering, and provenance-derived state.
- The highest median exact observations should guide Step 5, but only behind Phase 2 table and float-order equivalence tests.

## Safe Step 5 candidates

1. Reduce repeated derived-table construction where inputs are already represented by one `ExactAnalysisResult`.
2. Share internal schema/table helpers without changing public DataFrame contracts.
3. Cache or reuse pure derived structures only when ownership and mutation safety are explicit.
4. Leave `engine.exact_tracking.run_simulation` untouched unless a later contract gate approves a dual reference/optimized path.
