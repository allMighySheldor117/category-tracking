"""Directed exact comparison contracts, alignment, and schema validation."""

from __future__ import annotations

import inspect
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from engine import comparisons
from engine.comparisons import (
    compare_convergence,
    compare_exact_to_sampled,
    compare_numeric_metric,
)
from engine.exact_analysis import (
    get_exact_category_metrics,
    get_exact_codon_outcomes,
    get_exact_convergence,
    get_exact_stop_outcomes,
    get_exact_survival_by_start,
    get_exact_survivor_fractions,
    run_exact_analysis,
)
from engine.models import (
    ComparisonResult,
    ConvergenceComparisonResult,
    MetricSchemaError,
    UnsupportedComparisonError,
)
from engine.mutation_matrix import build_substitution_matrix


NUMERIC_COLUMNS = [
    "generation",
    "metric",
    "entity",
    "baseline_label",
    "candidate_label",
    "baseline_value",
    "candidate_value",
    "signed_delta",
    "absolute_delta",
    "relative_delta",
    "direction",
]
NUMERIC_DTYPES = [
    "Int64",
    "object",
    "object",
    "object",
    "object",
    "float64",
    "float64",
    "float64",
    "float64",
    "Float64",
    "object",
]
CONVERGENCE_COLUMNS = [
    "start_scope",
    "start_key",
    "basis",
    "baseline_label",
    "candidate_label",
    "baseline_generation",
    "candidate_generation",
    "generation_delta",
    "baseline_status",
    "candidate_status",
]
CONVERGENCE_DTYPES = [
    "object",
    "object",
    "object",
    "object",
    "object",
    "Int64",
    "Int64",
    "Int64",
    "object",
    "object",
]


class ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = run_exact_analysis(
            2,
            build_substitution_matrix(0.2, 0.5, 0.3),
            {"AAA": 2.5, "AAG": 1.5, "TGG": 3.0},
        )
        cls.candidate = run_exact_analysis(
            2,
            build_substitution_matrix(0.1, 0.7, 0.2),
            {"AAA": 1.0, "AAG": 3.0, "TGG": 4.0},
        )

    def assert_schema(
        self,
        frame: pd.DataFrame,
        columns: list[str],
        dtypes: list[str],
    ) -> None:
        self.assertEqual(list(frame.columns), columns)
        self.assertEqual([str(dtype) for dtype in frame.dtypes], dtypes)
        self.assertIsInstance(frame.index, pd.RangeIndex)
        self.assertEqual((frame.index.start, frame.index.step), (0, 1))

    def test_public_functions_are_typed_with_approved_defaults(self) -> None:
        for function in (compare_numeric_metric, compare_convergence):
            with self.subTest(function=function.__name__):
                signature = inspect.signature(function)
                self.assertTrue(
                    all(
                        parameter.annotation is not inspect.Parameter.empty
                        for parameter in signature.parameters.values()
                    )
                )
                self.assertIsNot(signature.return_annotation, inspect.Signature.empty)
                self.assertTrue(
                    all(
                        parameter.default is inspect.Parameter.empty
                        for parameter in signature.parameters.values()
                    )
                )
        signature = inspect.signature(compare_exact_to_sampled)
        self.assertTrue(
            all(
                parameter.annotation is not inspect.Parameter.empty
                for parameter in signature.parameters.values()
            )
        )
        self.assertIsNot(signature.return_annotation, inspect.Signature.empty)
        self.assertTrue(
            all(
                signature.parameters[name].default is inspect.Parameter.empty
                for name in (
                    "exact_table",
                    "sampled_table",
                    "metric",
                    "denominator_scope",
                )
            )
        )
        self.assertEqual(
            signature.parameters["familywise_alpha"].default,
            0.01,
        )
        self.assertIs(comparisons.compare_exact_to_sampled, compare_exact_to_sampled)

    def test_every_approved_numeric_metric_has_canonical_output(self) -> None:
        baseline_categories = get_exact_category_metrics(
            self.baseline, start_scope="population", start_key="all"
        )
        candidate_categories = get_exact_category_metrics(
            self.candidate, start_scope="population", start_key="all"
        )
        baseline_fractions = get_exact_survivor_fractions(
            self.baseline, start_scope="population", start_key="all"
        )
        candidate_fractions = get_exact_survivor_fractions(
            self.candidate, start_scope="population", start_key="all"
        )
        baseline_survival = get_exact_survival_by_start(
            self.baseline, start_scope="population", start_key="all"
        )
        candidate_survival = get_exact_survival_by_start(
            self.candidate, start_scope="population", start_key="all"
        )
        baseline_stops = get_exact_stop_outcomes(
            self.baseline, start_scope="population", start_key="all"
        )
        candidate_stops = get_exact_stop_outcomes(
            self.candidate, start_scope="population", start_key="all"
        )
        baseline_codons = get_exact_codon_outcomes(
            self.baseline, start_codon="TGG", generation=2
        )
        candidate_codons = get_exact_codon_outcomes(
            self.candidate, start_codon="TGG", generation=2
        )
        cases = (
            ("category_live_value", baseline_categories, candidate_categories, 10),
            ("category_fraction", baseline_fractions, candidate_fractions, 10),
            ("survivor_fraction", baseline_survival, candidate_survival, 2),
            ("stop_fraction", baseline_survival, candidate_survival, 2),
            ("new_stop_value", baseline_stops, candidate_stops, 6),
            ("cumulative_stop_value", baseline_stops, candidate_stops, 6),
            ("cumulative_stop_fraction", baseline_stops, candidate_stops, 6),
            ("codon_live_value", baseline_codons, candidate_codons, 64),
            ("codon_new_stop_value", baseline_codons, candidate_codons, 64),
            ("codon_cumulative_stop_value", baseline_codons, candidate_codons, 64),
        )
        for metric, baseline, candidate, row_count in cases:
            with self.subTest(metric=metric):
                result = compare_numeric_metric(
                    baseline,
                    candidate,
                    metric=metric,
                    baseline_label="Baseline",
                    candidate_label="Candidate",
                )
                self.assertIsInstance(result, ComparisonResult)
                self.assertEqual(result.metric, metric)
                self.assertEqual(len(result.table), row_count)
                self.assert_schema(result.table, NUMERIC_COLUMNS, NUMERIC_DTYPES)
                self.assertEqual(result.table["metric"].unique().tolist(), [metric])
                self.assertEqual(
                    result.table["direction"].unique().tolist(),
                    ["candidate_minus_baseline"],
                )
                for row in result.table.itertuples(index=False):
                    self.assertEqual(
                        row.signed_delta.hex(),
                        (row.candidate_value - row.baseline_value).hex(),
                    )
                    self.assertEqual(row.absolute_delta.hex(), abs(row.signed_delta).hex())

    def test_scenario_comparisons_support_codon_amino_acid_and_trait(self) -> None:
        cases = (
            (
                get_exact_category_metrics(
                    self.baseline, start_scope="codon", start_key="AAA"
                ),
                get_exact_category_metrics(
                    self.baseline, start_scope="codon", start_key="TGG"
                ),
            ),
            (
                get_exact_category_metrics(
                    self.baseline, start_scope="amino_acid", start_key="Lys"
                ),
                get_exact_category_metrics(
                    self.baseline, start_scope="amino_acid", start_key="Trp"
                ),
            ),
            (
                get_exact_category_metrics(
                    self.baseline,
                    start_scope="trait",
                    start_key="Positively charged",
                ),
                get_exact_category_metrics(
                    self.baseline,
                    start_scope="trait",
                    start_key="Hydrophobic",
                ),
            ),
        )
        for baseline, candidate in cases:
            result = compare_numeric_metric(
                baseline,
                candidate,
                metric="category_live_value",
                baseline_label="A",
                candidate_label="B",
            )
            self.assertEqual(len(result.table), 10)
            self.assertEqual(result.key_columns, ("generation", "category"))

    def test_self_swap_zero_baseline_and_directional_relative_delta(self) -> None:
        source = get_exact_category_metrics(
            self.baseline, start_scope="population", start_key="all"
        ).iloc[[0]].reset_index(drop=True)
        baseline = source.copy(deep=True)
        candidate = source.copy(deep=True)
        baseline.loc[0, "live_value"] = 0.2
        candidate.loc[0, "live_value"] = 0.3

        forward = compare_numeric_metric(
            baseline,
            candidate,
            metric="category_live_value",
            baseline_label="base",
            candidate_label="candidate",
        ).table.iloc[0]
        swapped = compare_numeric_metric(
            candidate,
            baseline,
            metric="category_live_value",
            baseline_label="candidate",
            candidate_label="base",
        ).table.iloc[0]
        self.assertEqual(swapped["signed_delta"].hex(), (-forward["signed_delta"]).hex())
        self.assertEqual(swapped["absolute_delta"].hex(), forward["absolute_delta"].hex())
        self.assertEqual(
            float(forward["relative_delta"]).hex(),
            (float(forward["signed_delta"]) / 0.2).hex(),
        )
        self.assertEqual(
            float(swapped["relative_delta"]).hex(),
            (float(swapped["signed_delta"]) / 0.3).hex(),
        )

        self_result = compare_numeric_metric(
            baseline,
            baseline,
            metric="category_live_value",
            baseline_label="same",
            candidate_label="same",
        ).table.iloc[0]
        self.assertEqual(self_result["signed_delta"], 0.0)
        self.assertEqual(self_result["absolute_delta"], 0.0)
        self.assertEqual(self_result["relative_delta"], 0.0)

        zero = baseline.copy(deep=True)
        zero.loc[0, "live_value"] = 0.0
        zero_result = compare_numeric_metric(
            zero,
            candidate,
            metric="category_live_value",
            baseline_label="zero",
            candidate_label="candidate",
        ).table.iloc[0]
        self.assertTrue(pd.isna(zero_result["relative_delta"]))

    def test_sparse_alignment_uses_scientific_keys_and_fills_missing_zero(self) -> None:
        baseline = get_exact_category_metrics(
            self.baseline, start_scope="population", start_key="all"
        )
        candidate = get_exact_category_metrics(
            self.candidate, start_scope="population", start_key="all"
        )
        missing_key = (
            int(baseline.loc[0, "generation"]),
            baseline.loc[0, "category"],
        )
        sparse = baseline.iloc[1:].reset_index(drop=True)

        result = compare_numeric_metric(
            sparse,
            candidate,
            metric="category_live_value",
            baseline_label="sparse",
            candidate_label="complete",
        ).table

        self.assertEqual(len(result), len(candidate))
        row = result[
            (result["generation"] == missing_key[0])
            & (result["entity"] == missing_key[1])
        ].iloc[0]
        self.assertEqual(row["baseline_value"], 0.0)
        self.assertGreaterEqual(row["candidate_value"], 0.0)
        self.assertEqual(
            result[["generation", "entity"]].to_records(index=False).tolist(),
            sorted(
                result[["generation", "entity"]].to_records(index=False).tolist(),
                key=lambda item: (item[0], list(baseline["category"].unique()).index(item[1])),
            ),
        )

    def test_typed_empty_comparison(self) -> None:
        empty_analysis = run_exact_analysis(
            0,
            build_substitution_matrix(0.2, 0.5, 0.3),
            {},
        )
        empty = get_exact_category_metrics(
            empty_analysis, start_scope="population", start_key="all"
        )
        result = compare_numeric_metric(
            empty,
            empty.copy(deep=True),
            metric="category_live_value",
            baseline_label="empty-a",
            candidate_label="empty-b",
        )
        self.assertTrue(result.table.empty)
        self.assert_schema(result.table, NUMERIC_COLUMNS, NUMERIC_DTYPES)

    def test_schema_scenario_duplicate_and_pairing_errors_are_explicit(self) -> None:
        category = get_exact_category_metrics(
            self.baseline, start_scope="population", start_key="all"
        )
        fraction = get_exact_survivor_fractions(
            self.baseline, start_scope="population", start_key="all"
        )
        cases = []
        wrong_columns = category.rename(columns={"live_value": "wrong"})
        cases.append(wrong_columns)
        wrong_dtype = category.copy(deep=True)
        wrong_dtype["generation"] = wrong_dtype["generation"].astype("Int64")
        cases.append(wrong_dtype)
        wrong_index = category.iloc[1:]
        cases.append(wrong_index)
        duplicate = pd.concat([category, category.iloc[[0]]], ignore_index=True)
        cases.append(duplicate)
        second_scenario = get_exact_category_metrics(
            self.baseline, start_scope="codon", start_key="AAA"
        )
        mixed_scenarios = pd.concat([category, second_scenario], ignore_index=True)
        cases.append(mixed_scenarios)

        for corrupt in cases:
            with self.subTest(columns=list(corrupt.columns), rows=len(corrupt)):
                with self.assertRaises(MetricSchemaError):
                    compare_numeric_metric(
                        corrupt,
                        category,
                        metric="category_live_value",
                        baseline_label="bad",
                        candidate_label="good",
                    )
        with self.assertRaises(MetricSchemaError):
            compare_numeric_metric(
                fraction,
                fraction,
                metric="category_live_value",
                baseline_label="wrong-source",
                candidate_label="wrong-source",
            )
        with self.assertRaises(UnsupportedComparisonError):
            compare_numeric_metric(
                category,
                category,
                metric="unknown_metric",
                baseline_label="a",
                candidate_label="b",
            )

    def test_convergence_comparison_preserves_statuses_and_nullable_generations(self) -> None:
        matrix = build_substitution_matrix(0.2, 0.5, 0.3)
        stable_analysis = run_exact_analysis(2, matrix, {"TGG": 2.0})
        stopped_analysis = run_exact_analysis(2, matrix, {})
        zero_analysis = run_exact_analysis(0, matrix, {})
        stable = get_exact_convergence(
            stable_analysis,
            start_scope="population",
            start_key="all",
            basis="category_weight",
            tolerance=10.0,
        )
        stopped = get_exact_convergence(
            stopped_analysis,
            start_scope="population",
            start_key="all",
            basis="category_weight",
            tolerance=10.0,
        )
        no_generations = get_exact_convergence(
            zero_analysis,
            start_scope="population",
            start_key="all",
            basis="category_weight",
            tolerance=10.0,
        )

        compared = compare_convergence(
            stable,
            stopped,
            baseline_label="live",
            candidate_label="stopped",
        )
        self.assertIsInstance(compared, ConvergenceComparisonResult)
        self.assert_schema(compared.table, CONVERGENCE_COLUMNS, CONVERGENCE_DTYPES)
        self.assertEqual(compared.table.loc[0, "baseline_status"], "stable")
        self.assertEqual(compared.table.loc[0, "candidate_status"], "all_stopped")
        self.assertEqual(compared.table.loc[0, "generation_delta"], 0)

        nullable = compare_convergence(
            no_generations,
            stable,
            baseline_label="empty",
            candidate_label="live",
        ).table
        self.assertTrue(pd.isna(nullable.loc[0, "baseline_generation"]))
        self.assertTrue(pd.isna(nullable.loc[0, "generation_delta"]))
        self.assertEqual(nullable.loc[0, "baseline_status"], "no_generations")

    def test_convergence_validation_empty_and_errors(self) -> None:
        stable = get_exact_convergence(
            self.baseline,
            start_scope="population",
            start_key="all",
            basis="category_weight",
            tolerance=0.0,
        )
        empty = stable.iloc[0:0].copy()
        empty_result = compare_convergence(
            empty,
            empty.copy(deep=True),
            baseline_label="a",
            candidate_label="b",
        )
        self.assertTrue(empty_result.table.empty)
        self.assert_schema(empty_result.table, CONVERGENCE_COLUMNS, CONVERGENCE_DTYPES)

        duplicate = pd.concat([stable, stable], ignore_index=True)
        with self.assertRaises(MetricSchemaError):
            compare_convergence(
                duplicate,
                stable,
                baseline_label="bad",
                candidate_label="good",
            )
        bad_status = stable.copy(deep=True)
        bad_status.loc[0, "status"] = "numeric-status"
        with self.assertRaises(MetricSchemaError):
            compare_convergence(
                bad_status,
                stable,
                baseline_label="bad",
                candidate_label="good",
            )
        different_tolerance = stable.copy(deep=True)
        different_tolerance.loc[0, "tolerance"] = 0.5
        with self.assertRaises(MetricSchemaError):
            compare_convergence(
                stable,
                different_tolerance,
                baseline_label="a",
                candidate_label="b",
            )

    def test_repeated_calls_and_input_ownership(self) -> None:
        baseline = get_exact_stop_outcomes(
            self.baseline, start_scope="trait", start_key="Positively charged"
        )
        candidate = get_exact_stop_outcomes(
            self.candidate, start_scope="trait", start_key="Positively charged"
        )
        baseline_before = baseline.copy(deep=True)
        candidate_before = candidate.copy(deep=True)
        first = compare_numeric_metric(
            baseline,
            candidate,
            metric="cumulative_stop_fraction",
            baseline_label="base",
            candidate_label="candidate",
        )
        second = compare_numeric_metric(
            baseline,
            candidate,
            metric="cumulative_stop_fraction",
            baseline_label="base",
            candidate_label="candidate",
        )

        assert_frame_equal(first.table, second.table, check_exact=True)
        assert_frame_equal(baseline, baseline_before, check_exact=True)
        assert_frame_equal(candidate, candidate_before, check_exact=True)


if __name__ == "__main__":
    unittest.main()
