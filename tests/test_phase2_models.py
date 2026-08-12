"""Contract tests for the approved Phase 2 named models and schema fixture."""

from __future__ import annotations

import hashlib
import inspect
import json
import os
import subprocess
import sys
import unittest
from collections import Counter
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path
from typing import Any, get_args, get_origin, get_type_hints

import pandas as pd

from engine.models import (
    AggregatedGenerationCounts,
    AggregatedSampledResult,
    ComparisonResult,
    ConvergenceBasis,
    ConvergenceComparisonResult,
    ConvergenceResult,
    ExactAnalysisResult,
    ExactResultProvenanceError,
    ExactSampledComparisonResult,
    ExactSimulationResult,
    InvalidScientificScopeError,
    MetricName,
    MetricSchemaError,
    NoMoreChangeResult,
    SampledSimulationResult,
    ScientificInvariantError,
    ScientificInvariantReport,
    StartScope,
    StartWeights,
    UnsupportedComparisonError,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "phase2_scientific_contract.json"
FIXTURE_SHA256 = "39e8387bd76c49ad426d6c336736c63540df4de0595eae921029e84bf8441887"

MODEL_FIELDS = {
    ExactAnalysisResult: [
        "simulation",
        "start_weights",
        "population_category_metrics",
        "population_survivor_fractions",
        "population_survival",
        "population_stop_outcomes",
    ],
    AggregatedGenerationCounts: [
        "generation",
        "live_codon",
        "live_amino_acid",
        "live_category",
        "live_by_start_codon",
        "live_by_start_trait",
        "current_codon_by_start_codon",
        "new_stop_codon_by_start_codon",
        "new_stops_by_stop_codon",
        "new_stops_by_start_codon",
        "new_stops_by_start_trait",
        "total_live",
        "new_stops",
        "cumulative_stops",
    ],
    AggregatedSampledResult: [
        "seed",
        "n_generations",
        "start_counts",
        "total_start_count",
        "generations",
        "final_live_codon",
        "final_live_amino_acid",
        "final_live_by_start_codon",
        "total_stopped",
    ],
    ComparisonResult: [
        "metric",
        "baseline_label",
        "candidate_label",
        "key_columns",
        "table",
    ],
    ConvergenceComparisonResult: ["baseline_label", "candidate_label", "table"],
    ExactSampledComparisonResult: [
        "metric",
        "denominator_scope",
        "familywise_alpha",
        "family_size",
        "table",
    ],
    ScientificInvariantReport: [
        "metric",
        "scope",
        "generation",
        "expected",
        "observed",
        "tolerance",
    ],
}


class Phase2FixtureTests(unittest.TestCase):
    def test_fixture_is_static_reviewed_contract_data(self) -> None:
        raw = FIXTURE_PATH.read_bytes()
        fixture = json.loads(raw)

        self.assertEqual(hashlib.sha256(raw).hexdigest(), FIXTURE_SHA256)
        self.assertEqual(fixture["schema_version"], 2)
        self.assertEqual(fixture["contract_version"], "2.1-approved")
        self.assertIs(fixture["generated_by_tests"], False)
        self.assertEqual(
            fixture["models"],
            {model.__name__: names for model, names in MODEL_FIELDS.items()},
        )

    def test_fixture_records_canonical_schema_and_calibration_metadata(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

        self.assertEqual(fixture["canonical"]["stops"], ["TAA", "TAG", "TGA"])
        self.assertEqual(
            fixture["tables"]["category_metrics"]["columns"],
            [
                "generation",
                "start_scope",
                "start_key",
                "category",
                "live_value",
                "value_kind",
            ],
        )
        self.assertEqual(
            fixture["tables"]["exact_sampled_calibration"]["dtypes"],
            [
                "int64",
                "object",
                "object",
                "object",
                "float64",
                "Float64",
                "Float64",
                "Float64",
                "int64",
                "Float64",
                "float64",
                "int64",
                "Float64",
                "Float64",
                "boolean",
            ],
        )
        self.assertEqual(fixture["calibration"]["seeds"], [1729, 271828, 314159])
        self.assertEqual(fixture["calibration"]["sample_sizes"], [610, 6100, 61000])
        self.assertEqual(
            fixture["approved_decisions"]["exact_conservation"],
            {"rel_tol": 1e-12, "abs_tol": 1e-12},
        )


class Phase2TypeContractTests(unittest.TestCase):
    def test_public_aliases_have_approved_literal_values(self) -> None:
        self.assertEqual(str(get_origin(StartWeights)), "<class 'collections.abc.Mapping'>")
        self.assertEqual(get_args(StartWeights), (str, float))
        self.assertEqual(
            get_args(StartScope),
            ("population", "codon", "amino_acid", "trait"),
        )
        self.assertEqual(
            get_args(ConvergenceBasis),
            ("category_weight", "survivor_fraction"),
        )
        self.assertEqual(
            get_args(MetricName),
            (
                "category_live_value",
                "category_fraction",
                "survivor_fraction",
                "stop_fraction",
                "new_stop_value",
                "cumulative_stop_value",
                "cumulative_stop_fraction",
                "codon_live_value",
                "codon_new_stop_value",
                "codon_cumulative_stop_value",
            ),
        )

    def test_named_errors_are_distinct_value_errors(self) -> None:
        errors = (
            ExactResultProvenanceError,
            InvalidScientificScopeError,
            UnsupportedComparisonError,
            MetricSchemaError,
            ScientificInvariantError,
        )

        for error in errors:
            with self.subTest(error=error.__name__):
                self.assertEqual(error.__bases__, (ValueError,))

    def test_new_models_are_frozen_required_named_results(self) -> None:
        for model, expected_fields in MODEL_FIELDS.items():
            with self.subTest(model=model.__name__):
                model_fields = fields(model)
                self.assertEqual([field.name for field in model_fields], expected_fields)
                self.assertTrue(model.__dataclass_params__.frozen)
                self.assertTrue(
                    all(
                        field.default is MISSING and field.default_factory is MISSING
                        for field in model_fields
                    )
                )
                self.assertTrue(
                    all(
                        parameter.default is inspect.Parameter.empty
                        for parameter in inspect.signature(model).parameters.values()
                    )
                )
                self.assertFalse(hasattr(model, "to_legacy_tuple"))
                self.assertFalse(hasattr(model, "from_legacy_tuple"))

    def test_new_models_use_approved_annotations(self) -> None:
        expected = {
            ExactAnalysisResult: {
                "simulation": ExactSimulationResult,
                "start_weights": dict[str, float],
                "population_category_metrics": pd.DataFrame,
                "population_survivor_fractions": pd.DataFrame,
                "population_survival": pd.DataFrame,
                "population_stop_outcomes": pd.DataFrame,
            },
            AggregatedGenerationCounts: {
                "generation": int,
                "live_codon": Counter[str],
                "live_amino_acid": Counter[str],
                "live_category": Counter[str],
                "live_by_start_codon": Counter[str],
                "live_by_start_trait": Counter[str],
                "current_codon_by_start_codon": dict[str, Counter[str]],
                "new_stop_codon_by_start_codon": dict[str, Counter[str]],
                "new_stops_by_stop_codon": Counter[str],
                "new_stops_by_start_codon": Counter[str],
                "new_stops_by_start_trait": Counter[str],
                "total_live": int,
                "new_stops": int,
                "cumulative_stops": int,
            },
            AggregatedSampledResult: {
                "seed": int,
                "n_generations": int,
                "start_counts": dict[str, int],
                "total_start_count": int,
                "generations": tuple[AggregatedGenerationCounts, ...],
                "final_live_codon": Counter[str],
                "final_live_amino_acid": Counter[str],
                "final_live_by_start_codon": dict[str, Counter[str]],
                "total_stopped": int,
            },
            ComparisonResult: {
                "metric": str,
                "baseline_label": str,
                "candidate_label": str,
                "key_columns": tuple[str, ...],
                "table": pd.DataFrame,
            },
            ConvergenceComparisonResult: {
                "baseline_label": str,
                "candidate_label": str,
                "table": pd.DataFrame,
            },
            ExactSampledComparisonResult: {
                "metric": str,
                "denominator_scope": str,
                "familywise_alpha": float,
                "family_size": int,
                "table": pd.DataFrame,
            },
            ScientificInvariantReport: {
                "metric": str,
                "scope": str,
                "generation": int | None,
                "expected": Any,
                "observed": Any,
                "tolerance": float,
            },
        }

        for model, expected_hints in expected.items():
            with self.subTest(model=model.__name__):
                self.assertEqual(get_type_hints(model), expected_hints)

    def test_frozen_models_reject_field_rebinding(self) -> None:
        table = pd.DataFrame()
        result = ComparisonResult("stop_fraction", "base", "candidate", ("generation",), table)

        with self.assertRaises(FrozenInstanceError):
            result.metric = "category_fraction"


class Phase1CompatibilityTests(unittest.TestCase):
    def test_phase1_dataclass_contracts_remain_unchanged(self) -> None:
        expected = {
            ConvergenceResult: (["generation", "max_delta"], True),
            NoMoreChangeResult: (["generation", "status"], True),
            ExactSimulationResult: (
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
                False,
            ),
            SampledSimulationResult: (
                ["records", "sample_fin_codon", "sample_fin_aa", "sample_start_to_fin"],
                False,
            ),
        }

        for model, (expected_fields, frozen) in expected.items():
            with self.subTest(model=model.__name__):
                self.assertEqual([field.name for field in fields(model)], expected_fields)
                self.assertEqual(model.__dataclass_params__.frozen, frozen)
                self.assertEqual(
                    list(inspect.signature(model).parameters),
                    expected_fields,
                )

        self.assertTrue(hasattr(ConvergenceResult, "to_legacy_tuple"))
        self.assertTrue(hasattr(NoMoreChangeResult, "to_legacy_tuple"))
        self.assertTrue(hasattr(ExactSimulationResult, "to_legacy_tuple"))
        self.assertTrue(hasattr(ExactSimulationResult, "from_legacy_tuple"))
        self.assertTrue(hasattr(SampledSimulationResult, "to_legacy_tuple"))
        self.assertTrue(hasattr(SampledSimulationResult, "from_legacy_tuple"))

    def test_engine_models_import_is_ui_independent_in_fresh_process(self) -> None:
        script = (
            "import sys; import engine.models; "
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
