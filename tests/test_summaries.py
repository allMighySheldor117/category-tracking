"""Exact comparisons for extracted stop, convergence, and outcome summaries."""

from __future__ import annotations

import collections
import random
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

import category_tracking as legacy
import category_tracking_web as web
from engine.category_analysis import exact_all_category_series
from engine.exact_tracking import run_simulation
from engine.models import ExactSimulationResult, SampledSimulationResult
from engine.mutation_matrix import build_substitution_matrix
from engine.sampled_tracking import run_experiment
from engine import summaries


class SummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        matrix = build_substitution_matrix(0.2, 0.5, 0.3)
        weights = {codon: 2.0 for codon in legacy.VALID_CODONS}
        cls.exact = run_simulation(3, matrix, weights)
        cls.legacy_exact = ExactSimulationResult.from_legacy_tuple(
            legacy.run_simulation(3, matrix, weights)
        )
        random.seed(442)
        cls.sampled = run_experiment(3, matrix, weights)
        random.seed(442)
        cls.legacy_sampled = SampledSimulationResult.from_legacy_tuple(
            legacy.run_experiment(3, matrix, weights)
        )

    def assert_frame_matches(self, observed: pd.DataFrame, expected: pd.DataFrame) -> None:
        assert_frame_equal(observed, expected, check_exact=True, check_dtype=True)
        self.assertEqual(list(observed.index), list(expected.index))
        self.assertEqual(list(observed.columns), list(expected.columns))

    def test_stop_series_match_legacy(self) -> None:
        self.assert_frame_matches(
            summaries.sampled_stop_series(self.sampled, "TGG", 3),
            web.sampled_stop_series(self.legacy_sampled.records, "TGG", 3),
        )
        self.assert_frame_matches(
            summaries.exact_stop_series(self.exact, "TGG", 3),
            web.exact_stop_series(self.legacy_exact.track_data, "TGG", 3),
        )

    def test_convergence_and_property_summaries_match_legacy(self) -> None:
        series_cases = (
            {},
            {"a": [1.0]},
            {"a": [1.0, 1.0, 1.0], "b": [0.0, 0.0]},
            {"a": [0.0, 0.5, 0.75]},
        )
        for series in series_cases:
            with self.subTest(series=series):
                self.assertEqual(
                    summaries.convergence_generation(series).to_legacy_tuple(),
                    legacy.convergence_generation(series),
                )
                self.assertEqual(
                    summaries.convergence_text(series),
                    legacy.convergence_text(series),
                )
        self.assertEqual(
            summaries.property_stop_counter(self.exact),
            legacy.property_stop_counter(self.legacy_exact.stop_data),
        )
        fallback = {"by_start_aa": collections.Counter({"Trp": 2.0})}
        self.assertEqual(
            summaries.property_stop_counter(fallback),
            legacy.property_stop_counter(fallback),
        )

    def test_no_more_change_labels_tolerances_and_all_stopped_match(self) -> None:
        for basis, alpha in (
            ("Current computation", 0.01),
            ("Exact surviving trait fractions", 0.01),
            ("Surviving trait fractions", 0.1),
        ):
            with self.subTest(basis=basis, alpha=alpha):
                self.assertEqual(
                    summaries.exact_no_more_change(
                        self.exact,
                        "TGG",
                        3,
                        basis,
                        alpha,
                    ).to_legacy_tuple(),
                    web.exact_no_more_change(
                        self.legacy_exact.track_data, "TGG", 3, basis, alpha
                    ),
                )
                self.assertEqual(
                    summaries.no_more_change_note(basis, alpha),
                    web.no_more_change_note(basis, alpha),
                )
        all_stopped = pd.DataFrame(
            [
                {"generation": 1, "category": "Hydrophobic", "value": 0.0},
                {"generation": 2, "category": "Hydrophobic", "value": 0.0},
            ]
        )
        self.assertEqual(
            summaries.no_more_change_from_df(all_stopped).to_legacy_tuple(),
            web.no_more_change_from_df(all_stopped),
        )

    def test_all_codon_summary_matches_legacy_schema_and_order(self) -> None:
        observed = summaries.all_codon_no_more_change(
            self.exact,
            3,
            "Exact surviving trait fractions",
            0.01,
        )
        expected = web.all_codon_no_more_change(
            self.legacy_sampled.records,
            self.legacy_exact.track_data,
            3,
            "Exact probabilities",
            "Exact surviving trait fractions",
            0.01,
        )
        self.assert_frame_matches(observed, expected)
        self.assertEqual(observed["codon"].tolist(), legacy.VALID_CODONS)

    def test_sampled_and_exact_outcome_tables_preserve_rows_and_order(self) -> None:
        sampled_records = [
            {
                "start": "TGG", "start_aa": "Trp", "final": "TGA",
                "final_aa": "Stop", "hit_stop": True, "stop_gen": 1,
                "copy": 1, "path": ["TGG", "TGA"],
            },
            {
                "start": "TGG", "start_aa": "Trp", "final": "TTG",
                "final_aa": "Leu", "hit_stop": False, "stop_gen": None,
                "copy": 2, "path": ["TGG", "TTG"],
            },
        ]
        sampled = summaries.sampled_codon_outcome_table(sampled_records, "TGG", 1)
        expected_sampled = pd.DataFrame(
            [
                {"codon": "TTG", "value": 1, "amino_acid": "Leu", "category": "Hydrophobic"},
                {"codon": "TGA stop", "value": 1, "amino_acid": "Stop", "category": "Stop"},
            ]
        ).sort_values("value", ascending=False)
        self.assert_frame_matches(sampled, expected_sampled)

        exact = summaries.exact_codon_outcome_table(self.exact, "TGG", 1)
        expected_rows = [
            {
                "codon": codon,
                "value": value,
                "amino_acid": legacy.CODON_TABLE[codon],
                "category": legacy.get_primary_group_name(legacy.CODON_TABLE[codon]),
            }
            for codon, value in self.exact.track_data["per_gen_codon_from"][0].get("TGG", {}).items()
        ]
        expected_rows.extend(
            {
                "codon": f"{codon} stop",
                "value": value,
                "amino_acid": "Stop",
                "category": "Stop",
            }
            for codon, value in self.exact.track_data["per_gen_stop_codon_to"][0].get("TGG", {}).items()
        )
        self.assert_frame_matches(
            exact,
            pd.DataFrame(expected_rows).sort_values("value", ascending=False),
        )

    def test_population_metrics_preserve_render_panel_arithmetic(self) -> None:
        starting = summaries.starting_population_metrics(
            self.exact,
            len(self.sampled.records),
        )
        self.assertEqual(starting.total_start_copies, 122.0)
        self.assertEqual(starting.copies_per_codon, 2.0)
        categories = exact_all_category_series(self.exact, 3)
        final = summaries.final_population_metrics(
            categories,
            3,
            starting.total_start_copies,
        )
        expected_live = float(categories[categories["generation"] == 3]["value"].sum())
        expected_stopped = max(0.0, starting.total_start_copies - expected_live)
        self.assertEqual(final.final_live.hex(), expected_live.hex())
        self.assertEqual(final.final_stopped.hex(), expected_stopped.hex())
        self.assertEqual(
            final.stop_fraction.hex(),
            (expected_stopped / starting.total_start_copies).hex(),
        )


if __name__ == "__main__":
    unittest.main()
