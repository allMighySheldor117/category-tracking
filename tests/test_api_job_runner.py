"""Phase 5 background job runner lifecycle tests."""

from __future__ import annotations

import unittest
from threading import Event, Lock, current_thread
from time import sleep, time

from api.jobs import DEFAULT_WORKER_COUNT, JobRunner, JobStatus, JobStore


class JobRunnerLifecycleTests(unittest.TestCase):
    def test_runner_completes_queued_work_and_retains_result(self) -> None:
        store = JobStore()
        runner = JobRunner(store)
        job = store.create_job(
            job_type="exact",
            scientific_authority="exact_probability",
            request_payload={},
            work=lambda: {"data": {"ok": True}},
        )

        runner.run_available()

        updated = store.get_job(job.job_id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, JobStatus.COMPLETED)
        self.assertEqual(updated.progress, 1.0)
        self.assertEqual(updated.result, {"data": {"ok": True}})
        self.assertIsNone(updated.error)
        self.assertIsNotNone(updated.started_at)
        self.assertIsNotNone(updated.completed_at)
        self.assertIsNotNone(updated.expires_at)

    def test_runner_captures_failure_without_stack_trace(self) -> None:
        store = JobStore()
        runner = JobRunner(store)

        def fail() -> dict[str, object]:
            raise ValueError("sensitive internal detail")

        job = store.create_job(
            job_type="exact",
            scientific_authority="exact_probability",
            request_payload={},
            work=fail,
        )

        runner.run_available()

        updated = store.get_job(job.job_id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, JobStatus.FAILED)
        self.assertIsNone(updated.result)
        self.assertEqual(updated.error["code"], "internal_job_error")
        self.assertNotIn("sensitive internal detail", str(updated.error))
        self.assertTrue(updated.retry_supported)

    def test_running_cancel_request_becomes_cancelled_at_safe_boundary(self) -> None:
        store = JobStore()
        runner = JobRunner(store)
        job_id_holder: dict[str, str] = {}

        def work() -> dict[str, object]:
            store.request_cancel(job_id_holder["job_id"])
            return {"data": {"finished": True}}

        job = store.create_job(
            job_type="aggregated",
            scientific_authority="experimental_sampled",
            request_payload={},
            work=work,
        )
        job_id_holder["job_id"] = job.job_id

        runner.run_available()

        updated = store.get_job(job.job_id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, JobStatus.CANCELLED)
        self.assertIsNone(updated.result)
        self.assertTrue(updated.retry_supported)

    def test_start_available_enforces_default_single_worker(self) -> None:
        store = JobStore()
        runner = JobRunner(store)
        started_threads: list[str] = []
        started = Event()
        release = Event()
        lock = Lock()

        def slow_work() -> dict[str, object]:
            with lock:
                started_threads.append(current_thread().name)
            started.set()
            release.wait(timeout=2.0)
            return {"data": {"ok": True}}

        for _ in range(3):
            store.create_job(
                job_type="exact",
                scientific_authority="exact_probability",
                request_payload={},
                work=slow_work,
            )

        runner.start_available()
        self.assertTrue(started.wait(timeout=1.0))

        for _ in range(3):
            runner.start_available()

        sleep(0.05)
        with lock:
            self.assertEqual(len(started_threads), DEFAULT_WORKER_COUNT)

        release.set()
        deadline = time() + 2.0
        while time() < deadline:
            if all(job.status == JobStatus.COMPLETED for job in store.snapshot()):
                break
            sleep(0.01)

        self.assertTrue(all(job.status == JobStatus.COMPLETED for job in store.snapshot()))


if __name__ == "__main__":
    unittest.main()
