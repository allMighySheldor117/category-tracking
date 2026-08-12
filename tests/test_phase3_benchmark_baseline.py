"""Phase 3 benchmark harness contract tests."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
import unittest
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))


class Phase3BenchmarkHarnessTests(unittest.TestCase):
    """Verify the benchmark harness is deterministic, advisory, and UI-safe."""

    def test_harness_imports_without_ui_frameworks(self) -> None:
        command = (
            "import sys, tools.benchmark_phase3 as benchmark; "
            "forbidden={'streamlit','tkinter','plotly','PyQt5'}; "
            "assert not forbidden.intersection(sys.modules), "
            "forbidden.intersection(sys.modules); "
            "assert benchmark.BYTECODE_POLICY_REQUIRED"
        )
        completed = subprocess.run(
            [sys.executable, "-c", command],
            cwd=APP_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual("", completed.stderr)
        self.assertEqual(0, completed.returncode)

    def test_workload_families_are_registered_and_deterministic(self) -> None:
        benchmark = importlib.import_module("tools.benchmark_phase3")
        first = benchmark.workload_definitions()
        second = benchmark.workload_definitions()
        self.assertEqual(first, second)
        families = {workload["family"] for workload in first}
        self.assertEqual(
            {"exact", "aggregated", "comparison", "calibration"},
            families,
        )
        for workload in first:
            self.assertIn("name", workload)
            self.assertIn("size", workload)
            self.assertIn("generations", workload)
            self.assertNotIn("threshold", workload)

    def test_measurement_policy_is_advisory(self) -> None:
        benchmark = importlib.import_module("tools.benchmark_phase3")
        policy = benchmark.measurement_policy()
        self.assertEqual("advisory", policy["timing_verdict"])
        self.assertEqual("advisory", policy["tracemalloc_verdict"])
        self.assertIsNone(policy["hard_runtime_threshold_seconds"])
        self.assertGreaterEqual(policy["warmups"], 0)
        self.assertGreaterEqual(policy["default_repeats"], 1)

    def test_structural_cardinality_does_not_scale_with_copy_count(self) -> None:
        benchmark = importlib.import_module("tools.benchmark_phase3")
        small = benchmark.aggregated_cardinality_probe(
            copies_per_codon=10,
            generations=3,
            seed=2718,
        )
        larger = benchmark.aggregated_cardinality_probe(
            copies_per_codon=100,
            generations=3,
            seed=2718,
        )
        self.assertEqual(small["snapshot_count"], larger["snapshot_count"])
        self.assertEqual(
            small["nested_counter_slots"],
            larger["nested_counter_slots"],
        )
        self.assertLess(small["total_start_count"], larger["total_start_count"])
        self.assertTrue(small["conservation_ok"])
        self.assertTrue(larger["conservation_ok"])

    def test_benchmark_does_not_mutate_exact_outputs(self) -> None:
        benchmark = importlib.import_module("tools.benchmark_phase3")
        before = benchmark.reference_exact_digest()
        benchmark.run_benchmark_suite(profile="quick")
        after = benchmark.reference_exact_digest()
        self.assertEqual(before, after)

    def test_bytecode_policy_is_visible_to_callers(self) -> None:
        benchmark = importlib.import_module("tools.benchmark_phase3")
        self.assertTrue(benchmark.BYTECODE_POLICY_REQUIRED)
        self.assertIn(
            os.environ.get("PYTHONDONTWRITEBYTECODE"),
            {None, "1"},
        )


if __name__ == "__main__":
    unittest.main()
