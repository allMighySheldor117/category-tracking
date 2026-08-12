"""Contract tests for the engine package and named result boundaries."""

from __future__ import annotations

import inspect
import subprocess
import sys
import unittest
from collections import Counter

from engine import ExactSimulationResult, SampledSimulationResult
from engine.models import ConvergenceResult, NoMoreChangeResult


class EngineBoundaryTests(unittest.TestCase):
    def test_summary_results_are_named_with_explicit_legacy_conversion(self) -> None:
        convergence = ConvergenceResult(generation=3, max_delta=0.01)
        stability = NoMoreChangeResult(
            generation="3",
            status="constant state starts: category counts stable",
        )

        self.assertEqual(convergence.to_legacy_tuple(), (3, 0.01))
        self.assertEqual(
            stability.to_legacy_tuple(),
            ("3", "constant state starts: category counts stable"),
        )
        self.assertEqual(list(vars(convergence)), ["generation", "max_delta"])
        self.assertEqual(list(vars(stability)), ["generation", "status"])

    def test_exact_result_maps_every_legacy_position_by_name(self) -> None:
        values = (
            Counter({"enc_codon": 1}),
            Counter({"enc_aa": 2}),
            Counter({"enc_codon_cnt": 3}),
            Counter({"enc_aa_cnt": 4}),
            Counter({"fin_codon": 5}),
            Counter({"fin_aa": 6}),
            [Counter({"generation": 7})],
            {"TGG": Counter({"TGG": 8})},
            {"first": 9, "second": 10},
            {"by_start_aa": Counter(), "detail": []},
            {"per_gen_cat_from": {"TGG": []}},
        )

        named = ExactSimulationResult.from_legacy_tuple(values)

        self.assertEqual(
            [field for field in vars(named)],
            [
                "enc_codon",
                "enc_aa",
                "enc_codon_cnt",
                "enc_aa_cnt",
                "fin_codon",
                "fin_aa",
                "per_gen_aa",
                "start_to_fin",
                "stats",
                "stop_data",
                "track_data",
            ],
        )
        self.assertEqual(named.to_legacy_tuple(), values)
        self.assertTrue(
            all(observed is expected for observed, expected in zip(named.to_legacy_tuple(), values))
        )
        self.assertEqual(list(named.stats), ["first", "second"])
        self.assertEqual(list(named.stop_data), ["by_start_aa", "detail"])

    def test_sampled_result_maps_every_legacy_position_by_name(self) -> None:
        record = {
            "start": "TGG",
            "start_aa": "Trp",
            "final": "TGA",
            "final_aa": "Stop",
            "hit_stop": True,
            "stop_gen": 1,
            "copy": 1,
            "path": ["TGG", "TGA"],
        }
        values = (
            [record],
            Counter(),
            Counter(),
            {"TGG": Counter()},
        )

        named = SampledSimulationResult.from_legacy_tuple(values)

        self.assertEqual(
            list(vars(named)),
            ["records", "sample_fin_codon", "sample_fin_aa", "sample_start_to_fin"],
        )
        self.assertEqual(named.to_legacy_tuple(), values)
        self.assertTrue(
            all(observed is expected for observed, expected in zip(named.to_legacy_tuple(), values))
        )
        self.assertEqual(
            list(named.records[0]),
            ["start", "start_aa", "final", "final_aa", "hit_stop", "stop_gen", "copy", "path"],
        )

    def test_empty_and_sparse_values_keep_concrete_types(self) -> None:
        exact = ExactSimulationResult(
            enc_codon=Counter(),
            enc_aa=Counter(),
            enc_codon_cnt=Counter(),
            enc_aa_cnt=Counter(),
            fin_codon=Counter({"TGG": 0.0}),
            fin_aa=Counter(),
            per_gen_aa=[],
            start_to_fin={"TGG": Counter()},
            stats={},
            stop_data={},
            track_data={},
        )
        sampled = SampledSimulationResult([], Counter(), Counter(), {})

        self.assertEqual(
            [type(value) for value in exact.to_legacy_tuple()],
            [Counter, Counter, Counter, Counter, Counter, Counter, list, dict, dict, dict, dict],
        )
        self.assertEqual(
            [type(value) for value in sampled.to_legacy_tuple()],
            [list, Counter, Counter, dict],
        )

    def test_public_result_methods_are_typed_and_have_no_defaults(self) -> None:
        for result_type in (ExactSimulationResult, SampledSimulationResult):
            with self.subTest(result_type=result_type.__name__):
                init_signature = inspect.signature(result_type)
                self.assertTrue(
                    all(parameter.annotation is not inspect.Parameter.empty for parameter in init_signature.parameters.values())
                )
                self.assertTrue(
                    all(parameter.default is inspect.Parameter.empty for parameter in init_signature.parameters.values())
                )
                self.assertIsNot(
                    inspect.signature(result_type.to_legacy_tuple).return_annotation,
                    inspect.Signature.empty,
                )

    def test_fresh_engine_import_does_not_load_ui_frameworks(self) -> None:
        command = (
            "import sys, engine; "
            "forbidden={'streamlit','tkinter','plotly','PyQt5'}; "
            "assert not forbidden.intersection(sys.modules), forbidden.intersection(sys.modules)"
        )
        completed = subprocess.run(
            [sys.executable, "-c", command],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
