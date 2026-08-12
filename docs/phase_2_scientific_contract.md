# Phase 2 Scientific Contract — Strengthen the Computation

## Contract metadata

- **Status:** Approved — Scientific Contract gate accepted 2026-08-11
- **Contract version:** `2.1-approved`
- **2.1 amendment:** Bounded `new_stop_codon_by_start_codon` joint counter approved 2026-08-11 to make scoped stop and codon-outcome tables identifiable
- **Compatibility version:** Phase 1 public and legacy behavior remains `v1`
- **Authoritative artifact:** `final code/docs/phase_2_scientific_contract.md`
- **Provider owner:** Python scientific engine under `final code/engine/`
- **Approver:** Project owner/user
- **Blueprint:** `plans/phase-2-strengthen-computation.md`
- **Execution evidence:** `plans/phase-2-execution-log.md`
- **Runtime boundary:** Shared Python runtime; no HTTP, event, RPC, or generated-client contract exists in Phase 2

This document is the human-reviewed authority for Phase 2. Step 3 must derive typed Python models and one compact static schema fixture from it. Implementations do not redefine this contract after coding. Any change follows the contract-change protocol below and requires approval before provider or consumer code changes.

## 1. Purpose and scientific authority

Exact probability is the authoritative deterministic scientific calculation. One exact propagation supplies every authoritative category, survival, stop, convergence, and comparison result. Exact probability values are **weights**, not integer counts.

Sampled simulation is experimental and has two explicit modes:

1. **Detailed sampled mode:** the frozen Phase 1 `run_experiment` API, including individual records and paths and module-global RNG effects.
2. **Aggregated sampled mode:** a new explicitly seeded API that retains bounded per-generation integer counters and no individual histories.

No caller or UI may silently switch between sampled modes. Exact and sampled outputs remain visibly and semantically distinct.

## 2. Owners, consumers, and consumer jobs

| Participant | Role and job | Contract owner |
|---|---|---|
| `engine` exact provider | Run the unchanged exact algorithm once and expose complete deterministic scientific tables | Engine owner |
| Aggregated sampled provider | Produce reproducible integer summaries without per-copy retention | Engine owner |
| Category/summary analysis | Derive tables without duplicating biology or propagation | Engine owner |
| Streamlit adapter | Render existing views and translate expected engine errors without calculating science | UI owner; consumes engine contract |
| Tkinter compatibility adapter | Preserve historical names, signatures, tuples, and behavior | Compatibility owner; consumes engine contract |
| Engine and compatibility tests | Prove schemas, invariants, exact equality, sampled behavior, and boundaries | Test owner |
| Python/notebook callers | Request named results without tuple indexes or UI imports | Contract consumer |
| Future FastAPI | Not an existing Phase 2 consumer and has no authority to alter this contract | Deferred |

The smallest useful boundary is a typed Python interface plus canonical pandas table contracts. OpenAPI, AsyncAPI, Protocol Buffers, JSON Schema generators, and generated clients are out of scope.

## 3. Locked Phase 1 compatibility

The following are immutable during Phase 2:

- `engine.exact_tracking.run_simulation(...) -> ExactSimulationResult`, including iteration order, accumulation order, concrete containers, insertion order, and same-process `float.hex()` values.
- `engine.sampled_tracking.run_experiment(...) -> SampledSimulationResult`, including module-global `random`, `VALID_CODONS` order, copy order, `randint` then `choices`, paths, records, early stops, copy numbering, consecutive calls, and final `random.getstate()`.
- `ExactSimulationResult.to_legacy_tuple()` and `SampledSimulationResult.to_legacy_tuple()` field positions and object identity behavior.
- Existing public signatures, defaults, tuple lengths, record keys, dictionary order, DataFrame columns/dtypes/index/order/empty behavior, Streamlit cache/RNG effects, widgets, labels, query bindings, charts, tables, errors, accessibility, visual identity, and Tkinter behavior.
- Codon table, 61-sense-codon order, stop definitions, amino-acid properties, category labels/order, probability presets, and substitution mapping.
- Root research files, all three diagnostic copies, and both Phase 1 JSON fixtures.

New Phase 2 interfaces are additive. New results have no positional tuple conversion. A breaking change requires an approved Blueprint mutation and version/migration decision.

## 4. Shared vocabulary and canonical order

### 4.1 Public type vocabulary

The approved Step 3 models use these meanings:

- `SubstitutionMatrix`: existing `engine.mutation_matrix.SubstitutionMatrix`.
- `StartWeights`: `Mapping[str, float]` accepted at the boundary and copied into a canonical `dict[str, float]`.
- `StartScope`: `Literal["population", "codon", "amino_acid", "trait"]`.
- `ConvergenceBasis`: `Literal["category_weight", "survivor_fraction"]`.
- `MetricName`: `Literal["category_live_value", "category_fraction", "survivor_fraction", "stop_fraction", "new_stop_value", "cumulative_stop_value", "cumulative_stop_fraction", "codon_live_value", "codon_new_stop_value", "codon_cumulative_stop_value"]`.
- Exact `value_kind`: the literal string `"probability_weight"`.
- Aggregated sampled `value_kind`: the literal string `"copy_count"`.

### 4.2 Canonical order

1. Generations: ascending `1..n_generations`.
2. Scope order: `population`, `codon`, `amino_acid`, `trait`.
3. Population key: `all`.
4. Codons: `VALID_CODONS` order.
5. Amino acids: existing `ALL_AAS` sorted order.
6. Traits/categories: `PROPERTY_LABELS.values()` insertion order.
7. Stops: `TAA`, `TAG`, `TGA`; never set iteration order.
8. Comparison rows: scientific key order, never incidental pandas order.

Every canonical DataFrame uses a zero-based `RangeIndex`. Every builder supplies explicit dtypes, including typed empty frames; pandas inference is not the contract.

## 5. Input normalization and common parameter behavior

### 5.1 Exact starting weights

The authoritative exact APIs accept `start_weights: Mapping[str, float] | None`.

- `None` means `1.0` for every `VALID_CODONS` entry.
- Unknown codon keys are rejected before simulation.
- The provider creates a new canonical dictionary containing all 61 valid codons in `VALID_CODONS` order.
- Each value is converted with `float(value)` and normalized to `value if value > 0 else 0.0`, matching the existing algorithm's active-start semantics for valid codons.
- Missing codons become `0.0`.
- The caller's mapping is never retained by reference or mutated.
- This phase does not add finite-number or substitution-probability range validation. Result invariants still reject non-conserving authoritative output.

### 5.2 Aggregated sampled starting counts

The aggregated provider creates a new canonical dictionary containing all valid codons in canonical order:

```text
start_count[codon] = max(0, int(start_weights.get(codon, 0)))
```

These actual simulated integers are the only sampled denominators. Unknown codon keys are rejected. The caller's mapping is not mutated.

### 5.3 Generations and seed

- New Phase 2 entry points require `n_generations` to be an `int >= 0`; otherwise they raise `ValueError("n_generations must be >= 0")`.
- Post-mutation rows are numbered `1..n_generations`.
- Zero generations produce typed empty time-series tables. Initial/final raw state still represents generation 0.
- Aggregated `seed` is a required `int`; no default and no automatic seed exists.

## 6. Authoritative exact entry points

```python
def run_exact_analysis(
    n_generations: int,
    sub_matrix: SubstitutionMatrix,
    start_weights: Mapping[str, float] | None = None,
) -> ExactAnalysisResult: ...

def build_exact_analysis(
    simulation: ExactSimulationResult,
    start_weights: Mapping[str, float] | None = None,
) -> ExactAnalysisResult: ...
```

### 6.1 `run_exact_analysis`

- Normalizes/copies starting weights.
- Calls the existing `run_simulation` exactly once.
- Passes the canonical mapping to that unchanged primitive.
- Calls `build_exact_analysis` without performing a second simulation.
- Propagation order and output are exactly the Phase 1 primitive's behavior.

### 6.2 `build_exact_analysis`

- Never runs a simulation.
- Normalizes/copies the supplied weights using the same exact rules.
- Validates that the result and weights have matching provenance before returning tables.
- Owns new DataFrames; consumers must treat result fields as read-only. Scoped query functions return new frames or defensive copies.
- Raises a named provenance error rather than returning partial results.

## 7. `ExactAnalysisResult` model

Step 3 creates a frozen named dataclass with these required, non-null fields in this exact order:

| Position | Field | Type | Ownership and meaning |
|---:|---|---|---|
| 1 | `simulation` | `ExactSimulationResult` | Unchanged named Phase 1 result; no tuple conversion is performed |
| 2 | `start_weights` | `dict[str, float]` | New canonical 61-key copy in `VALID_CODONS` order |
| 3 | `population_category_metrics` | `pd.DataFrame` | Eager whole-population category weight table |
| 4 | `population_survivor_fractions` | `pd.DataFrame` | Eager whole-population category fraction table |
| 5 | `population_survival` | `pd.DataFrame` | Eager whole-population survival/stop table |
| 6 | `population_stop_outcomes` | `pd.DataFrame` | Eager whole-population stop table by canonical stop codon |

The dataclass has no `to_legacy_tuple`. Freezing prevents field rebinding; contained mappings/DataFrames are provider-owned and treated as immutable contract values.

### 7.1 Scoped exact queries

```python
def get_exact_category_metrics(
    analysis: ExactAnalysisResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame: ...

def get_exact_survivor_fractions(
    analysis: ExactAnalysisResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame: ...

def get_exact_survival_by_start(
    analysis: ExactAnalysisResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame: ...

def get_exact_stop_outcomes(
    analysis: ExactAnalysisResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame: ...

def get_exact_codon_outcomes(
    analysis: ExactAnalysisResult,
    *,
    start_codon: str,
    generation: int,
) -> pd.DataFrame: ...

def get_exact_convergence(
    analysis: ExactAnalysisResult,
    *,
    start_scope: StartScope,
    start_key: str,
    basis: ConvergenceBasis,
    tolerance: float,
) -> pd.DataFrame: ...
```

Population queries require `start_key="all"`. Other keys must belong to their canonical codon, amino-acid, or trait domain. Invalid combinations raise `InvalidScientificScopeError`.

## 8. Canonical DataFrame contracts

### 8.1 Category metrics

| Ordinal | Column | Exact dtype | Aggregated dtype | Meaning |
|---:|---|---|---|---|
| 1 | `generation` | `int64` | `int64` | Post-mutation generation |
| 2 | `start_scope` | `object` | `object` | Canonical scope literal |
| 3 | `start_key` | `object` | `object` | Canonical scope member |
| 4 | `category` | `object` | `object` | Current surviving category label |
| 5 | `live_value` | `float64` | `int64` | Exact live weight or sampled live count |
| 6 | `value_kind` | `object` | `object` | Exact/sample literal |

Rows: five categories for every requested generation/scope, including zero-valued categories. Order is generation, scope, key, category. Zero generations return a typed empty table.

### 8.2 Survivor fractions

| Ordinal | Column | Exact dtype | Aggregated dtype | Meaning |
|---:|---|---|---|---|
| 1 | `generation` | `int64` | `int64` | Post-mutation generation |
| 2 | `start_scope` | `object` | `object` | Canonical scope |
| 3 | `start_key` | `object` | `object` | Canonical scope member |
| 4 | `category` | `object` | `object` | Current category |
| 5 | `numerator` | `float64` | `int64` | Live value in category |
| 6 | `denominator` | `float64` | `int64` | All live non-stop value in the same scope/generation |
| 7 | `fraction` | `float64` | `float64` | Numerator divided by denominator, or `0.0` |

Rows/order match category metrics. When denominator is zero, every fraction in that scope/generation is `0.0`.

### 8.3 Survival by start

| Ordinal | Column | Exact dtype | Aggregated dtype | Meaning |
|---:|---|---|---|---|
| 1 | `generation` | `int64` | `int64` | Post-mutation generation |
| 2 | `start_scope` | `object` | `object` | Population/codon/amino acid/trait |
| 3 | `start_key` | `object` | `object` | Scope member |
| 4 | `initial_value` | `float64` | `int64` | Actual eligible starting weight/count |
| 5 | `live_value` | `float64` | `int64` | Non-stop value still live |
| 6 | `stopped_value` | `float64` | `int64` | Cumulative stopped value from that start scope |
| 7 | `survivor_fraction` | `float64` | `float64` | Live divided by initial, or `0.0` |
| 8 | `stop_fraction` | `float64` | `float64` | Cumulative stopped divided by initial, or `0.0` |
| 9 | `value_kind` | `object` | `object` | Exact/sample literal |

One row per requested scope/generation. `stopped_value` comes from tracked cumulative stops, not clipping or presentation subtraction.

### 8.4 Stop outcomes

| Ordinal | Column | Exact dtype | Aggregated dtype | Meaning |
|---:|---|---|---|---|
| 1 | `generation` | `int64` | `int64` | Post-mutation generation |
| 2 | `start_scope` | `object` | `object` | Canonical scope |
| 3 | `start_key` | `object` | `object` | Scope member |
| 4 | `stop_codon` | `object` | `object` | `TAA`, `TAG`, or `TGA` |
| 5 | `new_stop_value` | `float64` | `int64` | First hitting that stop at this generation |
| 6 | `cumulative_stop_value` | `float64` | `int64` | Stops at or before this generation |
| 7 | `initial_value` | `float64` | `int64` | Eligible starting denominator |
| 8 | `cumulative_stop_fraction` | `float64` | `float64` | Cumulative value divided by initial, or `0.0` |
| 9 | `value_kind` | `object` | `object` | Exact/sample literal |

Rows: three canonical stop codons per requested generation/scope, including zeros. “Stop percentage” presentation formats `cumulative_stop_fraction`; the stored value remains `[0,1]` fraction.

### 8.5 Codon outcomes

| Ordinal | Column | Exact dtype | Aggregated dtype | Meaning |
|---:|---|---|---|---|
| 1 | `generation` | `int64` | `int64` | Requested post-mutation generation |
| 2 | `start_codon` | `object` | `object` | Valid starting codon |
| 3 | `target_codon` | `object` | `object` | Sense codon, then canonical stop codon |
| 4 | `target_aa` | `object` | `object` | Encoded amino acid or `Stop` |
| 5 | `target_category` | `object` | `object` | Current category or `Stop` |
| 6 | `live_value` | `float64` | `int64` | Live target value; zero for stop rows |
| 7 | `new_stop_value` | `float64` | `int64` | New stop value at generation; zero for live rows |
| 8 | `cumulative_stop_value` | `float64` | `int64` | Stop value through generation; zero for live rows |
| 9 | `value_kind` | `object` | `object` | Exact/sample literal |

Rows: all 61 sense codons in canonical order followed by `TAA`, `TAG`, `TGA`, including zeros. An unavailable generation raises `InvalidScientificScopeError`; zero-generation analyses have no valid outcome generation and do not return a placeholder row.

### 8.6 Convergence

| Ordinal | Column | Dtype | Meaning |
|---:|---|---|---|
| 1 | `start_scope` | `object` | Canonical scope |
| 2 | `start_key` | `object` | Scope member |
| 3 | `basis` | `object` | `category_weight` or `survivor_fraction` |
| 4 | `tolerance` | `float64` | Explicit stability threshold |
| 5 | `generation` | `Int64` | First stable generation or `pd.NA` |
| 6 | `max_delta` | `float64` | Maximum future deviation at the chosen generation, or `0.0` for empty input |
| 7 | `status` | `object` | Stable, all stopped, or still changing/no data status |

One row per requested scope. Canonical status values are exactly `stable`, `all_stopped`, `still_changing`, and `no_generations`. With zero generations, generation is `pd.NA`, `max_delta=0.0`, and status is `no_generations`. Compatibility wrappers retain their existing strings and tuple forms.

### 8.7 Directed numeric comparison

| Ordinal | Column | Dtype | Meaning |
|---:|---|---|---|
| 1 | `generation` | `Int64` | Generation or `pd.NA` for non-time metrics |
| 2 | `metric` | `object` | Approved metric identifier |
| 3 | `entity` | `object` | Aligned category/codon/AA/trait/stop identifier |
| 4 | `baseline_label` | `object` | Human-stable baseline label |
| 5 | `candidate_label` | `object` | Human-stable candidate label |
| 6 | `baseline_value` | `float64` | Baseline measurement |
| 7 | `candidate_value` | `float64` | Candidate measurement |
| 8 | `signed_delta` | `float64` | Candidate minus baseline |
| 9 | `absolute_delta` | `float64` | Absolute signed delta |
| 10 | `relative_delta` | `Float64` | Signed delta / baseline, or `pd.NA` at zero baseline |
| 11 | `direction` | `object` | Literal `candidate_minus_baseline` |

Typed-empty versus typed-empty returns typed empty. When one valid sparse table omits an otherwise approved aligned row, numeric value is `0.0`; unexpected duplicate keys or noncanonical schema raise `MetricSchemaError`.

### 8.8 Convergence/status comparison

| Ordinal | Column | Dtype | Meaning |
|---:|---|---|---|
| 1 | `start_scope` | `object` | Canonical scope |
| 2 | `start_key` | `object` | Scope member |
| 3 | `basis` | `object` | Convergence basis |
| 4 | `baseline_label` | `object` | Baseline label |
| 5 | `candidate_label` | `object` | Candidate label |
| 6 | `baseline_generation` | `Int64` | Baseline stable generation or `pd.NA` |
| 7 | `candidate_generation` | `Int64` | Candidate stable generation or `pd.NA` |
| 8 | `generation_delta` | `Int64` | Candidate minus baseline when both exist |
| 9 | `baseline_status` | `object` | Baseline status |
| 10 | `candidate_status` | `object` | Candidate status |

This schema is separate because status values are not numeric metrics.

### 8.9 Exact-versus-sampled calibration

| Ordinal | Column | Dtype | Meaning |
|---:|---|---|---|
| 1 | `generation` | `int64` | Post-mutation generation |
| 2 | `metric` | `object` | Compared fraction identifier |
| 3 | `entity` | `object` | Aligned scientific entity |
| 4 | `denominator_scope` | `object` | Explicit eligible-copy scope |
| 5 | `exact_fraction` | `float64` | Exact reference fraction |
| 6 | `sampled_fraction` | `Float64` | Sample estimate or `pd.NA` |
| 7 | `signed_error` | `Float64` | Sampled minus exact |
| 8 | `absolute_error` | `Float64` | Absolute signed error |
| 9 | `sample_size` | `int64` | Eligible sampled copies |
| 10 | `standard_error` | `Float64` | Bernoulli marginal standard error |
| 11 | `adjusted_alpha` | `float64` | Family-wise alpha divided by family size |
| 12 | `family_size` | `int64` | Rows in the aligned request family |
| 13 | `confidence_lower` | `Float64` | Wilson lower bound or `pd.NA` |
| 14 | `confidence_upper` | `Float64` | Wilson upper bound or `pd.NA` |
| 15 | `within_interval` | `boolean` | Nullable exact-in-interval verdict |

When `sample_size == 0`, sampled fraction, both errors, standard error, bounds, and verdict are `pd.NA`; exact fraction, adjusted alpha, and family metadata remain present.

## 9. Scientific formulas and denominator matrix

Let `I(S)` be the eligible initial exact weight or sampled count for start scope `S`, `L_g(S)` the non-stop live value after generation `g`, `C_g(S,c)` live value in category `c`, and `D_g(S,s)` new stops into stop codon `s` at generation `g`.

```text
I(population)                  = sum_(valid codon q) positive_start_weight(q)
I(starting codon q)           = positive_start_weight(q)
I(starting amino acid a)      = sum_(q encodes a) positive_start_weight(q)
I(starting trait t)           = sum_(primary_group(CODON_TABLE[q])=t) positive_start_weight(q)
category_live(g,S,c)       = C_g(S,c)
live_denominator(g,S)      = sum_c C_g(S,c) = L_g(S)
category_fraction(g,S,c)   = C_g(S,c) / L_g(S), or 0 when L_g(S)=0
live_codon_outcome(g,q,r)     = live value at target sense codon r from starting codon q after g
new_stop_codon(g,q,s)         = first-hit stop value into s from q exactly at generation g
cumulative_stop(g,S,s)     = sum_(j=1..g) D_j(S,s)
cumulative_stop_codon(g,q,s)  = sum_(j=1..g) new_stop_codon(j,q,s)
all_cumulative_stops(g,S)  = sum_s cumulative_stop(g,S,s)
survivor_fraction(g,S)     = L_g(S) / I(S), or 0 when I(S)=0
stop_fraction(g,S)         = all_cumulative_stops(g,S) / I(S), or 0 when I(S)=0
stop_percentage(g,S)       = 100 * stop_fraction(g,S), presentation only
signed_delta               = candidate_value - baseline_value
absolute_delta             = abs(signed_delta)
relative_delta             = signed_delta / baseline_value; pd.NA when baseline_value=0
signed_error               = sampled_fraction - exact_fraction
absolute_error             = abs(signed_error)
```

| Scope/metric | Eligible denominator | Zero behavior |
|---|---|---|
| Population | Sum of all canonical positive exact weights or simulated start counts | Fractions `0.0` |
| Starting codon | That codon's canonical positive exact weight or simulated count | Requested zero codon emits zero rows/fractions |
| Starting amino acid | Sum over canonical starting codons encoding that amino acid | Requested zero AA emits zero rows/fractions |
| Starting trait | Sum over canonical starting codons whose starting AA has that trait | Requested zero trait emits zero rows/fractions |
| Category among survivors | All live non-stop value in the same generation/start scope | Five category fractions are `0.0` |
| Exact stop fraction | Cumulative exact stop weight / exact initial scope weight | `0.0` |
| Aggregated stop fraction | Cumulative integer stops / normalized simulated start count | `0.0` |
| Exact-vs-sampled | Same named eligible start scope for exact and sample; both are normalized before comparison | Sample fields nullable when sampled denominator is zero |

Unrequested inactive scopes are absent. Explicit queries for a valid zero-start scope emit their complete canonical zero rows.

### 9.1 Worked scientific examples

These examples freeze meaning, not new reference values. Exact examples use probability weights; sampled examples use integer copy counts.

1. **Category fraction among survivors:** if one category has exact live weight `0.30` and all five categories total `0.50`, its category fraction is `0.30 / 0.50 = 0.60`. If all five live weights are zero, every category fraction is `0.0`.
2. **Starting-codon survival:** if a requested codon starts with exact weight `2.0`, has live weight `1.5`, and cumulative stopped weight `0.5`, survivor fraction is `0.75` and stop fraction is `0.25`.
3. **Starting-amino-acid survival:** if the codons encoding one starting amino acid have initial weights `1.0` and `3.0` and live weights `0.8` and `2.2`, the amino-acid denominator is `4.0`, live weight is `3.0`, and survivor fraction is `0.75`. It is not the unweighted mean of per-codon fractions.
4. **Starting-trait survival:** if three eligible starting amino-acid groups contribute initial weights `1.0`, `2.0`, and `3.0` to the same trait and retain live weights `0.5`, `1.5`, and `2.5`, the trait denominator is `6.0`, live weight is `4.5`, and survivor fraction is `0.75`.
5. **Cumulative stop outcome:** if new `TAA` weight is `0.10` at generation 1 and `0.20` at generation 2, cumulative `TAA` weight at generation 2 is `0.30`. With initial scope weight `2.0`, its cumulative stop fraction is `0.15`. Population stop fraction uses the sum over all three stop codons.
6. **Convergence:** with tolerance `0.0` and successive two-category vectors `(0.6, 0.4)`, `(0.5, 0.5)`, `(0.5, 0.5)`, generation 2 is the first stable generation and `max_delta=0.0`.
7. **Directed comparison:** baseline `0.20` and candidate `0.30` yield signed delta `0.10`, absolute delta `0.10`, and relative delta `0.50`. Swapping them yields signed delta `-0.10`, absolute delta `0.10`, and directional relative delta `-1/3`.
8. **Exact-versus-sampled normalization:** exact fraction `0.30` and sampled successes `32` from `100` eligible copies yield sampled fraction `0.32`, signed error `0.02`, and absolute error `0.02`; the Wilson interval uses `n=100`, not a UI-requested or pre-truncation weight.

## 10. Convergence semantics

For a requested category vector `v_g`:

- `category_weight` uses raw live category weights/counts.
- `survivor_fraction` uses the five category fractions among survivors.
- A candidate generation `i` is stable when every later vector `v_j`, `j >= i`, differs from `v_i` by at most `tolerance` in every category.
- The result is the first such 1-based generation.
- `max_delta` is `max(|v_j[k]-v_i[k]|)` across all later generations/categories at the selected generation.
- Canonical status values are exactly `stable`, `all_stopped`, `still_changing`, and `no_generations`.
- An all-zero selected vector returns status `all_stopped` at the first generation from which all later vectors remain zero.
- A nonzero first-stable vector returns `stable`; when no candidate is stable, generation is `pd.NA`, status is `still_changing`, and `max_delta` is the maximum observed candidate-to-later deviation.
- Zero generations return generation `pd.NA`, `max_delta=0.0`, and status `no_generations`.

New authoritative callers provide `basis` and `tolerance` explicitly. Compatibility functions retain count tolerance `1.0`, surviving-fraction alpha defaults, labels, and tuple/status behavior. Conservation tolerance (`1e-12`) and statistical family-wise alpha (`0.01`) are unrelated to convergence tolerance.

## 11. Exact-result provenance validation

`build_exact_analysis` must validate before returning any authoritative table:

1. Canonical input has exactly 61 keys in `VALID_CODONS` order.
2. Positive input keys equal `simulation.start_to_fin` keys in canonical active-start order.
3. `simulation.stats["n_starts"]` equals positive-key count.
4. `simulation.stats["total_start_copies"]` matches the positive input total under the exact conservation tolerance.
5. `simulation.stats["n_generations"]` is an integer `>= 0`.
6. For each active start codon, final live weight from `start_to_fin[start]` plus `stop_data["by_start_codon"][start]` matches that start's initial weight.
7. For zero generations, each active `start_to_fin[start]` contains exactly its start codon with its initial weight and no stops.
8. Global final live plus total stop weight matches the input total.

Failure raises `ExactResultProvenanceError` before table creation. Message template:

```text
Exact result provenance mismatch for <scope>: expected <expected>, observed <observed>.
```

No validation renormalizes or repairs the supplied result.

## 12. Aggregated sampled API and result models

```python
def run_aggregated_experiment(
    n_generations: int,
    sub_matrix: SubstitutionMatrix,
    start_weights: Mapping[str, float],
    seed: int,
) -> AggregatedSampledResult: ...
```

### 12.1 `AggregatedGenerationCounts`

A frozen named dataclass with fields in exact order:

| Position | Field | Type | Bound/meaning |
|---:|---|---|---|
| 1 | `generation` | `int` | `1..n_generations` |
| 2 | `live_codon` | `Counter[str]` | At most 61 current sense codons |
| 3 | `live_amino_acid` | `Counter[str]` | At most 20 amino acids |
| 4 | `live_category` | `Counter[str]` | At most five categories |
| 5 | `live_by_start_codon` | `Counter[str]` | At most 61 starting codons |
| 6 | `live_by_start_trait` | `Counter[str]` | At most five starting traits |
| 7 | `current_codon_by_start_codon` | `dict[str, Counter[str]]` | At most `61 x 61` nonzero cells |
| 8 | `new_stop_codon_by_start_codon` | `dict[str, Counter[str]]` | All 61 canonical start keys; at most `61 x 3` nonzero start/stop cells |
| 9 | `new_stops_by_stop_codon` | `Counter[str]` | At most three stops; derived from the joint counter |
| 10 | `new_stops_by_start_codon` | `Counter[str]` | At most 61 starts; derived from the joint counter |
| 11 | `new_stops_by_start_trait` | `Counter[str]` | At most five traits; derived from the joint counter and canonical biology |
| 12 | `total_live` | `int` | All live copies after generation |
| 13 | `new_stops` | `int` | Stops first hit during generation |
| 14 | `cumulative_stops` | `int` | Stops through generation |

AA/category and trait counters are updated using the single biological definitions in `genetic_code`; they are cross-checked against codon/start-codon rollups and never become new biological authorities.

### 12.2 `AggregatedSampledResult`

A frozen named dataclass with fields in exact order:

| Position | Field | Type | Meaning |
|---:|---|---|---|
| 1 | `seed` | `int` | Explicit deterministic local seed |
| 2 | `n_generations` | `int` | Requested non-negative count |
| 3 | `start_counts` | `dict[str, int]` | All 61 normalized counts in canonical order |
| 4 | `total_start_count` | `int` | Sum of normalized counts |
| 5 | `generations` | `tuple[AggregatedGenerationCounts, ...]` | Ordered snapshots; length equals generations |
| 6 | `final_live_codon` | `Counter[str]` | Final surviving current codons |
| 7 | `final_live_amino_acid` | `Counter[str]` | Final surviving current amino acids |
| 8 | `final_live_by_start_codon` | `dict[str, Counter[str]]` | Final current codons grouped by start; all canonical start keys |
| 9 | `total_stopped` | `int` | Cumulative stopped copies |

At zero generations, final counters equal the normalized initial population, the snapshot tuple is empty, and `total_stopped=0`. New result models have no legacy tuple conversion. All fields in both aggregate dataclasses are required and non-null. The provider creates and owns fresh counters/mappings in canonical insertion order; callers treat them as read-only even though `Counter` and `dict` are mutable Python containers.

Retained counters have one derivation hierarchy. `live_codon`, `current_codon_by_start_codon`, and `new_stop_codon_by_start_codon` are updated from the transient copy state. The joint stop counter is the authoritative retained stop grouping: its outer mapping contains all 61 starting codons in canonical order, and each inner Counter uses canonical stop order. New-stop marginals by stop codon, starting codon, and starting trait are derived and cross-checked from this joint counter; starting-trait rollup uses canonical `genetic_code` definitions. Amino-acid, category, start-trait, and scalar live totals are derived during the same update from canonical definitions and must equal regrouping of the codon/start-codon counters. `total_live`, `new_stops`, and `cumulative_stops` equal the corresponding counter sums rather than independent scientific measurements. Cumulative stop counters are prefix sums of the retained per-generation new-stop counters and are not retained again. Final category/start-trait live counters and grouped stop counters are likewise derived from the final snapshot or those prefix sums. Final codon/AA/start-codon counters are derived from the last snapshot, or from normalized initial counts when there are zero generations; `total_stopped` equals the final cumulative-stop total. No derived table or counter is a second biological or simulation source of truth.

### 12.3 Aggregated sampled scoped queries

These functions derive canonical sampled tables from the retained counters. They do not reconstruct paths or rerun sampling:

```python
def get_aggregated_category_metrics(
    result: AggregatedSampledResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame: ...

def get_aggregated_survivor_fractions(
    result: AggregatedSampledResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame: ...

def get_aggregated_survival_by_start(
    result: AggregatedSampledResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame: ...

def get_aggregated_stop_outcomes(
    result: AggregatedSampledResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame: ...

def get_aggregated_codon_outcomes(
    result: AggregatedSampledResult,
    *,
    start_codon: str,
    generation: int,
) -> pd.DataFrame: ...

def get_aggregated_convergence(
    result: AggregatedSampledResult,
    *,
    start_scope: StartScope,
    start_key: str,
    basis: ConvergenceBasis,
    tolerance: float,
) -> pd.DataFrame: ...
```

Scope validation, requested-zero inclusion, row order, typed-empty behavior, and defensive-copy ownership exactly mirror the corresponding exact query. Integer fields and `value_kind` follow the aggregated column contracts. These functions are the only production conversion from aggregate counters to canonical tables.

## 13. Aggregated RNG and iteration semantics

Aggregated sampling uses `random.Random(seed)` local to the call. It does not read or mutate module-global RNG state.

For exact reduction equivalence, execution order is fixed:

1. Iterate `VALID_CODONS`.
2. For each start, iterate copies `1..start_counts[start]`.
3. Start each transient copy at its start codon.
4. For each generation, call local `randint(0, 2)` once.
5. Read substitution keys/probabilities in existing row insertion order.
6. Call local `choices(keys, probs)[0]` once.
7. On a stop, update that generation's/new/cumulative counters and break.
8. Otherwise update the copy's transient codon and all generation counters.
9. Discard transient per-copy state after its final update.

Python's `random.Random(seed)` uses the same draw sequence as module-global `random` immediately after `random.seed(seed)` when calls and input order match. Therefore canonical reduction of detailed records must equal aggregate counters for the same reviewed seed/input. Aggregated mode intentionally does **not** reproduce or expose the detailed API's final module-global RNG side effect.

Generation-major sampling, multinomial/binomial draws, NumPy RNG, batching that changes draw order, and vectorization are separate Phase 3 algorithms and are prohibited here.

## 14. Information unavailable in aggregated mode

Aggregated mode does not return or retain:

- individual copy IDs;
- individual record dictionaries;
- individual mutation paths;
- per-copy final records;
- individual stop-generation records;
- the detailed API's final module-global RNG state.

Consumers requiring any of these must explicitly use `run_experiment`.

## 15. Detailed-record reducer contract

A test-only canonical reducer consumes frozen detailed records without altering them. For each record and every post-mutation generation reached before/at a stop, it derives the same counters as `AggregatedGenerationCounts`. For generations after an early stop, that copy contributes only to cumulative-stop totals and never to live/new-stop values.

For identical inputs and seed, equality requires:

- every generation number and ordering;
- every live codon, AA, and category Counter and insertion order;
- live by starting codon/trait;
- every nested current-codon-by-start Counter;
- every nested new-stop-codon-by-start Counter;
- new stops by stop codon/start codon/start trait;
- total live, new stops, and cumulative stops;
- final codon, AA, and start-to-final counters;
- total starting, surviving, and stopped counts.

Equality only at final totals is insufficient.

## 16. Comparison result models and APIs

Step 3 defines these frozen result dataclasses without tuple conversion:

### `ComparisonResult`

1. `metric: str`
2. `baseline_label: str`
3. `candidate_label: str`
4. `key_columns: tuple[str, ...]`
5. `table: pd.DataFrame`

### `ConvergenceComparisonResult`

1. `baseline_label: str`
2. `candidate_label: str`
3. `table: pd.DataFrame`

### `ExactSampledComparisonResult`

1. `metric: str`
2. `denominator_scope: str`
3. `familywise_alpha: float`
4. `family_size: int`
5. `table: pd.DataFrame`

Public comparison functions accept named exact/aggregated results or canonical tables plus explicit labels/metric request. They validate canonical schemas and align by approved keys. Self-comparison produces zero signed/absolute delta; relative delta is `0.0` only when the nonzero baseline equals candidate and remains `pd.NA` when baseline is zero. Swapping inputs negates signed delta but not absolute delta; relative delta remains directional.

The public operations and defaults are:

```python
def compare_numeric_metric(
    baseline_table: pd.DataFrame,
    candidate_table: pd.DataFrame,
    *,
    metric: MetricName,
    baseline_label: str,
    candidate_label: str,
) -> ComparisonResult: ...

def compare_convergence(
    baseline_table: pd.DataFrame,
    candidate_table: pd.DataFrame,
    *,
    baseline_label: str,
    candidate_label: str,
) -> ConvergenceComparisonResult: ...

def compare_exact_to_sampled(
    exact_table: pd.DataFrame,
    sampled_table: pd.DataFrame,
    *,
    metric: MetricName,
    denominator_scope: str,
    familywise_alpha: float = 0.01,
) -> ExactSampledComparisonResult: ...
```

Each numeric metric has one source value and alignment contract:

| Metric | Required source table/value | Comparison keys | `entity` |
|---|---|---|---|
| `category_live_value` | Category metrics / `live_value` | `generation`, `category` | Category label |
| `category_fraction` | Survivor fractions / `fraction` | `generation`, `category` | Category label |
| `survivor_fraction` | Survival by start / `survivor_fraction` | `generation` | `all` |
| `stop_fraction` | Survival by start / `stop_fraction` | `generation` | `all` |
| `new_stop_value` | Stop outcomes / `new_stop_value` | `generation`, `stop_codon` | Stop codon |
| `cumulative_stop_value` | Stop outcomes / `cumulative_stop_value` | `generation`, `stop_codon` | Stop codon |
| `cumulative_stop_fraction` | Stop outcomes / `cumulative_stop_fraction` | `generation`, `stop_codon` | Stop codon |
| `codon_live_value` | Codon outcomes / `live_value` | `generation`, `target_codon` | Target codon |
| `codon_new_stop_value` | Codon outcomes / `new_stop_value` | `generation`, `target_codon` | Target codon |
| `codon_cumulative_stop_value` | Codon outcomes / `cumulative_stop_value` | `generation`, `target_codon` | Target codon |

Each input table represents one scenario. `start_scope` and `start_key` identify and validate that scenario but are not alignment keys, allowing explicit mutation-setting, starting-codon, amino-acid, or trait comparisons. `compare_exact_to_sampled` accepts only fraction metrics (`category_fraction`, `survivor_fraction`, `stop_fraction`, and `cumulative_stop_fraction`) because Wilson intervals require Bernoulli successes and an explicit eligible denominator. Other pairings raise `UnsupportedComparisonError`.

## 17. Scientific invariants

Invariant checks return a named report on success and raise `ScientificInvariantError` on failure. They report metric, scope, generation, expected, observed, and tolerance. They never mutate, clip, fill, or repair output.

Required checks:

1. 64 codons, 61 ordered sense codons, stops exactly `TAA`, `TAG`, `TGA`.
2. Each substitution row has the established three targets/order and supplied probability sum.
3. Per exact start scope/generation: live weight plus cumulative stopped weight equals initial weight.
4. Per sampled scope/generation: live integer count plus cumulative stopped count equals initial count exactly.
5. Codon totals group exactly to AA and category totals.
6. Category fractions sum to `1.0` when live denominator is positive and are all `0.0` otherwise.
7. Population/codon/AA/trait denominators equal canonical starting inputs.
8. Generation rows are complete, 1-based, ordered, and typed empty at zero generations.
9. Convergence follows its explicit basis/tolerance and first-stable rule.
10. Repeated exact calls are deterministic.
11. Detailed sampled calls retain exact frozen output and final global RNG state.
12. Aggregated same-seed calls are exactly repeatable and leave global RNG unchanged.
13. Numeric comparison self/swap laws and convergence comparison null laws hold.
14. Every canonical/compatibility table retains columns, dtypes, RangeIndex/index, rows, order, and empty behavior.

New exact invariant tolerance is:

```text
rel_tol = 1e-12
abs_tol = 1e-12
```

Existing Phase 1 same-process overlap tests still require `float.hex()` equality. Every overlapping metric uses the Phase 1 source iteration and summation order; pandas regrouping may not replace it if it changes a bit or row order.

## 18. Statistical calibration

Exact fraction is the deterministic reference. Aggregated sampled fraction is an estimate based on integer successes `k` and eligible sample size `n`.

### 18.1 Family definition

One family is the exact set of aligned rows produced by one comparison request after validating metric, generation range, scope, and entities. Let `m` be family size:

```text
familywise_alpha = 0.01
adjusted_alpha = familywise_alpha / m
z = NormalDist().inv_cdf(1 - adjusted_alpha / 2)
```

### 18.2 Wilson interval

For `n > 0`, `p_hat = k/n`:

```text
denom = 1 + z^2/n
center = (p_hat + z^2/(2n)) / denom
half = z/denom * sqrt(p_hat*(1-p_hat)/n + z^2/(4*n^2))
confidence_lower = max(0, center - half)
confidence_upper = min(1, center + half)
standard_error = sqrt(p_hat*(1-p_hat)/n)
within_interval = confidence_lower <= exact_fraction <= confidence_upper
```

At `n=0`, the nullable fields follow the calibration table contract. The denominator scope is explicit for every row; sample size is never inferred from a displayed percentage.

### 18.3 Deterministic correctness versus scientific calibration

Deterministic constructed-count unit tests prove formula implementation for `n=0`, `p=0`, `p=1`, one-row families, and multirow Bonferroni families.

Scientific calibration uses a fixed reviewed seed panel and at least three predeclared increasing sample sizes. It always verifies schemas, repeatability, denominators, and count conservation; it reports interval coverage and pooled RMSE and expects the largest pooled sample to improve on the smallest. It does not require every seed or adjacent size to improve.

A legitimate preregistered rejection stops for human scientific review. Seeds, family definition, alpha, sample sizes, fixtures, and tolerances are not searched or weakened after failure.

### 18.4 Approved preregistered calibration panel

Human approval of this contract freezes the following Phase 2 calibration inputs:

- seeds, in order: `(1729, 271828, 314159)`;
- total population sample sizes, in order: `(610, 6100, 61000)`;
- starting population: equal counts for every codon in `VALID_CODONS` order, respectively `10`, `100`, and `1000` copies per codon;
- exact starting weights: `1.0` for every valid codon, so exact and sampled population compositions are identical after normalization;
- mutation matrix: the existing preset `build_substitution_matrix(PRESET_AT, PRESET_AG, PRESET_AC)`, preserving `(1/6, 2/3, 1/6)` and row insertion order;
- generations: `10` post-mutation generations;
- reviewed comparison families: population category fractions among survivors, population survival/stop fractions, and cumulative outcomes for `TAA`, `TAG`, and `TGA`, each aligned across generations `1..10` by its canonical scientific keys.

This produces nine preregistered aggregate runs. For category families, the eligible denominator is the live population at that generation; for survival and stop families, it is the fixed initial population size. Reports show per-family interval coverage and pooled RMSE across the three seeds. The acceptance expectation compares the pooled `61000` result with the pooled `610` result. An unmet expectation pauses for scientific review and does not authorize changing this panel.

## 19. Structural memory contract

The deterministic memory gate is structural:

- `AggregatedSampledResult` and snapshots contain no record/path/copy collection.
- No retained collection cardinality grows with copy count.
- Snapshot count grows only with `n_generations`.
- Per-snapshot cardinality is bounded by 61 codons, 20 amino acids, five categories/traits, three stops, at most `61 x 61` start/current codon cells, and at most `61 x 3` start/stop-codon cells.
- Integer magnitude may grow with copy count; collection cardinality may not.
- Source/contract tests reject `records`, `paths`, copy identifiers, or per-copy append retention.
- Wall-clock time is not a correctness assertion.
- `tracemalloc` is advisory unless a later approved contract amendment freezes environment, warmup, measurement procedure, and bound.

Phase 2 reduces memory, not CPU complexity.

## 20. Error contract

Step 3 defines these named exceptions, each subclassing `ValueError`:

| Exception | Trigger | Message shape | UI behavior |
|---|---|---|---|
| `ExactResultProvenanceError` | Result/starting weights cannot describe the same run | `Exact result provenance mismatch for <scope>: expected <expected>, observed <observed>.` | Adapter may translate to concise error |
| `InvalidScientificScopeError` | Unknown scope/key, invalid generation, or invalid scope/key combination | `Invalid scientific scope <scope>=<key>.` | Adapter may translate |
| `UnsupportedComparisonError` | Metric/mode pairing has no approved comparison | `Unsupported comparison: <metric> for <modes>.` | Adapter may translate |
| `MetricSchemaError` | Columns, dtypes, index, duplicate keys, or row contract differ | `Metric schema mismatch for <metric>: <detail>.` | Normally diagnostic/developer error |
| `ScientificInvariantError` | Conservation, denominator, rollup, order, or tolerance failure | `Scientific invariant failed for <metric> at <scope>/generation <g>: expected <expected>, observed <observed>.` | Never silently converted to empty data |

Engine code never imports Streamlit or displays UI messages. Expected input/domain errors may be caught at adapters; unexpected failures propagate. No error becomes a silent partial or empty result.

This contract does not add substitution-probability finite/range validation to existing or new paths.

## 21. UI and compatibility adapter contract

- Aggregated mode is engine-only in Phase 2.
- Streamlit continues its frozen detailed sampled path and exact path.
- No widget, selector, automatic threshold, cache key, label, chart, table, query binding, or error changes.
- Existing labels `Sampled copies` and `Exact probability` remain.
- Exact is scientifically authoritative even though the compatibility UI permits choosing either display mode.
- Tkinter remains a compatibility adapter.
- Any aggregated UI exposure requires a Blueprint mutation, new approved UI contract/fixture, and human approval.

## 22. Fixture and testing contract

- Step 3 creates one compact reviewed static fixture at `final code/tests/fixtures/phase2_scientific_contract.json`.
- The fixture records schema metadata and compact representative results only.
- Tests never generate or rewrite it.
- Same-process exact equivalence is compared directly, including `float.hex()` and order.
- Detailed sampled output and final RNG state remain directly compared.
- Phase 1 fixtures and diagnostics remain immutable.
- Standard-library `unittest` remains the framework.
- No generator, network source, dependency, or external `$ref` is introduced.

## 23. Consumer/provider verification matrix

| Provider/consumer | Produces/consumes | Verification | Empty/error paths | Owner |
|---|---|---|---|---|
| Exact primitive | `ExactSimulationResult` | Existing exact hex/order tests | Sparse, empty, zero generation | Engine |
| Exact analysis | `ExactAnalysisResult` and exact tables | Contract fixture, same-process overlap, provenance and invariant tests | Zero starts/generations, invalid provenance | Engine |
| Aggregated provider | Aggregate dataclasses/counters | Detailed reducer equality, conservation, seed/global-RNG, structural memory tests | Empty/zero/negative-truncated starts, early stops | Engine |
| Category/summary analysis | Canonical exact/sample tables | Schema/dtype/RangeIndex/order and rollup tests | No survivors and requested zero scope | Engine |
| Numeric comparisons | Directed comparison table | Self/swap/key-alignment/schema tests | Empty family, zero baseline | Engine |
| Convergence comparisons | Status comparison table | Nullable generation/status tests | No generations, all stopped | Engine |
| Statistical calibration | Exact/sample calibration table | Constructed Wilson tests plus reviewed seed report | `sample_size=0`, extremes 0/1 | Engine/tests |
| Streamlit adapter | Existing named/legacy-compatible engine results | Frozen AppTest, cache/RNG, diagnostics | Existing validation messages | UI |
| Tkinter adapter | Legacy signatures/tuples | Legacy adapter and diagnostic tests | Existing behavior | Compatibility |
| Phase 1 regression tests | Frozen v1 surface | Immutable hashes and full suite | Existing cases | Test owner |
| Phase 2 tests | New v2 additive surface | Focused TDD and fresh-process boundaries | Every documented alternate path | Test owner |
| Python/notebook callers | Named public API/tables | Public signature and example contract tests | Explicit engine exceptions | Consumer |

Provider and consumers pass against this one contract; independent handwritten schema copies are prohibited.

## 24. Contract change protocol

1. State the consumer/scientific need and compatibility impact.
2. Propose this contract change first.
3. Record affected fields, schemas, owners, steps, files, dependencies, rollback, and version impact in the Phase 2 log.
4. Obtain explicit human approval.
5. Update typed models and the reviewed static fixture from the approved contract.
6. Write focused failing tests.
7. Update providers and consumers.
8. Run focused, full, diagnostic, boundary, and immutable-hash verification.
9. Obtain compatibility/UI approval before completion.

Implementation-first contract edits, private field renames, casts that hide runtime schema drift, and duplicate sources of truth are prohibited.

## 25. Decisions awaiting human approval

| Decision | Proposed contract | Status |
|---|---|---|
| Aggregated RNG | Required integer seed with local `random.Random(seed)` and no global side effect | Approved — accepted 2026-08-11 |
| Aggregated iteration | Copy-major streaming with detailed-reduction draw-order equivalence | Approved — accepted 2026-08-11 |
| UI exposure | Engine-only aggregated API; frozen Streamlit surface | Approved — accepted 2026-08-11 |
| Exact materialization | Eager population core plus named on-demand scoped queries | Approved — accepted 2026-08-11 |
| Relative delta at zero baseline | Nullable `pd.NA` | Approved — accepted 2026-08-11 |
| Codon stop outcomes | Both new-at-generation and cumulative-through-generation values | Approved — accepted 2026-08-11 |
| Statistical policy | Constructed Wilson/Bonferroni correctness plus reviewed fixed-seed calibration | Approved — accepted 2026-08-11 |
| Phase 2 fixture | One compact reviewed static fixture created in Step 3 | Approved — accepted 2026-08-11 |
| Exact conservation | `rel_tol=1e-12`, `abs_tol=1e-12`; Phase 1 overlaps keep hex equality | Approved — accepted 2026-08-11 |

Approval accepts all nine decisions unless the approver identifies a specific row for amendment.

## 26. Deferred and prohibited work

The contract excludes Phase 3 vectorization, transition matrices, NumPy/SciPy optimization, pruning, caching redesign, automatic sampled thresholds, new random-count algorithms, and performance refactoring. It also excludes FastAPI, Next.js, workers, queues, Redis, PostgreSQL, Kubernetes, exports, authentication, deployment, OpenAPI/service schemas, and unrelated probability validation.

## 27. Completion checklist

- [x] Provider owner and approver identified.
- [x] Current and future consumers distinguished.
- [x] One authoritative Step 2 artifact named.
- [x] New public operations and result fields specified.
- [x] Required fields, ordering, nullability, defaults, and errors explicit.
- [x] Every canonical table column and dtype specified.
- [x] RangeIndex, row order, generation numbering, canonical category/codon/AA/stop order specified.
- [x] Formulas, units, denominators, and zero behavior specified.
- [x] Exact-result provenance specified.
- [x] Detailed and aggregated RNG contracts separated.
- [x] Aggregated retained/unavailable information specified.
- [x] Reducer equality and structural memory contract specified.
- [x] Comparison direction and convergence comparison separated.
- [x] Statistical correctness and calibration separated.
- [x] Phase 1 compatibility and immutable artifacts protected.
- [x] Step 3 can derive models/tests without guessing.
- [x] All human decisions listed as proposed.
- [x] Human Scientific Contract approval recorded.

The user explicitly approved this contract on 2026-08-11. Phase 2 implementation may proceed from Blueprint Step 3 under the contract-change protocol.
