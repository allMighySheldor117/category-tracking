"""Phase 3 comparison-layer optimization guards."""

from __future__ import annotations

import unittest

from pandas.testing import assert_frame_equal

from engine import comparisons
from engine.aggregated_tracking import run_aggregated_experiment
from engine.comparisons import compare_exact_to_sampled, compare_numeric_metric
from engine.exact_analysis import (
    get_exact_category_metrics,
    get_exact_survival_by_start,
    run_exact_analysis,
)
from engine.mutation_matrix import build_substitution_matrix
from engine.summaries import get_aggregated_survival_by_start


class Phase3ComparisonOptimizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline_exact = run_exact_analysis(
            3,
            build_substitution_matrix(0.2, 0.5, 0.3),
            {"AAA": 2.0, "TGG": 1.0},
        )
        cls.candidate_exact = run_exact_analysis(
            3,
            build_substitution_matrix(0.1, 0.7, 0.2),
            {"AAA": 2.0, "TGG": 1.0},
        )
        cls.sampled = run_aggregated_experiment(
            3,
            build_substitution_matrix(0.2, 0.5, 0.3),
            {"AAA": 25, "TGG": 25},
            seed=12345,
        )

    def setUp(self) -> None:
        comparisons._EXPECTED_SIGNATURE_CACHE.clear()

    def test_expected_schema_signatures_are_cached_without_output_drift(self) -> None:
        baseline = get_exact_category_metrics(
            self.baseline_exact, start_scope="population", start_key="all"
        )
        candidate = get_exact_category_metrics(
            self.candidate_exact, start_scope="population", start_key="all"
        )

        first = compare_numeric_metric(
            baseline,
            candidate,
            metric="category_live_value",
            baseline_label="Baseline",
            candidate_label="Candidate",
        )
        cache_size = len(comparisons._EXPECTED_SIGNATURE_CACHE)
        second = compare_numeric_metric(
            baseline,
            candidate,
            metric="category_live_value",
            baseline_label="Baseline",
            candidate_label="Candidate",
        )

        self.assertGreater(cache_size, 0)
        self.assertEqual(len(comparisons._EXPECTED_SIGNATURE_CACHE), cache_size)
        assert_frame_equal(first.table, second.table)

    def test_exact_to_sampled_statistics_are_unchanged_by_schema_cache(self) -> None:
        exact = get_exact_survival_by_start(
            self.baseline_exact, start_scope="population", start_key="all"
        )
        sampled = get_aggregated_survival_by_start(
            self.sampled, start_scope="population", start_key="all"
        )

        first = compare_exact_to_sampled(
            exact,
            sampled,
            metric="survivor_fraction",
            denominator_scope="population_initial",
        )
        cache_keys_after_first = tuple(comparisons._EXPECTED_SIGNATURE_CACHE)
        second = compare_exact_to_sampled(
            exact,
            sampled,
            metric="survivor_fraction",
            denominator_scope="population_initial",
        )

        self.assertEqual(
            tuple(comparisons._EXPECTED_SIGNATURE_CACHE),
            cache_keys_after_first,
        )
        assert_frame_equal(first.table, second.table)
        self.assertEqual(first.familywise_alpha, 0.01)
        self.assertEqual(second.familywise_alpha, 0.01)


if __name__ == "__main__":
    unittest.main()
