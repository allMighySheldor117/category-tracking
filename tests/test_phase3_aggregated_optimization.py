"""Phase 3 aggregated sampled optimization contracts."""

from __future__ import annotations

import random
import unittest
from typing import Any

from engine import aggregated_tracking
from engine.aggregated_tracking import run_aggregated_experiment
from engine.mutation_matrix import PRESET_AC, PRESET_AG, PRESET_AT, build_substitution_matrix
from tests.test_aggregated_tracking import _reduce_detailed


class Phase3AggregatedOptimizationTests(unittest.TestCase):
    """Protect aggregated sampled contracts while allowing internal cleanup."""

    def setUp(self) -> None:
        self.matrix = build_substitution_matrix(PRESET_AT, PRESET_AG, PRESET_AC)

    def test_uses_precomputed_trait_lookup_during_execution(self) -> None:
        original = aggregated_tracking.get_primary_group_name
        calls: list[str] = []

        def counted(amino_acid: str) -> str:
            calls.append(amino_acid)
            return original(amino_acid)

        aggregated_tracking.get_primary_group_name = counted
        try:
            run_aggregated_experiment(
                3,
                self.matrix,
                {"AAA": 25, "TGG": 25},
                2718,
            )
        finally:
            aggregated_tracking.get_primary_group_name = original

        self.assertEqual([], calls)

    def test_reducer_equivalence_and_rng_isolation_remain_exact(self) -> None:
        seed = 314159
        weights = {"AAA": 3, "TGG": 2}
        before = random.getstate()
        aggregated = run_aggregated_experiment(4, self.matrix, weights, seed)
        after = random.getstate()
        self.assertEqual(before, after)

        reduced = _reduce_detailed(seed, 4, weights, self.matrix)
        self.assertEqual(reduced.generations, aggregated.generations)
        self.assertEqual(reduced.final_live_codon, aggregated.final_live_codon)
        self.assertEqual(reduced.total_stopped, aggregated.total_stopped)

    def test_count_conservation_and_no_per_copy_retention_hold(self) -> None:
        result = run_aggregated_experiment(
            10,
            self.matrix,
            {"AAA": 100, "TGG": 100},
            8675309,
        )
        for snapshot in result.generations:
            self.assertEqual(
                result.total_start_count,
                snapshot.total_live + snapshot.cumulative_stops,
            )
        for forbidden_name in ("records", "paths", "copy_ids", "final_records"):
            self.assertFalse(hasattr(result, forbidden_name))

    def test_structural_slots_are_stable_across_copy_counts(self) -> None:
        small = run_aggregated_experiment(3, self.matrix, {"AAA": 10, "TGG": 10}, 7)
        large = run_aggregated_experiment(3, self.matrix, {"AAA": 1000, "TGG": 1000}, 7)

        def structure(result: Any) -> tuple[int, tuple[int, ...]]:
            return (
                len(result.generations),
                tuple(
                    len(snapshot.current_codon_by_start_codon)
                    + len(snapshot.new_stop_codon_by_start_codon)
                    for snapshot in result.generations
                ),
            )

        self.assertLess(small.total_start_count, large.total_start_count)
        self.assertEqual(structure(small), structure(large))


if __name__ == "__main__":
    unittest.main()
