"""Schema-validated directed comparisons for authoritative exact tables."""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any, NamedTuple

import pandas as pd

from .exact_analysis import (
    CATEGORY_SCHEMA,
    CODON_OUTCOME_SCHEMA,
    CONVERGENCE_SCHEMA,
    FRACTION_SCHEMA,
    STOP_SCHEMA,
    SURVIVAL_SCHEMA,
)
from .genetic_code import PROPERTY_LABELS, VALID_CODONS
from .models import (
    ComparisonResult,
    ConvergenceComparisonResult,
    ExactSampledComparisonResult,
    MetricName,
    MetricSchemaError,
    UnsupportedComparisonError,
)


CANONICAL_STOP_CODONS = ("TAA", "TAG", "TGA")
CANONICAL_STATUSES = ("stable", "all_stopped", "still_changing", "no_generations")
NUMERIC_COMPARISON_SCHEMA = (
    ("generation", "Int64"),
    ("metric", "object"),
    ("entity", "object"),
    ("baseline_label", "object"),
    ("candidate_label", "object"),
    ("baseline_value", "float64"),
    ("candidate_value", "float64"),
    ("signed_delta", "float64"),
    ("absolute_delta", "float64"),
    ("relative_delta", "Float64"),
    ("direction", "object"),
)
CONVERGENCE_COMPARISON_SCHEMA = (
    ("start_scope", "object"),
    ("start_key", "object"),
    ("basis", "object"),
    ("baseline_label", "object"),
    ("candidate_label", "object"),
    ("baseline_generation", "Int64"),
    ("candidate_generation", "Int64"),
    ("generation_delta", "Int64"),
    ("baseline_status", "object"),
    ("candidate_status", "object"),
)
EXACT_SAMPLED_COMPARISON_SCHEMA = (
    ("generation", "int64"),
    ("metric", "object"),
    ("entity", "object"),
    ("denominator_scope", "object"),
    ("exact_fraction", "float64"),
    ("sampled_fraction", "Float64"),
    ("signed_error", "Float64"),
    ("absolute_error", "Float64"),
    ("sample_size", "int64"),
    ("standard_error", "Float64"),
    ("adjusted_alpha", "float64"),
    ("family_size", "int64"),
    ("confidence_lower", "Float64"),
    ("confidence_upper", "Float64"),
    ("within_interval", "boolean"),
)


class _MetricContract(NamedTuple):
    schema: tuple[tuple[str, str], ...]
    value_column: str
    key_columns: tuple[str, ...]
    entity_column: str | None
    scenario_columns: tuple[str, ...]
    entity_order: tuple[str, ...]


class _CalibrationContract(NamedTuple):
    metric_contract: _MetricContract
    sampled_schema: tuple[tuple[str, str], ...]
    success_column: str
    denominator_column: str
    denominator_scope: str


METRIC_CONTRACTS: dict[str, _MetricContract] = {
    "category_live_value": _MetricContract(
        CATEGORY_SCHEMA,
        "live_value",
        ("generation", "category"),
        "category",
        ("start_scope", "start_key"),
        tuple(PROPERTY_LABELS.values()),
    ),
    "category_fraction": _MetricContract(
        FRACTION_SCHEMA,
        "fraction",
        ("generation", "category"),
        "category",
        ("start_scope", "start_key"),
        tuple(PROPERTY_LABELS.values()),
    ),
    "survivor_fraction": _MetricContract(
        SURVIVAL_SCHEMA,
        "survivor_fraction",
        ("generation",),
        None,
        ("start_scope", "start_key"),
        ("all",),
    ),
    "stop_fraction": _MetricContract(
        SURVIVAL_SCHEMA,
        "stop_fraction",
        ("generation",),
        None,
        ("start_scope", "start_key"),
        ("all",),
    ),
    "new_stop_value": _MetricContract(
        STOP_SCHEMA,
        "new_stop_value",
        ("generation", "stop_codon"),
        "stop_codon",
        ("start_scope", "start_key"),
        CANONICAL_STOP_CODONS,
    ),
    "cumulative_stop_value": _MetricContract(
        STOP_SCHEMA,
        "cumulative_stop_value",
        ("generation", "stop_codon"),
        "stop_codon",
        ("start_scope", "start_key"),
        CANONICAL_STOP_CODONS,
    ),
    "cumulative_stop_fraction": _MetricContract(
        STOP_SCHEMA,
        "cumulative_stop_fraction",
        ("generation", "stop_codon"),
        "stop_codon",
        ("start_scope", "start_key"),
        CANONICAL_STOP_CODONS,
    ),
    "codon_live_value": _MetricContract(
        CODON_OUTCOME_SCHEMA,
        "live_value",
        ("generation", "target_codon"),
        "target_codon",
        ("start_codon",),
        tuple(VALID_CODONS) + CANONICAL_STOP_CODONS,
    ),
    "codon_new_stop_value": _MetricContract(
        CODON_OUTCOME_SCHEMA,
        "new_stop_value",
        ("generation", "target_codon"),
        "target_codon",
        ("start_codon",),
        tuple(VALID_CODONS) + CANONICAL_STOP_CODONS,
    ),
    "codon_cumulative_stop_value": _MetricContract(
        CODON_OUTCOME_SCHEMA,
        "cumulative_stop_value",
        ("generation", "target_codon"),
        "target_codon",
        ("start_codon",),
        tuple(VALID_CODONS) + CANONICAL_STOP_CODONS,
    ),
}


def _sampled_schema(
    exact_schema: tuple[tuple[str, str], ...],
    integer_columns: set[str],
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (column, "int64" if column in integer_columns else dtype)
        for column, dtype in exact_schema
    )


CALIBRATION_CONTRACTS: dict[str, _CalibrationContract] = {
    "category_fraction": _CalibrationContract(
        METRIC_CONTRACTS["category_fraction"],
        _sampled_schema(FRACTION_SCHEMA, {"numerator", "denominator"}),
        "numerator",
        "denominator",
        "live_population",
    ),
    "survivor_fraction": _CalibrationContract(
        METRIC_CONTRACTS["survivor_fraction"],
        _sampled_schema(
            SURVIVAL_SCHEMA,
            {"initial_value", "live_value", "stopped_value"},
        ),
        "live_value",
        "initial_value",
        "population_initial",
    ),
    "stop_fraction": _CalibrationContract(
        METRIC_CONTRACTS["stop_fraction"],
        _sampled_schema(
            SURVIVAL_SCHEMA,
            {"initial_value", "live_value", "stopped_value"},
        ),
        "stopped_value",
        "initial_value",
        "population_initial",
    ),
    "cumulative_stop_fraction": _CalibrationContract(
        METRIC_CONTRACTS["cumulative_stop_fraction"],
        _sampled_schema(
            STOP_SCHEMA,
            {"new_stop_value", "cumulative_stop_value", "initial_value"},
        ),
        "cumulative_stop_value",
        "initial_value",
        "population_initial",
    ),
}


def _typed_frame(
    rows: list[dict[str, Any]],
    schema: tuple[tuple[str, str], ...],
) -> pd.DataFrame:
    columns = [column for column, _dtype in schema]
    frame = pd.DataFrame.from_records(rows, columns=columns)
    frame = frame.astype({column: dtype for column, dtype in schema})
    return frame.reset_index(drop=True)


def _schema_error(metric: str, detail: str) -> None:
    raise MetricSchemaError(f"Metric schema mismatch for {metric}: {detail}.")


def _schema_signature(frame: pd.DataFrame) -> tuple[Any, ...]:
    index = frame.index
    return (
        tuple(frame.columns),
        tuple(str(dtype) for dtype in frame.dtypes),
        type(index).__name__,
        getattr(index, "start", None),
        getattr(index, "stop", None),
        getattr(index, "step", None),
    )


def _expected_signature(
    schema: tuple[tuple[str, str], ...],
    row_count: int,
) -> tuple[Any, ...]:
    return (
        tuple(column for column, _dtype in schema),
        tuple(dtype for _column, dtype in schema),
        "RangeIndex",
        0,
        row_count,
        1,
    )


def _validate_schema(
    table: pd.DataFrame,
    schema: tuple[tuple[str, str], ...],
    metric: str,
) -> None:
    expected = _expected_signature(schema, len(table))
    observed = _schema_signature(table)
    if observed != expected:
        _schema_error(metric, f"expected {expected}, observed {observed}")


def _validate_numeric_source(
    table: pd.DataFrame,
    metric: str,
    contract: _MetricContract,
) -> None:
    _validate_schema(table, contract.schema, metric)
    if table.empty:
        return
    scenarios = table.loc[:, list(contract.scenario_columns)].drop_duplicates()
    if len(scenarios) != 1:
        _schema_error(metric, "each input must contain exactly one scenario")
    if "value_kind" in table and set(table["value_kind"]) != {"probability_weight"}:
        _schema_error(metric, "exact inputs require value_kind=probability_weight")
    if any(int(generation) < 1 for generation in table["generation"]):
        _schema_error(metric, "generation keys must be positive")
    if contract.entity_column is not None:
        allowed = set(contract.entity_order)
        unexpected = [
            value for value in table[contract.entity_column] if value not in allowed
        ]
        if unexpected:
            _schema_error(metric, f"noncanonical entities {unexpected}")
    if table.duplicated(list(contract.key_columns)).any():
        _schema_error(metric, f"duplicate scientific keys {contract.key_columns}")


def _source_values(
    table: pd.DataFrame,
    contract: _MetricContract,
) -> dict[tuple[Any, ...], float]:
    values: dict[tuple[Any, ...], float] = {}
    for row in table.itertuples(index=False):
        key = tuple(getattr(row, column) for column in contract.key_columns)
        values[key] = float(getattr(row, contract.value_column))
    return values


def _key_sorter(contract: _MetricContract) -> Any:
    entity_rank = {entity: index for index, entity in enumerate(contract.entity_order)}

    def sort_key(key: tuple[Any, ...]) -> tuple[int, int]:
        generation, entity = _generation_and_entity(key)
        return generation, entity_rank[entity]

    return sort_key


def _generation_and_entity(key: tuple[Any, ...]) -> tuple[int, str]:
    iterator = iter(key)
    generation = int(next(iterator))
    entity = str(next(iterator, "all"))
    return generation, entity


def compare_numeric_metric(
    baseline_table: pd.DataFrame,
    candidate_table: pd.DataFrame,
    *,
    metric: MetricName,
    baseline_label: str,
    candidate_label: str,
) -> ComparisonResult:
    """Compare one approved exact metric as candidate minus baseline."""
    contract = METRIC_CONTRACTS.get(metric)
    if contract is None:
        raise UnsupportedComparisonError(
            f"Unsupported comparison: {metric} for exact numeric tables."
        )
    _validate_numeric_source(baseline_table, metric, contract)
    _validate_numeric_source(candidate_table, metric, contract)
    baseline_values = _source_values(baseline_table, contract)
    candidate_values = _source_values(candidate_table, contract)
    keys = sorted(
        baseline_values.keys() | candidate_values.keys(),
        key=_key_sorter(contract),
    )
    rows: list[dict[str, Any]] = []
    for key in keys:
        baseline_value = baseline_values.get(key, 0.0)
        candidate_value = candidate_values.get(key, 0.0)
        signed_delta = candidate_value - baseline_value
        relative_delta: float | Any = (
            signed_delta / baseline_value if baseline_value != 0.0 else pd.NA
        )
        generation, entity = _generation_and_entity(key)
        rows.append(
            {
                "generation": generation,
                "metric": metric,
                "entity": entity,
                "baseline_label": baseline_label,
                "candidate_label": candidate_label,
                "baseline_value": baseline_value,
                "candidate_value": candidate_value,
                "signed_delta": signed_delta,
                "absolute_delta": abs(signed_delta),
                "relative_delta": relative_delta,
                "direction": "candidate_minus_baseline",
            }
        )
    table = _typed_frame(rows, NUMERIC_COMPARISON_SCHEMA)
    return ComparisonResult(
        metric=metric,
        baseline_label=baseline_label,
        candidate_label=candidate_label,
        key_columns=contract.key_columns,
        table=table,
    )


def _validate_convergence_source(table: pd.DataFrame) -> None:
    metric = "convergence"
    _validate_schema(table, CONVERGENCE_SCHEMA, metric)
    if table.empty:
        return
    if table.duplicated(["start_scope", "start_key", "basis"]).any():
        _schema_error(metric, "duplicate scientific keys")
    scenarios = table[["start_scope", "start_key", "basis"]].drop_duplicates()
    if len(scenarios) != 1 or len(table) != 1:
        _schema_error(metric, "each input must contain exactly one scenario")
    if table.loc[0, "status"] not in CANONICAL_STATUSES:
        _schema_error(metric, f"unknown status {table.loc[0, 'status']}")


def compare_convergence(
    baseline_table: pd.DataFrame,
    candidate_table: pd.DataFrame,
    *,
    baseline_label: str,
    candidate_label: str,
) -> ConvergenceComparisonResult:
    """Compare nullable convergence generations while preserving statuses."""
    _validate_convergence_source(baseline_table)
    _validate_convergence_source(candidate_table)
    if baseline_table.empty and candidate_table.empty:
        return ConvergenceComparisonResult(
            baseline_label=baseline_label,
            candidate_label=candidate_label,
            table=_typed_frame([], CONVERGENCE_COMPARISON_SCHEMA),
        )
    if baseline_table.empty or candidate_table.empty:
        _schema_error("convergence", "both inputs must be empty or populated")

    scenario_columns = ["start_scope", "start_key", "basis"]
    baseline_scenario = tuple(baseline_table.loc[0, scenario_columns])
    candidate_scenario = tuple(candidate_table.loc[0, scenario_columns])
    if baseline_scenario != candidate_scenario:
        _schema_error(
            "convergence",
            f"scenario mismatch {baseline_scenario} versus {candidate_scenario}",
        )
    baseline_tolerance = float(baseline_table.loc[0, "tolerance"])
    candidate_tolerance = float(candidate_table.loc[0, "tolerance"])
    if baseline_tolerance != candidate_tolerance:
        _schema_error(
            "convergence",
            f"tolerance mismatch {baseline_tolerance} versus {candidate_tolerance}",
        )
    start_scope, start_key, basis = baseline_scenario

    baseline_generation = baseline_table.loc[0, "generation"]
    candidate_generation = candidate_table.loc[0, "generation"]
    generation_delta: int | Any = pd.NA
    if not pd.isna(baseline_generation) and not pd.isna(candidate_generation):
        generation_delta = int(candidate_generation) - int(baseline_generation)
    table = _typed_frame(
        [
            {
                "start_scope": start_scope,
                "start_key": start_key,
                "basis": basis,
                "baseline_label": baseline_label,
                "candidate_label": candidate_label,
                "baseline_generation": baseline_generation,
                "candidate_generation": candidate_generation,
                "generation_delta": generation_delta,
                "baseline_status": baseline_table.loc[0, "status"],
                "candidate_status": candidate_table.loc[0, "status"],
            }
        ],
        CONVERGENCE_COMPARISON_SCHEMA,
    )
    return ConvergenceComparisonResult(
        baseline_label=baseline_label,
        candidate_label=candidate_label,
        table=table,
    )


def _validate_calibration_source(
    table: pd.DataFrame,
    schema: tuple[tuple[str, str], ...],
    metric: str,
    contract: _MetricContract,
    value_kind: str,
) -> tuple[tuple[Any, ...], list[tuple[Any, ...]]]:
    _validate_schema(table, schema, metric)
    if table.empty:
        _schema_error(metric, "statistical family must not be empty")
    scenarios = table.loc[:, list(contract.scenario_columns)].drop_duplicates()
    if len(scenarios) != 1:
        _schema_error(metric, "each input must contain exactly one scenario")
    if "value_kind" in table and set(table["value_kind"]) != {value_kind}:
        _schema_error(metric, f"inputs require value_kind={value_kind}")
    if any(int(generation) < 1 for generation in table["generation"]):
        _schema_error(metric, "generation keys must be positive")
    if contract.entity_column is not None:
        unexpected = [
            value
            for value in table[contract.entity_column]
            if value not in set(contract.entity_order)
        ]
        if unexpected:
            _schema_error(metric, f"noncanonical entities {unexpected}")
    if table.duplicated(list(contract.key_columns)).any():
        _schema_error(metric, f"duplicate scientific keys {contract.key_columns}")

    keys = [
        tuple(getattr(row, column) for column in contract.key_columns)
        for row in table.itertuples(index=False)
    ]
    canonical_keys = sorted(keys, key=_key_sorter(contract))
    if keys != canonical_keys:
        _schema_error(metric, "rows are not in canonical scientific-key order")
    scenario_row = next(scenarios.itertuples(index=False))
    scenario = tuple(getattr(scenario_row, column) for column in contract.scenario_columns)
    return scenario, keys


def _row_map(
    table: pd.DataFrame,
    contract: _MetricContract,
) -> dict[tuple[Any, ...], Any]:
    return {
        tuple(getattr(row, column) for column in contract.key_columns): row
        for row in table.itertuples(index=False)
    }


def compare_exact_to_sampled(
    exact_table: pd.DataFrame,
    sampled_table: pd.DataFrame,
    *,
    metric: MetricName,
    denominator_scope: str,
    familywise_alpha: float = 0.01,
) -> ExactSampledComparisonResult:
    """Compare sampled Bernoulli estimates with authoritative exact fractions."""
    calibration = CALIBRATION_CONTRACTS.get(metric)
    if calibration is None:
        raise UnsupportedComparisonError(
            f"Unsupported comparison: {metric} for exact versus sampled tables."
        )
    if denominator_scope != calibration.denominator_scope:
        _schema_error(
            metric,
            "denominator_scope must be "
            f"{calibration.denominator_scope}, observed {denominator_scope}",
        )
    alpha = float(familywise_alpha)
    if not math.isfinite(alpha) or not 0.0 < alpha < 1.0:
        raise ValueError("familywise_alpha must be between 0 and 1")

    contract = calibration.metric_contract
    exact_scenario, exact_keys = _validate_calibration_source(
        exact_table,
        contract.schema,
        metric,
        contract,
        "probability_weight",
    )
    sampled_scenario, sampled_keys = _validate_calibration_source(
        sampled_table,
        calibration.sampled_schema,
        metric,
        contract,
        "copy_count",
    )
    if exact_scenario != sampled_scenario:
        _schema_error(
            metric,
            f"scenario mismatch {exact_scenario} versus {sampled_scenario}",
        )
    if exact_keys != sampled_keys:
        _schema_error(metric, "exact and sampled scientific keys do not align")

    family_size = len(exact_keys)
    adjusted_alpha = alpha / family_size
    z_value = NormalDist().inv_cdf(1.0 - adjusted_alpha / 2.0)
    exact_rows = _row_map(exact_table, contract)
    sampled_rows = _row_map(sampled_table, contract)
    rows: list[dict[str, Any]] = []
    for key in exact_keys:
        exact_row = exact_rows[key]
        sampled_row = sampled_rows[key]
        exact_fraction = float(getattr(exact_row, contract.value_column))
        successes = int(getattr(sampled_row, calibration.success_column))
        sample_size = int(getattr(sampled_row, calibration.denominator_column))
        if sample_size < 0 or successes < 0 or successes > sample_size:
            _schema_error(
                metric,
                f"invalid sampled counts successes={successes}, sample_size={sample_size}",
            )

        sampled_fraction: float | Any = pd.NA
        signed_error: float | Any = pd.NA
        absolute_error: float | Any = pd.NA
        standard_error: float | Any = pd.NA
        confidence_lower: float | Any = pd.NA
        confidence_upper: float | Any = pd.NA
        within_interval: bool | Any = pd.NA
        if sample_size > 0:
            sampled_fraction = successes / sample_size
            signed_error = sampled_fraction - exact_fraction
            absolute_error = abs(signed_error)
            standard_error = math.sqrt(
                sampled_fraction * (1.0 - sampled_fraction) / sample_size
            )
            denominator = 1.0 + z_value * z_value / sample_size
            center = (
                sampled_fraction + z_value * z_value / (2.0 * sample_size)
            ) / denominator
            half_width = z_value / denominator * math.sqrt(
                sampled_fraction * (1.0 - sampled_fraction) / sample_size
                + z_value * z_value / (4.0 * sample_size * sample_size)
            )
            confidence_lower = max(0.0, center - half_width)
            confidence_upper = min(1.0, center + half_width)
            within_interval = (
                confidence_lower <= exact_fraction <= confidence_upper
            )

        generation, entity = _generation_and_entity(key)
        rows.append(
            {
                "generation": generation,
                "metric": metric,
                "entity": entity,
                "denominator_scope": denominator_scope,
                "exact_fraction": exact_fraction,
                "sampled_fraction": sampled_fraction,
                "signed_error": signed_error,
                "absolute_error": absolute_error,
                "sample_size": sample_size,
                "standard_error": standard_error,
                "adjusted_alpha": adjusted_alpha,
                "family_size": family_size,
                "confidence_lower": confidence_lower,
                "confidence_upper": confidence_upper,
                "within_interval": within_interval,
            }
        )

    table = _typed_frame(rows, EXACT_SAMPLED_COMPARISON_SCHEMA)
    return ExactSampledComparisonResult(
        metric=metric,
        denominator_scope=denominator_scope,
        familywise_alpha=alpha,
        family_size=family_size,
        table=table,
    )
