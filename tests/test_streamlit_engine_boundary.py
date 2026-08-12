"""Focused checks for the Streamlit-to-engine cutover boundary."""

from __future__ import annotations

import ast
import inspect
import subprocess
import sys
import unittest
from pathlib import Path

import category_tracking_web as web
from engine.models import ExactSimulationResult, SampledSimulationResult


APP_PATH = Path(__file__).parents[1] / "category_tracking_web.py"


class StreamlitEngineBoundaryTests(unittest.TestCase):
    def test_fresh_web_import_does_not_import_tkinter_compatibility_module(self) -> None:
        command = (
            "import sys, category_tracking_web; "
            "assert 'category_tracking' not in sys.modules; "
            "assert 'tkinter' not in sys.modules"
        )
        completed = subprocess.run(
            [sys.executable, "-c", command],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_render_consumers_use_named_result_annotations(self) -> None:
        functions = (
            web.fullscreen_two_codon_comparison,
            web.render_all_codon_population_panel,
            web.render_trait_codon_survival_panel,
            web.render_codon_panel,
            web.render_whole_population_view,
            web.render_codon_focus_view,
        )
        for function in functions:
            signature = inspect.signature(function)
            with self.subTest(function=function.__name__):
                for name, parameter in signature.parameters.items():
                    if name.endswith("sim") or name == "sim":
                        self.assertEqual(parameter.annotation, "ExactSimulationResult")
                    if name.endswith("exp") or name == "exp":
                        self.assertEqual(parameter.annotation, "SampledSimulationResult")

    def test_web_source_has_no_legacy_scientific_import_or_tuple_consumers(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        self.assertNotIn("from category_tracking import", source)
        self.assertNotIn("sim[8]", source)
        self.assertNotIn("sim[10]", source)
        self.assertNotIn("exp[0]", source)
        self.assertNotIn("for start_codon in VALID_CODONS", source)
        self.assertNotIn("per_gen_codon_from", source)
        self.assertNotIn("per_gen_stop_codon_from", source)

    def test_scientific_compatibility_helpers_are_thin_engine_adapters(self) -> None:
        functions = (
            web.sampled_category_series,
            web.exact_category_series,
            web.sampled_all_category_series,
            web.exact_all_category_series,
            web.sampled_start_trait_survival_series,
            web.exact_start_trait_survival_series,
            web.sampled_start_trait_stop_percentage_series,
            web.exact_start_trait_stop_percentage_series,
            web.codons_for_trait,
            web.sampled_trait_codon_survival_series,
            web.exact_trait_codon_survival_series,
            web.sampled_trait_aa_survival_series,
            web.exact_trait_aa_survival_series,
            web.surviving_category_fraction_series,
            web.survival_balance_series,
            web.trait_codon_survival_summary,
            web.sampled_stop_series,
            web.exact_stop_series,
            web.no_more_change_from_df,
            web.exact_no_more_change,
            web.no_more_change_note,
            web.all_codon_no_more_change,
        )
        for function in functions:
            tree = ast.parse(inspect.getsource(function))
            with self.subTest(function=function.__name__):
                self.assertFalse(any(isinstance(node, (ast.For, ast.While)) for node in ast.walk(tree)))
                calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
                self.assertGreaterEqual(len(calls), 1)

    def test_local_probability_adapter_preserves_existing_formats_and_errors(self) -> None:
        self.assertEqual(web.parse_prob("1/4").hex(), (0.25).hex())
        self.assertEqual(web.parse_prob("25%").hex(), (0.25).hex())
        self.assertEqual(web.parse_prob(" 0.25 ").hex(), (0.25).hex())
        with self.assertRaisesRegex(ValueError, "^Cannot parse probability: 'abc'$"):
            web.parse_prob("abc")

    def test_cached_boundary_still_returns_legacy_tuple_contracts(self) -> None:
        web.run_cached.clear()
        exact_legacy, sampled_legacy = web.run_cached(1, 1, 0.2, 0.5, 0.3, 7)
        self.assertIsInstance(exact_legacy, tuple)
        self.assertIsInstance(sampled_legacy, tuple)
        self.assertEqual(len(exact_legacy), 11)
        self.assertEqual(len(sampled_legacy), 4)
        self.assertIsInstance(
            ExactSimulationResult.from_legacy_tuple(exact_legacy),
            ExactSimulationResult,
        )
        self.assertIsInstance(
            SampledSimulationResult.from_legacy_tuple(sampled_legacy),
            SampledSimulationResult,
        )


if __name__ == "__main__":
    unittest.main()
