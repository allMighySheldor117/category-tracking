"""Phase 3 exact-analysis optimization contracts."""

from __future__ import annotations

import unittest
from typing import Any

import pandas as pd
from pandas.testing import assert_frame_equal

from engine import exact_analysis
from engine.exact_analysis import (
    get_exact_category_metrics,
    get_exact_codon_outcomes,
    get_exact_convergence,
    get_exact_stop_outcomes,
    get_exact_survival_by_start,
    get_exact_survivor_fractions,
    run_exact_analysis,
)
from engine.mutation_matrix import PRESET_AC, PRESET_AG, PRESET_AT, build_substitution_matrix


def _float_hexes(frame: pd.DataFrame) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for column in frame.columns:
        if pd.api.types.is_float_dtype(frame[column]):
            values[column] = [float(value).hex() for value in frame[column]]
    return values


class Phase3ExactOptimizationTests(unittest.TestCase):
    """Protect Phase 2 exact contracts while allowing derived-table reuse."""

    def setUp(self) -> None:
        self.matrix = build_substitution_matrix(PRESET_AT, PRESET_AG, PRESET_AC)
        self.analysis = run_exact_analysis(
            4,
            self.matrix,
            {"AAA": 1.0, "TGG": 2.0},
        )

    def assert_frame_contract_equal(
        self,
        left: pd.DataFrame,
        right: pd.DataFrame,
    ) -> None:
        self.assertEqual(list(left.columns), list(right.columns))
        self.assertEqual([str(dtype) for dtype in left.dtypes], [str(dtype) for dtype in right.dtypes])
        self.assertEqual(list(left.index), list(right.index))
        assert_frame_equal(left, right, check_exact=True)
        self.assertEqual(_float_hexes(left), _float_hexes(right))

    def test_repeated_scoped_category_metrics_reuse_internal_derivation(self) -> None:
        original = exact_analysis._category_metrics
        calls: list[tuple[Any, ...]] = []

        def counted(*args: Any, **kwargs: Any) -> pd.DataFrame:
            calls.append(args)
            return original(*args, **kwargs)

        exact_analysis._category_metrics = counted
        try:
            first = get_exact_category_metrics(
                self.analysis,
                start_scope="codon",
                start_key="TGG",
            )
            second = get_exact_category_metrics(
                self.analysis,
                start_scope="codon",
                start_key="TGG",
            )
        finally:
            exact_analysis._category_metrics = original

        self.assertEqual(1, len(calls))
        self.assert_frame_contract_equal(first, second)

    def test_cached_scoped_queries_return_mutation_safe_frames(self) -> None:
        first = get_exact_category_metrics(
            self.analysis,
            start_scope="codon",
            start_key="TGG",
        )
        original_second = get_exact_category_metrics(
            self.analysis,
            start_scope="codon",
            start_key="TGG",
        )
        first.loc[0, "live_value"] = 999.0
        after_mutation = get_exact_category_metrics(
            self.analysis,
            start_scope="codon",
            start_key="TGG",
        )
        self.assert_frame_contract_equal(original_second, after_mutation)

    def test_scoped_exact_query_outputs_are_stable_across_repeated_calls(self) -> None:
        query_pairs = (
            (
                lambda: get_exact_survivor_fractions(
                    self.analysis,
                    start_scope="codon",
                    start_key="TGG",
                ),
                "survivor_fractions",
            ),
            (
                lambda: get_exact_survival_by_start(
                    self.analysis,
                    start_scope="codon",
                    start_key="TGG",
                ),
                "survival_by_start",
            ),
            (
                lambda: get_exact_stop_outcomes(
                    self.analysis,
                    start_scope="codon",
                    start_key="TGG",
                ),
                "stop_outcomes",
            ),
            (
                lambda: get_exact_codon_outcomes(
                    self.analysis,
                    start_codon="TGG",
                    generation=2,
                ),
                "codon_outcomes",
            ),
            (
                lambda: get_exact_convergence(
                    self.analysis,
                    start_scope="codon",
                    start_key="TGG",
                    basis="survivor_fraction",
                    tolerance=0.01,
                ),
                "convergence",
            ),
        )
        for query, label in query_pairs:
            with self.subTest(query=label):
                self.assert_frame_contract_equal(query(), query())

    def test_run_exact_analysis_still_calls_exact_simulation_once(self) -> None:
        original = exact_analysis.run_simulation
        calls: list[tuple[Any, ...]] = []

        def counted(*args: Any, **kwargs: Any) -> Any:
            calls.append(args)
            return original(*args, **kwargs)

        exact_analysis.run_simulation = counted
        try:
            run_exact_analysis(2, self.matrix, {"TGG": 1.0})
        finally:
            exact_analysis.run_simulation = original

        self.assertEqual(1, len(calls))

    def test_zero_generation_and_population_scope_remain_stable(self) -> None:
        zero = run_exact_analysis(0, self.matrix, {"AAA": 1.0, "TGG": 2.0})
        self.assert_frame_contract_equal(
            zero.population_category_metrics,
            get_exact_category_metrics(
                zero,
                start_scope="population",
                start_key="all",
            ),
        )
        all_codon = run_exact_analysis(2, self.matrix)
        self.assert_frame_contract_equal(
            all_codon.population_survival,
            get_exact_survival_by_start(
                all_codon,
                start_scope="population",
                start_key="all",
            ),
        )


if __name__ == "__main__":
    unittest.main()
