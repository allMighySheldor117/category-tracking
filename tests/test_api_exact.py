"""Phase 4 exact simulation endpoint contract tests."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from api.main import app
from api.serializers import serialize_table
from engine.exact_analysis import (
    get_exact_category_metrics,
    get_exact_codon_outcomes,
    get_exact_convergence,
    get_exact_stop_outcomes,
    get_exact_survival_by_start,
    get_exact_survivor_fractions,
    run_exact_analysis,
)
from engine.mutation_matrix import build_substitution_matrix


class ApiExactEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.request = {
            "n_generations": 2,
            "probabilities": {"a_to_t": 1 / 6, "a_to_g": 2 / 3, "a_to_c": 1 / 6},
            "start_weights": {"AAA": 1.0, "TGG": 2.0},
            "scopes": [{"start_scope": "population", "start_key": "all"}],
            "codon_outcomes": [{"start_codon": "TGG", "generation": 2}],
            "convergence": [
                {
                    "start_scope": "population",
                    "start_key": "all",
                    "basis": "category_weight",
                    "tolerance": 0.01,
                }
            ],
        }

    def test_exact_endpoint_matches_engine_tables(self) -> None:
        response = self.client.post("/api/v1/simulations/exact", json=self.request)
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()

        matrix = build_substitution_matrix(1 / 6, 2 / 3, 1 / 6)
        analysis = run_exact_analysis(2, matrix, {"AAA": 1.0, "TGG": 2.0})

        self.assertEqual(payload["api_version"], "phase4-api-v1")
        self.assertEqual(payload["mode"], "exact")
        self.assertEqual(payload["scientific_authority"], "exact_probability")
        self.assertEqual(payload["data"]["n_generations"], 2)
        self.assertEqual(payload["data"]["start_weights"]["AAA"], 1.0)
        self.assertEqual(payload["data"]["start_weights"]["TGG"], 2.0)

        scope = payload["data"]["scopes"][0]
        self.assertEqual(scope["start_scope"], "population")
        self.assertEqual(scope["start_key"], "all")
        self.assertEqual(
            scope["category_metrics"],
            serialize_table(
                get_exact_category_metrics(analysis, start_scope="population", start_key="all"),
                value_kind="probability_weight",
            ),
        )
        self.assertEqual(
            scope["survivor_fractions"],
            serialize_table(
                get_exact_survivor_fractions(analysis, start_scope="population", start_key="all"),
                value_kind="fraction",
            ),
        )
        self.assertEqual(
            scope["survival_by_start"],
            serialize_table(
                get_exact_survival_by_start(analysis, start_scope="population", start_key="all"),
                value_kind="fraction",
            ),
        )
        self.assertEqual(
            scope["stop_outcomes"],
            serialize_table(
                get_exact_stop_outcomes(analysis, start_scope="population", start_key="all"),
                value_kind="probability_weight",
            ),
        )

        self.assertEqual(
            payload["data"]["codon_outcomes"][0]["table"],
            serialize_table(
                get_exact_codon_outcomes(analysis, start_codon="TGG", generation=2),
                value_kind="probability_weight",
            ),
        )
        self.assertEqual(
            payload["data"]["convergence"][0]["table"],
            serialize_table(
                get_exact_convergence(
                    analysis,
                    start_scope="population",
                    start_key="all",
                    basis="category_weight",
                    tolerance=0.01,
                ),
                value_kind="status",
            ),
        )

    def test_exact_endpoint_supports_zero_generations_with_typed_empty_tables(self) -> None:
        request = dict(self.request)
        request["n_generations"] = 0
        request["codon_outcomes"] = []
        request["convergence"] = []

        response = self.client.post("/api/v1/simulations/exact", json=request)

        self.assertEqual(response.status_code, 200, response.text)
        scope = response.json()["data"]["scopes"][0]
        self.assertEqual(scope["category_metrics"]["row_count"], 0)
        self.assertEqual(scope["survivor_fractions"]["row_count"], 0)
        self.assertEqual(scope["stop_outcomes"]["row_count"], 0)

    def test_exact_endpoint_rejects_oversized_generation_request(self) -> None:
        request = dict(self.request)
        request["n_generations"] = 2001

        response = self.client.post("/api/v1/simulations/exact", json=request)

        self.assertEqual(response.status_code, 413)
        payload = response.json()
        self.assertEqual(payload["mode"], "error")
        self.assertEqual(payload["errors"][0]["code"], "oversized_request")

    def test_openapi_registers_exact_endpoint(self) -> None:
        schema = app.openapi()
        self.assertIn("/api/v1/simulations/exact", schema["paths"])
        self.assertIn("post", schema["paths"]["/api/v1/simulations/exact"])


if __name__ == "__main__":
    unittest.main()
