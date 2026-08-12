"""Phase 3 advisory benchmark harness.

This module records comparable baseline observations. It is not an optimizer and
does not define runtime acceptance thresholds.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import statistics
import sys
import time
import tracemalloc
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from engine.aggregated_tracking import run_aggregated_experiment
from engine.comparisons import compare_convergence, compare_exact_to_sampled, compare_numeric_metric
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
from engine.mutation_matrix import PRESET_AC, PRESET_AG, PRESET_AT, build_substitution_matrix
from engine.summaries import get_aggregated_stop_outcomes, get_aggregated_survival_by_start
from engine.genetic_code import ALL_AAS, PROPERTY_LABELS, STOP_CODONS, VALID_CODONS


BYTECODE_POLICY_REQUIRED = True
RESULTS_PATH = APP_ROOT / "docs" / "phase_3_benchmark_results.md"
EXACT_PROFILE_PATH = APP_ROOT / "docs" / "phase_3_exact_profile.md"


@dataclass(frozen=True)
class BenchmarkObservation:
    """One advisory benchmark observation row."""

    benchmark_name: str
    benchmark_family: str
    input_case: str
    generations: int
    copies_or_weights: str
    seed: str
    warmups: int
    repeats: int
    median_seconds: float
    min_seconds: float
    max_seconds: float
    advisory_peak_bytes: int
    structural_cardinality: str
    correctness_command: str
    status: str
    notes: str


def measurement_policy() -> dict[str, Any]:
    """Return the approved advisory measurement policy."""
    return {
        "warmups": 1,
        "default_repeats": 3,
        "larger_repeats": 1,
        "timing_verdict": "advisory",
        "tracemalloc_verdict": "advisory",
        "hard_runtime_threshold_seconds": None,
        "bytecode_policy": "PYTHONDONTWRITEBYTECODE=1",
    }


def workload_definitions() -> tuple[dict[str, Any], ...]:
    """Return deterministic benchmark workload definitions."""
    return (
        {
            "name": "exact_single_codon_small",
            "family": "exact",
            "size": "small",
            "generations": 5,
            "start_weights": {"TGG": 1.0},
            "operation": "run_exact_analysis",
        },
        {
            "name": "exact_single_codon_medium",
            "family": "exact",
            "size": "medium",
            "generations": 25,
            "start_weights": {"TGG": 1.0},
            "operation": "run_exact_analysis",
        },
        {
            "name": "exact_all_codon_small",
            "family": "exact",
            "size": "small",
            "generations": 5,
            "start_weights": None,
            "operation": "run_exact_analysis",
        },
        {
            "name": "exact_repeated_queries",
            "family": "exact",
            "size": "medium",
            "generations": 15,
            "start_weights": {"AAA": 1.0, "TGG": 1.0},
            "operation": "exact_query_cycle",
        },
        {
            "name": "aggregated_small",
            "family": "aggregated",
            "size": "small",
            "generations": 10,
            "start_weights": {"AAA": 100, "TGG": 100},
            "seed": 2718,
            "operation": "run_aggregated_experiment",
        },
        {
            "name": "aggregated_medium",
            "family": "aggregated",
            "size": "medium",
            "generations": 10,
            "start_weights": {"AAA": 1_000, "TGG": 1_000},
            "seed": 314159,
            "operation": "run_aggregated_experiment",
        },
        {
            "name": "comparison_numeric",
            "family": "comparison",
            "size": "small",
            "generations": 5,
            "start_weights": {"AAA": 1.0, "TGG": 1.0},
            "operation": "compare_numeric_metric",
        },
        {
            "name": "calibration_exact_sampled",
            "family": "calibration",
            "size": "small",
            "generations": 5,
            "start_weights": {"AAA": 100, "TGG": 100},
            "seed": 8675309,
            "operation": "compare_exact_to_sampled",
        },
    )


def _matrix() -> dict[str, dict[str, float]]:
    return build_substitution_matrix(PRESET_AT, PRESET_AG, PRESET_AC)


def _json_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _frame_digest(frame: pd.DataFrame) -> str:
    payload = {
        "columns": list(frame.columns),
        "dtypes": [str(dtype) for dtype in frame.dtypes],
        "index": list(frame.index),
        "rows": frame.astype(object).where(pd.notna(frame), None).to_dict("records"),
    }
    return _json_digest(payload)


def reference_exact_digest() -> str:
    """Digest a compact exact result to prove benchmarks do not mutate it."""
    analysis = run_exact_analysis(3, _matrix(), {"AAA": 1.0, "TGG": 1.0})
    payload = {
        "category": _frame_digest(analysis.population_category_metrics),
        "survival": _frame_digest(analysis.population_survival),
        "stops": _frame_digest(analysis.population_stop_outcomes),
        "stats": dict(analysis.simulation.stats),
    }
    return _json_digest(payload)


def aggregated_cardinality_probe(
    *,
    copies_per_codon: int,
    generations: int,
    seed: int,
) -> dict[str, Any]:
    """Return structural memory/cardinality evidence for aggregate output."""
    result = run_aggregated_experiment(
        generations,
        _matrix(),
        {"AAA": copies_per_codon, "TGG": copies_per_codon},
        seed,
    )
    bounded_slots_per_generation = (
        len(VALID_CODONS)
        + len(ALL_AAS)
        + len(PROPERTY_LABELS)
        + len(VALID_CODONS)
        + len(PROPERTY_LABELS)
        + (len(VALID_CODONS) * len(VALID_CODONS))
        + (len(VALID_CODONS) * len(STOP_CODONS))
        + len(STOP_CODONS)
        + len(VALID_CODONS)
        + len(PROPERTY_LABELS)
    )
    nested_counter_slots = bounded_slots_per_generation * len(result.generations)
    conservation_ok = True
    for snapshot in result.generations:
        if snapshot.total_live + snapshot.cumulative_stops != result.total_start_count:
            conservation_ok = False
    return {
        "copies_per_codon": copies_per_codon,
        "total_start_count": result.total_start_count,
        "snapshot_count": len(result.generations),
        "nested_counter_slots": nested_counter_slots,
        "conservation_ok": conservation_ok,
        "retains_paths_or_records": any(
            hasattr(result, name)
            for name in ("records", "paths", "copy_ids", "final_records")
        ),
    }


def _exact_query_cycle(generations: int, start_weights: dict[str, float] | None) -> None:
    analysis = run_exact_analysis(generations, _matrix(), start_weights)
    get_exact_category_metrics(analysis, start_scope="population", start_key="all")
    get_exact_survivor_fractions(analysis, start_scope="population", start_key="all")
    get_exact_survival_by_start(analysis, start_scope="population", start_key="all")
    get_exact_stop_outcomes(analysis, start_scope="population", start_key="all")
    get_exact_codon_outcomes(analysis, start_codon="TGG", generation=generations)
    get_exact_convergence(
        analysis,
        start_scope="population",
        start_key="all",
        basis="survivor_fraction",
        tolerance=0.01,
    )


def _comparison_numeric(generations: int, start_weights: dict[str, float] | None) -> None:
    baseline = run_exact_analysis(generations, _matrix(), start_weights)
    candidate = run_exact_analysis(
        generations,
        build_substitution_matrix(0.20, 0.60, 0.20),
        start_weights,
    )
    compare_numeric_metric(
        baseline.population_survivor_fractions,
        candidate.population_survivor_fractions,
        metric="category_fraction",
        baseline_label="baseline",
        candidate_label="candidate",
    )
    compare_convergence(
        get_exact_convergence(
            baseline,
            start_scope="population",
            start_key="all",
            basis="survivor_fraction",
            tolerance=0.01,
        ),
        get_exact_convergence(
            candidate,
            start_scope="population",
            start_key="all",
            basis="survivor_fraction",
            tolerance=0.01,
        ),
        baseline_label="baseline",
        candidate_label="candidate",
    )


def _calibration(generations: int, start_weights: dict[str, float] | None, seed: int) -> None:
    exact = run_exact_analysis(generations, _matrix(), start_weights)
    sampled = run_aggregated_experiment(generations, _matrix(), start_weights or {}, seed)
    sampled_table = get_aggregated_survival_by_start(
        sampled,
        start_scope="population",
        start_key="all",
    )
    compare_exact_to_sampled(
        exact.population_survival,
        sampled_table,
        metric="survivor_fraction",
        denominator_scope="population_initial",
    )


def _call_for_workload(workload: dict[str, Any]) -> Callable[[], None]:
    generations = int(workload["generations"])
    start_weights = copy.deepcopy(workload.get("start_weights"))
    operation = workload["operation"]
    if operation == "run_exact_analysis":
        return lambda: run_exact_analysis(generations, _matrix(), start_weights)
    if operation == "exact_query_cycle":
        return lambda: _exact_query_cycle(generations, start_weights)
    if operation == "run_aggregated_experiment":
        seed = int(workload["seed"])
        return lambda: run_aggregated_experiment(generations, _matrix(), start_weights or {}, seed)
    if operation == "compare_numeric_metric":
        return lambda: _comparison_numeric(generations, start_weights)
    if operation == "compare_exact_to_sampled":
        seed = int(workload["seed"])
        return lambda: _calibration(generations, start_weights, seed)
    raise ValueError(f"Unknown benchmark operation {operation}.")


def _measure(workload: dict[str, Any], *, repeats: int, warmups: int) -> BenchmarkObservation:
    operation = _call_for_workload(workload)
    for _index in range(warmups):
        operation()

    elapsed_values: list[float] = []
    peak_values: list[int] = []
    for _index in range(repeats):
        tracemalloc.start()
        started = time.perf_counter()
        operation()
        elapsed = time.perf_counter() - started
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        elapsed_values.append(elapsed)
        peak_values.append(peak)

    structural = "not_applicable"
    if workload["family"] == "aggregated":
        probe = aggregated_cardinality_probe(
            copies_per_codon=int((workload.get("start_weights") or {"AAA": 0})["AAA"]),
            generations=int(workload["generations"]),
            seed=int(workload["seed"]),
        )
        structural = (
            f"snapshots={probe['snapshot_count']}; "
            f"nested_counter_slots={probe['nested_counter_slots']}; "
            f"conservation_ok={probe['conservation_ok']}"
        )

    return BenchmarkObservation(
        benchmark_name=str(workload["name"]),
        benchmark_family=str(workload["family"]),
        input_case=str(workload["operation"]),
        generations=int(workload["generations"]),
        copies_or_weights=str(workload.get("start_weights")),
        seed=str(workload.get("seed", "not_applicable")),
        warmups=warmups,
        repeats=repeats,
        median_seconds=statistics.median(elapsed_values),
        min_seconds=min(elapsed_values),
        max_seconds=max(elapsed_values),
        advisory_peak_bytes=max(peak_values),
        structural_cardinality=structural,
        correctness_command='python -m unittest discover -s tests -p "test_*.py"',
        status="measured",
        notes="advisory baseline; no hard runtime threshold",
    )


def run_benchmark_suite(profile: str = "baseline") -> tuple[BenchmarkObservation, ...]:
    """Run the approved advisory benchmark suite."""
    policy = measurement_policy()
    workloads = list(workload_definitions())
    if profile == "quick":
        workloads = workloads[:2]
    if profile == "exact-profile":
        workloads = [
            workload
            for workload in workloads
            if workload["family"] == "exact"
        ]
    observations: list[BenchmarkObservation] = []
    for workload in workloads:
        repeats = int(policy["larger_repeats"] if workload["size"] == "larger" else policy["default_repeats"])
        observations.append(
            _measure(
                workload,
                repeats=repeats,
                warmups=int(policy["warmups"]),
            )
        )
    return tuple(observations)


def environment_report() -> dict[str, str]:
    """Return environment metadata without importing Streamlit runtime."""
    try:
        import streamlit as st

        streamlit_version = st.__version__
    except Exception as exc:  # pragma: no cover - defensive environment report
        streamlit_version = f"unavailable:{type(exc).__name__}"
    return {
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "pandas": pd.__version__,
        "streamlit": streamlit_version,
    }


def _markdown_table(observations: tuple[BenchmarkObservation, ...]) -> str:
    headers = [
        "benchmark_name",
        "benchmark_family",
        "generations",
        "copies_or_weights",
        "seed",
        "warmups",
        "repeats",
        "median_seconds",
        "min_seconds",
        "max_seconds",
        "advisory_peak_bytes",
        "structural_cardinality",
        "status",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _header in headers) + " |",
    ]
    for observation in observations:
        row = []
        for header in headers:
            value = getattr(observation, header)
            if isinstance(value, float):
                row.append(f"{value:.6f}")
            else:
                row.append(str(value).replace("|", "\\|"))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_results(observations: tuple[BenchmarkObservation, ...]) -> None:
    """Write concise Markdown baseline benchmark results."""
    environment = environment_report()
    content = [
        "# Phase 3 Benchmark Results",
        "",
        "Status: Baseline captured — advisory measurements only.",
        "",
        "## Environment",
        "",
    ]
    for key, value in environment.items():
        content.append(f"- {key}: `{value}`")
    content.extend(
        [
            "",
            "## Baseline observations",
            "",
            _markdown_table(observations),
            "",
            "## Interpretation",
            "",
            "These observations are a Phase 2 reference baseline for Phase 3. "
            "They do not define a runtime SLA and do not prove scientific correctness. "
            "Correctness remains owned by regression tests, diagnostics, exact equivalence, "
            "RNG preservation, reducer equivalence, and conservation checks.",
            "",
        ]
    )
    RESULTS_PATH.write_text("\n".join(content), encoding="utf-8")


def write_exact_profile(observations: tuple[BenchmarkObservation, ...]) -> None:
    """Write a read-only exact hot-path profile summary."""
    sorted_observations = sorted(
        observations,
        key=lambda observation: observation.median_seconds,
        reverse=True,
    )
    content = [
        "# Phase 3 Exact-Probability Hot-Path Profile",
        "",
        "Status: Profile captured — no optimization implemented.",
        "",
        "## Scope",
        "",
        "This profile separates exact propagation, exact analysis construction, "
        "and repeated derived-table query work using the Phase 3 benchmark harness.",
        "",
        "## Exact observations",
        "",
        _markdown_table(tuple(sorted_observations)),
        "",
        "## Hot-path findings",
        "",
        "- `run_exact_analysis` includes the unchanged exact propagation primitive plus eager population table construction.",
        "- Repeated scoped queries exercise DataFrame construction, Counter/dict iteration, canonical ordering, and provenance-derived state.",
        "- The highest median exact observations should guide Step 5, but only behind Phase 2 table and float-order equivalence tests.",
        "",
        "## Safe Step 5 candidates",
        "",
        "1. Reduce repeated derived-table construction where inputs are already represented by one `ExactAnalysisResult`.",
        "2. Share internal schema/table helpers without changing public DataFrame contracts.",
        "3. Cache or reuse pure derived structures only when ownership and mutation safety are explicit.",
        "4. Leave `engine.exact_tracking.run_simulation` untouched unless a later contract gate approves a dual reference/optimized path.",
        "",
    ]
    EXACT_PROFILE_PATH.write_text("\n".join(content), encoding="utf-8")


def append_exact_profile_summary(observations: tuple[BenchmarkObservation, ...]) -> None:
    """Append exact-profile summary to the results document."""
    if not RESULTS_PATH.exists():
        write_results(observations)
        return
    summary = [
        "",
        "## Exact-profile summary",
        "",
        "Exact profiling was run with `--exact-profile`. The detailed profile is in "
        "`docs/phase_3_exact_profile.md`.",
        "",
        _markdown_table(observations),
        "",
    ]
    with RESULTS_PATH.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(summary))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--exact-profile",
        action="store_true",
        help="Run exact-only profile and write docs/phase_3_exact_profile.md.",
    )
    args = parser.parse_args(argv)

    profile = "exact-profile" if args.exact_profile else "baseline"
    observations = run_benchmark_suite(profile=profile)
    if args.exact_profile:
        write_exact_profile(observations)
        append_exact_profile_summary(observations)
    else:
        write_results(observations)
    print(_markdown_table(observations))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
