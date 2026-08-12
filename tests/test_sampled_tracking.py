"""Exact sampled-output and RNG-state comparisons against the legacy engine."""

from __future__ import annotations

import inspect
import random
import unittest

import category_tracking as legacy
from engine.models import SampledSimulationResult
from engine.mutation_matrix import build_substitution_matrix
from engine.sampled_tracking import run_experiment


class SampledTrackingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.matrix = build_substitution_matrix(0.2, 0.5, 0.3)

    def assert_legacy_match(
        self,
        seed: int,
        generations: int,
        weights: dict[str, float],
    ) -> SampledSimulationResult:
        random.seed(seed)
        expected = legacy.run_experiment(generations, self.matrix, weights)
        expected_state = random.getstate()

        random.seed(seed)
        observed = run_experiment(generations, self.matrix, weights)
        observed_state = random.getstate()

        self.assertIsInstance(observed, SampledSimulationResult)
        self.assertEqual(observed.to_legacy_tuple(), expected)
        self.assertEqual(observed_state, expected_state)
        return observed

    def test_nonuniform_sparse_multiple_start_and_early_stop_cases(self) -> None:
        cases = (
            (1729, 4, {"TGG": 4.0}),
            (3, 8, {"TGG": 20.0}),
            (919, 3, {"TGG": 2.0, "ATG": 3.0, "AAA": 0.0}),
            (41, 2, {"TGG": 0.0, "ATG": -2.0}),
        )
        for seed, generations, weights in cases:
            with self.subTest(seed=seed, generations=generations, weights=weights):
                result = self.assert_legacy_match(seed, generations, weights)
                for record in result.records:
                    self.assertEqual(
                        list(record),
                        ["start", "start_aa", "final", "final_aa", "hit_stop", "stop_gen", "copy", "path"],
                    )

    def test_zero_generations_does_not_advance_rng(self) -> None:
        random.seed(2026)
        before = random.getstate()
        result = run_experiment(0, self.matrix, {"TGG": 3.0, "ATG": 2.0})
        after = random.getstate()
        self.assertEqual(before, after)
        self.assertTrue(all(record["path"] == [record["start"]] for record in result.records))
        self.assert_legacy_match(2026, 0, {"TGG": 3.0, "ATG": 2.0})

    def test_consecutive_calls_preserve_draw_order_and_states(self) -> None:
        weights = {"TGG": 5.0, "ATG": 2.0}
        random.seed(8675309)
        expected_first = legacy.run_experiment(4, self.matrix, weights)
        expected_first_state = random.getstate()
        expected_second = legacy.run_experiment(4, self.matrix, weights)
        expected_second_state = random.getstate()

        random.seed(8675309)
        observed_first = run_experiment(4, self.matrix, weights)
        observed_first_state = random.getstate()
        observed_second = run_experiment(4, self.matrix, weights)
        observed_second_state = random.getstate()

        self.assertEqual(observed_first.to_legacy_tuple(), expected_first)
        self.assertEqual(observed_first_state, expected_first_state)
        self.assertEqual(observed_second.to_legacy_tuple(), expected_second)
        self.assertEqual(observed_second_state, expected_second_state)

    def test_record_paths_and_copy_numbers_are_preserved(self) -> None:
        result = self.assert_legacy_match(55, 5, {"TGG": 4.9, "ATG": 2.1})
        by_start: dict[str, list[int]] = {}
        for record in result.records:
            by_start.setdefault(record["start"], []).append(record["copy"])
            expected_path_length = record["stop_gen"] + 1 if record["hit_stop"] else 6
            self.assertEqual(len(record["path"]), expected_path_length)
        self.assertEqual(by_start, {"ATG": [1, 2], "TGG": [1, 2, 3, 4]})

    def test_public_function_is_typed_and_has_no_rng_parameter(self) -> None:
        signature = inspect.signature(run_experiment)
        self.assertEqual(list(signature.parameters), ["n_generations", "sub_matrix", "start_weights"])
        self.assertTrue(all(parameter.annotation is not inspect.Parameter.empty for parameter in signature.parameters.values()))
        self.assertIsNot(signature.return_annotation, inspect.Signature.empty)


if __name__ == "__main__":
    unittest.main()
