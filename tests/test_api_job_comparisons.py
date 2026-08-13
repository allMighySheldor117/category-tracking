"""Phase 5 comparison job endpoint tests."""

from __future__ import annotations

import unittest
import time

from fastapi.testclient import TestClient

from api.main import create_app


PROBABILITIES = {"a_to_t": 0.2, "a_to_g": 0.5, "a_to_c": 0.3}


class ApiComparisonJobTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def _wait_for_result(self, job_id: str) -> dict[str, object]:
        for _ in range(50):
            response = self.client.get(f"/api/v1/jobs/{job_id}/result")
            if response.status_code == 200:
                return response.json()
            time.sleep(0.01)
        self.fail(f"job {job_id} did not complete")

    def test_exact_comparison_job_returns_completed_comparison_payload(self) -> None:
        simulation = {
            "n_generations": 1,
            "probabilities": PROBABILITIES,
            "start_weights": {"TGG": 1.0},
        }
        request = {
            "metric": "survivor_fraction",
            "scope": {"start_scope": "population", "start_key": "all"},
            "baseline": {"label": "baseline", "simulation": simulation},
            "candidate": {"label": "candidate", "simulation": simulation},
        }

        accepted = self.client.post("/api/v1/jobs/comparisons/exact", json=request)

        self.assertEqual(accepted.status_code, 202)
        job_id = accepted.json()["data"]["job"]["job_id"]
        result = self._wait_for_result(job_id)
        self.assertEqual(result["data"]["result"]["mode"], "exact_comparison")

    def test_exact_vs_sampled_job_returns_completed_calibration_payload(self) -> None:
        request = {
            "metric": "survivor_fraction",
            "denominator_scope": "population_initial",
            "exact": {
                "n_generations": 1,
                "probabilities": PROBABILITIES,
                "start_weights": {"TGG": 1.0},
            },
            "sampled": {
                "n_generations": 1,
                "probabilities": PROBABILITIES,
                "start_weights": {"TGG": 10},
                "seed": 8675309,
            },
        }

        accepted = self.client.post("/api/v1/jobs/comparisons/exact-vs-sampled", json=request)

        self.assertEqual(accepted.status_code, 202)
        job_id = accepted.json()["data"]["job"]["job_id"]
        result = self._wait_for_result(job_id)
        payload = result["data"]["result"]
        self.assertEqual(payload["mode"], "exact_vs_sampled")
        self.assertEqual(payload["scientific_authority"], "exact_probability")


if __name__ == "__main__":
    unittest.main()
