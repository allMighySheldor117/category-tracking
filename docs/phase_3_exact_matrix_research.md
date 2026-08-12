# Phase 3 Exact Matrix / Transition-Model Research

## Status

Complete — no new contract recommended now.

## Decision summary

Phase 3 should keep the current exact algorithm as the authoritative reference path and continue pure-Python internal optimization by default.

Do not add NumPy, SciPy, transition matrices, or a new optimized exact API yet.

Reason: current Phase 3 evidence shows useful improvement is still possible behind the existing Phase 2 exact-analysis contracts, and a matrix/array implementation would create non-trivial equivalence risk around floating-point order, stop accounting, sparse starts, and canonical table semantics. The cost/risk tradeoff does not yet justify a dependency or public-contract change.

If matrix, NumPy, or SciPy work is pursued later, it should be introduced only as a separately approved experimental optimized exact path compared against the trusted Phase 2/3 reference path. It must not silently replace `run_exact_analysis` or `run_simulation`.

## 1. Current exact algorithm

The current exact path is:

1. `engine.exact_tracking.run_simulation(...)`
2. `engine.exact_analysis.run_exact_analysis(...)`
3. scoped exact table/query functions in `engine.exact_analysis`

`run_simulation` is the trusted exact propagation primitive. It propagates probability weight through codon mutation states in Python containers with stable ordering. Its output is wrapped in `ExactSimulationResult` and then transformed into the approved Phase 2 scientific tables.

Why it is trusted:

- Phase 1 froze the exact primitive against historical scientific behavior.
- Phase 2 made exact probability the authoritative deterministic scientific path.
- Tests protect same-process float behavior, container order, DataFrame schemas, denominators, zero behavior, and compatibility boundaries.
- Phase 3 Step 5 optimized only derived-table reuse and left exact propagation untouched.

Contracts protected:

- exact `float.hex()` equality where Phase 2 requires it;
- stable codon/category/amino-acid/stop ordering;
- canonical DataFrame columns, dtypes, RangeIndexes, and row order;
- denominator and zero-case behavior;
- exact-result provenance validation;
- no UI imports in the engine;
- no silent replacement of detailed sampled or aggregated sampled behavior.

Recommendation: keep this path authoritative and treat it as the reference for any future optimized algorithm.

## 2. Pure-Python internal optimization path

Pure-Python internal optimization remains the safest default.

Still-available opportunities:

- reduce repeated derived-table construction;
- reuse internal scoped table results with defensive copies;
- reduce duplicate schema/table conversion work;
- simplify hot loops in table derivation without changing propagation;
- profile exact all-codon analysis for expensive derived-table queries;
- improve benchmark harness coverage before considering dependency work.

Expected benefit:

- modest but low-risk runtime reductions for repeated exact queries;
- lower avoidable DataFrame construction overhead;
- clearer implementation boundaries for future optimization review.

Risks:

- accidental mutation sharing if cached frames are returned directly;
- altered row ordering if helper refactors use non-canonical iteration;
- changed dtype inference if table construction shortcuts bypass approved schemas.

Verification strategy:

- focused TDD tests for schema/dtype/index/order equality;
- exact float hex equality where covered;
- mutation-safety tests for returned frames;
- full Phase 2/3 regression suite;
- frozen diagnostics;
- benchmark before/after observations, interpreted as advisory only.

Recommendation: continue this route before introducing matrix/dependency complexity.

## 3. Matrix / transition representation

A transition matrix would represent codon-to-codon probability movement across generations. In principle, one generation can be modeled as multiplying a probability vector by a transition matrix whose rows/columns represent codon states, including stop-state handling.

Potential value:

- compact mathematical model;
- possible speedups for repeated propagation;
- easier future vectorized implementation;
- possible support for long generation counts once equivalence is proven.

Equivalence concerns:

- current exact propagation accumulates floats in a specific Python iteration order;
- matrix multiplication would likely change floating-point addition order;
- `float.hex()` equality for existing APIs may not be preserved;
- stop outcomes require new and cumulative stop weights, not just final live mass;
- scoped starting weights, zero starts, sparse starts, and provenance validation must map exactly;
- canonical row ordering and table dtypes must still be produced by the existing contracts.

Public API impact:

- a matrix path should not replace existing `run_exact_analysis`;
- if pursued, it likely needs a new experimental API or internal dual-path contract;
- a public API would require a separate contract naming reference path, optimized path, equivalence rules, and fallback behavior.

Recommendation: research only for now. Do not implement a matrix path in Step 6.

## 4. NumPy option

Potential benefits:

- faster dense vector/matrix operations;
- well-tested numeric arrays;
- possible speedups for all-codon population analysis;
- useful if future Phase 3/4 work needs larger exact workloads.

Dependency impact:

- adds an installation dependency not currently required by the clean repo;
- requires version pinning and platform installation testing;
- changes README/setup expectations;
- may increase package size and environment complexity.

Scientific equivalence risks:

- different floating-point accumulation order;
- dtype coercion to array floats;
- possible loss of exact same-process `float.hex()` equality;
- harder mapping between array positions and canonical codon/stop ordering;
- risk of treating probability weight as count-like arrays in documentation or code.

Test strategy if approved later:

- keep Python exact path as reference;
- compare optimized output to reference over reviewed cases;
- require `float.hex()` equality only if demonstrably preserved;
- otherwise require a human-approved tolerance contract for the new experimental path only;
- preserve all public Phase 2 table schemas by adapting optimized state back through canonical table builders.

Fallback:

- keep pure-Python exact path as default and authoritative;
- make any NumPy path optional/experimental if dependency approval is granted.

Recommendation: do not add NumPy now.

## 5. SciPy option

SciPy could support sparse matrices and more advanced linear algebra. It is likely overkill for the current Phase 3 evidence.

Potential benefits:

- sparse transition matrix representation;
- efficient repeated multiplications for large state spaces;
- possible future analytical tooling.

Costs and risks:

- heavier dependency than NumPy;
- more installation friction;
- no current evidence that sparse matrix work is needed before simpler exact optimizations;
- same float-order and equivalence risks as NumPy;
- risk of pulling Phase 3 toward algorithm replacement instead of contract-preserving optimization.

Fallback:

- avoid SciPy unless future benchmark evidence shows pure-Python and optional NumPy paths are insufficient.

Recommendation: do not add SciPy now.

## 6. Recommendation

Recommended default:

- keep current exact algorithm as authoritative reference;
- continue pure-Python internal optimization;
- do not add NumPy or SciPy in Phase 3 Step 6;
- do not create a new exact optimization contract now;
- do not implement matrix/transition code now.

If future evidence strongly supports matrix work, create a separate contract first. That contract should define a new experimental optimized exact path and must compare against the current reference. It must not silently replace `run_exact_analysis` or `run_simulation`.

## 7. Contract / dependency gate

Decision:

No new contract recommended now.

No `docs/phase_3_exact_optimization_contract.md` is created by this Step 6 decision.

Step 7 may proceed because no immediate human dependency/contract approval is required.

