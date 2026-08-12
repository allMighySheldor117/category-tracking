"""Wilson/Bonferroni correctness and preregistered sampled calibration."""

from __future__ import annotations

import copy
import json
import math
from statistics import NormalDist
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from engine.aggregated_tracking import run_aggregated_experiment
from engine.category_analysis import get_aggregated_survivor_fractions
from engine.comparisons import compare_exact_to_sampled
from engine.exact_analysis import (
    get_exact_stop_outcomes,
    get_exact_survival_by_start,
    get_exact_survivor_fractions,
    run_exact_analysis,
)
from engine.genetic_code import PROPERTY_LABELS, VALID_CODONS
from engine.models import (
    ExactSampledComparisonResult,
    MetricSchemaError,
    UnsupportedComparisonError,
)
from engine.mutation_matrix import (
    PRESET_AC,
    PRESET_AG,
    PRESET_AT,
    build_substitution_matrix,
)
from engine.summaries import (
    get_aggregated_stop_outcomes,
    get_aggregated_survival_by_start,
)


CALIBRATION_COLUMNS = [
    "generation", "metric", "entity", "denominator_scope", "exact_fraction",
    "sampled_fraction", "signed_error", "absolute_error", "sample_size",
    "standard_error", "adjusted_alpha", "family_size", "confidence_lower",
    "confidence_upper", "within_interval",
]
CALIBRATION_DTYPES = [
    "int64", "object", "object", "object", "float64", "Float64", "Float64",
    "Float64", "int64", "Float64", "float64", "int64", "Float64", "Float64",
    "boolean",
]
FRACTION_SCHEMA = (
    ("generation", "int64"),
    ("start_scope", "object"),
    ("start_key", "object"),
    ("category", "object"),
    ("numerator", "float64"),
    ("denominator", "float64"),
    ("fraction", "float64"),
)
SAMPLED_FRACTION_SCHEMA = tuple(
    (column, "int64" if column in {"numerator", "denominator"} else dtype)
    for column, dtype in FRACTION_SCHEMA
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
SAMPLED_SURVIVAL_SCHEMA = tuple(
    (
        column,
        "int64"
        if column in {"initial_value", "live_value", "stopped_value"}
        else dtype,
    )
    for column, dtype in SURVIVAL_SCHEMA
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
SAMPLED_STOP_SCHEMA = tuple(
    (
        column,
        "int64"
        if column in {"new_stop_value", "cumulative_stop_value", "initial_value"}
        else dtype,
    )
    for column, dtype in STOP_SCHEMA
)


def typed_frame(
    rows: list[dict[str, object]],
    schema: tuple[tuple[str, str], ...],
) -> pd.DataFrame:
    frame = pd.DataFrame.from_records(rows, columns=[column for column, _dtype in schema])
    return frame.astype({column: dtype for column, dtype in schema}).reset_index(drop=True)


def category_family(
    exact_values: list[float],
    successes: list[int],
    denominators: list[int],
    displayed: list[float] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    categories = list(PROPERTY_LABELS.values())[:len(exact_values)]
    shown = displayed if displayed is not None else [
        success / denominator if denominator else 0.0
        for success, denominator in zip(successes, denominators)
    ]
    exact_rows = []
    sampled_rows = []
    for category, exact, success, denominator, sampled in zip(
        categories, exact_values, successes, denominators, shown
    ):
        common = {
            "generation": 1,
            "start_scope": "population",
            "start_key": "all",
            "category": category,
        }
        exact_rows.append(
            {**common, "numerator": exact, "denominator": 1.0, "fraction": exact}
        )
        sampled_rows.append(
            {
                **common,
                "numerator": success,
                "denominator": denominator,
                "fraction": sampled,
            }
        )
    return (
        typed_frame(exact_rows, FRACTION_SCHEMA),
        typed_frame(sampled_rows, SAMPLED_FRACTION_SCHEMA),
    )


def survival_family(
    *,
    exact_survivor: float,
    live: int,
    stopped: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    initial = live + stopped
    common = {"generation": 1, "start_scope": "population", "start_key": "all"}
    exact = typed_frame(
        [
            {
                **common,
                "initial_value": 1.0,
                "live_value": exact_survivor,
                "stopped_value": 1.0 - exact_survivor,
                "survivor_fraction": exact_survivor,
                "stop_fraction": 1.0 - exact_survivor,
                "value_kind": "probability_weight",
            }
        ],
        SURVIVAL_SCHEMA,
    )
    sampled = typed_frame(
        [
            {
                **common,
                "initial_value": initial,
                "live_value": live,
                "stopped_value": stopped,
                "survivor_fraction": 0.999,
                "stop_fraction": 0.999,
                "value_kind": "copy_count",
            }
        ],
        SAMPLED_SURVIVAL_SCHEMA,
    )
    return exact, sampled


def stop_family() -> tuple[pd.DataFrame, pd.DataFrame]:
    exact_rows = []
    sampled_rows = []
    for stop, exact, stopped in zip(("TAA", "TAG", "TGA"), (0.05, 0.10, 0.15), (4, 11, 15)):
        common = {
            "generation": 1,
            "start_scope": "population",
            "start_key": "all",
            "stop_codon": stop,
        }
        exact_rows.append(
            {
                **common,
                "new_stop_value": exact,
                "cumulative_stop_value": exact,
                "initial_value": 1.0,
                "cumulative_stop_fraction": exact,
                "value_kind": "probability_weight",
            }
        )
        sampled_rows.append(
            {
                **common,
                "new_stop_value": stopped,
                "cumulative_stop_value": stopped,
                "initial_value": 100,
                "cumulative_stop_fraction": 0.999,
                "value_kind": "copy_count",
            }
        )
    return typed_frame(exact_rows, STOP_SCHEMA), typed_frame(sampled_rows, SAMPLED_STOP_SCHEMA)


class StatisticalComparisonTests(unittest.TestCase):
    def assert_schema(self, frame: pd.DataFrame) -> None:
        self.assertEqual(list(frame.columns), CALIBRATION_COLUMNS)
        self.assertEqual([str(dtype) for dtype in frame.dtypes], CALIBRATION_DTYPES)
        self.assertIsInstance(frame.index, pd.RangeIndex)
        self.assertEqual((frame.index.start, frame.index.step), (0, 1))

    def test_raw_counts_drive_all_four_approved_fraction_metrics(self) -> None:
        category_exact, category_sampled = category_family(
            [0.2], [25], [100], displayed=[0.999]
        )
        survival_exact, survival_sampled = survival_family(
            exact_survivor=0.7, live=60, stopped=40
        )
        stop_exact, stop_sampled = stop_family()
        cases = (
            ("category_fraction", "live_population", category_exact, category_sampled, 0.25, 100),
            ("survivor_fraction", "population_initial", survival_exact, survival_sampled, 0.60, 100),
            ("stop_fraction", "population_initial", survival_exact, survival_sampled, 0.40, 100),
            ("cumulative_stop_fraction", "population_initial", stop_exact, stop_sampled, 0.04, 100),
        )
        for metric, denominator_scope, exact, sampled, expected_fraction, expected_n in cases:
            with self.subTest(metric=metric):
                result = compare_exact_to_sampled(
                    exact,
                    sampled,
                    metric=metric,
                    denominator_scope=denominator_scope,
                )
                self.assertIsInstance(result, ExactSampledComparisonResult)
                self.assertEqual(result.metric, metric)
                self.assertEqual(result.denominator_scope, denominator_scope)
                self.assertEqual(result.familywise_alpha, 0.01)
                self.assertEqual(result.family_size, len(exact))
                self.assert_schema(result.table)
                self.assertEqual(float(result.table.loc[0, "sampled_fraction"]), expected_fraction)
                self.assertEqual(result.table.loc[0, "sample_size"], expected_n)

    def test_wilson_bonferroni_formula_extremes_and_multirow_family(self) -> None:
        exact, sampled = category_family(
            [0.0, 0.30, 1.0],
            [0, 25, 100],
            [100, 100, 100],
        )
        result = compare_exact_to_sampled(
            exact,
            sampled,
            metric="category_fraction",
            denominator_scope="live_population",
            familywise_alpha=0.01,
        )
        table = result.table
        adjusted = 0.01 / 3
        z = NormalDist().inv_cdf(1.0 - adjusted / 2.0)
        self.assertTrue(all(value == adjusted for value in table["adjusted_alpha"]))
        for index, (successes, n) in enumerate(((0, 100), (25, 100), (100, 100))):
            p_hat = successes / n
            denominator = 1.0 + z * z / n
            center = (p_hat + z * z / (2.0 * n)) / denominator
            half = z / denominator * math.sqrt(
                p_hat * (1.0 - p_hat) / n + z * z / (4.0 * n * n)
            )
            lower = max(0.0, center - half)
            upper = min(1.0, center + half)
            standard_error = math.sqrt(p_hat * (1.0 - p_hat) / n)
            row = table.iloc[index]
            self.assertEqual(float(row["confidence_lower"]).hex(), lower.hex())
            self.assertEqual(float(row["confidence_upper"]).hex(), upper.hex())
            self.assertEqual(float(row["standard_error"]).hex(), standard_error.hex())
            signed = p_hat - float(row["exact_fraction"])
            self.assertEqual(float(row["signed_error"]).hex(), signed.hex())
            self.assertEqual(float(row["absolute_error"]).hex(), abs(signed).hex())
            self.assertEqual(
                bool(row["within_interval"]),
                lower <= float(row["exact_fraction"]) <= upper,
            )

    def test_single_row_and_zero_sample_contract(self) -> None:
        exact, sampled = survival_family(exact_survivor=0.5, live=50, stopped=50)
        single = compare_exact_to_sampled(
            exact,
            sampled,
            metric="survivor_fraction",
            denominator_scope="population_initial",
        )
        self.assertEqual(single.family_size, 1)
        self.assertEqual(single.table.loc[0, "adjusted_alpha"], 0.01)

        zero_exact, zero_sampled = category_family([0.4], [0], [0])
        zero = compare_exact_to_sampled(
            zero_exact,
            zero_sampled,
            metric="category_fraction",
            denominator_scope="live_population",
        ).table.iloc[0]
        self.assertEqual(zero["exact_fraction"], 0.4)
        self.assertEqual(zero["sample_size"], 0)
        for column in (
            "sampled_fraction", "signed_error", "absolute_error", "standard_error",
            "confidence_lower", "confidence_upper", "within_interval",
        ):
            self.assertTrue(pd.isna(zero[column]), column)

    def test_schema_alignment_scenario_pairing_alpha_and_input_ownership(self) -> None:
        exact, sampled = category_family([0.2, 0.3], [20, 30], [100, 100])
        exact_before = exact.copy(deep=True)
        sampled_before = sampled.copy(deep=True)
        compare_exact_to_sampled(
            exact,
            sampled,
            metric="category_fraction",
            denominator_scope="live_population",
        )
        assert_frame_equal(exact, exact_before, check_exact=True)
        assert_frame_equal(sampled, sampled_before, check_exact=True)

        corruptions = []
        corruptions.append(sampled.rename(columns={"numerator": "wrong"}))
        bad_dtype = sampled.copy(deep=True)
        bad_dtype["denominator"] = bad_dtype["denominator"].astype("float64")
        corruptions.append(bad_dtype)
        corruptions.append(sampled.iloc[1:])
        corruptions.append(pd.concat([sampled, sampled.iloc[[0]]], ignore_index=True))
        wrong_scenario = sampled.copy(deep=True)
        wrong_scenario["start_key"] = "TGG"
        corruptions.append(wrong_scenario)
        misaligned = sampled.iloc[[0]].reset_index(drop=True)
        corruptions.append(misaligned)
        for corrupt in corruptions:
            with self.subTest(columns=list(corrupt.columns), rows=len(corrupt)):
                with self.assertRaises(MetricSchemaError):
                    compare_exact_to_sampled(
                        exact,
                        corrupt,
                        metric="category_fraction",
                        denominator_scope="live_population",
                    )

        for metric in ("category_live_value", "new_stop_value", "unknown"):
            with self.subTest(metric=metric):
                with self.assertRaises(UnsupportedComparisonError):
                    compare_exact_to_sampled(
                        exact,
                        sampled,
                        metric=metric,
                        denominator_scope="live_population",
                    )
        for scope in ("", None):
            with self.subTest(scope=scope):
                with self.assertRaises(MetricSchemaError):
                    compare_exact_to_sampled(
                        exact,
                        sampled,
                        metric="category_fraction",
                        denominator_scope=scope,  # type: ignore[arg-type]
                    )
        with self.assertRaisesRegex(MetricSchemaError, "denominator_scope"):
            compare_exact_to_sampled(
                exact,
                sampled,
                metric="category_fraction",
                denominator_scope="population_initial_or_live",
            )
        for alpha in (0.0, 1.0, -0.1, float("nan"), float("inf")):
            with self.subTest(alpha=alpha):
                with self.assertRaisesRegex(ValueError, "familywise_alpha"):
                    compare_exact_to_sampled(
                        exact,
                        sampled,
                        metric="category_fraction",
                        denominator_scope="live_population",
                        familywise_alpha=alpha,
                    )
        denominator_mismatches = (
            ("category_fraction", "population_initial", exact, sampled),
            (
                "survivor_fraction",
                "live_population",
                *survival_family(exact_survivor=0.7, live=60, stopped=40),
            ),
            (
                "stop_fraction",
                "live_population",
                *survival_family(exact_survivor=0.7, live=60, stopped=40),
            ),
            ("cumulative_stop_fraction", "live_population", *stop_family()),
        )
        for metric, denominator_scope, exact_source, sampled_source in denominator_mismatches:
            with self.subTest(metric=metric, denominator_scope=denominator_scope):
                with self.assertRaisesRegex(MetricSchemaError, "denominator_scope"):
                    compare_exact_to_sampled(
                        exact_source,
                        sampled_source,
                        metric=metric,
                        denominator_scope=denominator_scope,
                    )


class PreregisteredCalibrationTests(unittest.TestCase):
    def test_fixed_seed_panel_conserves_repeats_and_largest_rmse_improves(self) -> None:
        seeds = (1729, 271828, 314159)
        copies_per_codon_values = (10, 100, 1000)
        matrix = build_substitution_matrix(PRESET_AT, PRESET_AG, PRESET_AC)
        exact = run_exact_analysis(
            10,
            matrix,
            {codon: 1.0 for codon in VALID_CODONS},
        )
        exact_category = get_exact_survivor_fractions(
            exact, start_scope="population", start_key="all"
        )
        exact_survival = get_exact_survival_by_start(
            exact, start_scope="population", start_key="all"
        )
        exact_stops = get_exact_stop_outcomes(
            exact, start_scope="population", start_key="all"
        )
        squared_errors: dict[int, list[float]] = {
            copies: [] for copies in copies_per_codon_values
        }
        family_names = (
            "category_fraction",
            "survivor_fraction",
            "stop_fraction",
            "cumulative_stop_fraction",
        )
        coverage: dict[int, dict[str, list[bool]]] = {
            copies: {family: [] for family in family_names}
            for copies in copies_per_codon_values
        }
        coverage_counts: dict[int, dict[str, int]] = {
            copies: {family: 0 for family in family_names}
            for copies in copies_per_codon_values
        }

        for copies_per_codon in copies_per_codon_values:
            weights = {codon: copies_per_codon for codon in VALID_CODONS}
            total = 61 * copies_per_codon
            for seed in seeds:
                with self.subTest(copies_per_codon=copies_per_codon, seed=seed):
                    sampled = run_aggregated_experiment(10, matrix, weights, seed)
                    repeated = run_aggregated_experiment(10, matrix, weights, seed)
                    self.assertEqual(sampled, repeated)
                    self.assertEqual(sampled.total_start_count, total)
                    for snapshot in sampled.generations:
                        self.assertEqual(
                            snapshot.total_live + snapshot.cumulative_stops,
                            total,
                        )
                    sampled_category = get_aggregated_survivor_fractions(
                        sampled, start_scope="population", start_key="all"
                    )
                    sampled_survival = get_aggregated_survival_by_start(
                        sampled, start_scope="population", start_key="all"
                    )
                    sampled_stops = get_aggregated_stop_outcomes(
                        sampled, start_scope="population", start_key="all"
                    )
                    families = (
                        compare_exact_to_sampled(
                            exact_category,
                            sampled_category,
                            metric="category_fraction",
                            denominator_scope="live_population",
                        ),
                        compare_exact_to_sampled(
                            exact_survival,
                            sampled_survival,
                            metric="survivor_fraction",
                            denominator_scope="population_initial",
                        ),
                        compare_exact_to_sampled(
                            exact_survival,
                            sampled_survival,
                            metric="stop_fraction",
                            denominator_scope="population_initial",
                        ),
                        compare_exact_to_sampled(
                            exact_stops,
                            sampled_stops,
                            metric="cumulative_stop_fraction",
                            denominator_scope="population_initial",
                        ),
                    )
                    self.assertEqual([family.family_size for family in families], [50, 10, 10, 30])
                    self.assertEqual(
                        families[0].table["sample_size"].tolist(),
                        sampled_category["denominator"].tolist(),
                    )
                    self.assertEqual(families[1].table["sample_size"].tolist(), [total] * 10)
                    self.assertEqual(families[2].table["sample_size"].tolist(), [total] * 10)
                    self.assertEqual(families[3].table["sample_size"].tolist(), [total] * 30)
                    for family_name, family in zip(family_names, families):
                        squared_errors[copies_per_codon].extend(
                            float(value) ** 2 for value in family.table["signed_error"]
                        )
                        coverage[copies_per_codon][family_name].extend(
                            bool(value) for value in family.table["within_interval"]
                        )
                        coverage_counts[copies_per_codon][family_name] += len(
                            family.table
                        )

        rmse = {
            copies: math.sqrt(sum(values) / len(values))
            for copies, values in squared_errors.items()
        }
        expected_coverage_counts = {
            "category_fraction": 3 * 50,
            "survivor_fraction": 3 * 10,
            "stop_fraction": 3 * 10,
            "cumulative_stop_fraction": 3 * 30,
        }
        coverage_report = {
            copies: {
                family: sum(values) / len(values)
                for family, values in families.items()
            }
            for copies, families in coverage.items()
        }
        for copies, families in coverage.items():
            for family, values in families.items():
                self.assertEqual(len(values), expected_coverage_counts[family])
                self.assertEqual(
                    coverage_counts[copies][family],
                    expected_coverage_counts[family],
                )
                self.assertTrue(
                    all(values),
                    (
                        "Preregistered rejection: every Wilson interval verdict "
                        f"must pass for {family} at {copies} copies per codon"
                    ),
                )
                self.assertEqual(coverage_report[copies][family], 1.0)
        report = {
            "coverage_by_copies_per_codon": coverage_report,
            "coverage_row_counts_by_copies_per_codon": coverage_counts,
            "pooled_rmse_by_copies_per_codon": rmse,
        }
        print("PREREGISTERED_CALIBRATION=" + json.dumps(report, sort_keys=True))
        self.assertLess(
            rmse[1000],
            rmse[10],
            "Preregistered rejection: pooled RMSE at 61000 must improve over 610",
        )


if __name__ == "__main__":
    unittest.main()
