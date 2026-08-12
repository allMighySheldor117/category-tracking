"""Authoritative exact scientific tables derived from one frozen simulation."""

from __future__ import annotations

import collections
import math
import weakref
from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd

from .category_analysis import surviving_category_fraction_series
from .exact_tracking import run_simulation
from .genetic_code import (
    ALL_AAS,
    CODON_TABLE,
    PROPERTY_LABELS,
    VALID_CODONS,
    get_primary_group_name,
)
from .models import (
    ConvergenceBasis,
    ExactAnalysisResult,
    ExactResultProvenanceError,
    ExactSimulationResult,
    InvalidScientificScopeError,
    StartScope,
    StartWeights,
)
from .mutation_matrix import SubstitutionMatrix


EXACT_VALUE_KIND = "probability_weight"
CANONICAL_STOP_CODONS = ("TAA", "TAG", "TGA")
EXACT_REL_TOL = 1e-12
EXACT_ABS_TOL = 1e-12
_DERIVED_FRAME_CACHE: dict[int, dict[tuple[Any, ...], pd.DataFrame]] = {}
_DERIVED_FRAME_FINALIZERS: dict[int, weakref.finalize] = {}

CATEGORY_SCHEMA = (
    ("generation", "int64"),
    ("start_scope", "object"),
    ("start_key", "object"),
    ("category", "object"),
    ("live_value", "float64"),
    ("value_kind", "object"),
)
FRACTION_SCHEMA = (
    ("generation", "int64"),
    ("start_scope", "object"),
    ("start_key", "object"),
    ("category", "object"),
    ("numerator", "float64"),
    ("denominator", "float64"),
    ("fraction", "float64"),
)
SURVIVAL_SCHEMA = (
    ("generation", "int64"),
    ("start_scope", "object"),
    ("start_key", "object"),
    ("initial_value", "float64"),
    ("live_value", "float64"),
    ("stopped_value", "float64"),
    ("survivor_fraction", "float64"),
    ("stop_fraction", "float64"),
    ("value_kind", "object"),
)
STOP_SCHEMA = (
    ("generation", "int64"),
    ("start_scope", "object"),
    ("start_key", "object"),
    ("stop_codon", "object"),
    ("new_stop_value", "float64"),
    ("cumulative_stop_value", "float64"),
    ("initial_value", "float64"),
    ("cumulative_stop_fraction", "float64"),
    ("value_kind", "object"),
)
CODON_OUTCOME_SCHEMA = (
    ("generation", "int64"),
    ("start_codon", "object"),
    ("target_codon", "object"),
    ("target_aa", "object"),
    ("target_category", "object"),
    ("live_value", "float64"),
    ("new_stop_value", "float64"),
    ("cumulative_stop_value", "float64"),
    ("value_kind", "object"),
)
CONVERGENCE_SCHEMA = (
    ("start_scope", "object"),
    ("start_key", "object"),
    ("basis", "object"),
    ("tolerance", "float64"),
    ("generation", "Int64"),
    ("max_delta", "float64"),
    ("status", "object"),
)


def _typed_frame(
    rows: Iterable[dict[str, Any]],
    schema: tuple[tuple[str, str], ...],
) -> pd.DataFrame:
    columns = [column for column, _dtype in schema]
    frame = pd.DataFrame.from_records(rows, columns=columns)
    frame = frame.astype({column: dtype for column, dtype in schema})
    return frame.reset_index(drop=True)


def _analysis_frame_cache(analysis: ExactAnalysisResult) -> dict[tuple[Any, ...], pd.DataFrame]:
    cache_key = id(analysis)
    cache = _DERIVED_FRAME_CACHE.get(cache_key)
    if cache is None:
        cache = {}
        _DERIVED_FRAME_CACHE[cache_key] = cache
        try:
            _DERIVED_FRAME_FINALIZERS[cache_key] = weakref.finalize(
                analysis,
                _DERIVED_FRAME_CACHE.pop,
                cache_key,
                None,
            )
        except TypeError:
            pass
    return cache


def _cached_frame(
    analysis: ExactAnalysisResult,
    key: tuple[Any, ...],
    factory: Any,
) -> pd.DataFrame:
    cache = _analysis_frame_cache(analysis)
    if key not in cache:
        cache[key] = factory()
    return cache[key].copy(deep=True)


def _validate_generation_count(n_generations: int) -> None:
    if not isinstance(n_generations, int) or n_generations < 0:
        raise ValueError("n_generations must be >= 0")


def _normalize_start_weights(start_weights: StartWeights | None) -> dict[str, float]:
    supplied: Mapping[str, float]
    if start_weights is None:
        supplied = {codon: 1.0 for codon in VALID_CODONS}
    else:
        supplied = start_weights
    for codon in supplied:
        if codon not in VALID_CODONS:
            raise InvalidScientificScopeError(f"Invalid scientific scope codon={codon}.")

    normalized: dict[str, float] = {}
    for codon in VALID_CODONS:
        value = float(supplied.get(codon, 0.0))
        normalized[codon] = value if value > 0 else 0.0
    return normalized


def _provenance_error(scope: str, expected: Any, observed: Any) -> None:
    raise ExactResultProvenanceError(
        f"Exact result provenance mismatch for {scope}: "
        f"expected {expected}, observed {observed}."
    )


def _matches(expected: Any, observed: Any) -> bool:
    try:
        return math.isclose(
            float(expected),
            float(observed),
            rel_tol=EXACT_REL_TOL,
            abs_tol=EXACT_ABS_TOL,
        )
    except (TypeError, ValueError):
        return False


def _validate_provenance(
    simulation: ExactSimulationResult,
    start_weights: dict[str, float],
) -> int:
    if len(start_weights) != len(VALID_CODONS) or list(start_weights) != VALID_CODONS:
        _provenance_error("start_weight_keys", VALID_CODONS, list(start_weights))

    active_starts = [codon for codon in VALID_CODONS if start_weights[codon] > 0]
    observed_starts = list(simulation.start_to_fin)
    if observed_starts != active_starts:
        _provenance_error("active_starts", active_starts, observed_starts)

    observed_count = simulation.stats.get("n_starts")
    if observed_count != len(active_starts):
        _provenance_error("active_start_count", len(active_starts), observed_count)

    total_start_weight = sum(start_weights[codon] for codon in VALID_CODONS if start_weights[codon] > 0)
    observed_total = simulation.stats.get("total_start_copies")
    if not _matches(total_start_weight, observed_total):
        _provenance_error("total_start_weight", total_start_weight, observed_total)

    n_generations = simulation.stats.get("n_generations")
    if not isinstance(n_generations, int) or n_generations < 0:
        _provenance_error("n_generations", "int >= 0", n_generations)

    stops_by_start = simulation.stop_data.get("by_start_codon", {})
    for start_codon in active_starts:
        final_live = sum(simulation.start_to_fin[start_codon].values())
        stopped = stops_by_start.get(start_codon, 0.0)
        observed_mass = final_live + stopped
        if not _matches(start_weights[start_codon], observed_mass):
            _provenance_error(
                f"start_codon={start_codon}",
                start_weights[start_codon],
                observed_mass,
            )

    if n_generations == 0:
        for start_codon in active_starts:
            final_for_start = simulation.start_to_fin[start_codon]
            expected_items = [(start_codon, start_weights[start_codon])]
            observed_items = list(final_for_start.items())
            no_stops = _matches(0.0, stops_by_start.get(start_codon, 0.0))
            if (
                [key for key, _value in observed_items] != [start_codon]
                or not _matches(start_weights[start_codon], final_for_start.get(start_codon))
                or not no_stops
            ):
                _provenance_error("zero_generation", expected_items, observed_items)

    global_live = sum(simulation.fin_codon.values())
    global_stopped = simulation.stop_data.get("total_prob")
    observed_global = global_live + global_stopped
    if not _matches(total_start_weight, observed_global):
        _provenance_error("global_conservation", total_start_weight, observed_global)
    return n_generations


def _scope_start_codons(start_scope: StartScope, start_key: str) -> list[str]:
    if start_scope == "population" and start_key == "all":
        return list(VALID_CODONS)
    if start_scope == "codon" and start_key in VALID_CODONS:
        return [start_key]
    if start_scope == "amino_acid" and start_key in ALL_AAS:
        return [codon for codon in VALID_CODONS if CODON_TABLE[codon] == start_key]
    if start_scope == "trait" and start_key in PROPERTY_LABELS.values():
        return [
            codon
            for codon in VALID_CODONS
            if get_primary_group_name(CODON_TABLE[codon]) == start_key
        ]
    raise InvalidScientificScopeError(
        f"Invalid scientific scope {start_scope}={start_key}."
    )


def _scope_initial_weight(
    start_weights: dict[str, float],
    start_codons: list[str],
) -> float:
    return sum(start_weights[codon] for codon in start_codons)


def _category_metrics(
    simulation: ExactSimulationResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame:
    start_codons = _scope_start_codons(start_scope, start_key)
    rows: list[dict[str, Any]] = []
    per_generation = simulation.track_data["per_gen_codon_from"]
    for generation_index in range(int(simulation.stats["n_generations"])):
        counts: collections.Counter[str] = collections.Counter()
        generation = per_generation[generation_index]
        for start_codon in start_codons:
            for current_codon, weight in generation.get(start_codon, {}).items():
                category = get_primary_group_name(CODON_TABLE[current_codon])
                counts[category] += weight
        for category in PROPERTY_LABELS.values():
            rows.append(
                {
                    "generation": generation_index + 1,
                    "start_scope": start_scope,
                    "start_key": start_key,
                    "category": category,
                    "live_value": float(counts[category]),
                    "value_kind": EXACT_VALUE_KIND,
                }
            )
    return _typed_frame(rows, CATEGORY_SCHEMA)


def _survivor_fractions(category_metrics: pd.DataFrame) -> pd.DataFrame:
    legacy_input = category_metrics[["generation", "category", "live_value"]].rename(
        columns={"live_value": "value"}
    )
    legacy_fraction = surviving_category_fraction_series(legacy_input)
    rows: list[dict[str, Any]] = []
    for source, fraction in zip(
        category_metrics.itertuples(index=False),
        legacy_fraction.itertuples(index=False),
    ):
        rows.append(
            {
                "generation": source.generation,
                "start_scope": source.start_scope,
                "start_key": source.start_key,
                "category": source.category,
                "numerator": source.live_value,
                "denominator": fraction.surviving,
                "fraction": fraction.value,
            }
        )
    return _typed_frame(rows, FRACTION_SCHEMA)


def _new_stop_total(
    simulation: ExactSimulationResult,
    generation_index: int,
    start_codons: list[str],
) -> float:
    generation = simulation.track_data["per_gen_stop_codon_from"][generation_index]
    total = 0.0
    for start_codon in start_codons:
        total += generation.get(start_codon, 0.0)
    return total


def _survival_by_start(
    simulation: ExactSimulationResult,
    start_weights: dict[str, float],
    category_metrics: pd.DataFrame,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame:
    start_codons = _scope_start_codons(start_scope, start_key)
    initial_value = _scope_initial_weight(start_weights, start_codons)
    fractions = _survivor_fractions(category_metrics)
    rows: list[dict[str, Any]] = []
    cumulative_stopped = 0.0
    for generation_index in range(int(simulation.stats["n_generations"])):
        generation = generation_index + 1
        generation_fraction = fractions[fractions["generation"] == generation]
        live_value = (
            float(generation_fraction.iloc[0]["denominator"])
            if not generation_fraction.empty
            else 0.0
        )
        cumulative_stopped += _new_stop_total(
            simulation,
            generation_index,
            start_codons,
        )
        rows.append(
            {
                "generation": generation,
                "start_scope": start_scope,
                "start_key": start_key,
                "initial_value": initial_value,
                "live_value": live_value,
                "stopped_value": cumulative_stopped,
                "survivor_fraction": live_value / initial_value if initial_value else 0.0,
                "stop_fraction": cumulative_stopped / initial_value if initial_value else 0.0,
                "value_kind": EXACT_VALUE_KIND,
            }
        )
    return _typed_frame(rows, SURVIVAL_SCHEMA)


def _stop_outcomes(
    simulation: ExactSimulationResult,
    start_weights: dict[str, float],
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame:
    start_codons = _scope_start_codons(start_scope, start_key)
    initial_value = _scope_initial_weight(start_weights, start_codons)
    cumulative = {stop_codon: 0.0 for stop_codon in CANONICAL_STOP_CODONS}
    rows: list[dict[str, Any]] = []
    per_generation = simulation.track_data["per_gen_stop_codon_to"]
    for generation_index in range(int(simulation.stats["n_generations"])):
        new_values = {stop_codon: 0.0 for stop_codon in CANONICAL_STOP_CODONS}
        generation = per_generation[generation_index]
        for start_codon in start_codons:
            start_stops = generation.get(start_codon, {})
            for stop_codon in CANONICAL_STOP_CODONS:
                new_values[stop_codon] += start_stops.get(stop_codon, 0.0)
        for stop_codon in CANONICAL_STOP_CODONS:
            cumulative[stop_codon] += new_values[stop_codon]
            rows.append(
                {
                    "generation": generation_index + 1,
                    "start_scope": start_scope,
                    "start_key": start_key,
                    "stop_codon": stop_codon,
                    "new_stop_value": new_values[stop_codon],
                    "cumulative_stop_value": cumulative[stop_codon],
                    "initial_value": initial_value,
                    "cumulative_stop_fraction": (
                        cumulative[stop_codon] / initial_value if initial_value else 0.0
                    ),
                    "value_kind": EXACT_VALUE_KIND,
                }
            )
    return _typed_frame(rows, STOP_SCHEMA)


def run_exact_analysis(
    n_generations: int,
    sub_matrix: SubstitutionMatrix,
    start_weights: StartWeights | None = None,
) -> ExactAnalysisResult:
    """Run the frozen exact propagation once and build authoritative tables."""
    _validate_generation_count(n_generations)
    normalized = _normalize_start_weights(start_weights)
    simulation = run_simulation(n_generations, sub_matrix, normalized)
    return build_exact_analysis(simulation, normalized)


def build_exact_analysis(
    simulation: ExactSimulationResult,
    start_weights: StartWeights | None = None,
) -> ExactAnalysisResult:
    """Validate an existing exact result and derive its canonical tables."""
    normalized = _normalize_start_weights(start_weights)
    _validate_provenance(simulation, normalized)
    categories = _category_metrics(
        simulation,
        start_scope="population",
        start_key="all",
    )
    fractions = _survivor_fractions(categories)
    survival = _survival_by_start(
        simulation,
        normalized,
        categories,
        start_scope="population",
        start_key="all",
    )
    stops = _stop_outcomes(
        simulation,
        normalized,
        start_scope="population",
        start_key="all",
    )
    return ExactAnalysisResult(
        simulation=simulation,
        start_weights=dict(normalized),
        population_category_metrics=categories,
        population_survivor_fractions=fractions,
        population_survival=survival,
        population_stop_outcomes=stops,
    )


def get_exact_category_metrics(
    analysis: ExactAnalysisResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame:
    """Return canonical live category weights for one starting scope."""
    _scope_start_codons(start_scope, start_key)
    if start_scope == "population":
        return analysis.population_category_metrics.copy(deep=True)
    return _cached_frame(
        analysis,
        ("category_metrics", start_scope, start_key),
        lambda: _category_metrics(
            analysis.simulation,
            start_scope=start_scope,
            start_key=start_key,
        ),
    )


def get_exact_survivor_fractions(
    analysis: ExactAnalysisResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame:
    """Return category fractions among survivors for one starting scope."""
    _scope_start_codons(start_scope, start_key)
    if start_scope == "population":
        return analysis.population_survivor_fractions.copy(deep=True)
    return _cached_frame(
        analysis,
        ("survivor_fractions", start_scope, start_key),
        lambda: _survivor_fractions(
            get_exact_category_metrics(
                analysis,
                start_scope=start_scope,
                start_key=start_key,
            )
        ),
    )


def get_exact_survival_by_start(
    analysis: ExactAnalysisResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame:
    """Return live and cumulative-stop weights against the explicit start base."""
    _scope_start_codons(start_scope, start_key)
    if start_scope == "population":
        return analysis.population_survival.copy(deep=True)
    return _cached_frame(
        analysis,
        ("survival_by_start", start_scope, start_key),
        lambda: _survival_by_start(
            analysis.simulation,
            analysis.start_weights,
            get_exact_category_metrics(
                analysis,
                start_scope=start_scope,
                start_key=start_key,
            ),
            start_scope=start_scope,
            start_key=start_key,
        ),
    )


def get_exact_stop_outcomes(
    analysis: ExactAnalysisResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame:
    """Return new and cumulative exact stop weights in canonical stop order."""
    _scope_start_codons(start_scope, start_key)
    if start_scope == "population":
        return analysis.population_stop_outcomes.copy(deep=True)
    return _cached_frame(
        analysis,
        ("stop_outcomes", start_scope, start_key),
        lambda: _stop_outcomes(
            analysis.simulation,
            analysis.start_weights,
            start_scope=start_scope,
            start_key=start_key,
        ),
    )


def get_exact_codon_outcomes(
    analysis: ExactAnalysisResult,
    *,
    start_codon: str,
    generation: int,
) -> pd.DataFrame:
    """Return all sense and stop outcomes for one start and generation."""
    _scope_start_codons("codon", start_codon)
    n_generations = int(analysis.simulation.stats["n_generations"])
    if not isinstance(generation, int) or generation < 1 or generation > n_generations:
        raise InvalidScientificScopeError(
            f"Invalid scientific scope generation={generation}."
        )

    return _cached_frame(
        analysis,
        ("codon_outcomes", start_codon, generation),
        lambda: _codon_outcomes(analysis, start_codon, generation),
    )


def _codon_outcomes(
    analysis: ExactAnalysisResult,
    start_codon: str,
    generation: int,
) -> pd.DataFrame:
    generation_index = generation - 1
    live = analysis.simulation.track_data["per_gen_codon_from"][generation_index].get(
        start_codon,
        {},
    )
    new_stops = analysis.simulation.track_data["per_gen_stop_codon_to"][generation_index].get(
        start_codon,
        {},
    )
    cumulative = {stop_codon: 0.0 for stop_codon in CANONICAL_STOP_CODONS}
    for stop_generation_index in range(generation):
        generation_stops = analysis.simulation.track_data["per_gen_stop_codon_to"][
            stop_generation_index
        ].get(start_codon, {})
        for stop_codon in CANONICAL_STOP_CODONS:
            cumulative[stop_codon] += generation_stops.get(stop_codon, 0.0)

    rows: list[dict[str, Any]] = []
    for target_codon in VALID_CODONS:
        target_aa = CODON_TABLE[target_codon]
        rows.append(
            {
                "generation": generation,
                "start_codon": start_codon,
                "target_codon": target_codon,
                "target_aa": target_aa,
                "target_category": get_primary_group_name(target_aa),
                "live_value": float(live.get(target_codon, 0.0)),
                "new_stop_value": 0.0,
                "cumulative_stop_value": 0.0,
                "value_kind": EXACT_VALUE_KIND,
            }
        )
    for stop_codon in CANONICAL_STOP_CODONS:
        rows.append(
            {
                "generation": generation,
                "start_codon": start_codon,
                "target_codon": stop_codon,
                "target_aa": "Stop",
                "target_category": "Stop",
                "live_value": 0.0,
                "new_stop_value": float(new_stops.get(stop_codon, 0.0)),
                "cumulative_stop_value": cumulative[stop_codon],
                "value_kind": EXACT_VALUE_KIND,
            }
        )
    return _typed_frame(rows, CODON_OUTCOME_SCHEMA)


def get_exact_convergence(
    analysis: ExactAnalysisResult,
    *,
    start_scope: StartScope,
    start_key: str,
    basis: ConvergenceBasis,
    tolerance: float,
) -> pd.DataFrame:
    """Return the first generation stable against every later category vector."""
    _scope_start_codons(start_scope, start_key)
    if basis not in {"category_weight", "survivor_fraction"}:
        raise InvalidScientificScopeError(
            f"Invalid scientific scope convergence_basis={basis}."
        )
    tolerance_value = float(tolerance)
    return _cached_frame(
        analysis,
        ("convergence", start_scope, start_key, basis, tolerance_value),
        lambda: _convergence(
            analysis,
            start_scope=start_scope,
            start_key=start_key,
            basis=basis,
            tolerance_value=tolerance_value,
        ),
    )


def _convergence(
    analysis: ExactAnalysisResult,
    *,
    start_scope: StartScope,
    start_key: str,
    basis: ConvergenceBasis,
    tolerance_value: float,
) -> pd.DataFrame:
    categories = get_exact_category_metrics(
        analysis,
        start_scope=start_scope,
        start_key=start_key,
    )
    source = (
        categories.rename(columns={"live_value": "basis_value"})
        if basis == "category_weight"
        else get_exact_survivor_fractions(
            analysis,
            start_scope=start_scope,
            start_key=start_key,
        ).rename(columns={"fraction": "basis_value"})
    )

    vectors: list[tuple[float, ...]] = []
    n_generations = int(analysis.simulation.stats["n_generations"])
    for generation in range(1, n_generations + 1):
        generation_rows = source[source["generation"] == generation]
        vectors.append(tuple(float(value) for value in generation_rows["basis_value"]))

    selected_generation: int | Any = pd.NA
    selected_delta = 0.0
    status = "no_generations"
    maximum_observed_delta = 0.0
    for index, vector in enumerate(vectors):
        candidate_delta = 0.0
        for future in vectors[index:]:
            for current, reference in zip(future, vector):
                candidate_delta = max(candidate_delta, abs(current - reference))
        maximum_observed_delta = max(maximum_observed_delta, candidate_delta)
        if candidate_delta <= tolerance_value:
            selected_generation = index + 1
            selected_delta = candidate_delta
            all_stopped = all(
                all(value == 0.0 for value in future)
                for future in vectors[index:]
            )
            status = "all_stopped" if all_stopped else "stable"
            break
    else:
        if vectors:
            selected_delta = maximum_observed_delta
            status = "still_changing"

    return _typed_frame(
        [
            {
                "start_scope": start_scope,
                "start_key": start_key,
                "basis": basis,
                "tolerance": tolerance_value,
                "generation": selected_generation,
                "max_delta": selected_delta,
                "status": status,
            }
        ],
        CONVERGENCE_SCHEMA,
    )
