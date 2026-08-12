"""Phase 4 comparison endpoint contract tests."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from api.main import app
from api.serializers import serialize_table
from engine.aggregated_tracking import run_aggregated_experiment
from engine.comparisons import compare_exact_to_sampled, compare_numeric_metric
from engine.exact_analysis import (
    get_exact_survival_by_start,
    get_exact_survivor_fractions,
    run_exact_analysis,
)
from engine.mutation_matrix import build_substitution_matrix
from engine.summaries import get_aggregated_survival_by_start


def _simulation(probabilities: dict[str, float], start_weights: dict[str, float], n_generations: int = 2) -> dict[str, object]:
    return {
        "n_generations": n_generations,
        "probabilities": probabilities,
        "start_weights": start_weights,
    }


class ApiComparisonEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.baseline_probabilities = {"a_to_t": 1 / 6, "a_to_g": 2 / 3, "a_to_c": 1 / 6}
        self.candidate_probabilities = {"a_to_t": 0.2, "a_to_g": 0.5, "a_to_c": 0.3}

    def test_exact_comparison_endpoint_matches_engine_directed_result(self) -> None:
        request = {
            "metric": "category_fraction",
            "baseline": {
                "label": "baseline",
                "simulation": _simulation(self.baseline_probabilities, {"TGG": 1.0}),
            },
            "candidate": {
                "label": "candidate",
                "simulation": _simulation(self.candidate_probabilities, {"TGG": 1.0}),
            },
            "scope": {"start_scope": "population", "start_key": "all"},
        }

        response = self.client.post("/api/v1/comparisons/exact", json=request)
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()

        baseline_matrix = build_substitution_matrix(1 / 6, 2 / 3, 1 / 6)
        candidate_matrix = build_substitution_matrix(0.2, 0.5, 0.3)
        baseline = run_exact_analysis(2, baseline_matrix, {"TGG": 1.0})
        candidate = run_exact_analysis(2, candidate_matrix, {"TGG": 1.0})
        expected = compare_numeric_metric(
            get_exact_survivor_fractions(baseline, start_scope="population", start_key="all"),
            get_exact_survivor_fractions(candidate, start_scope="population", start_key="all"),
            metric="category_fraction",
            baseline_label="baseline",
            candidate_label="candidate",
        )

        self.assertEqual(payload["mode"], "exact_comparison")
        self.assertEqual(payload["scientific_authority"], "exact_probability")
        self.assertEqual(payload["data"]["metric"], "category_fraction")
        self.assertEqual(payload["data"]["baseline_label"], "baseline")
        self.assertEqual(payload["data"]["candidate_label"], "candidate")
        self.assertEqual(payload["data"]["table"], serialize_table(expected.table, value_kind="delta"))

    def test_exact_vs_sampled_endpoint_matches_engine_calibration_result(self) -> None:
        request = {
            "metric": "survivor_fraction",
            "denominator_scope": "population_initial",
            "familywise_alpha": 0.01,
            "exact": _simulation(self.baseline_probabilities, {"TGG": 1.0}),
            "sampled": {
                "n_generations": 2,
                "probabilities": self.baseline_probabilities,
                "start_weights": {"TGG": 20},
                "seed": 8675309,
            },
        }

        response = self.client.post("/api/v1/comparisons/exact-vs-sampled", json=request)
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()

        matrix = build_substitution_matrix(1 / 6, 2 / 3, 1 / 6)
        exact = run_exact_analysis(2, matrix, {"TGG": 1.0})
        sampled = run_aggregated_experiment(2, matrix, {"TGG": 20}, seed=8675309)
        expected = compare_exact_to_sampled(
            get_exact_survival_by_start(exact, start_scope="population", start_key="all"),
            get_aggregated_survival_by_start(sampled, start_scope="population", start_key="all"),
            metric="survivor_fraction",
            denominator_scope="population_initial",
            familywise_alpha=0.01,
        )

        self.assertEqual(payload["mode"], "exact_vs_sampled")
        self.assertEqual(payload["scientific_authority"], "exact_probability")
        self.assertEqual(payload["data"]["metric"], "survivor_fraction")
        self.assertEqual(payload["data"]["family_size"], expected.family_size)
        self.assertEqual(payload["data"]["table"], serialize_table(expected.table, value_kind="calibration"))

    def test_exact_comparison_rejects_oversized_nested_exact_simulation(self) -> None:
        request = {
            "metric": "category_fraction",
            "baseline": {
                "label": "baseline",
                "simulation": _simulation(
                    self.baseline_probabilities,
                    {"TGG": 1.0},
                    n_generations=2001,
                ),
            },
            "candidate": {
                "label": "candidate",
                "simulation": _simulation(self.candidate_probabilities, {"TGG": 1.0}),
            },
            "scope": {"start_scope": "population", "start_key": "all"},
        }

        response = self.client.post("/api/v1/comparisons/exact", json=request)

        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json()["errors"][0]["code"], "oversized_request")

    def test_exact_vs_sampled_rejects_oversized_nested_sampled_simulation(self) -> None:
        request = {
            "metric": "survivor_fraction",
            "denominator_scope": "population_initial",
            "familywise_alpha": 0.01,
            "exact": _simulation(self.baseline_probabilities, {"TGG": 1.0}),
            "sampled": {
                "n_generations": 501,
                "probabilities": self.baseline_probabilities,
                "start_weights": {"TGG": 20},
                "seed": 8675309,
            },
        }

        response = self.client.post("/api/v1/comparisons/exact-vs-sampled", json=request)

        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json()["errors"][0]["code"], "oversized_request")

    def test_comparison_endpoints_are_registered_in_openapi(self) -> None:
        schema = app.openapi()
        self.assertIn("/api/v1/comparisons/exact", schema["paths"])
        self.assertIn("/api/v1/comparisons/exact-vs-sampled", schema["paths"])


if __name__ == "__main__":
    unittest.main()
