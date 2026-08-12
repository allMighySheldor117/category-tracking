"""Schema- and denominator-exact comparisons for extracted analysis functions."""

from __future__ import annotations

import random
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

import category_tracking as legacy
import category_tracking_web as web
from engine import category_analysis as analysis
from engine.exact_tracking import run_simulation
from engine.models import ExactSimulationResult, SampledSimulationResult
from engine.mutation_matrix import build_substitution_matrix
from engine.sampled_tracking import run_experiment


class CategoryAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        matrix = build_substitution_matrix(0.2, 0.5, 0.3)
        cls.weights = {codon: 2.0 for codon in legacy.VALID_CODONS}
        cls.exact = run_simulation(3, matrix, cls.weights)
        random.seed(1781)
        cls.sampled = run_experiment(3, matrix, cls.weights)

        cls.legacy_exact = ExactSimulationResult.from_legacy_tuple(
            legacy.run_simulation(3, matrix, cls.weights)
        )
        random.seed(1781)
        cls.legacy_sampled = SampledSimulationResult.from_legacy_tuple(
            legacy.run_experiment(3, matrix, cls.weights)
        )

    def assert_frame_matches(self, observed: pd.DataFrame, expected: pd.DataFrame) -> None:
        assert_frame_equal(observed, expected, check_exact=True, check_dtype=True)
        self.assertEqual(list(observed.index), list(expected.index))
        self.assertEqual(list(observed.columns), list(expected.columns))

    def test_category_and_population_series_match_legacy(self) -> None:
        cases = (
            (
                analysis.sampled_category_series(self.sampled, "TGG", 3),
                web.sampled_category_series(self.legacy_sampled.records, "TGG", 3),
            ),
            (
                analysis.exact_category_series(self.exact, "TGG", 3),
                web.exact_category_series(self.legacy_exact.track_data, "TGG", 3),
            ),
            (
                analysis.sampled_all_category_series(self.sampled, 3),
                web.sampled_all_category_series(self.legacy_sampled.records, 3),
            ),
            (
                analysis.exact_all_category_series(self.exact, 3),
                web.exact_all_category_series(self.legacy_exact.track_data, 3),
            ),
        )
        for observed, expected in cases:
            with self.subTest(columns=list(expected.columns)):
                self.assert_frame_matches(observed, expected)

    def test_start_trait_survival_and_stop_denominators_match_legacy(self) -> None:
        cases = (
            (
                analysis.sampled_start_trait_survival_series(self.sampled, 3),
                web.sampled_start_trait_survival_series(self.legacy_sampled.records, 3),
            ),
            (
                analysis.exact_start_trait_survival_series(self.exact, 3),
                web.exact_start_trait_survival_series(self.legacy_exact.track_data, 3),
            ),
            (
                analysis.sampled_start_trait_stop_percentage_series(self.sampled, 3),
                web.sampled_start_trait_stop_percentage_series(self.legacy_sampled.records, 3),
            ),
            (
                analysis.exact_start_trait_stop_percentage_series(self.exact, 3, 2.0),
                web.exact_start_trait_stop_percentage_series(self.legacy_exact.track_data, 3, 2.0),
            ),
        )
        for observed, expected in cases:
            with self.subTest(columns=list(expected.columns)):
                self.assert_frame_matches(observed, expected)

    def test_trait_codon_and_amino_acid_series_match_legacy(self) -> None:
        trait = "Hydrophobic"
        self.assertEqual(analysis.codons_for_trait(trait), web.codons_for_trait(trait))
        cases = (
            (
                analysis.sampled_trait_codon_survival_series(self.sampled, trait, 3),
                web.sampled_trait_codon_survival_series(self.legacy_sampled.records, trait, 3),
            ),
            (
                analysis.exact_trait_codon_survival_series(self.exact, trait, 3),
                web.exact_trait_codon_survival_series(self.legacy_exact.track_data, trait, 3),
            ),
            (
                analysis.sampled_trait_aa_survival_series(self.sampled, trait, 3),
                web.sampled_trait_aa_survival_series(self.legacy_sampled.records, trait, 3),
            ),
            (
                analysis.exact_trait_aa_survival_series(self.exact, trait, 3),
                web.exact_trait_aa_survival_series(self.legacy_exact.track_data, trait, 3),
            ),
        )
        for observed, expected in cases:
            with self.subTest(columns=list(expected.columns)):
                self.assert_frame_matches(observed, expected)

    def test_fraction_balance_and_trait_summary_match_legacy(self) -> None:
        exact_categories = analysis.exact_category_series(self.exact, "TGG", 3)
        cases = (
            (
                analysis.surviving_category_fraction_series(exact_categories),
                web.surviving_category_fraction_series(exact_categories),
            ),
            (
                analysis.survival_balance_series(exact_categories, 2.0),
                web.survival_balance_series(exact_categories, 2.0),
            ),
        )
        trait_series = analysis.exact_trait_codon_survival_series(
            self.exact, "Hydrophobic", 3
        )
        cases += (
            (
                analysis.trait_codon_survival_summary(trait_series, 2.0),
                web.trait_codon_survival_summary(trait_series, 2.0),
            ),
        )
        for observed, expected in cases:
            with self.subTest(columns=list(expected.columns)):
                self.assert_frame_matches(observed, expected)

    def test_zero_denominators_and_empty_schemas_match_legacy(self) -> None:
        zero_categories = pd.DataFrame(
            [
                {"generation": 1, "category": "Hydrophobic", "value": 0.0},
                {"generation": 1, "category": "Polar uncharged", "value": 0.0},
            ]
        )
        self.assert_frame_matches(
            analysis.surviving_category_fraction_series(zero_categories),
            web.surviving_category_fraction_series(zero_categories),
        )
        self.assert_frame_matches(
            analysis.trait_codon_survival_summary(
                pd.DataFrame(columns=["generation", "codon", "aa", "value"]),
                0,
            ),
            web.trait_codon_survival_summary(
                pd.DataFrame(columns=["generation", "codon", "aa", "value"]),
                0,
            ),
        )
        empty_exact = run_simulation(0, build_substitution_matrix(0.2, 0.5, 0.3), {})
        self.assert_frame_matches(
            analysis.exact_category_series(empty_exact, "TGG", 0),
            web.exact_category_series(empty_exact.track_data, "TGG", 0),
        )

    def test_engine_analysis_accepts_named_and_compatibility_inputs(self) -> None:
        self.assert_frame_matches(
            analysis.exact_category_series(self.exact, "TGG", 3),
            analysis.exact_category_series(self.exact.track_data, "TGG", 3),
        )
        self.assert_frame_matches(
            analysis.sampled_category_series(self.sampled, "TGG", 3),
            analysis.sampled_category_series(self.sampled.records, "TGG", 3),
        )


if __name__ == "__main__":
    unittest.main()
