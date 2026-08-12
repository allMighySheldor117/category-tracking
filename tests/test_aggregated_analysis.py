"""Canonical scientific tables derived from bounded sampled counters."""

from __future__ import annotations

import copy
from collections import Counter
import inspect
import os
from pathlib import Path
import random
import subprocess
import sys
import unittest
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal

from engine.aggregated_tracking import run_aggregated_experiment
from engine.category_analysis import (
    get_aggregated_category_metrics,
    get_aggregated_survivor_fractions,
    sampled_all_category_series,
    sampled_category_series,
    surviving_category_fraction_series,
)
from engine.genetic_code import (
    CODON_TABLE,
    PROPERTY_LABELS,
    VALID_CODONS,
    get_primary_group_name,
)
from engine.models import InvalidScientificScopeError
from engine.mutation_matrix import build_substitution_matrix
from engine.sampled_tracking import run_experiment
from engine.summaries import (
    get_aggregated_codon_outcomes,
    get_aggregated_convergence,
    get_aggregated_stop_outcomes,
    get_aggregated_survival_by_start,
)


CATEGORIES = list(PROPERTY_LABELS.values())
STOPS = ["TAA", "TAG", "TGA"]
CATEGORY_COLUMNS = [
    "generation", "start_scope", "start_key", "category", "live_value", "value_kind",
]
CATEGORY_DTYPES = ["int64", "object", "object", "object", "int64", "object"]
FRACTION_COLUMNS = [
    "generation", "start_scope", "start_key", "category", "numerator", "denominator", "fraction",
]
FRACTION_DTYPES = ["int64", "object", "object", "object", "int64", "int64", "float64"]
SURVIVAL_COLUMNS = [
    "generation", "start_scope", "start_key", "initial_value", "live_value", "stopped_value",
    "survivor_fraction", "stop_fraction", "value_kind",
]
SURVIVAL_DTYPES = [
    "int64", "object", "object", "int64", "int64", "int64", "float64", "float64", "object",
]
STOP_COLUMNS = [
    "generation", "start_scope", "start_key", "stop_codon", "new_stop_value",
    "cumulative_stop_value", "initial_value", "cumulative_stop_fraction", "value_kind",
]
STOP_DTYPES = [
    "int64", "object", "object", "object", "int64", "int64", "int64", "float64", "object",
]
OUTCOME_COLUMNS = [
    "generation", "start_codon", "target_codon", "target_aa", "target_category", "live_value",
    "new_stop_value", "cumulative_stop_value", "value_kind",
]
OUTCOME_DTYPES = [
    "int64", "object", "object", "object", "object", "int64", "int64", "int64", "object",
]
CONVERGENCE_COLUMNS = [
    "start_scope", "start_key", "basis", "tolerance", "generation", "max_delta", "status",
]
CONVERGENCE_DTYPES = ["object", "object", "object", "float64", "Int64", "float64", "object"]


class AggregatedAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = build_substitution_matrix(0.2, 0.5, 0.3)
        cls.weights = {
            "AAA": 5.9,
            "AAG": 2.2,
            "ATG": 4.0,
            "GCT": 3.0,
            "TGG": 6.0,
            "CAA": 0.0,
        }
        cls.result = run_aggregated_experiment(4, cls.matrix, cls.weights, 314159)

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

    def detailed_result(self, seed: int, generations: int, weights: dict[str, float]):
        prior = random.getstate()
        try:
            random.seed(seed)
            return run_experiment(generations, self.matrix, weights)
        finally:
            random.setstate(prior)

    def test_public_functions_are_fully_typed(self) -> None:
        functions = (
            get_aggregated_category_metrics,
            get_aggregated_survivor_fractions,
            get_aggregated_survival_by_start,
            get_aggregated_stop_outcomes,
            get_aggregated_codon_outcomes,
            get_aggregated_convergence,
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

    def test_all_scopes_have_canonical_schemas_order_and_integer_denominators(self) -> None:
        cases = (
            ("population", "all", 20),
            ("codon", "TGG", 6),
            ("amino_acid", "Lys", 7),
            ("trait", "Positively charged", 7),
        )
        for scope, key, initial in cases:
            with self.subTest(scope=scope, key=key):
                categories = get_aggregated_category_metrics(
                    self.result, start_scope=scope, start_key=key
                )
                fractions = get_aggregated_survivor_fractions(
                    self.result, start_scope=scope, start_key=key
                )
                survival = get_aggregated_survival_by_start(
                    self.result, start_scope=scope, start_key=key
                )
                stops = get_aggregated_stop_outcomes(
                    self.result, start_scope=scope, start_key=key
                )
                self.assert_schema(categories, CATEGORY_COLUMNS, CATEGORY_DTYPES)
                self.assert_schema(fractions, FRACTION_COLUMNS, FRACTION_DTYPES)
                self.assert_schema(survival, SURVIVAL_COLUMNS, SURVIVAL_DTYPES)
                self.assert_schema(stops, STOP_COLUMNS, STOP_DTYPES)
                self.assertEqual(categories["category"].tolist(), CATEGORIES * 4)
                self.assertEqual(stops["stop_codon"].tolist(), STOPS * 4)
                self.assertEqual(survival["initial_value"].tolist(), [initial] * 4)
                self.assertEqual(categories["value_kind"].unique().tolist(), ["copy_count"])
                self.assertEqual(stops["value_kind"].unique().tolist(), ["copy_count"])
                for row in survival.itertuples(index=False):
                    self.assertEqual(row.live_value + row.stopped_value, initial)
                for generation in range(1, 5):
                    fraction_rows = fractions[fractions["generation"] == generation]
                    denominator = int(fraction_rows.iloc[0]["denominator"])
                    expected_sum = 1.0 if denominator else 0.0
                    self.assertAlmostEqual(float(fraction_rows["fraction"].sum()), expected_sum)
                    stop_total = int(
                        stops.loc[stops["generation"] == generation, "cumulative_stop_value"].sum()
                    )
                    self.assertEqual(
                        stop_total,
                        int(survival.loc[survival["generation"] == generation, "stopped_value"].iloc[0]),
                    )

    def test_requested_zero_scopes_are_complete_zero_rows(self) -> None:
        cases = (
            ("codon", "CAA"),
            ("amino_acid", "Gln"),
            ("trait", "Polar uncharged"),
        )
        for scope, key in cases:
            with self.subTest(scope=scope, key=key):
                categories = get_aggregated_category_metrics(
                    self.result, start_scope=scope, start_key=key
                )
                fractions = get_aggregated_survivor_fractions(
                    self.result, start_scope=scope, start_key=key
                )
                survival = get_aggregated_survival_by_start(
                    self.result, start_scope=scope, start_key=key
                )
                stops = get_aggregated_stop_outcomes(
                    self.result, start_scope=scope, start_key=key
                )
                self.assertEqual(len(categories), 20)
                self.assertEqual(categories["live_value"].tolist(), [0] * 20)
                self.assertEqual(fractions["numerator"].tolist(), [0] * 20)
                self.assertEqual(fractions["denominator"].tolist(), [0] * 20)
                self.assertEqual(fractions["fraction"].tolist(), [0.0] * 20)
                self.assertTrue((survival.iloc[:, 3:8] == 0).all().all())
                self.assertEqual(stops["new_stop_value"].tolist(), [0] * 12)

    def test_zero_generations_return_typed_empty_tables_and_no_data_convergence(self) -> None:
        result = run_aggregated_experiment(0, self.matrix, {"AAA": 2, "TGG": 1}, 99)
        calls = (
            (get_aggregated_category_metrics, CATEGORY_COLUMNS, CATEGORY_DTYPES),
            (get_aggregated_survivor_fractions, FRACTION_COLUMNS, FRACTION_DTYPES),
            (get_aggregated_survival_by_start, SURVIVAL_COLUMNS, SURVIVAL_DTYPES),
            (get_aggregated_stop_outcomes, STOP_COLUMNS, STOP_DTYPES),
        )
        for function, columns, dtypes in calls:
            frame = function(result, start_scope="population", start_key="all")
            self.assert_schema(frame, columns, dtypes)
            self.assertTrue(frame.empty)
        convergence = get_aggregated_convergence(
            result,
            start_scope="population",
            start_key="all",
            basis="category_weight",
            tolerance=0.0,
        )
        self.assert_schema(convergence, CONVERGENCE_COLUMNS, CONVERGENCE_DTYPES)
        self.assertTrue(pd.isna(convergence.loc[0, "generation"]))
        self.assertEqual(convergence.loc[0, "max_delta"], 0.0)
        self.assertEqual(convergence.loc[0, "status"], "no_generations")
        with self.assertRaises(InvalidScientificScopeError):
            get_aggregated_codon_outcomes(result, start_codon="TGG", generation=1)

    def test_no_survivors_and_convergence_statuses(self) -> None:
        stopped = run_aggregated_experiment(4, self.matrix, {"TGG": 1}, 12)
        survival = get_aggregated_survival_by_start(
            stopped, start_scope="codon", start_key="TGG"
        )
        self.assertEqual(survival["live_value"].tolist(), [0, 0, 0, 0])
        self.assertEqual(survival["stopped_value"].tolist(), [1, 1, 1, 1])
        fractions = get_aggregated_survivor_fractions(
            stopped, start_scope="codon", start_key="TGG"
        )
        self.assertEqual(fractions["fraction"].tolist(), [0.0] * 20)
        all_stopped = get_aggregated_convergence(
            stopped,
            start_scope="codon",
            start_key="TGG",
            basis="category_weight",
            tolerance=0.0,
        )
        self.assertEqual(all_stopped.loc[0, "generation"], 1)
        self.assertEqual(all_stopped.loc[0, "status"], "all_stopped")

        for basis in ("category_weight", "survivor_fraction"):
            stable = get_aggregated_convergence(
                self.result,
                start_scope="population",
                start_key="all",
                basis=basis,
                tolerance=100.0,
            )
            self.assert_schema(stable, CONVERGENCE_COLUMNS, CONVERGENCE_DTYPES)
            self.assertEqual(stable.loc[0, "generation"], 1)
            self.assertEqual(stable.loc[0, "status"], "stable")
        changing = get_aggregated_convergence(
            self.result,
            start_scope="population",
            start_key="all",
            basis="category_weight",
            tolerance=-1.0,
        )
        self.assertTrue(pd.isna(changing.loc[0, "generation"]))
        self.assertEqual(changing.loc[0, "status"], "still_changing")

    def test_joint_stop_and_codon_outcomes_are_complete_and_cumulative(self) -> None:
        broad = run_aggregated_experiment(
            3, self.matrix, {codon: 3 for codon in VALID_CODONS}, 0
        )
        population = get_aggregated_stop_outcomes(
            broad, start_scope="population", start_key="all"
        )
        self.assertEqual(
            set(population.loc[population["new_stop_value"] > 0, "stop_codon"]),
            set(STOPS),
        )
        for stop_codon in STOPS:
            values = population.loc[
                population["stop_codon"] == stop_codon,
                ["new_stop_value", "cumulative_stop_value"],
            ]
            self.assertEqual(values["new_stop_value"].cumsum().tolist(), values["cumulative_stop_value"].tolist())

        outcome = get_aggregated_codon_outcomes(
            self.result, start_codon="TGG", generation=4
        )
        self.assert_schema(outcome, OUTCOME_COLUMNS, OUTCOME_DTYPES)
        self.assertEqual(outcome["target_codon"].tolist(), VALID_CODONS + STOPS)
        self.assertEqual(len(outcome), 64)
        self.assertEqual(outcome.tail(3)["target_aa"].tolist(), ["Stop"] * 3)
        snapshot = self.result.generations[3]
        for target in VALID_CODONS:
            observed = int(outcome.loc[outcome["target_codon"] == target, "live_value"].iloc[0])
            self.assertEqual(observed, snapshot.current_codon_by_start_codon["TGG"][target])
        cumulative = Counter()
        for snapshot in self.result.generations:
            cumulative.update(snapshot.new_stop_codon_by_start_codon["TGG"])
        for stop in STOPS:
            row = outcome[outcome["target_codon"] == stop].iloc[0]
            self.assertEqual(int(row["new_stop_value"]), self.result.generations[3].new_stop_codon_by_start_codon["TGG"][stop])
            self.assertEqual(int(row["cumulative_stop_value"]), cumulative[stop])

    def test_detailed_record_overlap_is_integer_and_order_exact(self) -> None:
        seed = 314159
        generations = 4
        detailed = self.detailed_result(seed, generations, self.weights)
        population = get_aggregated_category_metrics(
            self.result, start_scope="population", start_key="all"
        )
        population_overlap = population[["generation", "category", "live_value"]].rename(
            columns={"live_value": "value"}
        )
        assert_frame_equal(
            population_overlap,
            sampled_all_category_series(detailed, generations),
            check_exact=True,
            check_dtype=True,
        )
        codon = get_aggregated_category_metrics(
            self.result, start_scope="codon", start_key="TGG"
        )
        codon_overlap = codon[["generation", "category", "live_value"]].rename(
            columns={"live_value": "value"}
        )
        assert_frame_equal(
            codon_overlap,
            sampled_category_series(detailed, "TGG", generations),
            check_exact=True,
            check_dtype=True,
        )
        expected_fraction = surviving_category_fraction_series(codon_overlap)
        observed_fraction = get_aggregated_survivor_fractions(
            self.result, start_scope="codon", start_key="TGG"
        )
        self.assertEqual(observed_fraction["numerator"].tolist(), codon_overlap["value"].tolist())
        self.assertEqual(observed_fraction["denominator"].tolist(), expected_fraction["surviving"].astype("int64").tolist())
        self.assertEqual(observed_fraction["fraction"].tolist(), expected_fraction["value"].tolist())

        expected_joint = [Counter() for _ in range(generations)]
        for record in detailed.records:
            if record["start"] == "TGG" and record["hit_stop"]:
                expected_joint[int(record["stop_gen"]) - 1][record["final"]] += 1
        stops = get_aggregated_stop_outcomes(
            self.result, start_scope="codon", start_key="TGG"
        )
        for generation in range(1, generations + 1):
            rows = stops[stops["generation"] == generation]
            self.assertEqual(rows["new_stop_value"].tolist(), [expected_joint[generation - 1][stop] for stop in STOPS])

    def test_queries_do_not_mutate_or_rerun_and_invalid_scopes_are_explicit(self) -> None:
        before = copy.deepcopy(self.result)
        with patch(
            "engine.sampled_tracking.run_experiment",
            side_effect=AssertionError("must not rerun detailed sampling"),
        ), patch(
            "engine.aggregated_tracking.run_aggregated_experiment",
            side_effect=AssertionError("must not rerun aggregate sampling"),
        ):
            get_aggregated_category_metrics(
                self.result, start_scope="population", start_key="all"
            )
            get_aggregated_stop_outcomes(
                self.result, start_scope="codon", start_key="TGG"
            )
            get_aggregated_survivor_fractions(
                self.result, start_scope="population", start_key="all"
            )
            get_aggregated_survival_by_start(
                self.result, start_scope="population", start_key="all"
            )
            get_aggregated_codon_outcomes(
                self.result, start_codon="TGG", generation=1
            )
            get_aggregated_convergence(
                self.result,
                start_scope="population",
                start_key="all",
                basis="category_weight",
                tolerance=0.0,
            )
        self.assertEqual(self.result, before)

        for function in (
            get_aggregated_category_metrics,
            get_aggregated_survivor_fractions,
            get_aggregated_survival_by_start,
            get_aggregated_stop_outcomes,
            get_aggregated_codon_outcomes,
            get_aggregated_convergence,
        ):
            source = inspect.getsource(function)
            self.assertNotIn("run_experiment", source)
            self.assertNotIn("run_aggregated_experiment", source)
            self.assertNotIn("path", source)

        invalid = (
            ("population", "TGG"),
            ("codon", "XXX"),
            ("amino_acid", "Stop"),
            ("trait", "Unknown"),
            ("unknown", "all"),
        )
        for scope, key in invalid:
            with self.subTest(scope=scope, key=key):
                with self.assertRaises(InvalidScientificScopeError):
                    get_aggregated_category_metrics(
                        self.result, start_scope=scope, start_key=key
                    )
        for generation in (0, 5):
            with self.assertRaises(InvalidScientificScopeError):
                get_aggregated_codon_outcomes(
                    self.result, start_codon="TGG", generation=generation
                )
        with self.assertRaises(InvalidScientificScopeError):
            get_aggregated_convergence(
                self.result,
                start_scope="population",
                start_key="all",
                basis="unknown",
                tolerance=0.0,
            )

    def test_fresh_analysis_import_is_ui_independent(self) -> None:
        script = (
            "import sys; import engine.category_analysis, engine.summaries; "
            "forbidden={'streamlit','tkinter','plotly','PyQt5'}; "
            "assert not forbidden.intersection(sys.modules)"
        )
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, "-c", script],
            cwd=Path(__file__).resolve().parents[1],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
