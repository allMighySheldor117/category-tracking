"""Phase 4 API error and OpenAPI metadata contract tests."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from api.main import app


class ApiErrorContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app, raise_server_exceptions=False)

    def test_malformed_json_uses_approved_error_envelope(self) -> None:
        response = self.client.post(
            "/api/v1/simulations/exact",
            content="{",
            headers={"content-type": "application/json"},
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertEqual(payload["api_version"], "phase4-api-v1")
        self.assertEqual(payload["mode"], "error")
        self.assertEqual(payload["scientific_authority"], "none")
        self.assertEqual(payload["errors"][0]["code"], "malformed_json")

    def test_missing_probability_key_returns_validation_error_envelope(self) -> None:
        response = self.client.post(
            "/api/v1/simulations/exact",
            json={
                "n_generations": 1,
                "probabilities": {"a_to_t": 0.1},
                "start_weights": {"TGG": 1.0},
            },
        )

        self.assertEqual(response.status_code, 422)
        payload = response.json()
        self.assertEqual(payload["api_version"], "phase4-api-v1")
        self.assertEqual(payload["mode"], "error")
        self.assertEqual(payload["scientific_authority"], "none")
        self.assertEqual(payload["errors"][0]["code"], "validation_error")

    def test_invalid_scientific_scope_is_translated(self) -> None:
        response = self.client.post(
            "/api/v1/simulations/exact",
            json={
                "n_generations": 1,
                "probabilities": {"a_to_t": 1 / 6, "a_to_g": 2 / 3, "a_to_c": 1 / 6},
                "start_weights": {"TGG": 1.0},
                "scopes": [{"start_scope": "bad", "start_key": "all"}],
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["errors"][0]["code"], "invalid_scientific_scope")

    def test_unsupported_comparison_is_translated(self) -> None:
        response = self.client.post(
            "/api/v1/comparisons/exact",
            json={
                "metric": "not_a_metric",
                "baseline": {
                    "label": "baseline",
                    "simulation": {
                        "n_generations": 1,
                        "probabilities": {"a_to_t": 1 / 6, "a_to_g": 2 / 3, "a_to_c": 1 / 6},
                        "start_weights": {"TGG": 1.0},
                    },
                },
                "candidate": {
                    "label": "candidate",
                    "simulation": {
                        "n_generations": 1,
                        "probabilities": {"a_to_t": 1 / 6, "a_to_g": 2 / 3, "a_to_c": 1 / 6},
                        "start_weights": {"TGG": 1.0},
                    },
                },
                "scope": {"start_scope": "population", "start_key": "all"},
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["errors"][0]["code"], "unsupported_comparison")

    def test_openapi_contains_approved_routes_version_and_tags(self) -> None:
        schema = app.openapi()

        self.assertEqual(schema["info"]["title"], "Codon Category Tracking API")
        self.assertEqual(schema["info"]["version"], "phase4-api-v1")
        self.assertEqual(
            set(schema["paths"]),
            {
                "/health",
                "/api/v1/metadata",
                "/api/v1/simulations/exact",
                "/api/v1/simulations/aggregated",
                "/api/v1/comparisons/exact",
                "/api/v1/comparisons/exact-vs-sampled",
                "/api/v1/jobs/exact",
                "/api/v1/jobs/aggregated",
                "/api/v1/jobs/comparisons/exact",
                "/api/v1/jobs/comparisons/exact-vs-sampled",
                "/api/v1/jobs/{job_id}",
                "/api/v1/jobs/{job_id}/result",
                "/api/v1/jobs/{job_id}/retry",
            },
        )
        tag_names = {tag["name"] for tag in schema["tags"]}
        self.assertTrue({"health", "metadata", "simulations", "comparisons", "jobs"}.issubset(tag_names))

if __name__ == "__main__":
    unittest.main()
