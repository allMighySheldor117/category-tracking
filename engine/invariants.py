"""Non-mutating scientific invariant validators for authoritative engine data."""

from __future__ import annotations

import collections
import math
from typing import Any

import pandas as pd

from .exact_analysis import (
    CATEGORY_SCHEMA,
    CONVERGENCE_SCHEMA,
    FRACTION_SCHEMA,
    STOP_SCHEMA,
    SURVIVAL_SCHEMA,
    get_exact_category_metrics,
    get_exact_convergence,
    get_exact_stop_outcomes,
    get_exact_survival_by_start,
    get_exact_survivor_fractions,
)
from .genetic_code import (
    ALL_AAS,
    BASES,
    CODON_TABLE,
    PROPERTY_LABELS,
    STOP_CODONS,
    VALID_CODONS,
    get_primary_group_name,
)
from .models import (
    ExactAnalysisResult,
    ScientificInvariantError,
    ScientificInvariantReport,
)
from .mutation_matrix import SubstitutionMatrix


EXACT_REL_TOL = 1e-12
EXACT_ABS_TOL = 1e-12
CANONICAL_STOP_CODONS = ("TAA", "TAG", "TGA")
CANONICAL_ROW_TARGETS = {
    "A": ("C", "G", "T"),
    "C": ("A", "G", "T"),
    "G": ("A", "C", "T"),
    "T": ("A", "C", "G"),
}


def _fail(
    metric: str,
    scope: str,
    generation: int | None,
    expected: Any,
    observed: Any,
    tolerance: float,
) -> None:
    raise ScientificInvariantError(
        f"Scientific invariant failed for {metric} at {scope}/generation "
        f"{generation}: expected {expected}, observed {observed} "
        f"(tolerance {tolerance})."
    )


def _record(
    reports: list[ScientificInvariantReport],
    metric: str,
    scope: str,
    generation: int | None,
    expected: Any,
    observed: Any,
    tolerance: float,
    passed: bool,
) -> None:
    if not passed:
        _fail(metric, scope, generation, expected, observed, tolerance)
    reports.append(
        ScientificInvariantReport(
            metric=metric,
            scope=scope,
            generation=generation,
            expected=expected,
            observed=observed,
            tolerance=tolerance,
        )
    )


def _close(expected: Any, observed: Any) -> bool:
    try:
        return math.isclose(
            float(expected),
            float(observed),
            rel_tol=EXACT_REL_TOL,
            abs_tol=EXACT_ABS_TOL,
        )
    except (TypeError, ValueError):
        return False


def _frame_schema(frame: pd.DataFrame) -> dict[str, Any]:
    index = frame.index
    index_contract = (
        type(index).__name__,
        getattr(index, "start", None),
        getattr(index, "stop", None),
        getattr(index, "step", None),
    )
    return {
        "columns": tuple(frame.columns),
        "dtypes": tuple(str(dtype) for dtype in frame.dtypes),
        "index": index_contract,
    }


def _expected_schema(
    schema: tuple[tuple[str, str], ...],
    row_count: int,
) -> dict[str, Any]:
    return {
        "columns": tuple(column for column, _dtype in schema),
        "dtypes": tuple(dtype for _column, dtype in schema),
        "index": ("RangeIndex", 0, row_count, 1),
    }


def _validate_schema(
    reports: list[ScientificInvariantReport],
    metric: str,
    scope: str,
    frame: pd.DataFrame,
    schema: tuple[tuple[str, str], ...],
) -> None:
    expected = _expected_schema(schema, len(frame))
    observed = _frame_schema(frame)
    _record(reports, metric, scope, None, expected, observed, 0.0, observed == expected)


def validate_biological_invariants() -> tuple[ScientificInvariantReport, ...]:
    """Validate canonical codon counts, order, and stop definitions."""
    reports: list[ScientificInvariantReport] = []
    _record(
        reports,
        "codon_table_count",
        "biology",
        None,
        64,
        len(CODON_TABLE),
        0.0,
        len(CODON_TABLE) == 64,
    )
    observed_stops = tuple(sorted(STOP_CODONS))
    _record(
        reports,
        "stop_codons",
        "biology",
        None,
        CANONICAL_STOP_CODONS,
        observed_stops,
        0.0,
        observed_stops == CANONICAL_STOP_CODONS,
    )
    _record(
        reports,
        "sense_codon_count",
        "biology",
        None,
        61,
        len(VALID_CODONS),
        0.0,
        len(VALID_CODONS) == 61,
    )
    expected_valid = sorted(
        first + second + third
        for first in BASES
        for second in BASES
        for third in BASES
        if first + second + third not in STOP_CODONS
    )
    _record(
        reports,
        "sense_codon_order",
        "biology",
        None,
        tuple(expected_valid),
        tuple(VALID_CODONS),
        0.0,
        VALID_CODONS == expected_valid,
    )
    observed_stop_labels = tuple(CODON_TABLE.get(codon) for codon in CANONICAL_STOP_CODONS)
    _record(
        reports,
        "stop_codon_labels",
        "biology",
        None,
        ("Stop", "Stop", "Stop"),
        observed_stop_labels,
        0.0,
        observed_stop_labels == ("Stop", "Stop", "Stop"),
    )
    return tuple(reports)


def validate_mutation_matrix(
    sub_matrix: SubstitutionMatrix,
) -> tuple[ScientificInvariantReport, ...]:
    """Validate mutation row shape, insertion order, and supplied row sums."""
    reports: list[ScientificInvariantReport] = []
    observed_bases = tuple(sub_matrix)
    expected_bases = tuple(BASES)
    _record(
        reports,
        "mutation_base_order",
        "mutation_matrix",
        None,
        expected_bases,
        observed_bases,
        0.0,
        observed_bases == expected_bases,
    )
    reference_sum = sum(sub_matrix["A"].values())
    for base in BASES:
        observed_targets = tuple(sub_matrix[base])
        expected_targets = CANONICAL_ROW_TARGETS[base]
        _record(
            reports,
            "mutation_row_targets",
            f"base={base}",
            None,
            expected_targets,
            observed_targets,
            0.0,
            observed_targets == expected_targets,
        )
        observed_sum = sum(sub_matrix[base].values())
        _record(
            reports,
            "mutation_row_sum",
            f"base={base}",
            None,
            reference_sum,
            observed_sum,
            EXACT_ABS_TOL,
            _close(reference_sum, observed_sum),
        )
    return tuple(reports)


def _scopes() -> list[tuple[str, str, list[str]]]:
    scopes: list[tuple[str, str, list[str]]] = [
        ("population", "all", list(VALID_CODONS))
    ]
    scopes.extend(("codon", codon, [codon]) for codon in VALID_CODONS)
    scopes.extend(
        (
            "amino_acid",
            amino_acid,
            [codon for codon in VALID_CODONS if CODON_TABLE[codon] == amino_acid],
        )
        for amino_acid in ALL_AAS
    )
    scopes.extend(
        (
            "trait",
            trait,
            [
                codon
                for codon in VALID_CODONS
                if get_primary_group_name(CODON_TABLE[codon]) == trait
            ],
        )
        for trait in PROPERTY_LABELS.values()
    )
    return scopes


def _validate_generation_rows(
    reports: list[ScientificInvariantReport],
    metric: str,
    scope: str,
    observed: list[int],
    expected: list[int],
) -> None:
    _record(
        reports,
        metric,
        scope,
        None,
        tuple(expected),
        tuple(observed),
        0.0,
        observed == expected,
    )


def _validate_deterministic_frame(
    reports: list[ScientificInvariantReport],
    scope: str,
    name: str,
    first: pd.DataFrame,
    second: pd.DataFrame,
) -> None:
    observed = first.equals(second) and _frame_schema(first) == _frame_schema(second)
    _record(
        reports,
        "deterministic_tables",
        f"{scope}/{name}",
        None,
        True,
        observed,
        0.0,
        observed,
    )


def _expected_convergence(
    frame: pd.DataFrame,
    value_column: str,
    n_generations: int,
    tolerance: float,
) -> tuple[int | None, float, str]:
    vectors = [
        tuple(
            float(value)
            for value in frame.loc[frame["generation"] == generation, value_column]
        )
        for generation in range(1, n_generations + 1)
    ]
    if not vectors:
        return None, 0.0, "no_generations"
    maximum_delta = 0.0
    for index, vector in enumerate(vectors):
        candidate_delta = 0.0
        for future in vectors[index:]:
            for current, reference in zip(future, vector):
                candidate_delta = max(candidate_delta, abs(current - reference))
        maximum_delta = max(maximum_delta, candidate_delta)
        if candidate_delta <= tolerance:
            all_stopped = all(
                all(value == 0.0 for value in future)
                for future in vectors[index:]
            )
            return index + 1, candidate_delta, "all_stopped" if all_stopped else "stable"
    return None, maximum_delta, "still_changing"


def _validate_population_rollups(
    reports: list[ScientificInvariantReport],
    analysis: ExactAnalysisResult,
) -> None:
    n_generations = int(analysis.simulation.stats["n_generations"])
    per_generation = analysis.simulation.track_data["per_gen_codon_from"]
    for generation_index in range(n_generations):
        generation = generation_index + 1
        codon_counts: collections.Counter[str] = collections.Counter()
        for start_codon in VALID_CODONS:
            for current_codon, weight in per_generation[generation_index].get(
                start_codon,
                {},
            ).items():
                codon_counts[current_codon] += weight
        amino_acid_from_codons: collections.Counter[str] = collections.Counter()
        for current_codon in VALID_CODONS:
            amino_acid_from_codons[CODON_TABLE[current_codon]] += codon_counts[current_codon]
        observed_amino_acids = analysis.simulation.per_gen_aa[generation_index]
        amino_acid_pairs = tuple(
            (
                amino_acid,
                float(amino_acid_from_codons[amino_acid]),
                float(observed_amino_acids[amino_acid]),
            )
            for amino_acid in ALL_AAS
        )
        _record(
            reports,
            "codon_to_amino_acid_rollup",
            "population",
            generation,
            "all amino-acid weights match",
            amino_acid_pairs,
            EXACT_ABS_TOL,
            all(_close(expected, observed) for _aa, expected, observed in amino_acid_pairs),
        )

        category_from_amino_acids: collections.Counter[str] = collections.Counter()
        for amino_acid in ALL_AAS:
            category_from_amino_acids[get_primary_group_name(amino_acid)] += (
                observed_amino_acids[amino_acid]
            )
        category_rows = analysis.population_category_metrics[
            analysis.population_category_metrics["generation"] == generation
        ]
        category_pairs = tuple(
            (
                category,
                float(category_from_amino_acids[category]),
                float(
                    category_rows.loc[
                        category_rows["category"] == category,
                        "live_value",
                    ].iloc[0]
                ),
            )
            for category in PROPERTY_LABELS.values()
        )
        _record(
            reports,
            "amino_acid_to_category_rollup",
            "population",
            generation,
            "all category weights match",
            category_pairs,
            EXACT_ABS_TOL,
            all(
                _close(expected, observed)
                for _category, expected, observed in category_pairs
            ),
        )


def validate_exact_analysis(
    analysis: ExactAnalysisResult,
) -> tuple[ScientificInvariantReport, ...]:
    """Validate exact schemas, conservation, rollups, denominators, and status."""
    reports: list[ScientificInvariantReport] = []
    n_generations = int(analysis.simulation.stats["n_generations"])

    _validate_schema(
        reports,
        "category_metrics_schema",
        "population",
        analysis.population_category_metrics,
        CATEGORY_SCHEMA,
    )
    _validate_schema(
        reports,
        "survivor_fractions_schema",
        "population",
        analysis.population_survivor_fractions,
        FRACTION_SCHEMA,
    )
    _validate_schema(
        reports,
        "survival_schema",
        "population",
        analysis.population_survival,
        SURVIVAL_SCHEMA,
    )
    _validate_schema(
        reports,
        "stop_outcomes_schema",
        "population",
        analysis.population_stop_outcomes,
        STOP_SCHEMA,
    )
    _validate_generation_rows(
        reports,
        "category_generation_rows",
        "population",
        analysis.population_category_metrics["generation"].tolist(),
        [generation for generation in range(1, n_generations + 1) for _ in range(5)],
    )
    _validate_generation_rows(
        reports,
        "fraction_generation_rows",
        "population",
        analysis.population_survivor_fractions["generation"].tolist(),
        [generation for generation in range(1, n_generations + 1) for _ in range(5)],
    )
    _validate_generation_rows(
        reports,
        "survival_generation_rows",
        "population",
        analysis.population_survival["generation"].tolist(),
        list(range(1, n_generations + 1)),
    )
    _validate_generation_rows(
        reports,
        "stop_generation_rows",
        "population",
        analysis.population_stop_outcomes["generation"].tolist(),
        [generation for generation in range(1, n_generations + 1) for _ in range(3)],
    )
    expected_category_order = list(PROPERTY_LABELS.values()) * n_generations
    observed_category_order = analysis.population_category_metrics["category"].tolist()
    observed_fraction_order = analysis.population_survivor_fractions["category"].tolist()
    _record(
        reports,
        "category_order",
        "population/category_metrics",
        None,
        tuple(expected_category_order),
        tuple(observed_category_order),
        0.0,
        observed_category_order == expected_category_order,
    )
    _record(
        reports,
        "category_order",
        "population/survivor_fractions",
        None,
        tuple(expected_category_order),
        tuple(observed_fraction_order),
        0.0,
        observed_fraction_order == expected_category_order,
    )
    expected_stop_order = list(CANONICAL_STOP_CODONS) * n_generations
    observed_stop_order = analysis.population_stop_outcomes["stop_codon"].tolist()
    _record(
        reports,
        "stop_codon_order",
        "population",
        None,
        tuple(expected_stop_order),
        tuple(observed_stop_order),
        0.0,
        observed_stop_order == expected_stop_order,
    )

    _validate_population_rollups(reports, analysis)

    for start_scope, start_key, start_codons in _scopes():
        scope = f"{start_scope}={start_key}"
        survival = get_exact_survival_by_start(
            analysis,
            start_scope=start_scope,
            start_key=start_key,
        )
        survival_repeat = get_exact_survival_by_start(
            analysis,
            start_scope=start_scope,
            start_key=start_key,
        )
        _validate_deterministic_frame(
            reports,
            scope,
            "survival",
            survival,
            survival_repeat,
        )
        categories = get_exact_category_metrics(
            analysis,
            start_scope=start_scope,
            start_key=start_key,
        )
        categories_repeat = get_exact_category_metrics(
            analysis,
            start_scope=start_scope,
            start_key=start_key,
        )
        _validate_deterministic_frame(
            reports,
            scope,
            "categories",
            categories,
            categories_repeat,
        )
        fractions = get_exact_survivor_fractions(
            analysis,
            start_scope=start_scope,
            start_key=start_key,
        )
        fractions_repeat = get_exact_survivor_fractions(
            analysis,
            start_scope=start_scope,
            start_key=start_key,
        )
        _validate_deterministic_frame(
            reports,
            scope,
            "fractions",
            fractions,
            fractions_repeat,
        )
        stops = get_exact_stop_outcomes(
            analysis,
            start_scope=start_scope,
            start_key=start_key,
        )
        stops_repeat = get_exact_stop_outcomes(
            analysis,
            start_scope=start_scope,
            start_key=start_key,
        )
        _validate_deterministic_frame(reports, scope, "stops", stops, stops_repeat)

        _validate_schema(reports, "category_metrics_schema", scope, categories, CATEGORY_SCHEMA)
        _validate_schema(reports, "survivor_fractions_schema", scope, fractions, FRACTION_SCHEMA)
        _validate_schema(reports, "survival_schema", scope, survival, SURVIVAL_SCHEMA)
        _validate_schema(reports, "stop_outcomes_schema", scope, stops, STOP_SCHEMA)
        scope_category_order = categories["category"].tolist()
        scope_fraction_order = fractions["category"].tolist()
        _record(
            reports,
            "category_order",
            f"{scope}/category_metrics",
            None,
            tuple(expected_category_order),
            tuple(scope_category_order),
            0.0,
            scope_category_order == expected_category_order,
        )
        _record(
            reports,
            "category_order",
            f"{scope}/survivor_fractions",
            None,
            tuple(expected_category_order),
            tuple(scope_fraction_order),
            0.0,
            scope_fraction_order == expected_category_order,
        )
        scope_stop_order = stops["stop_codon"].tolist()
        _record(
            reports,
            "stop_codon_order",
            scope,
            None,
            tuple(expected_stop_order),
            tuple(scope_stop_order),
            0.0,
            scope_stop_order == expected_stop_order,
        )
        expected_initial = sum(analysis.start_weights[codon] for codon in start_codons)
        prior_cumulative_stops = {
            stop_codon: 0.0 for stop_codon in CANONICAL_STOP_CODONS
        }

        for generation in range(1, n_generations + 1):
            survival_row = survival[survival["generation"] == generation].iloc[0]
            _record(
                reports,
                "start_denominator",
                scope,
                generation,
                expected_initial,
                float(survival_row["initial_value"]),
                EXACT_ABS_TOL,
                _close(expected_initial, survival_row["initial_value"]),
            )
            observed_conservation = float(
                survival_row["live_value"] + survival_row["stopped_value"]
            )
            _record(
                reports,
                "exact_conservation",
                scope,
                generation,
                expected_initial,
                observed_conservation,
                EXACT_ABS_TOL,
                _close(expected_initial, observed_conservation),
            )

            category_rows = categories[categories["generation"] == generation]
            fraction_rows = fractions[fractions["generation"] == generation]
            live_denominator = sum(float(value) for value in category_rows["live_value"])
            for category_row, fraction_row in zip(
                category_rows.itertuples(index=False),
                fraction_rows.itertuples(index=False),
            ):
                expected_fraction = (
                    float(category_row.live_value) / live_denominator
                    if live_denominator
                    else 0.0
                )
                fraction_observed = (
                    float(fraction_row.numerator),
                    float(fraction_row.denominator),
                    float(fraction_row.fraction),
                )
                fraction_expected = (
                    float(category_row.live_value),
                    live_denominator,
                    expected_fraction,
                )
                _record(
                    reports,
                    "category_fraction",
                    f"{scope}/{category_row.category}",
                    generation,
                    fraction_expected,
                    fraction_observed,
                    EXACT_ABS_TOL,
                    all(
                        _close(expected, observed)
                        for expected, observed in zip(fraction_expected, fraction_observed)
                    ),
                )
            fraction_sum = sum(float(value) for value in fraction_rows["fraction"])
            expected_fraction_sum = 1.0 if live_denominator > 0 else 0.0
            _record(
                reports,
                "category_fraction_sum",
                scope,
                generation,
                expected_fraction_sum,
                fraction_sum,
                EXACT_ABS_TOL,
                _close(expected_fraction_sum, fraction_sum),
            )

            stop_rows = stops[stops["generation"] == generation]
            stop_initials = tuple(float(value) for value in stop_rows["initial_value"])
            _record(
                reports,
                "stop_denominator",
                scope,
                generation,
                (expected_initial,) * 3,
                stop_initials,
                EXACT_ABS_TOL,
                all(_close(expected_initial, value) for value in stop_initials),
            )
            for stop_row in stop_rows.itertuples(index=False):
                expected_cumulative = (
                    prior_cumulative_stops[stop_row.stop_codon]
                    + float(stop_row.new_stop_value)
                )
                _record(
                    reports,
                    "stop_cumulative_progression",
                    f"{scope}/{stop_row.stop_codon}",
                    generation,
                    expected_cumulative,
                    float(stop_row.cumulative_stop_value),
                    EXACT_ABS_TOL,
                    _close(expected_cumulative, stop_row.cumulative_stop_value),
                )
                prior_cumulative_stops[stop_row.stop_codon] = float(
                    stop_row.cumulative_stop_value
                )
            stopped_from_codons = sum(
                float(value) for value in stop_rows["cumulative_stop_value"]
            )
            _record(
                reports,
                "stop_rollup",
                scope,
                generation,
                float(survival_row["stopped_value"]),
                stopped_from_codons,
                EXACT_ABS_TOL,
                _close(survival_row["stopped_value"], stopped_from_codons),
            )

        for basis, value_column, source in (
            ("category_weight", "live_value", categories),
            ("survivor_fraction", "fraction", fractions),
        ):
            tolerance = 0.0
            convergence = get_exact_convergence(
                analysis,
                start_scope=start_scope,
                start_key=start_key,
                basis=basis,
                tolerance=tolerance,
            )
            _validate_schema(
                reports,
                "convergence_schema",
                f"{scope}/{basis}",
                convergence,
                CONVERGENCE_SCHEMA,
            )
            expected_generation, expected_delta, expected_status = _expected_convergence(
                source,
                value_column,
                n_generations,
                tolerance,
            )
            observed_row = convergence.iloc[0]
            observed_generation = (
                None if pd.isna(observed_row["generation"]) else int(observed_row["generation"])
            )
            expected = (expected_generation, expected_delta, expected_status, tolerance)
            observed = (
                observed_generation,
                float(observed_row["max_delta"]),
                observed_row["status"],
                float(observed_row["tolerance"]),
            )
            passed = (
                observed_generation == expected_generation
                and _close(expected_delta, observed[1])
                and observed[2] == expected_status
                and _close(tolerance, observed[3])
            )
            _record(
                reports,
                "convergence",
                f"{scope}/{basis}",
                expected_generation,
                expected,
                observed,
                tolerance,
                passed,
            )
    return tuple(reports)
