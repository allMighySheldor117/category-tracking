"""Authoritative exact-analysis contracts and Phase 1 overlap guarantees."""

from __future__ import annotations

import copy
import inspect
import math
import unittest
from collections import Counter
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal

from engine.category_analysis import (
    exact_all_category_series,
    exact_category_series,
    surviving_category_fraction_series,
)
from engine.exact_analysis import (
    build_exact_analysis,
    get_exact_category_metrics,
    get_exact_codon_outcomes,
    get_exact_convergence,
    get_exact_stop_outcomes,
    get_exact_survival_by_start,
    get_exact_survivor_fractions,
    run_exact_analysis,
)
from engine.exact_tracking import run_simulation
from engine.genetic_code import (
    ALL_AAS,
    CODON_TABLE,
    PROPERTY_LABELS,
    VALID_CODONS,
    get_primary_group_name,
)
from engine.models import (
    ExactAnalysisResult,
    ExactResultProvenanceError,
    InvalidScientificScopeError,
)
from engine.mutation_matrix import build_substitution_matrix
from engine.summaries import exact_stop_series


CATEGORY_COLUMNS = [
    "generation",
    "start_scope",
    "start_key",
    "category",
    "live_value",
    "value_kind",
]
CATEGORY_DTYPES = ["int64", "object", "object", "object", "float64", "object"]
FRACTION_COLUMNS = [
    "generation",
    "start_scope",
    "start_key",
    "category",
    "numerator",
    "denominator",
    "fraction",
]
FRACTION_DTYPES = [
    "int64",
    "object",
    "object",
    "object",
    "float64",
    "float64",
    "float64",
]
SURVIVAL_COLUMNS = [
    "generation",
    "start_scope",
    "start_key",
    "initial_value",
    "live_value",
    "stopped_value",
    "survivor_fraction",
    "stop_fraction",
    "value_kind",
]
SURVIVAL_DTYPES = [
    "int64",
    "object",
    "object",
    "float64",
    "float64",
    "float64",
    "float64",
    "float64",
    "object",
]
STOP_COLUMNS = [
    "generation",
    "start_scope",
    "start_key",
    "stop_codon",
    "new_stop_value",
    "cumulative_stop_value",
    "initial_value",
    "cumulative_stop_fraction",
    "value_kind",
]
STOP_DTYPES = [
    "int64",
    "object",
    "object",
    "object",
    "float64",
    "float64",
    "float64",
    "float64",
    "object",
]
OUTCOME_COLUMNS = [
    "generation",
    "start_codon",
    "target_codon",
    "target_aa",
    "target_category",
    "live_value",
    "new_stop_value",
    "cumulative_stop_value",
    "value_kind",
]
OUTCOME_DTYPES = [
    "int64",
    "object",
    "object",
    "object",
    "object",
    "float64",
    "float64",
    "float64",
    "object",
]
CONVERGENCE_COLUMNS = [
    "start_scope",
    "start_key",
    "basis",
    "tolerance",
    "generation",
    "max_delta",
    "status",
]
CONVERGENCE_DTYPES = [
    "object",
    "object",
    "object",
    "float64",
    "Int64",
    "float64",
    "object",
]


def float_hexes(values: pd.Series) -> list[str]:
    return [float(value).hex() for value in values]


class ExactAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = build_substitution_matrix(0.2, 0.5, 0.3)

    def assert_schema(
        self,
        frame: pd.DataFrame,
        columns: list[str],
        dtypes: list[str],
    ) -> None:
        self.assertEqual(list(frame.columns), columns)
        self.assertEqual([str(dtype) for dtype in frame.dtypes], dtypes)
        self.assertIsInstance(frame.index, pd.RangeIndex)
        self.assertEqual(frame.index.start, 0)
        self.assertEqual(frame.index.step, 1)

    def test_public_functions_are_fully_typed_with_approved_defaults(self) -> None:
        functions = (
            run_exact_analysis,
            build_exact_analysis,
            get_exact_category_metrics,
            get_exact_survivor_fractions,
            get_exact_survival_by_start,
            get_exact_stop_outcomes,
            get_exact_codon_outcomes,
            get_exact_convergence,
        )
        for function in functions:
            with self.subTest(function=function.__name__):
                signature = inspect.signature(function)
                self.assertTrue(
                    all(
                        parameter.annotation is not inspect.Parameter.empty
                        for parameter in signature.parameters.values()
                    )
                )
                self.assertIsNot(signature.return_annotation, inspect.Signature.empty)
        self.assertIsNone(
            inspect.signature(run_exact_analysis).parameters["start_weights"].default
        )
        self.assertIsNone(
            inspect.signature(build_exact_analysis).parameters["start_weights"].default
        )

    def test_run_calls_frozen_simulation_once_and_build_never_calls_it(self) -> None:
        weights = {"AAA": 2.0, "TGG": 3.0}
        with patch(
            "engine.exact_analysis.run_simulation",
            wraps=run_simulation,
        ) as tracked:
            analysis = run_exact_analysis(2, self.matrix, weights)
        self.assertEqual(tracked.call_count, 1)
        self.assertEqual(tracked.call_args.args[0:2], (2, self.matrix))
        self.assertEqual(list(tracked.call_args.args[2]), VALID_CODONS)

        with patch(
            "engine.exact_analysis.run_simulation",
            side_effect=AssertionError("build must not run propagation"),
        ) as forbidden:
            rebuilt = build_exact_analysis(analysis.simulation, weights)
        forbidden.assert_not_called()
        assert_frame_equal(
            rebuilt.population_category_metrics,
            analysis.population_category_metrics,
            check_exact=True,
        )

    def test_default_analysis_has_canonical_inputs_and_eager_schemas(self) -> None:
        analysis = run_exact_analysis(1, self.matrix)

        self.assertIsInstance(analysis, ExactAnalysisResult)
        self.assertEqual(list(analysis.start_weights), VALID_CODONS)
        self.assertTrue(all(weight == 1.0 for weight in analysis.start_weights.values()))
        self.assert_schema(analysis.population_category_metrics, CATEGORY_COLUMNS, CATEGORY_DTYPES)
        self.assert_schema(
            analysis.population_survivor_fractions,
            FRACTION_COLUMNS,
            FRACTION_DTYPES,
        )
        self.assert_schema(analysis.population_survival, SURVIVAL_COLUMNS, SURVIVAL_DTYPES)
        self.assert_schema(analysis.population_stop_outcomes, STOP_COLUMNS, STOP_DTYPES)
        self.assertEqual(len(analysis.population_category_metrics), 5)
        self.assertEqual(len(analysis.population_stop_outcomes), 3)
        self.assertEqual(
            analysis.population_category_metrics["category"].tolist(),
            list(PROPERTY_LABELS.values()),
        )
        self.assertEqual(
            analysis.population_stop_outcomes["stop_codon"].tolist(),
            ["TAA", "TAG", "TGA"],
        )

    def test_category_and_fraction_overlaps_are_same_process_exact(self) -> None:
        weights = {"AAA": 1.25, "ATG": 2.5, "TGG": 3.75}
        analysis = run_exact_analysis(3, self.matrix, weights)

        population = analysis.population_category_metrics[
            ["generation", "category", "live_value"]
        ].rename(columns={"live_value": "value"})
        legacy_population = exact_all_category_series(analysis.simulation, 3)
        assert_frame_equal(population, legacy_population, check_exact=True, check_dtype=True)
        self.assertEqual(
            float_hexes(population["value"]),
            float_hexes(legacy_population["value"]),
        )

        codon = get_exact_category_metrics(
            analysis,
            start_scope="codon",
            start_key="TGG",
        )
        legacy_codon = exact_category_series(analysis.simulation, "TGG", 3)
        codon_overlap = codon[["generation", "category", "live_value"]].rename(
            columns={"live_value": "value"}
        )
        assert_frame_equal(codon_overlap, legacy_codon, check_exact=True, check_dtype=True)
        self.assertEqual(
            float_hexes(codon_overlap["value"]),
            float_hexes(legacy_codon["value"]),
        )

        observed_fraction = get_exact_survivor_fractions(
            analysis,
            start_scope="codon",
            start_key="TGG",
        )
        legacy_fraction = surviving_category_fraction_series(legacy_codon)
        expected_fraction = legacy_fraction.rename(
            columns={"value": "fraction", "surviving": "denominator"}
        )
        expected_fraction["numerator"] = legacy_codon["value"]
        expected_fraction = expected_fraction[
            ["generation", "category", "numerator", "denominator", "fraction"]
        ]
        overlap_fraction = observed_fraction[
            ["generation", "category", "numerator", "denominator", "fraction"]
        ]
        assert_frame_equal(
            overlap_fraction,
            expected_fraction,
            check_exact=True,
            check_dtype=True,
        )

    def test_sparse_unequal_denominators_cover_all_start_scopes(self) -> None:
        weights = {"AAA": 2.5, "AAG": 1.5, "TGG": 3.0, "CAA": 0.0}
        analysis = run_exact_analysis(2, self.matrix, weights)
        cases = (
            ("population", "all", 7.0),
            ("codon", "TGG", 3.0),
            ("codon", "CAA", 0.0),
            ("amino_acid", "Lys", 4.0),
            ("trait", "Positively charged", 4.0),
        )

        for scope, key, denominator in cases:
            with self.subTest(scope=scope, key=key):
                survival = get_exact_survival_by_start(
                    analysis,
                    start_scope=scope,
                    start_key=key,
                )
                self.assert_schema(survival, SURVIVAL_COLUMNS, SURVIVAL_DTYPES)
                self.assertEqual(survival["initial_value"].tolist(), [denominator] * 2)
                self.assertTrue(
                    all(
                        math.isclose(
                            row.live_value + row.stopped_value,
                            denominator,
                            rel_tol=1e-12,
                            abs_tol=1e-12,
                        )
                        for row in survival.itertuples(index=False)
                    )
                )
                category = get_exact_category_metrics(
                    analysis,
                    start_scope=scope,
                    start_key=key,
                )
                self.assertEqual(len(category), 10)
                self.assertEqual(category["start_scope"].unique().tolist(), [scope])
                self.assertEqual(category["start_key"].unique().tolist(), [key])

        zero = get_exact_survivor_fractions(
            analysis,
            start_scope="codon",
            start_key="CAA",
        )
        self.assertEqual(zero["numerator"].tolist(), [0.0] * 10)
        self.assertEqual(zero["denominator"].tolist(), [0.0] * 10)
        self.assertEqual(zero["fraction"].tolist(), [0.0] * 10)

    def test_every_amino_acid_and_trait_scope_has_canonical_complete_rows(self) -> None:
        analysis = run_exact_analysis(
            1,
            self.matrix,
            {"AAA": 2.0, "ATG": 1.0, "TGG": 3.0},
        )
        for amino_acid in ALL_AAS:
            with self.subTest(amino_acid=amino_acid):
                frame = get_exact_category_metrics(
                    analysis,
                    start_scope="amino_acid",
                    start_key=amino_acid,
                )
                self.assertEqual(frame["category"].tolist(), list(PROPERTY_LABELS.values()))
        for trait in PROPERTY_LABELS.values():
            with self.subTest(trait=trait):
                frame = get_exact_stop_outcomes(
                    analysis,
                    start_scope="trait",
                    start_key=trait,
                )
                self.assertEqual(frame["stop_codon"].tolist(), ["TAA", "TAG", "TGA"])

    def test_stop_tables_track_every_stop_and_preserve_phase1_totals(self) -> None:
        analysis = run_exact_analysis(3, self.matrix)
        outcomes = analysis.population_stop_outcomes

        self.assert_schema(outcomes, STOP_COLUMNS, STOP_DTYPES)
        for generation in range(1, 4):
            rows = outcomes[outcomes["generation"] == generation]
            self.assertEqual(rows["stop_codon"].tolist(), ["TAA", "TAG", "TGA"])
        self.assertEqual(
            set(outcomes.loc[outcomes["new_stop_value"] > 0, "stop_codon"]),
            {"TAA", "TAG", "TGA"},
        )

        codon_analysis = run_exact_analysis(3, self.matrix, {"TGG": 2.0})
        survival = get_exact_survival_by_start(
            codon_analysis,
            start_scope="codon",
            start_key="TGG",
        )
        legacy = exact_stop_series(codon_analysis.simulation, "TGG", 3)
        self.assertEqual(
            float_hexes(survival["stopped_value"]),
            float_hexes(legacy["cumulative_stops"]),
        )
        new_from_canonical = (
            get_exact_stop_outcomes(
                codon_analysis,
                start_scope="codon",
                start_key="TGG",
            )
            .groupby("generation", sort=False)["new_stop_value"]
            .sum()
        )
        self.assertEqual(len(new_from_canonical), 3)
        for observed, expected in zip(new_from_canonical, legacy["new_stops"]):
            self.assertTrue(math.isclose(observed, expected, rel_tol=1e-12, abs_tol=1e-12))

    def test_codon_outcomes_are_complete_ordered_and_cumulative(self) -> None:
        analysis = run_exact_analysis(3, self.matrix, {"TGG": 2.0})
        frame = get_exact_codon_outcomes(analysis, start_codon="TGG", generation=3)

        self.assert_schema(frame, OUTCOME_COLUMNS, OUTCOME_DTYPES)
        self.assertEqual(frame["target_codon"].tolist(), VALID_CODONS + ["TAA", "TAG", "TGA"])
        self.assertEqual(len(frame), 64)
        stop_rows = frame.tail(3)
        self.assertEqual(stop_rows["target_aa"].tolist(), ["Stop", "Stop", "Stop"])
        self.assertEqual(stop_rows["target_category"].tolist(), ["Stop", "Stop", "Stop"])
        self.assertEqual(stop_rows["live_value"].tolist(), [0.0, 0.0, 0.0])
        self.assertTrue(
            all(
                cumulative >= new
                for cumulative, new in zip(
                    stop_rows["cumulative_stop_value"],
                    stop_rows["new_stop_value"],
                )
            )
        )
        raw_live = analysis.simulation.track_data["per_gen_codon_from"][2]["TGG"]
        for codon, expected in raw_live.items():
            observed = frame.loc[frame["target_codon"] == codon, "live_value"].iloc[0]
            self.assertEqual(float(observed).hex(), float(expected).hex())

    def test_convergence_contract_covers_bases_statuses_and_tolerance(self) -> None:
        analysis = run_exact_analysis(3, self.matrix, {"TGG": 2.0})
        for basis in ("category_weight", "survivor_fraction"):
            with self.subTest(basis=basis):
                stable = get_exact_convergence(
                    analysis,
                    start_scope="codon",
                    start_key="TGG",
                    basis=basis,
                    tolerance=10.0,
                )
                self.assert_schema(stable, CONVERGENCE_COLUMNS, CONVERGENCE_DTYPES)
                self.assertEqual(stable.loc[0, "generation"], 1)
                self.assertEqual(stable.loc[0, "status"], "stable")

        stopped = get_exact_convergence(
            run_exact_analysis(3, self.matrix, {}),
            start_scope="population",
            start_key="all",
            basis="category_weight",
            tolerance=0.0,
        )
        self.assertEqual(stopped.loc[0, "generation"], 1)
        self.assertEqual(stopped.loc[0, "status"], "all_stopped")

        changing = get_exact_convergence(
            analysis,
            start_scope="codon",
            start_key="TGG",
            basis="category_weight",
            tolerance=-1.0,
        )
        self.assertTrue(pd.isna(changing.loc[0, "generation"]))
        self.assertEqual(changing.loc[0, "status"], "still_changing")

    def test_zero_generations_return_typed_empty_time_series(self) -> None:
        analysis = run_exact_analysis(0, self.matrix, {"AAA": 2.5, "TGG": 1.0})

        self.assert_schema(analysis.population_category_metrics, CATEGORY_COLUMNS, CATEGORY_DTYPES)
        self.assert_schema(
            analysis.population_survivor_fractions,
            FRACTION_COLUMNS,
            FRACTION_DTYPES,
        )
        self.assert_schema(analysis.population_survival, SURVIVAL_COLUMNS, SURVIVAL_DTYPES)
        self.assert_schema(analysis.population_stop_outcomes, STOP_COLUMNS, STOP_DTYPES)
        self.assertTrue(analysis.population_category_metrics.empty)
        self.assertTrue(analysis.population_survivor_fractions.empty)
        self.assertTrue(analysis.population_survival.empty)
        self.assertTrue(analysis.population_stop_outcomes.empty)
        convergence = get_exact_convergence(
            analysis,
            start_scope="population",
            start_key="all",
            basis="category_weight",
            tolerance=0.0,
        )
        self.assertTrue(pd.isna(convergence.loc[0, "generation"]))
        self.assertEqual(convergence.loc[0, "max_delta"], 0.0)
        self.assertEqual(convergence.loc[0, "status"], "no_generations")

    def test_invalid_inputs_raise_explicit_errors(self) -> None:
        with self.assertRaisesRegex(ValueError, "n_generations must be >= 0"):
            run_exact_analysis(-1, self.matrix, {})
        with self.assertRaisesRegex(
            InvalidScientificScopeError,
            "Invalid scientific scope codon=XXX",
        ):
            run_exact_analysis(1, self.matrix, {"XXX": 1.0})

        analysis = run_exact_analysis(1, self.matrix, {"TGG": 1.0})
        invalid_scopes = (
            ("population", "TGG"),
            ("codon", "XXX"),
            ("amino_acid", "Stop"),
            ("trait", "Unknown"),
            ("unknown", "all"),
        )
        for scope, key in invalid_scopes:
            with self.subTest(scope=scope, key=key):
                with self.assertRaises(InvalidScientificScopeError):
                    get_exact_category_metrics(
                        analysis,
                        start_scope=scope,
                        start_key=key,
                    )
        for generation in (0, 2):
            with self.subTest(generation=generation):
                with self.assertRaises(InvalidScientificScopeError):
                    get_exact_codon_outcomes(
                        analysis,
                        start_codon="TGG",
                        generation=generation,
                    )
        with self.assertRaises(InvalidScientificScopeError):
            get_exact_convergence(
                analysis,
                start_scope="population",
                start_key="all",
                basis="unknown",
                tolerance=0.0,
            )

    def test_provenance_rejects_unrelated_and_mutated_results(self) -> None:
        base = run_simulation(2, self.matrix, {"AAA": 2.0, "TGG": 3.0})
        with self.assertRaisesRegex(ExactResultProvenanceError, "active_starts"):
            build_exact_analysis(base, {"AAC": 2.0, "TGG": 3.0})

        reordered = copy.deepcopy(base)
        reordered.start_to_fin = dict(reversed(list(reordered.start_to_fin.items())))
        with self.assertRaisesRegex(ExactResultProvenanceError, "active_starts"):
            build_exact_analysis(reordered, {"AAA": 2.0, "TGG": 3.0})

        bad_total = copy.deepcopy(base)
        bad_total.stats["total_start_copies"] = 6.0
        with self.assertRaisesRegex(ExactResultProvenanceError, "total_start_weight"):
            build_exact_analysis(bad_total, {"AAA": 2.0, "TGG": 3.0})

        bad_per_start = copy.deepcopy(base)
        first_final = next(iter(bad_per_start.start_to_fin["AAA"]))
        bad_per_start.start_to_fin["AAA"][first_final] += 0.25
        with self.assertRaisesRegex(ExactResultProvenanceError, "start_codon=AAA"):
            build_exact_analysis(bad_per_start, {"AAA": 2.0, "TGG": 3.0})

        bad_global = copy.deepcopy(base)
        first_final = next(iter(bad_global.fin_codon))
        bad_global.fin_codon[first_final] += 0.25
        with self.assertRaisesRegex(ExactResultProvenanceError, "global_conservation"):
            build_exact_analysis(bad_global, {"AAA": 2.0, "TGG": 3.0})

        zero = run_simulation(0, self.matrix, {"AAA": 2.0})
        zero.start_to_fin["AAA"] = Counter({"AAC": 2.0})
        with self.assertRaisesRegex(ExactResultProvenanceError, "zero_generation"):
            build_exact_analysis(zero, {"AAA": 2.0})

    def test_repeated_calls_are_exact_and_queries_return_defensive_frames(self) -> None:
        weights = {"AAA": 1.25, "TGG": 2.75}
        first = run_exact_analysis(2, self.matrix, weights)
        second = run_exact_analysis(2, self.matrix, weights)

        self.assertEqual(
            first.simulation.to_legacy_tuple(),
            second.simulation.to_legacy_tuple(),
        )
        for name in (
            "population_category_metrics",
            "population_survivor_fractions",
            "population_survival",
            "population_stop_outcomes",
        ):
            assert_frame_equal(getattr(first, name), getattr(second, name), check_exact=True)

        returned = get_exact_category_metrics(
            first,
            start_scope="population",
            start_key="all",
        )
        returned.loc[0, "live_value"] = -999.0
        refreshed = get_exact_category_metrics(
            first,
            start_scope="population",
            start_key="all",
        )
        self.assertNotEqual(refreshed.loc[0, "live_value"], -999.0)


if __name__ == "__main__":
    unittest.main()
