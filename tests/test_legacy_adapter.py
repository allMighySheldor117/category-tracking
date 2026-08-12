"""Focused compatibility-boundary tests for the Tkinter application module."""

from __future__ import annotations

import inspect
import subprocess
import sys
import unittest

import category_tracking as legacy
from engine import genetic_code, mutation_matrix


class LegacyAdapterTests(unittest.TestCase):
    def test_scientific_definitions_are_engine_reexports(self) -> None:
        self.assertIs(legacy.BASES, genetic_code.BASES)
        self.assertIs(legacy.STOP_CODONS, genetic_code.STOP_CODONS)
        self.assertIs(legacy.CODON_TABLE, genetic_code.CODON_TABLE)
        self.assertIs(legacy.AA_FULL, genetic_code.AA_FULL)
        self.assertIs(legacy.VALID_CODONS, genetic_code.VALID_CODONS)
        self.assertIs(legacy.ALL_AAS, genetic_code.ALL_AAS)
        self.assertIs(legacy.AA_PROPERTIES, genetic_code.AA_PROPERTIES)
        self.assertIs(legacy.CODON_COUNT_MAP, genetic_code.CODON_COUNT_MAP)
        self.assertIs(legacy.CODON_COUNT_GROUPS, genetic_code.CODON_COUNT_GROUPS)
        self.assertEqual(
            list(legacy.PROPERTY_GROUPS),
            list(genetic_code.PROPERTY_LABELS),
        )

    def test_public_adapter_signatures_remain_unannotated_and_exact(self) -> None:
        expected = {
            "get_primary_group": "(aa)",
            "get_primary_group_name": "(aa)",
            "property_stop_counter": "(stop_data)",
            "convergence_generation": "(series, threshold=0.0001)",
            "convergence_text": "(series, threshold=0.0001)",
            "count_codons_for_aa": "(aa)",
            "get_codon_count": "(aa)",
            "build_substitution_matrix": "(p_at, p_ag, p_ac)",
            "run_simulation": "(n_generations, sub_matrix, start_weights=None)",
            "run_experiment": "(n_generations, sub_matrix, start_weights)",
        }
        self.assertEqual(
            {name: str(inspect.signature(getattr(legacy, name))) for name in expected},
            expected,
        )

    def test_simulation_functions_are_thin_legacy_tuple_boundaries(self) -> None:
        exact_source = inspect.getsource(legacy.run_simulation)
        sampled_source = inspect.getsource(legacy.run_experiment)
        self.assertIn("_engine_run_simulation", exact_source)
        self.assertIn("to_legacy_tuple", exact_source)
        self.assertIn("_engine_run_experiment", sampled_source)
        self.assertIn("to_legacy_tuple", sampled_source)
        for source in (exact_source, sampled_source):
            self.assertNotIn("for start_codon in VALID_CODONS", source)
            self.assertNotIn("collections.defaultdict", source)

    def test_matrix_adapter_delegates_to_engine_primitive(self) -> None:
        observed = legacy.build_substitution_matrix(0.2, 0.5, 0.3)
        expected = mutation_matrix.build_substitution_matrix(0.2, 0.5, 0.3)
        self.assertEqual(observed, expected)

    def test_import_does_not_create_or_enter_a_tkinter_window(self) -> None:
        command = (
            "import tkinter, category_tracking; "
            "assert tkinter._default_root is None"
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
