"""Phase 5 job API boundary and lifecycle endpoint tests."""

from __future__ import annotations

import ast
import json
import time
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api.jobs import DEFAULT_WORKER_COUNT, JobRunner, JobStore
from api.main import create_app


PROBABILITIES = {"a_to_t": 0.2, "a_to_g": 0.5, "a_to_c": 0.3}


class ApiJobBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def _create_completed_exact_job(self) -> str:
        response = self.client.post(
            "/api/v1/jobs/exact",
            json={
                "n_generations": 0,
                "probabilities": PROBABILITIES,
                "start_weights": {"TGG": 1.0},
            },
        )
        self.assertEqual(response.status_code, 202)
        job_id = response.json()["data"]["job"]["job_id"]
        for _ in range(50):
            status = self.client.get(f"/api/v1/jobs/{job_id}").json()["data"]["job"]["status"]
            if status == "completed":
                return job_id
            time.sleep(0.01)
        self.fail(f"job {job_id} did not complete")

    def test_retry_completed_job_is_not_allowed(self) -> None:
        job_id = self._create_completed_exact_job()

        response = self.client.post(f"/api/v1/jobs/{job_id}/retry")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["errors"][0]["code"], "job_retry_not_allowed")

    def test_delete_completed_job_removes_retained_job(self) -> None:
        job_id = self._create_completed_exact_job()

        deleted = self.client.delete(f"/api/v1/jobs/{job_id}")
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(deleted.json()["data"]["job"]["status"], "completed")

        missing = self.client.get(f"/api/v1/jobs/{job_id}")
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.json()["errors"][0]["code"], "job_not_found")

    def test_openapi_contains_approved_job_routes_and_no_detailed_sampled_job(self) -> None:
        schema = self.client.get("/openapi.json").json()
        paths = set(schema["paths"])
        approved = {
            "/api/v1/jobs/exact",
            "/api/v1/jobs/aggregated",
            "/api/v1/jobs/comparisons/exact",
            "/api/v1/jobs/comparisons/exact-vs-sampled",
            "/api/v1/jobs/{job_id}",
            "/api/v1/jobs/{job_id}/result",
            "/api/v1/jobs/{job_id}/retry",
        }
        self.assertTrue(approved.issubset(paths))
        self.assertIn("delete", schema["paths"]["/api/v1/jobs/{job_id}"])
        self.assertFalse(any("detailed" in path or "sampled/details" in path for path in paths))

    def test_openapi_matches_phase5_static_route_fixture(self) -> None:
        fixture = json.loads(
            Path("tests/fixtures/phase5_openapi.json").read_text(encoding="utf-8")
        )
        schema = self.client.get("/openapi.json").json()

        self.assertEqual(schema["info"]["title"], fixture["info"]["title"])
        self.assertEqual(schema["info"]["version"], fixture["info"]["version"])
        self.assertEqual({tag["name"] for tag in schema["tags"]}, set(fixture["tags"]))
        self.assertEqual(set(schema["paths"]), set(fixture["paths"]))
        for path, expected_methods in fixture["paths"].items():
            with self.subTest(path=path):
                self.assertEqual(
                    sorted(schema["paths"][path]),
                    expected_methods,
                )

    def test_api_jobs_uses_no_filesystem_or_infrastructure_dependencies(self) -> None:
        source = Path("api/jobs.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".")[0])

        forbidden = {
            "pathlib",
            "sqlite3",
            "redis",
            "celery",
            "rq",
            "streamlit",
            "tkinter",
            "plotly",
            "category_tracking",
            "category_tracking_web",
        }
        self.assertFalse(forbidden.intersection(imported_roots))
        self.assertNotIn("open(", source)
        self.assertNotIn("write_text", source)
        self.assertNotIn("write_bytes", source)

    def test_job_runner_default_worker_count_is_one(self) -> None:
        runner = JobRunner(JobStore())

        self.assertEqual(DEFAULT_WORKER_COUNT, 1)
        self.assertEqual(runner.worker_count, DEFAULT_WORKER_COUNT)


if __name__ == "__main__":
    unittest.main()
