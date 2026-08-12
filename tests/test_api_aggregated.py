"""Phase 4 aggregated sampled endpoint contract tests."""

from __future__ import annotations

import random
import unittest

from fastapi.testclient import TestClient

from api.main import app
from api.serializers import serialize_table
from engine.aggregated_tracking import run_aggregated_experiment
from engine.category_analysis import get_aggregated_category_metrics, get_aggregated_survivor_fractions
from engine.mutation_matrix import build_substitution_matrix
from engine.summaries import (
    get_aggregated_codon_outcomes,
    get_aggregated_convergence,
    get_aggregated_stop_outcomes,
    get_aggregated_survival_by_start,
)


class ApiAggregatedEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.request = {
            "n_generations": 2,
            "probabilities": {"a_to_t": 1 / 6, "a_to_g": 2 / 3, "a_to_c": 1 / 6},
            "start_weights": {"AAA": 2, "TGG": 3},
            "seed": 7,
            "scopes": [{"start_scope": "population", "start_key": "all"}],
            "codon_outcomes": [{"start_codon": "TGG", "generation": 2}],
            "convergence": [
                {
                    "start_scope": "population",
                    "start_key": "all",
                    "basis": "category_weight",
                    "tolerance": 1.0,
                }
            ],
        }

    def test_aggregated_endpoint_matches_engine_tables_and_counters(self) -> None:
        response = self.client.post("/api/v1/simulations/aggregated", json=self.request)
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()

        matrix = build_substitution_matrix(1 / 6, 2 / 3, 1 / 6)
        result = run_aggregated_experiment(2, matrix, {"AAA": 2, "TGG": 3}, seed=7)

        self.assertEqual(payload["mode"], "aggregated_sampled")
        self.assertEqual(payload["scientific_authority"], "experimental_sampled")
        self.assertEqual(payload["data"]["seed"], 7)
        self.assertEqual(payload["data"]["total_start_count"], result.total_start_count)
        self.assertEqual(payload["data"]["start_counts"], dict(result.start_counts))
        self.assertEqual(payload["data"]["total_stopped"], result.total_stopped)
        self.assertEqual(payload["data"]["final_live_codon"], dict(result.final_live_codon))
        self.assertEqual(payload["data"]["final_live_amino_acid"], dict(result.final_live_amino_acid))
        self.assertEqual(len(payload["data"]["generation_counts"]), 2)
        self.assertEqual(
            payload["data"]["generation_counts"][0]["new_stop_codon_by_start_codon"]["TGG"],
            {"TAG": 1},
        )

        scope = payload["data"]["scopes"][0]
        self.assertEqual(
            scope["category_metrics"],
            serialize_table(
                get_aggregated_category_metrics(result, start_scope="population", start_key="all"),
                value_kind="copy_count",
            ),
        )
        self.assertEqual(
            scope["survivor_fractions"],
            serialize_table(
                get_aggregated_survivor_fractions(result, start_scope="population", start_key="all"),
                value_kind="fraction",
            ),
        )
        self.assertEqual(
            scope["survival_by_start"],
            serialize_table(
                get_aggregated_survival_by_start(result, start_scope="population", start_key="all"),
                value_kind="fraction",
            ),
        )
        self.assertEqual(
            scope["stop_outcomes"],
            serialize_table(
                get_aggregated_stop_outcomes(result, start_scope="population", start_key="all"),
                value_kind="copy_count",
            ),
        )
        self.assertEqual(
            payload["data"]["codon_outcomes"][0]["table"],
            serialize_table(
                get_aggregated_codon_outcomes(result, start_codon="TGG", generation=2),
                value_kind="copy_count",
            ),
        )
        self.assertEqual(
            payload["data"]["convergence"][0]["table"],
            serialize_table(
                get_aggregated_convergence(
                    result,
                    start_scope="population",
                    start_key="all",
                    basis="category_weight",
                    tolerance=1.0,
                ),
                value_kind="status",
            ),
        )

    def test_aggregated_endpoint_requires_explicit_integer_seed(self) -> None:
        request = dict(self.request)
        request.pop("seed")

        response = self.client.post("/api/v1/simulations/aggregated", json=request)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["errors"][0]["code"], "validation_error")

    def test_aggregated_endpoint_does_not_mutate_global_rng_state(self) -> None:
        random.seed(12345)
        before = random.getstate()

        response = self.client.post("/api/v1/simulations/aggregated", json=self.request)

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(random.getstate(), before)

    def test_aggregated_endpoint_rejects_oversized_request(self) -> None:
        request = dict(self.request)
        request["n_generations"] = 501

        response = self.client.post("/api/v1/simulations/aggregated", json=request)

        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json()["errors"][0]["code"], "oversized_request")

    def test_aggregated_endpoint_does_not_expose_detailed_records_or_paths(self) -> None:
        response = self.client.post("/api/v1/simulations/aggregated", json=self.request)

        self.assertEqual(response.status_code, 200, response.text)
        text = response.text
        for forbidden in ("records_by_copy", "paths", "copy_id", "final_rng_state", "stop_generation_records"):
            self.assertNotIn(forbidden, text)

    def test_openapi_registers_aggregated_endpoint(self) -> None:
        schema = app.openapi()
        self.assertIn("/api/v1/simulations/aggregated", schema["paths"])
        self.assertIn("post", schema["paths"]["/api/v1/simulations/aggregated"])


if __name__ == "__main__":
    unittest.main()
