"""Exact same-process comparisons for extracted probability tracking."""

from __future__ import annotations

import collections
import inspect
import unittest
from typing import Any

import category_tracking as legacy
from engine.exact_tracking import run_simulation
from engine.models import ExactSimulationResult
from engine.mutation_matrix import build_substitution_matrix


def freeze(value: Any) -> Any:
    """Represent floats, container types, and insertion order exactly."""
    if isinstance(value, float):
        return ("float", value.hex())
    if isinstance(value, collections.Counter):
        return ("Counter", [(freeze(key), freeze(item)) for key, item in value.items()])
    if isinstance(value, dict):
        return (type(value).__name__, [(freeze(key), freeze(item)) for key, item in value.items()])
    if isinstance(value, tuple):
        return ("tuple", [freeze(item) for item in value])
    if isinstance(value, list):
        return ("list", [freeze(item) for item in value])
    return value


class ExactTrackingTests(unittest.TestCase):
    def test_all_frozen_exact_shapes_match_same_process_legacy(self) -> None:
        nonuniform = build_substitution_matrix(0.2, 0.5, 0.3)
        uniform = build_substitution_matrix(1 / 3, 1 / 3, 1 / 3)
        cases = (
            (0, nonuniform, {"TGG": 2.0}),
            (1, nonuniform, {"TGG": 2.0}),
            (2, nonuniform, {"TGG": 2.0}),
            (3, uniform, {"TGG": 1.0, "ATG": 2.0, "AAA": 0.0}),
            (1, nonuniform, {}),
            (2, nonuniform, {codon: 1.0 for codon in legacy.VALID_CODONS}),
        )
        for generations, matrix, weights in cases:
            with self.subTest(generations=generations, weights=len(weights)):
                expected = legacy.run_simulation(generations, matrix, weights)
                observed = run_simulation(generations, matrix, weights)
                self.assertIsInstance(observed, ExactSimulationResult)
                self.assertEqual(freeze(observed.to_legacy_tuple()), freeze(expected))

    def test_default_weights_match_legacy_exactly(self) -> None:
        matrix = build_substitution_matrix(0.2, 0.5, 0.3)
        observed = run_simulation(1, matrix)
        expected = legacy.run_simulation(1, matrix)
        self.assertEqual(freeze(observed.to_legacy_tuple()), freeze(expected))

    def test_stats_order_and_conservation_are_preserved(self) -> None:
        result = run_simulation(
            3,
            build_substitution_matrix(0.2, 0.5, 0.3),
            {"TGG": 2.0, "ATG": 3.0},
        )
        self.assertEqual(
            list(result.stats),
            [
                "n_starts",
                "total_start_copies",
                "n_generations",
                "unique_aas_seen",
                "unique_codons_seen",
                "total_enc_weight",
                "total_fin_weight",
                "total_stop_prob",
            ],
        )
        self.assertEqual(
            (result.stats["total_fin_weight"] + result.stats["total_stop_prob"]).hex(),
            (result.stats["total_start_copies"]).hex(),
        )

    def test_public_function_is_typed_with_legacy_defaults(self) -> None:
        signature = inspect.signature(run_simulation)
        self.assertTrue(all(parameter.annotation is not inspect.Parameter.empty for parameter in signature.parameters.values()))
        self.assertIsNone(signature.parameters["start_weights"].default)
        self.assertIsNot(signature.return_annotation, inspect.Signature.empty)


if __name__ == "__main__":
    unittest.main()
