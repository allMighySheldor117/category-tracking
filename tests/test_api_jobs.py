"""Phase 5 background job store contract tests."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from uuid import UUID

from api.jobs import (
    DEFAULT_JOB_TTL,
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_MAX_RETAINED_JOBS,
    DEFAULT_QUEUE_CAPACITY,
    JobStatus,
    JobStore,
)


class JobStoreContractTests(unittest.TestCase):
    def test_created_job_has_contract_metadata_and_uuid4_id(self) -> None:
        store = JobStore()

        job = store.create_job(
            job_type="exact",
            scientific_authority="exact_probability",
            request_payload={"n_generations": 1},
            work=lambda: {"ok": True},
        )

        parsed = UUID(job.job_id)
        self.assertEqual(parsed.version, 4)
        self.assertEqual(job.job_type, "exact")
        self.assertEqual(job.status, JobStatus.QUEUED)
        self.assertEqual(job.progress, 0.0)
        self.assertEqual(job.attempt, 1)
        self.assertEqual(job.max_attempts, DEFAULT_MAX_ATTEMPTS)
        self.assertTrue(job.cancel_supported)
        self.assertFalse(job.retry_supported)
        self.assertIsNone(job.started_at)
        self.assertIsNone(job.completed_at)
        self.assertIsNone(job.expires_at)

        payload = job.to_metadata()
        self.assertEqual(
            list(payload),
            [
                "job_id",
                "job_type",
                "status",
                "created_at",
                "started_at",
                "completed_at",
                "updated_at",
                "progress",
                "attempt",
                "max_attempts",
                "expires_at",
                "cancel_supported",
                "retry_supported",
            ],
        )
        self.assertEqual(payload["status"], "queued")
        self.assertTrue(payload["created_at"].endswith("Z"))

    def test_store_enforces_queue_capacity_without_unbounded_growth(self) -> None:
        store = JobStore(queue_capacity=2)
        for index in range(2):
            store.create_job(
                job_type="exact",
                scientific_authority="exact_probability",
                request_payload={"index": index},
                work=lambda: {"ok": True},
            )

        with self.assertRaisesRegex(RuntimeError, "Job queue is full"):
            store.create_job(
                job_type="exact",
                scientific_authority="exact_probability",
                request_payload={"index": 3},
                work=lambda: {"ok": True},
            )

        self.assertEqual(store.queued_count, 2)

    def test_store_expires_terminal_jobs_and_bounds_retention(self) -> None:
        now = datetime(2026, 8, 13, tzinfo=timezone.utc)
        store = JobStore(max_retained_jobs=2, ttl=timedelta(seconds=1), clock=lambda: now)
        jobs = [
            store.create_job(
                job_type="exact",
                scientific_authority="exact_probability",
                request_payload={"index": index},
                work=lambda: {"ok": True},
            )
            for index in range(3)
        ]

        for job in jobs:
            store.mark_running(job.job_id)
            store.mark_completed(job.job_id, {"result": job.job_id})

        self.assertLessEqual(len(store.snapshot()), 2)

        later = now + timedelta(seconds=5)
        store.clock = lambda: later
        store.cleanup()

        for job in jobs:
            self.assertIsNone(store.get_job(job.job_id))


if __name__ == "__main__":
    unittest.main()
