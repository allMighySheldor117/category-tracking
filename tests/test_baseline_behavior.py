"""Immutable characterization tests for the pre-extraction scientific behavior.

The JSON fixture is intentionally static. These tests must never rewrite or
regenerate it; a mismatch is a compatibility failure requiring review.
"""

from __future__ import annotations

import collections
import hashlib
import inspect
import json
import random
import unittest
from pathlib import Path
from typing import Any

import pandas as pd

import category_tracking as legacy
import category_tracking_web as web


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "phase1_scientific_baseline.json"


def freeze(value: Any) -> Any:
    """Return an order- and type-preserving JSON-compatible representation."""
    if isinstance(value, float):
        return {"float_hex": value.hex()}
    if isinstance(value, collections.Counter):
        return {
            "type": "Counter",
            "items": [[freeze(key), freeze(item)] for key, item in value.items()],
        }
    if isinstance(value, dict):
        return {
            "type": type(value).__name__,
            "items": [[freeze(key), freeze(item)] for key, item in value.items()],
        }
    if isinstance(value, tuple):
        return {"type": "tuple", "items": [freeze(item) for item in value]}
    if isinstance(value, list):
        return {"type": "list", "items": [freeze(item) for item in value]}
    if isinstance(value, set):
        return {"type": "set", "items": [freeze(item) for item in sorted(value)]}
    return value


def structural_digest(value: Any) -> str:
    payload = json.dumps(freeze(value), ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def dataframe_digest(frame: pd.DataFrame) -> str:
    contract = (
        list(frame.columns),
        list(frame.index),
        [str(dtype) for dtype in frame.dtypes],
        frame.to_dict(orient="records"),
    )
    return structural_digest(contract)


class BaselineBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.nonuniform_matrix = legacy.build_substitution_matrix(0.2, 0.5, 0.3)
        cls.uniform_matrix = legacy.build_substitution_matrix(1 / 3, 1 / 3, 1 / 3)

    def test_biological_constants_and_order(self) -> None:
        expected = self.fixture["constants"]
        self.assertEqual(len(legacy.CODON_TABLE), expected["codon_count"])
        self.assertEqual(len(legacy.VALID_CODONS), expected["valid_count"])
        self.assertEqual(sorted(legacy.STOP_CODONS), expected["stop_codons"])
        self.assertEqual(
            [legacy.VALID_CODONS[0], legacy.VALID_CODONS[-1]],
            expected["first_last_valid"],
        )
        self.assertEqual(
            [legacy.CODON_TABLE["TGG"], legacy.get_primary_group_name("Trp")],
            expected["tgg"],
        )
        self.assertEqual(
            structural_digest(list(legacy.CODON_TABLE.items())),
            expected["codon_table_digest"],
        )
        self.assertEqual(structural_digest(legacy.VALID_CODONS), expected["valid_codons_digest"])
        self.assertEqual(
            structural_digest(list(legacy.AA_PROPERTIES.items())),
            expected["aa_properties_digest"],
        )
        self.assertEqual(
            structural_digest(list(legacy.PROPERTY_GROUPS.items())),
            expected["property_groups_digest"],
        )
        self.assertEqual(
            [legacy.PRESET_AT.hex(), legacy.PRESET_AG.hex(), legacy.PRESET_AC.hex()],
            expected["preset_hex"],
        )

    def test_public_callable_signatures(self) -> None:
        modules = {
            "category_tracking": legacy,
            "category_tracking_web": web,
        }
        for module_name, expected in self.fixture["public_surface"].items():
            module = modules[module_name]
            with self.subTest(module=module_name):
                observed = {
                    name: str(inspect.signature(getattr(module, name)))
                    for name in expected
                }
                self.assertEqual(observed, expected)

    def test_probability_parsing_and_matrix_order(self) -> None:
        expected = self.fixture["parsing"]
        for text in ("1/4", "25%", "0.25"):
            with self.subTest(text=text):
                self.assertEqual(legacy.parse_prob(text).hex(), expected[text])
        with self.assertRaisesRegex(ValueError, "^Cannot parse probability: 'abc'$" ):
            legacy.parse_prob("abc")
        self.assertEqual(expected["invalid"], "Cannot parse probability: 'abc'")
        self.assertEqual(
            structural_digest(self.nonuniform_matrix),
            self.fixture["matrix_digest"],
        )
        self.assertEqual(list(self.nonuniform_matrix), legacy.BASES)
        self.assertTrue(all(len(row) == 3 for row in self.nonuniform_matrix.values()))

    def test_exact_simulation_cases(self) -> None:
        contract = self.fixture["legacy_result_contracts"]
        for name, expected in self.fixture["exact_cases"].items():
            if expected["start_weights"] == "all_valid_codons_one":
                start_weights = {codon: 1.0 for codon in legacy.VALID_CODONS}
            else:
                start_weights = expected["start_weights"]
            matrix = (
                self.uniform_matrix
                if expected["matrix"] == "uniform"
                else self.nonuniform_matrix
            )
            result = legacy.run_simulation(expected["generations"], matrix, start_weights)
            with self.subTest(case=name):
                self.assertEqual(len(result), contract["exact_tuple_length"])
                self.assertEqual(
                    [type(item).__name__ for item in result],
                    contract["exact_top_level_types"],
                )
                self.assertEqual(structural_digest(result), expected["digest"])
                self.assertEqual(list(result[8]), contract["stats_key_order"])
                self.assertEqual(list(result[9]), contract["stop_key_order"])
                self.assertEqual(list(result[10]), contract["track_key_order"])
                self.assertEqual(freeze(result[8]), expected["stats"])
                self.assertEqual(len(result[4]), expected["final_codon_count"])
                self.assertEqual(freeze(result[9]["by_stop_codon"]), expected["stop_codons"])
                self.assertIsInstance(result[7], dict)
                self.assertTrue(
                    all(isinstance(value, collections.Counter) for value in result[7].values())
                )
                self.assertAlmostEqual(
                    float(result[8]["total_fin_weight"] + result[8]["total_stop_prob"]),
                    float(result[8]["total_start_copies"]),
                    places=12,
                )

    def test_analysis_denominators_and_dataframe_contracts(self) -> None:
        result = legacy.run_simulation(2, self.nonuniform_matrix, {"TGG": 2.0})
        track_data = result[10]
        frames = {
            "exact_category_tgg": web.exact_category_series(track_data, "TGG", 2),
            "exact_stop_tgg": web.exact_stop_series(track_data, "TGG", 2),
        }
        frames["surviving_fraction_tgg"] = web.surviving_category_fraction_series(
            frames["exact_category_tgg"]
        )

        for name, frame in frames.items():
            expected = self.fixture["analysis_cases"][name]
            with self.subTest(frame=name):
                self.assertEqual(list(frame.columns), expected["columns"])
                self.assertEqual([str(dtype) for dtype in frame.dtypes], expected["dtypes"])
                self.assertEqual(len(frame), expected["row_count"])
                self.assertEqual(dataframe_digest(frame), expected["digest"])

        final_cumulative = frames["exact_stop_tgg"]["cumulative_stops"].iloc[-1]
        self.assertEqual(float(final_cumulative).hex(), self.fixture["analysis_cases"]["exact_stop_tgg"]["final_cumulative_hex"])
        sums = frames["surviving_fraction_tgg"].groupby("generation")["value"].sum()
        self.assertEqual(
            {str(index): float(value).hex() for index, value in sums.items()},
            self.fixture["analysis_cases"]["surviving_fraction_tgg"]["generation_fraction_sums"],
        )
        self.assertEqual(
            list(web.exact_no_more_change(track_data, "TGG", 2)),
            self.fixture["analysis_cases"]["no_more_change_counts"],
        )
        self.assertEqual(
            list(
                web.exact_no_more_change(
                    track_data,
                    "TGG",
                    2,
                    "Exact surviving trait fractions",
                    0.01,
                )
            ),
            self.fixture["analysis_cases"]["no_more_change_fractions"],
        )

        zero_source = pd.DataFrame(
            [
                {"generation": 1, "category": "Hydrophobic", "value": 0.0},
                {"generation": 1, "category": "Polar uncharged", "value": 0.0},
            ]
        )
        zero_fraction = web.surviving_category_fraction_series(zero_source)
        self.assertEqual(zero_fraction["value"].tolist(), [0.0, 0.0])
        empty_summary = web.trait_codon_survival_summary(
            pd.DataFrame(columns=["generation", "codon", "aa", "value"]),
            0,
        )
        self.assertEqual(
            list(empty_summary.columns),
            ["codon", "aa", "final_surviving", "stopped", "stop_fraction"],
        )
        self.assertTrue(empty_summary.empty)

    def test_seeded_sampled_cases_and_rng_state(self) -> None:
        contract = self.fixture["legacy_result_contracts"]
        for name, expected in self.fixture["sampled_cases"].items():
            if name == "consecutive_calls":
                continue
            random.seed(expected["seed"])
            before = random.getstate()
            result = legacy.run_experiment(
                expected["generations"],
                self.nonuniform_matrix,
                expected["start_weights"],
            )
            after = random.getstate()
            with self.subTest(case=name):
                self.assertEqual(len(result), contract["sampled_tuple_length"])
                self.assertEqual(
                    [type(item).__name__ for item in result],
                    contract["sampled_top_level_types"],
                )
                self.assertEqual(structural_digest(result), expected["result_digest"])
                self.assertEqual(len(result[0]), expected["record_count"])
                self.assertEqual(sum(record["hit_stop"] for record in result[0]), expected["stop_count"])
                self.assertEqual([record["path"] for record in result[0]], expected["paths"])
                self.assertEqual(list(result[3]), legacy.VALID_CODONS)
                self.assertTrue(
                    all(isinstance(value, collections.Counter) for value in result[3].values())
                )
                for record in result[0]:
                    self.assertEqual(list(record), contract["record_key_order"])
                if expected.get("rng_unchanged"):
                    self.assertEqual(before, after)
                else:
                    self.assertEqual(structural_digest(before), expected["before_state_digest"])
                    self.assertEqual(structural_digest(after), expected["after_state_digest"])

    def test_consecutive_sampled_calls_preserve_draw_order(self) -> None:
        expected = self.fixture["sampled_cases"]["consecutive_calls"]
        random.seed(expected["seed"])
        first = legacy.run_experiment(
            expected["generations"],
            self.nonuniform_matrix,
            expected["start_weights"],
        )
        state_after_first = random.getstate()
        second = legacy.run_experiment(
            expected["generations"],
            self.nonuniform_matrix,
            expected["start_weights"],
        )
        state_after_second = random.getstate()
        self.assertEqual(structural_digest(first), expected["first_result_digest"])
        self.assertEqual(structural_digest(state_after_first), expected["first_state_digest"])
        self.assertEqual(structural_digest(second), expected["second_result_digest"])
        self.assertEqual(structural_digest(state_after_second), expected["second_state_digest"])
        self.assertEqual([record["path"] for record in first[0]], expected["first_paths"])
        self.assertEqual([record["path"] for record in second[0]], expected["second_paths"])


if __name__ == "__main__":
    unittest.main()
