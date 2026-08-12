"""Targeted success and corruption tests for Phase 2 scientific validators."""

from __future__ import annotations

import copy
import inspect
import unittest
from dataclasses import FrozenInstanceError, replace
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal

from engine.exact_analysis import get_exact_convergence, run_exact_analysis
from engine.invariants import (
    validate_biological_invariants,
    validate_exact_analysis,
    validate_mutation_matrix,
)
from engine.models import ScientificInvariantError, ScientificInvariantReport
from engine.mutation_matrix import build_substitution_matrix


class ScientificInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = build_substitution_matrix(0.2, 0.5, 0.3)

    def assert_failure_context(
        self,
        error: ScientificInvariantError,
        metric: str,
    ) -> None:
        message = str(error)
        self.assertIn(f"Scientific invariant failed for {metric}", message)
        self.assertIn(" at ", message)
        self.assertIn("/generation ", message)
        self.assertIn("expected ", message)
        self.assertIn("observed ", message)
        self.assertIn("tolerance ", message)

    def test_public_validators_are_typed_and_have_no_defaults(self) -> None:
        for function in (
            validate_biological_invariants,
            validate_mutation_matrix,
            validate_exact_analysis,
        ):
            with self.subTest(function=function.__name__):
                signature = inspect.signature(function)
                self.assertTrue(
                    all(
                        parameter.annotation is not inspect.Parameter.empty
                        and parameter.default is inspect.Parameter.empty
                        for parameter in signature.parameters.values()
                    )
                )
                self.assertIsNot(signature.return_annotation, inspect.Signature.empty)

    def test_biological_and_mutation_validators_return_frozen_reports(self) -> None:
        biological = validate_biological_invariants()
        mutation = validate_mutation_matrix(self.matrix)

        self.assertIsInstance(biological, tuple)
        self.assertIsInstance(mutation, tuple)
        self.assertGreaterEqual(len(biological), 3)
        self.assertGreaterEqual(len(mutation), 9)
        for report in (*biological, *mutation):
            self.assertIsInstance(report, ScientificInvariantReport)
            with self.assertRaises(FrozenInstanceError):
                report.metric = "changed"

    def test_mutation_validator_accepts_supplied_non_probability_ranges(self) -> None:
        for values in ((0.0, 0.0, 0.0), (-0.2, 1.4, -0.2), (2.0, 3.0, 4.0)):
            with self.subTest(values=values):
                reports = validate_mutation_matrix(build_substitution_matrix(*values))
                self.assertTrue(any(report.metric == "mutation_row_sum" for report in reports))

    def test_valid_all_sparse_unequal_and_zero_generation_analyses_pass(self) -> None:
        analyses = (
            run_exact_analysis(2, self.matrix),
            run_exact_analysis(
                3,
                self.matrix,
                {"AAA": 2.5, "AAG": 1.5, "ATG": 0.0, "TGG": 3.25},
            ),
            run_exact_analysis(0, self.matrix, {"AAA": 2.5, "TGG": 1.0}),
        )
        for analysis in analyses:
            with self.subTest(generations=analysis.simulation.stats["n_generations"]):
                reports = validate_exact_analysis(analysis)
                self.assertIsInstance(reports, tuple)
                self.assertGreater(len(reports), 100)
                self.assertTrue(
                    all(isinstance(report, ScientificInvariantReport) for report in reports)
                )

    def test_validation_does_not_mutate_inputs(self) -> None:
        matrix = build_substitution_matrix(0.2, 0.5, 0.3)
        matrix_before = copy.deepcopy(matrix)
        analysis = run_exact_analysis(
            2,
            matrix,
            {"AAA": 2.5, "AAG": 1.5, "TGG": 3.25},
        )
        weights_before = dict(analysis.start_weights)
        simulation_before = copy.deepcopy(analysis.simulation.to_legacy_tuple())
        frames_before = {
            name: getattr(analysis, name).copy(deep=True)
            for name in (
                "population_category_metrics",
                "population_survivor_fractions",
                "population_survival",
                "population_stop_outcomes",
            )
        }

        validate_mutation_matrix(matrix)
        validate_exact_analysis(analysis)

        self.assertEqual(matrix, matrix_before)
        self.assertEqual(analysis.start_weights, weights_before)
        self.assertEqual(analysis.simulation.to_legacy_tuple(), simulation_before)
        for name, before in frames_before.items():
            assert_frame_equal(getattr(analysis, name), before, check_exact=True)

    def test_biological_count_corruption_fails_with_context(self) -> None:
        with patch("engine.invariants.CODON_TABLE", {"AAA": "Lys"}):
            with self.assertRaises(ScientificInvariantError) as raised:
                validate_biological_invariants()
        self.assert_failure_context(raised.exception, "codon_table_count")

    def test_biological_stop_corruption_fails_independently(self) -> None:
        with patch("engine.invariants.STOP_CODONS", {"TAA", "TAG"}):
            with self.assertRaises(ScientificInvariantError) as raised:
                validate_biological_invariants()
        self.assert_failure_context(raised.exception, "stop_codons")

    def test_mutation_row_order_corruption_fails_independently(self) -> None:
        corrupt = copy.deepcopy(self.matrix)
        corrupt["A"] = {"G": 0.5, "C": 0.3, "T": 0.2}
        with self.assertRaises(ScientificInvariantError) as raised:
            validate_mutation_matrix(corrupt)
        self.assert_failure_context(raised.exception, "mutation_row_targets")

    def test_mutation_row_sum_corruption_fails_independently(self) -> None:
        corrupt = copy.deepcopy(self.matrix)
        corrupt["T"]["G"] += 0.25
        with self.assertRaises(ScientificInvariantError) as raised:
            validate_mutation_matrix(corrupt)
        self.assert_failure_context(raised.exception, "mutation_row_sum")

    def test_exact_schema_corruption_fails_independently(self) -> None:
        analysis = run_exact_analysis(2, self.matrix, {"AAA": 2.0, "TGG": 3.0})
        corrupt = analysis.population_category_metrics.rename(
            columns={"live_value": "wrong_value"}
        )
        with self.assertRaises(ScientificInvariantError) as raised:
            validate_exact_analysis(
                replace(analysis, population_category_metrics=corrupt)
            )
        self.assert_failure_context(raised.exception, "category_metrics_schema")

    def test_exact_generation_corruption_fails_independently(self) -> None:
        analysis = run_exact_analysis(2, self.matrix, {"AAA": 2.0, "TGG": 3.0})
        corrupt = analysis.population_category_metrics.copy(deep=True)
        corrupt.loc[0, "generation"] = 2
        with self.assertRaises(ScientificInvariantError) as raised:
            validate_exact_analysis(
                replace(analysis, population_category_metrics=corrupt)
            )
        self.assert_failure_context(raised.exception, "category_generation_rows")

    def test_exact_stop_order_corruption_fails_independently(self) -> None:
        analysis = run_exact_analysis(2, self.matrix, {"AAA": 2.0, "TGG": 3.0})
        corrupt = analysis.population_stop_outcomes.copy(deep=True)
        corrupt.iloc[[0, 1]] = corrupt.iloc[[1, 0]].to_numpy()
        with self.assertRaises(ScientificInvariantError) as raised:
            validate_exact_analysis(replace(analysis, population_stop_outcomes=corrupt))
        self.assert_failure_context(raised.exception, "stop_codon_order")

    def test_exact_category_order_corruption_fails_independently(self) -> None:
        analysis = run_exact_analysis(2, self.matrix, {"AAA": 2.0, "TGG": 3.0})
        categories = analysis.population_category_metrics.copy(deep=True)
        fractions = analysis.population_survivor_fractions.copy(deep=True)
        categories.iloc[[0, 1]] = categories.iloc[[1, 0]].to_numpy()
        fractions.iloc[[0, 1]] = fractions.iloc[[1, 0]].to_numpy()
        with self.assertRaises(ScientificInvariantError) as raised:
            validate_exact_analysis(
                replace(
                    analysis,
                    population_category_metrics=categories,
                    population_survivor_fractions=fractions,
                )
            )
        self.assert_failure_context(raised.exception, "category_order")

    def test_exact_stop_prefix_corruption_fails_independently(self) -> None:
        analysis = run_exact_analysis(2, self.matrix, {"AAA": 2.0, "TGG": 3.0})
        corrupt = analysis.population_stop_outcomes.copy(deep=True)
        corrupt.loc[3, "new_stop_value"] += 0.5
        with self.assertRaises(ScientificInvariantError) as raised:
            validate_exact_analysis(replace(analysis, population_stop_outcomes=corrupt))
        self.assert_failure_context(raised.exception, "stop_cumulative_progression")

    def test_exact_rollup_corruption_fails_independently(self) -> None:
        analysis = run_exact_analysis(2, self.matrix, {"AAA": 2.0, "TGG": 3.0})
        corrupt = analysis.population_category_metrics.copy(deep=True)
        corrupt.loc[0, "live_value"] += 0.5
        with self.assertRaises(ScientificInvariantError) as raised:
            validate_exact_analysis(
                replace(analysis, population_category_metrics=corrupt)
            )
        self.assert_failure_context(raised.exception, "amino_acid_to_category_rollup")

    def test_exact_denominator_corruption_fails_independently(self) -> None:
        analysis = run_exact_analysis(2, self.matrix, {"AAA": 2.0, "TGG": 3.0})
        corrupt = analysis.population_survival.copy(deep=True)
        corrupt.loc[0, "initial_value"] = 99.0
        with self.assertRaises(ScientificInvariantError) as raised:
            validate_exact_analysis(replace(analysis, population_survival=corrupt))
        self.assert_failure_context(raised.exception, "start_denominator")

    def test_exact_conservation_corruption_fails_independently(self) -> None:
        analysis = run_exact_analysis(2, self.matrix, {"AAA": 2.0, "TGG": 3.0})
        corrupt = analysis.population_survival.copy(deep=True)
        corrupt.loc[0, "stopped_value"] += 0.5
        with self.assertRaises(ScientificInvariantError) as raised:
            validate_exact_analysis(replace(analysis, population_survival=corrupt))
        self.assert_failure_context(raised.exception, "exact_conservation")

    def test_exact_fraction_corruption_fails_independently(self) -> None:
        analysis = run_exact_analysis(2, self.matrix, {"AAA": 2.0, "TGG": 3.0})
        corrupt = analysis.population_survivor_fractions.copy(deep=True)
        corrupt.loc[0, "fraction"] += 0.25
        with self.assertRaises(ScientificInvariantError) as raised:
            validate_exact_analysis(
                replace(analysis, population_survivor_fractions=corrupt)
            )
        self.assert_failure_context(raised.exception, "category_fraction")

    def test_exact_convergence_corruption_fails_independently(self) -> None:
        analysis = run_exact_analysis(2, self.matrix, {"AAA": 2.0, "TGG": 3.0})
        bad = get_exact_convergence(
            analysis,
            start_scope="population",
            start_key="all",
            basis="category_weight",
            tolerance=0.0,
        )
        bad.loc[0, "status"] = "wrong"
        with patch("engine.invariants.get_exact_convergence", return_value=bad):
            with self.assertRaises(ScientificInvariantError) as raised:
                validate_exact_analysis(analysis)
        self.assert_failure_context(raised.exception, "convergence")

    def test_exact_determinism_corruption_fails_independently(self) -> None:
        analysis = run_exact_analysis(1, self.matrix, {"AAA": 2.0, "TGG": 3.0})
        first = analysis.population_survival.copy(deep=True)
        second = first.copy(deep=True)
        second.loc[0, "live_value"] += 0.5
        with patch(
            "engine.invariants.get_exact_survival_by_start",
            side_effect=[first, second],
        ):
            with self.assertRaises(ScientificInvariantError) as raised:
                validate_exact_analysis(analysis)
        self.assert_failure_context(raised.exception, "deterministic_tables")


if __name__ == "__main__":
    unittest.main()
