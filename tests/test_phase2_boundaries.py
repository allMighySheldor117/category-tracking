"""Phase 2 public-surface and architecture boundary tests."""

from __future__ import annotations

import dataclasses
import hashlib
import inspect
import re
import subprocess
import sys
import unittest
from pathlib import Path


APP_ROOT = Path(__file__).parents[1].resolve()
WORKSPACE_ROOT = APP_ROOT.parent
ENGINE_ROOT = APP_ROOT / "engine"
FORBIDDEN_UI_MODULES = {"streamlit", "tkinter", "plotly", "PyQt5"}

EXPECTED_EXPORTS = (
    "AggregatedGenerationCounts",
    "AggregatedSampledResult",
    "ComparisonResult",
    "ConvergenceComparisonResult",
    "ConvergenceResult",
    "ExactAnalysisResult",
    "ExactResultProvenanceError",
    "ExactSampledComparisonResult",
    "ExactSimulationResult",
    "InvalidScientificScopeError",
    "MetricSchemaError",
    "NoMoreChangeResult",
    "SampledSimulationResult",
    "ScientificInvariantError",
    "ScientificInvariantReport",
    "UnsupportedComparisonError",
    "build_exact_analysis",
    "compare_convergence",
    "compare_exact_to_sampled",
    "compare_numeric_metric",
    "get_aggregated_category_metrics",
    "get_aggregated_codon_outcomes",
    "get_aggregated_convergence",
    "get_aggregated_stop_outcomes",
    "get_aggregated_survival_by_start",
    "get_aggregated_survivor_fractions",
    "get_exact_category_metrics",
    "get_exact_codon_outcomes",
    "get_exact_convergence",
    "get_exact_stop_outcomes",
    "get_exact_survival_by_start",
    "get_exact_survivor_fractions",
    "run_aggregated_experiment",
    "run_exact_analysis",
    "validate_biological_invariants",
    "validate_exact_analysis",
    "validate_mutation_matrix",
)

EXPECTED_OWNERS = {
    "run_exact_analysis": "engine.exact_analysis",
    "build_exact_analysis": "engine.exact_analysis",
    "get_exact_category_metrics": "engine.exact_analysis",
    "get_exact_survivor_fractions": "engine.exact_analysis",
    "get_exact_survival_by_start": "engine.exact_analysis",
    "get_exact_stop_outcomes": "engine.exact_analysis",
    "get_exact_codon_outcomes": "engine.exact_analysis",
    "get_exact_convergence": "engine.exact_analysis",
    "run_aggregated_experiment": "engine.aggregated_tracking",
    "get_aggregated_category_metrics": "engine.category_analysis",
    "get_aggregated_survivor_fractions": "engine.category_analysis",
    "get_aggregated_survival_by_start": "engine.summaries",
    "get_aggregated_stop_outcomes": "engine.summaries",
    "get_aggregated_codon_outcomes": "engine.summaries",
    "get_aggregated_convergence": "engine.summaries",
    "compare_numeric_metric": "engine.comparisons",
    "compare_convergence": "engine.comparisons",
    "compare_exact_to_sampled": "engine.comparisons",
    "validate_biological_invariants": "engine.invariants",
    "validate_mutation_matrix": "engine.invariants",
    "validate_exact_analysis": "engine.invariants",
}

EXPECTED_MODEL_EXPORTS = (
    "AggregatedGenerationCounts",
    "AggregatedSampledResult",
    "ComparisonResult",
    "ConvergenceComparisonResult",
    "ConvergenceResult",
    "ExactAnalysisResult",
    "ExactSampledComparisonResult",
    "ExactSimulationResult",
    "NoMoreChangeResult",
    "SampledSimulationResult",
    "ScientificInvariantReport",
)

EXPECTED_ERROR_EXPORTS = (
    "ExactResultProvenanceError",
    "InvalidScientificScopeError",
    "MetricSchemaError",
    "ScientificInvariantError",
    "UnsupportedComparisonError",
)


def run_fresh(command: str) -> subprocess.CompletedProcess[str]:
    """Run a boundary assertion in a fresh Python process."""
    return subprocess.run(
        [sys.executable, "-c", command],
        cwd=APP_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class Phase2BoundaryTests(unittest.TestCase):
    def assert_fresh_passes(self, command: str) -> None:
        completed = run_fresh(command)
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)

    def test_public_surface_exports_only_approved_names(self) -> None:
        import engine

        self.assertEqual(tuple(engine.__all__), EXPECTED_EXPORTS)
        forbidden_exports = {"run_simulation", "run_experiment", "METRIC_CONTRACTS"}
        self.assertFalse(forbidden_exports.intersection(engine.__all__))

    def test_public_exports_resolve_to_their_single_owners(self) -> None:
        import engine

        for name, module_name in EXPECTED_OWNERS.items():
            with self.subTest(name=name):
                exported = getattr(engine, name)
                self.assertEqual(exported.__module__, module_name)

        for name in EXPECTED_MODEL_EXPORTS + EXPECTED_ERROR_EXPORTS:
            with self.subTest(name=name):
                exported = getattr(engine, name)
                self.assertEqual(exported.__module__, "engine.models")

    def test_phase2_result_models_are_dataclasses_without_legacy_tuple_api(self) -> None:
        import engine

        phase2_models = (
            engine.ExactAnalysisResult,
            engine.AggregatedGenerationCounts,
            engine.AggregatedSampledResult,
            engine.ComparisonResult,
            engine.ConvergenceComparisonResult,
            engine.ExactSampledComparisonResult,
            engine.ScientificInvariantReport,
        )
        for model in phase2_models:
            with self.subTest(model=model.__name__):
                self.assertTrue(dataclasses.is_dataclass(model))
                self.assertFalse(hasattr(model, "to_legacy_tuple"))
                signature = inspect.signature(model)
                self.assertTrue(
                    all(
                        parameter.annotation is not inspect.Parameter.empty
                        for parameter in signature.parameters.values()
                    )
                )

    def test_public_functions_are_typed_and_keep_approved_defaults(self) -> None:
        import engine

        for name in EXPECTED_OWNERS:
            with self.subTest(name=name):
                signature = inspect.signature(getattr(engine, name))
                self.assertIsNot(signature.return_annotation, inspect.Signature.empty)
                for parameter in signature.parameters.values():
                    self.assertIsNot(parameter.annotation, inspect.Parameter.empty)

        exact_signature = inspect.signature(engine.run_exact_analysis)
        self.assertEqual(exact_signature.parameters["start_weights"].default, None)
        aggregated_signature = inspect.signature(engine.run_aggregated_experiment)
        self.assertIs(aggregated_signature.parameters["seed"].default, inspect.Parameter.empty)
        calibration_signature = inspect.signature(engine.compare_exact_to_sampled)
        self.assertEqual(calibration_signature.parameters["familywise_alpha"].default, 0.01)

    def test_fresh_engine_import_is_ui_independent_and_local(self) -> None:
        modules = (
            "engine",
            "engine.models",
            "engine.genetic_code",
            "engine.mutation_matrix",
            "engine.exact_tracking",
            "engine.exact_analysis",
            "engine.sampled_tracking",
            "engine.aggregated_tracking",
            "engine.category_analysis",
            "engine.summaries",
            "engine.comparisons",
            "engine.invariants",
        )
        self.assert_fresh_passes(
            "import importlib, sys; "
            f"[importlib.import_module(name) for name in {modules!r}]; "
            f"forbidden={FORBIDDEN_UI_MODULES!r}; "
            "assert not forbidden.intersection(sys.modules), forbidden.intersection(sys.modules)"
        )
        self.assert_fresh_passes(
            "from pathlib import Path; "
            "import category_tracking, category_tracking_web, engine; "
            "root=Path.cwd().resolve(); "
            "modules=(category_tracking, category_tracking_web, engine); "
            "assert all(root in Path(module.__file__).resolve().parents for module in modules)"
        )

    def test_engine_import_order_has_no_adapter_cycle(self) -> None:
        orders = (
            ("engine", "category_tracking", "category_tracking_web"),
            ("category_tracking_web", "engine", "category_tracking"),
            ("category_tracking", "engine", "category_tracking_web"),
        )
        for order in orders:
            with self.subTest(order=order):
                self.assert_fresh_passes(
                    "import importlib; "
                    f"[importlib.import_module(name) for name in {order!r}]"
                )

    def test_single_source_owners_remain_unambiguous(self) -> None:
        patterns = {
            r"^CODON_TABLE\s=": ("genetic_code.py",),
            r"^VALID_CODONS\s=": ("genetic_code.py",),
            r"^STOP_CODONS\s=": ("genetic_code.py",),
            r"^PROPERTY_LABELS\s=": ("genetic_code.py",),
            r"^def run_simulation\(": ("exact_tracking.py",),
            r"^def run_experiment\(": ("sampled_tracking.py",),
            r"^def run_aggregated_experiment\(": ("aggregated_tracking.py",),
        }
        for pattern, expected_files in patterns.items():
            with self.subTest(pattern=pattern):
                observed = tuple(
                    path.name
                    for path in sorted(ENGINE_ROOT.glob("*.py"))
                    if re.search(pattern, path.read_text(encoding="utf-8"), re.MULTILINE)
                )
                self.assertEqual(observed, expected_files)

    def test_boundaries_have_no_wildcards_or_new_positional_tuple_consumers(self) -> None:
        init_source = (ENGINE_ROOT / "__init__.py").read_text(encoding="utf-8")
        self.assertNotIn("import *", init_source)
        self.assertNotIn("run_simulation", init_source)
        self.assertNotIn("run_experiment", init_source)

        new_consumers = (
            "category_analysis.py",
            "summaries.py",
            "comparisons.py",
        )
        for name in new_consumers:
            with self.subTest(path=name):
                source = (ENGINE_ROOT / name).read_text(encoding="utf-8")
                self.assertIsNone(re.search(r"\[[0-9]+\]", source))

    def test_aggregated_public_models_do_not_retain_per_copy_information(self) -> None:
        import engine

        forbidden_fragments = ("record", "path", "copy_id", "copy_ids", "stop_generation")
        for model in (engine.AggregatedSampledResult, engine.AggregatedGenerationCounts):
            with self.subTest(model=model.__name__):
                field_names = tuple(field.name for field in dataclasses.fields(model))
                for fragment in forbidden_fragments:
                    self.assertFalse(any(fragment in field_name for field_name in field_names))
        self.assertIn(
            "new_stop_codon_by_start_codon",
            tuple(field.name for field in dataclasses.fields(engine.AggregatedGenerationCounts)),
        )

    def test_frozen_artifact_hashes_remain_unchanged(self) -> None:
        expected = {
            APP_ROOT / "diagnose_category_tracking_web.py": "03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4",
            APP_ROOT / "tests" / "compat" / "diagnose_category_tracking_web_phase1_baseline.py": "03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4",
            WORKSPACE_ROOT / "diagnose_category_tracking_web.py": "03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4",
            APP_ROOT / "tests" / "fixtures" / "phase1_scientific_baseline.json": "96c75420dbde1ccc497fe05419a163703e0ca251b7c466ed8b976bdbad3ed95b",
            APP_ROOT / "tests" / "fixtures" / "phase1_streamlit_surface.json": "4e4b1ce860cd07bc495b818f99e3f873a463e482005756e39f0041db48fb1035",
            APP_ROOT / "tests" / "fixtures" / "phase2_scientific_contract.json": "39e8387bd76c49ad426d6c336736c63540df4de0595eae921029e84bf8441887",
            WORKSPACE_ROOT / "category_tracking.py": "7f017a872252450fb10546b3d9f4d6de4f98e0d513f047e32dd1a48643cb47de",
            WORKSPACE_ROOT / "category_tracking_web.py": "eb04c1e6e1e1272a8cbf84ef5e8543b13fcf6ae7e1783aeacd709ad3073441e8",
        }
        for path, digest in expected.items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)

    def test_phase2_documentation_registers_approved_runtime_contracts(self) -> None:
        app_readme = (APP_ROOT / "README.md").read_text(encoding="utf-8")
        engine_readme = (ENGINE_ROOT / "README.md").read_text(encoding="utf-8")
        final_instructions = (APP_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        root_instructions = (WORKSPACE_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        blueprint = (WORKSPACE_ROOT / "plans" / "phase-2-strengthen-computation.md").read_text(
            encoding="utf-8"
        )

        required_app_terms = (
            "Phase 2",
            "run_exact_analysis",
            "Exact probability is the authoritative deterministic scientific path",
            "run_aggregated_experiment",
            "engine-only experimental API",
            "Sampled copies",
            "Exact probability",
        )
        for term in required_app_terms:
            with self.subTest(document="final README", term=term):
                self.assertIn(term, app_readme)

        required_engine_terms = (
            "ExactAnalysisResult",
            "AggregatedSampledResult",
            "compare_exact_to_sampled",
            "Wilson",
            "Bonferroni",
            "new_stop_codon_by_start_codon",
            "No per-copy records",
        )
        for term in required_engine_terms:
            with self.subTest(document="engine README", term=term):
                self.assertIn(term, engine_readme)

        for document_name, source in (
            ("final CLAUDE", final_instructions),
            ("root CLAUDE", root_instructions),
        ):
            with self.subTest(document=document_name):
                self.assertIn("final code/.ai-style-rules.md", source)
                self.assertIn("exact analysis", source.lower())
                self.assertIn("aggregated sampled", source.lower())

        self.assertIn("**Status:** Complete", blueprint)
        self.assertIn("Gate 2 handoff ready", blueprint)


if __name__ == "__main__":
    unittest.main()
