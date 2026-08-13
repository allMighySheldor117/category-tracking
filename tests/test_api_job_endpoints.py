"""Phase 5 job endpoint tests."""

from __future__ import annotations

import random
import time
import unittest

from fastapi.testclient import TestClient

from api.main import create_app


PROBABILITIES = {"a_to_t": 0.2, "a_to_g": 0.5, "a_to_c": 0.3}


class ApiJobEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def _wait_for_result(self, job_id: str) -> dict[str, object]:
        for _ in range(50):
            response = self.client.get(f"/api/v1/jobs/{job_id}/result")
            if response.status_code == 200:
                return response.json()
            time.sleep(0.01)
        self.fail(f"job {job_id} did not complete")

    def test_exact_job_submission_status_and_result_match_sync_shape(self) -> None:
        request = {
            "n_generations": 1,
            "probabilities": PROBABILITIES,
            "start_weights": {"TGG": 1.0},
        }

        accepted = self.client.post("/api/v1/jobs/exact", json=request)
        self.assertEqual(accepted.status_code, 202)
        accepted_data = accepted.json()["data"]
        job_id = accepted_data["job"]["job_id"]
        self.assertEqual(accepted_data["job"]["job_type"], "exact")

        payload = self._wait_for_result(job_id)
        self.assertEqual(payload["mode"], "job_result")
        self.assertEqual(payload["scientific_authority"], "exact_probability")
        self.assertEqual(payload["data"]["result"]["mode"], "exact")
        self.assertIn("scopes", payload["data"]["result"]["data"])

    def test_aggregated_job_requires_seed_and_preserves_global_rng(self) -> None:
        missing_seed = self.client.post(
            "/api/v1/jobs/aggregated",
            json={
                "n_generations": 1,
                "probabilities": PROBABILITIES,
                "start_weights": {"TGG": 10},
            },
        )
        self.assertEqual(missing_seed.status_code, 422)
        self.assertEqual(missing_seed.json()["errors"][0]["code"], "validation_error")

        random.seed(12345)
        before = random.getstate()
        accepted = self.client.post(
            "/api/v1/jobs/aggregated",
            json={
                "n_generations": 1,
                "probabilities": PROBABILITIES,
                "start_weights": {"TGG": 10},
                "seed": 8675309,
            },
        )
        after = random.getstate()

        self.assertEqual(accepted.status_code, 202)
        self.assertEqual(after, before)
        job_id = accepted.json()["data"]["job"]["job_id"]
        result = self._wait_for_result(job_id)
        self.assertEqual(result["data"]["result"]["mode"], "aggregated_sampled")

    def test_phase4_synchronous_exact_route_still_works(self) -> None:
        response = self.client.post(
            "/api/v1/simulations/exact",
            json={
                "n_generations": 0,
                "probabilities": PROBABILITIES,
                "start_weights": {"TGG": 1.0},
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mode"], "exact")


if __name__ == "__main__":
    unittest.main()
