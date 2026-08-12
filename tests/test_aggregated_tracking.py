"""Contract tests for memory-bounded sampled aggregation."""

from __future__ import annotations

import ast
from collections import Counter
from dataclasses import MISSING, fields, is_dataclass
import inspect
from pathlib import Path
import random
import unittest

from engine.aggregated_tracking import run_aggregated_experiment
from engine.genetic_code import (
    ALL_AAS,
    CODON_TABLE,
    PROPERTY_LABELS,
    VALID_CODONS,
    get_primary_group_name,
)
from engine.models import (
    AggregatedGenerationCounts,
    AggregatedSampledResult,
    InvalidScientificScopeError,
)
from engine.mutation_matrix import build_substitution_matrix
from engine.sampled_tracking import run_experiment


STOP_ORDER = ("TAA", "TAG", "TGA")
CATEGORY_ORDER = tuple(PROPERTY_LABELS.values())


def _ordered_counter(counter: Counter[str], order: tuple[str, ...] | list[str]) -> Counter[str]:
    return Counter({key: counter[key] for key in order if counter[key]})


def _reduce_detailed(
    seed: int,
    n_generations: int,
    start_weights: dict[str, float],
    matrix: dict[str, dict[str, float]],
) -> AggregatedSampledResult:
    """Reduce frozen detailed records into the approved aggregate contract."""
    prior_state = random.getstate()
    try:
        random.seed(seed)
        detailed = run_experiment(n_generations, matrix, start_weights)
    finally:
        random.setstate(prior_state)

    start_counts = {
        codon: max(0, int(start_weights.get(codon, 0)))
        for codon in VALID_CODONS
    }
    snapshots: list[AggregatedGenerationCounts] = []
    cumulative_stops = 0
    for generation in range(1, n_generations + 1):
        live_codon: Counter[str] = Counter()
        live_amino_acid: Counter[str] = Counter()
        live_category: Counter[str] = Counter()
        live_by_start_codon: Counter[str] = Counter()
        live_by_start_trait: Counter[str] = Counter()
        current_by_start = {codon: Counter() for codon in VALID_CODONS}
        stop_codon_by_start = {codon: Counter() for codon in VALID_CODONS}

        for record in detailed.records:
            start_codon = record["start"]
            start_trait = get_primary_group_name(record["start_aa"])
            if record["hit_stop"] and record["stop_gen"] == generation:
                stop_codon_by_start[start_codon][record["final"]] += 1
            if len(record["path"]) <= generation:
                continue
            current_codon = record["path"][generation]
            if CODON_TABLE[current_codon] == "Stop":
                continue
            current_aa = CODON_TABLE[current_codon]
            current_trait = get_primary_group_name(current_aa)
            live_codon[current_codon] += 1
            live_amino_acid[current_aa] += 1
            live_category[current_trait] += 1
            live_by_start_codon[start_codon] += 1
            live_by_start_trait[start_trait] += 1
            current_by_start[start_codon][current_codon] += 1

        canonical_joint = {
            codon: _ordered_counter(stop_codon_by_start[codon], STOP_ORDER)
            for codon in VALID_CODONS
        }
        stops_by_codon: Counter[str] = Counter()
        stops_by_start: Counter[str] = Counter()
        stops_by_trait: Counter[str] = Counter()
        for start_codon in VALID_CODONS:
            for stop_codon in STOP_ORDER:
                count = canonical_joint[start_codon][stop_codon]
                if not count:
                    continue
                stops_by_codon[stop_codon] += count
                stops_by_start[start_codon] += count
                start_trait = get_primary_group_name(CODON_TABLE[start_codon])
                stops_by_trait[start_trait] += count
        new_stops = sum(stops_by_codon.values())
        cumulative_stops += new_stops
        snapshots.append(
            AggregatedGenerationCounts(
                generation=generation,
                live_codon=_ordered_counter(live_codon, VALID_CODONS),
                live_amino_acid=_ordered_counter(live_amino_acid, ALL_AAS),
                live_category=_ordered_counter(live_category, CATEGORY_ORDER),
                live_by_start_codon=_ordered_counter(live_by_start_codon, VALID_CODONS),
                live_by_start_trait=_ordered_counter(live_by_start_trait, CATEGORY_ORDER),
                current_codon_by_start_codon={
                    codon: _ordered_counter(current_by_start[codon], VALID_CODONS)
                    for codon in VALID_CODONS
                },
                new_stop_codon_by_start_codon=canonical_joint,
                new_stops_by_stop_codon=_ordered_counter(stops_by_codon, STOP_ORDER),
                new_stops_by_start_codon=_ordered_counter(stops_by_start, VALID_CODONS),
                new_stops_by_start_trait=_ordered_counter(stops_by_trait, CATEGORY_ORDER),
                total_live=sum(live_codon.values()),
                new_stops=new_stops,
                cumulative_stops=cumulative_stops,
            )
        )

    if snapshots:
        final_snapshot = snapshots[-1]
        final_live_codon = Counter(final_snapshot.live_codon)
        final_live_amino_acid = Counter(final_snapshot.live_amino_acid)
        final_by_start = {
            codon: Counter(final_snapshot.current_codon_by_start_codon[codon])
            for codon in VALID_CODONS
        }
    else:
        final_live_codon = Counter(
            {codon: start_counts[codon] for codon in VALID_CODONS if start_counts[codon]}
        )
        aa_counts = Counter()
        for codon in VALID_CODONS:
            aa_counts[CODON_TABLE[codon]] += start_counts[codon]
        final_live_amino_acid = _ordered_counter(aa_counts, ALL_AAS)
        final_by_start = {
            codon: Counter({codon: start_counts[codon]}) if start_counts[codon] else Counter()
            for codon in VALID_CODONS
        }

    return AggregatedSampledResult(
        seed=seed,
        n_generations=n_generations,
        start_counts=start_counts,
        total_start_count=sum(start_counts.values()),
        generations=tuple(snapshots),
        final_live_codon=final_live_codon,
        final_live_amino_acid=final_live_amino_acid,
        final_live_by_start_codon=final_by_start,
        total_stopped=cumulative_stops,
    )


class AggregatedTrackingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.matrix = build_substitution_matrix(0.2, 0.5, 0.3)

    def assert_reduction_equivalent(
        self,
        seed: int,
        generations: int,
        weights: dict[str, float],
    ) -> AggregatedSampledResult:
        expected = _reduce_detailed(seed, generations, weights, self.matrix)
        observed = run_aggregated_experiment(generations, self.matrix, weights, seed)
        self.assert_ordered_structure_equal(observed, expected)
        return observed

    def assert_ordered_structure_equal(self, observed: object, expected: object) -> None:
        """Compare recursively while treating mapping insertion order as contractual."""
        self.assertIs(type(observed), type(expected))
        if is_dataclass(expected) and not isinstance(expected, type):
            for field in fields(expected):
                self.assert_ordered_structure_equal(
                    getattr(observed, field.name),
                    getattr(expected, field.name),
                )
            return
        if isinstance(expected, dict):
            self.assertEqual(list(observed), list(expected))  # type: ignore[arg-type]
            for key in expected:
                self.assert_ordered_structure_equal(
                    observed[key],  # type: ignore[index]
                    expected[key],
                )
            return
        if isinstance(expected, (tuple, list)):
            self.assertEqual(len(observed), len(expected))  # type: ignore[arg-type]
            for observed_item, expected_item in zip(observed, expected):  # type: ignore[arg-type]
                self.assert_ordered_structure_equal(observed_item, expected_item)
            return
        self.assertEqual(observed, expected)

    def assert_bounded_result_shape(
        self,
        result: AggregatedSampledResult,
        expected_generations: int,
    ) -> None:
        """Prove retained cardinality is bounded by generations and biology."""
        self.assertEqual(len(result.start_counts), 61)
        self.assertEqual(list(result.start_counts), VALID_CODONS)
        self.assertEqual(len(result.generations), expected_generations)
        self.assertLessEqual(len(result.final_live_codon), 61)
        self.assertLessEqual(len(result.final_live_amino_acid), 20)
        self.assertEqual(len(result.final_live_by_start_codon), 61)
        self.assertEqual(list(result.final_live_by_start_codon), VALID_CODONS)
        self.assertLessEqual(
            sum(len(counter) for counter in result.final_live_by_start_codon.values()),
            61 * 61,
        )
        for snapshot in result.generations:
            self.assertLessEqual(len(snapshot.live_codon), 61)
            self.assertLessEqual(len(snapshot.live_amino_acid), 20)
            self.assertLessEqual(len(snapshot.live_category), 5)
            self.assertLessEqual(len(snapshot.live_by_start_codon), 61)
            self.assertLessEqual(len(snapshot.live_by_start_trait), 5)
            self.assertLessEqual(len(snapshot.new_stops_by_stop_codon), 3)
            self.assertLessEqual(len(snapshot.new_stops_by_start_codon), 61)
            self.assertLessEqual(len(snapshot.new_stops_by_start_trait), 5)
            self.assertEqual(len(snapshot.current_codon_by_start_codon), 61)
            self.assertEqual(list(snapshot.current_codon_by_start_codon), VALID_CODONS)
            self.assertTrue(
                all(
                    len(counter) <= 61
                    for counter in snapshot.current_codon_by_start_codon.values()
                )
            )
            self.assertLessEqual(
                sum(
                    len(counter)
                    for counter in snapshot.current_codon_by_start_codon.values()
                ),
                61 * 61,
            )
            self.assertEqual(len(snapshot.new_stop_codon_by_start_codon), 61)
            self.assertEqual(list(snapshot.new_stop_codon_by_start_codon), VALID_CODONS)
            self.assertTrue(
                all(
                    list(counter)
                    == [stop for stop in STOP_ORDER if counter[stop]]
                    and len(counter) <= 3
                    for counter in snapshot.new_stop_codon_by_start_codon.values()
                )
            )
            self.assertLessEqual(
                sum(
                    len(counter)
                    for counter in snapshot.new_stop_codon_by_start_codon.values()
                ),
                61 * 3,
            )

    def test_public_signature_and_named_dataclass_contract(self) -> None:
        signature = inspect.signature(run_aggregated_experiment)
        self.assertEqual(
            list(signature.parameters),
            ["n_generations", "sub_matrix", "start_weights", "seed"],
        )
        self.assertTrue(
            all(
                parameter.annotation is not inspect.Parameter.empty
                for parameter in signature.parameters.values()
            )
        )
        self.assertIsNot(signature.return_annotation, inspect.Signature.empty)
        self.assertTrue(is_dataclass(AggregatedGenerationCounts))
        self.assertTrue(is_dataclass(AggregatedSampledResult))
        self.assertTrue(AggregatedGenerationCounts.__dataclass_params__.frozen)
        self.assertTrue(AggregatedSampledResult.__dataclass_params__.frozen)
        self.assertEqual(
            [field.name for field in fields(AggregatedGenerationCounts)],
            [
                "generation", "live_codon", "live_amino_acid", "live_category",
                "live_by_start_codon", "live_by_start_trait",
                "current_codon_by_start_codon", "new_stop_codon_by_start_codon",
                "new_stops_by_stop_codon",
                "new_stops_by_start_codon", "new_stops_by_start_trait",
                "total_live", "new_stops", "cumulative_stops",
            ],
        )
        self.assertEqual(
            [field.name for field in fields(AggregatedSampledResult)],
            [
                "seed", "n_generations", "start_counts", "total_start_count",
                "generations", "final_live_codon", "final_live_amino_acid",
                "final_live_by_start_codon", "total_stopped",
            ],
        )
        for result_type in (AggregatedGenerationCounts, AggregatedSampledResult):
            self.assertTrue(
                all(
                    field.default is MISSING and field.default_factory is MISSING
                    for field in fields(result_type)
                )
            )
            self.assertFalse(hasattr(result_type, "to_legacy_tuple"))

    def test_zero_generation_empty_sparse_and_normalized_inputs(self) -> None:
        weights = {"AAA": 2.9, "CAA": 0.0, "TGG": -4.0, "ATG": 1.2}
        original = dict(weights)
        original_matrix = {base: dict(row) for base, row in self.matrix.items()}
        result = self.assert_reduction_equivalent(99, 0, weights)
        self.assertEqual(weights, original)
        self.assertEqual(self.matrix, original_matrix)
        self.assertEqual(result.start_counts["AAA"], 2)
        self.assertEqual(result.start_counts["ATG"], 1)
        self.assertEqual(result.start_counts["TGG"], 0)
        self.assertEqual(list(result.start_counts), VALID_CODONS)
        self.assertEqual(result.total_start_count, 3)
        self.assertEqual(result.generations, ())
        self.assertEqual(result.total_stopped, 0)
        self.assertEqual(result.final_live_codon, Counter({"AAA": 2, "ATG": 1}))
        self.assertEqual(list(result.final_live_by_start_codon), VALID_CODONS)

        empty = run_aggregated_experiment(3, self.matrix, {}, 123)
        self.assertEqual(empty.total_start_count, 0)
        self.assertEqual(len(empty.generations), 3)
        self.assertTrue(all(snapshot.total_live == 0 for snapshot in empty.generations))
        self.assertTrue(all(snapshot.cumulative_stops == 0 for snapshot in empty.generations))

    def test_invalid_generation_seed_and_unknown_start_contracts(self) -> None:
        for value in (-1, 1.5, "2", True):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "^n_generations must be >= 0$"):
                    run_aggregated_experiment(value, self.matrix, {}, 1)  # type: ignore[arg-type]
        for seed in (1.5, "1", True):
            with self.subTest(seed=seed):
                with self.assertRaisesRegex(TypeError, "^seed must be an int$"):
                    run_aggregated_experiment(1, self.matrix, {}, seed)  # type: ignore[arg-type]
        with self.assertRaisesRegex(InvalidScientificScopeError, "Invalid scientific scope codon=BAD"):
            run_aggregated_experiment(1, self.matrix, {"BAD": 1}, 1)

    def test_reduces_detailed_records_exactly_for_reviewed_cases(self) -> None:
        cases = (
            (314159, 3, {"AAA": 2, "CAA": 0, "TGG": 3}),
            (2, 3, {"TGG": 4}),
            (919, 3, {"TGG": 2, "ATG": 3, "AAA": 0}),
            (41, 2, {"TGG": -2, "ATG": 0}),
            (99, 0, {"AAA": 2, "TGG": 1}),
        )
        for seed, generations, weights in cases:
            with self.subTest(seed=seed, generations=generations):
                self.assert_reduction_equivalent(seed, generations, weights)

    def test_early_stop_no_survivors_and_all_stop_codons(self) -> None:
        stopped = self.assert_reduction_equivalent(12, 4, {"TGG": 1})
        self.assertEqual(stopped.total_stopped, 1)
        self.assertEqual(stopped.final_live_codon, Counter())
        self.assertEqual(stopped.generations[0].new_stops_by_stop_codon, Counter({"TAG": 1}))
        self.assertEqual(stopped.generations[0].new_stops, 1)
        self.assertEqual(stopped.generations[0].cumulative_stops, 1)
        for snapshot in stopped.generations[1:]:
            self.assertEqual(snapshot.total_live, 0)
            self.assertEqual(snapshot.new_stops, 0)
            self.assertEqual(snapshot.cumulative_stops, 1)

        broad = self.assert_reduction_equivalent(
            0,
            3,
            {codon: 3 for codon in VALID_CODONS},
        )
        seen_stops = set()
        for snapshot in broad.generations:
            seen_stops.update(snapshot.new_stops_by_stop_codon)
        self.assertEqual(seen_stops, set(STOP_ORDER))

    def test_conservation_rollups_and_canonical_ordering(self) -> None:
        result = self.assert_reduction_equivalent(
            1729,
            5,
            {"AAA": 7, "ATG": 5, "TGG": 9, "GCT": 3},
        )
        for expected_generation, snapshot in enumerate(result.generations, start=1):
            self.assertEqual(snapshot.generation, expected_generation)
            self.assertEqual(snapshot.total_live + snapshot.cumulative_stops, result.total_start_count)
            self.assertEqual(sum(snapshot.live_codon.values()), snapshot.total_live)
            self.assertEqual(sum(snapshot.live_amino_acid.values()), snapshot.total_live)
            self.assertEqual(sum(snapshot.live_category.values()), snapshot.total_live)
            self.assertEqual(sum(snapshot.live_by_start_codon.values()), snapshot.total_live)
            self.assertEqual(sum(snapshot.live_by_start_trait.values()), snapshot.total_live)
            self.assertEqual(sum(snapshot.new_stops_by_stop_codon.values()), snapshot.new_stops)
            self.assertEqual(sum(snapshot.new_stops_by_start_codon.values()), snapshot.new_stops)
            self.assertEqual(sum(snapshot.new_stops_by_start_trait.values()), snapshot.new_stops)
            self.assertEqual(list(snapshot.live_codon), [c for c in VALID_CODONS if snapshot.live_codon[c]])
            self.assertEqual(list(snapshot.live_amino_acid), [a for a in ALL_AAS if snapshot.live_amino_acid[a]])
            self.assertEqual(list(snapshot.live_category), [c for c in CATEGORY_ORDER if snapshot.live_category[c]])
            self.assertEqual(list(snapshot.current_codon_by_start_codon), VALID_CODONS)
            self.assertEqual(
                list(snapshot.new_stops_by_stop_codon),
                [codon for codon in STOP_ORDER if snapshot.new_stops_by_stop_codon[codon]],
            )
            derived_by_stop: Counter[str] = Counter()
            derived_by_start: Counter[str] = Counter()
            derived_by_trait: Counter[str] = Counter()
            for start_codon in VALID_CODONS:
                for stop_codon in STOP_ORDER:
                    count = snapshot.new_stop_codon_by_start_codon[start_codon][stop_codon]
                    if not count:
                        continue
                    derived_by_stop[stop_codon] += count
                    derived_by_start[start_codon] += count
                    derived_by_trait[get_primary_group_name(CODON_TABLE[start_codon])] += count
            self.assertEqual(
                snapshot.new_stops_by_stop_codon,
                _ordered_counter(derived_by_stop, STOP_ORDER),
            )
            self.assertEqual(
                list(snapshot.new_stops_by_stop_codon),
                list(_ordered_counter(derived_by_stop, STOP_ORDER)),
            )
            self.assertEqual(
                snapshot.new_stops_by_start_codon,
                _ordered_counter(derived_by_start, VALID_CODONS),
            )
            self.assertEqual(
                list(snapshot.new_stops_by_start_codon),
                list(_ordered_counter(derived_by_start, VALID_CODONS)),
            )
            self.assertEqual(
                snapshot.new_stops_by_start_trait,
                _ordered_counter(derived_by_trait, CATEGORY_ORDER),
            )
            self.assertEqual(
                list(snapshot.new_stops_by_start_trait),
                list(_ordered_counter(derived_by_trait, CATEGORY_ORDER)),
            )
            self.assertEqual(
                snapshot.new_stops,
                sum(
                    sum(counter.values())
                    for counter in snapshot.new_stop_codon_by_start_codon.values()
                ),
            )

    def test_seed_repeatability_consecutive_calls_and_global_rng_isolation(self) -> None:
        weights = {"AAA": 20, "TGG": 20}
        random.seed(8675309)
        before = random.getstate()
        first = run_aggregated_experiment(4, self.matrix, weights, 2718)
        middle = random.getstate()
        second = run_aggregated_experiment(4, self.matrix, weights, 2718)
        after = random.getstate()
        different = run_aggregated_experiment(4, self.matrix, weights, 2719)
        self.assertEqual(first, second)
        self.assertNotEqual(first, different)
        self.assertEqual(before, middle)
        self.assertEqual(before, after)

    def test_result_structure_is_independent_of_copy_count(self) -> None:
        generations = 4
        small = run_aggregated_experiment(generations, self.matrix, {"TGG": 1}, 7)
        large = run_aggregated_experiment(generations, self.matrix, {"TGG": 10_000}, 7)
        self.assert_bounded_result_shape(small, generations)
        self.assert_bounded_result_shape(large, generations)
        self.assertEqual(len(small.generations), len(large.generations))
        self.assertEqual(large.total_start_count, 10_000)
        self.assertEqual(
            large.generations[-1].total_live + large.total_stopped,
            large.total_start_count,
        )

    def test_source_and_result_contract_prohibit_per_copy_retention(self) -> None:
        source_path = Path(inspect.getsourcefile(run_aggregated_experiment) or "")
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        forbidden_names = {"records", "paths", "copy_ids", "copy_id", "path"}
        observed_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        self.assertFalse(forbidden_names.intersection(observed_names))
        self.assertNotIn(".append(", source)

        copy_loops = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.For)
            and isinstance(node.target, ast.Name)
            and node.target.id == "_copy_number"
        ]
        self.assertEqual(len(copy_loops), 1)
        copy_loop = copy_loops[0]
        copy_number_loads = [
            node
            for node in ast.walk(copy_loop)
            if isinstance(node, ast.Name)
            and node.id == "_copy_number"
            and isinstance(node.ctx, ast.Load)
        ]
        self.assertEqual(copy_number_loads, [])
        forbidden_retained_value_nodes = (
            ast.List,
            ast.Set,
            ast.Dict,
            ast.Tuple,
            ast.ListComp,
            ast.SetComp,
            ast.DictComp,
            ast.GeneratorExp,
        )
        forbidden_mutators = {"append", "extend", "add", "update", "setdefault"}
        self.assertFalse(
            any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in forbidden_mutators
                for node in ast.walk(copy_loop)
            )
        )
        assignments = [
            node
            for node in ast.walk(copy_loop)
            if isinstance(node, (ast.Assign, ast.AnnAssign))
        ]
        for assignment in assignments:
            self.assertFalse(
                any(
                    isinstance(node, forbidden_retained_value_nodes)
                    for node in ast.walk(assignment.value)
                )
            )
            assignment_targets = (
                assignment.targets
                if isinstance(assignment, ast.Assign)
                else [assignment.target]
            )
            for target in assignment_targets:
                self.assertFalse(
                    any(
                        isinstance(node, (ast.Attribute, ast.Subscript))
                        and isinstance(node.ctx, ast.Store)
                        for node in ast.walk(target)
                    )
                )

        approved_counter_attributes = {
            "live_codon",
            "live_amino_acid",
            "live_category",
            "live_by_start_codon",
            "live_by_start_trait",
            "current_codon_by_start_codon",
            "new_stop_codon_by_start_codon",
        }
        for node in ast.walk(copy_loop):
            if not isinstance(node, ast.AugAssign):
                continue
            self.assertIsInstance(node.target, ast.Subscript)
            self.assertIsInstance(node.op, ast.Add)
            self.assertIsInstance(node.value, ast.Constant)
            self.assertEqual(node.value.value, 1)

            counter_attribute = node.target.value
            while isinstance(counter_attribute, ast.Subscript):
                counter_attribute = counter_attribute.value
            self.assertIsInstance(counter_attribute, ast.Attribute)
            self.assertIsInstance(counter_attribute.value, ast.Name)
            self.assertEqual(counter_attribute.value.id, "state")
            self.assertIn(counter_attribute.attr, approved_counter_attributes)

        result_fields = {field.name for field in fields(AggregatedSampledResult)}
        snapshot_fields = {field.name for field in fields(AggregatedGenerationCounts)}
        self.assertFalse(forbidden_names.intersection(result_fields | snapshot_fields))
        runtime_result = run_aggregated_experiment(3, self.matrix, {"AAA": 25, "TGG": 25}, 8)
        self.assert_bounded_result_shape(runtime_result, 3)


if __name__ == "__main__":
    unittest.main()
