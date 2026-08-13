"""In-process Phase 5 background job provider."""

from __future__ import annotations

from collections import OrderedDict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from threading import Lock, Thread
from typing import Any
from uuid import uuid4


DEFAULT_WORKER_COUNT = 1
DEFAULT_QUEUE_CAPACITY = 20
DEFAULT_MAX_RETAINED_JOBS = 100
DEFAULT_JOB_TTL = timedelta(minutes=30)
DEFAULT_MAX_ATTEMPTS = 2


class JobStatus(StrEnum):
    """Approved Phase 5 job statuses."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCEL_REQUESTED = "cancel_requested"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


def utc_now() -> datetime:
    """Return the current UTC timestamp."""

    return datetime.now(timezone.utc)


def timestamp(value: datetime | None) -> str | None:
    """Serialize UTC datetimes with a stable trailing Z."""

    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class JobRecord:
    """A bounded in-process job record."""

    job_id: str
    job_type: str
    scientific_authority: str
    request_payload: dict[str, Any]
    work: Callable[[], dict[str, Any]]
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    progress: float = 0.0
    attempt: int = 1
    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    expires_at: datetime | None = None
    cancel_supported: bool = True
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None

    @property
    def retry_supported(self) -> bool:
        """Return whether this retained job can be retried."""

        return (
            self.status in {JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.EXPIRED}
            and self.attempt < self.max_attempts
        )

    def to_metadata(self) -> dict[str, Any]:
        """Return the approved job metadata object in contract order."""

        return {
            "job_id": self.job_id,
            "job_type": self.job_type,
            "status": self.status.value,
            "created_at": timestamp(self.created_at),
            "started_at": timestamp(self.started_at),
            "completed_at": timestamp(self.completed_at),
            "updated_at": timestamp(self.updated_at),
            "progress": float(self.progress),
            "attempt": int(self.attempt),
            "max_attempts": int(self.max_attempts),
            "expires_at": timestamp(self.expires_at),
            "cancel_supported": bool(self.cancel_supported),
            "retry_supported": bool(self.retry_supported),
        }


@dataclass
class JobStore:
    """Bounded process-memory job store."""

    queue_capacity: int = DEFAULT_QUEUE_CAPACITY
    max_retained_jobs: int = DEFAULT_MAX_RETAINED_JOBS
    ttl: timedelta = DEFAULT_JOB_TTL
    clock: Callable[[], datetime] = utc_now
    _jobs: OrderedDict[str, JobRecord] = field(default_factory=OrderedDict)
    _queue: deque[str] = field(default_factory=deque)
    _lock: Lock = field(default_factory=Lock)

    @property
    def queued_count(self) -> int:
        """Return current queued job count."""

        with self._lock:
            return len(self._queue)

    def snapshot(self) -> list[JobRecord]:
        """Return retained jobs in insertion order."""

        with self._lock:
            return list(self._jobs.values())

    def get_job(self, job_id: str) -> JobRecord | None:
        """Return a retained job, or None."""

        with self._lock:
            return self._jobs.get(job_id)

    def create_job(
        self,
        *,
        job_type: str,
        scientific_authority: str,
        request_payload: dict[str, Any],
        work: Callable[[], dict[str, Any]],
    ) -> JobRecord:
        """Create a queued job with a server-generated UUID4 ID."""

        with self._lock:
            self._cleanup_locked()
            if len(self._queue) >= self.queue_capacity:
                raise RuntimeError("Job queue is full")
            now = self.clock()
            job = JobRecord(
                job_id=str(uuid4()),
                job_type=job_type,
                scientific_authority=scientific_authority,
                request_payload=dict(request_payload),
                work=work,
                status=JobStatus.QUEUED,
                created_at=now,
                updated_at=now,
            )
            self._jobs[job.job_id] = job
            self._queue.append(job.job_id)
            self._enforce_retention_locked()
            return job

    def pop_next_queued(self) -> JobRecord | None:
        """Pop the next queued job for a worker."""

        with self._lock:
            while self._queue:
                job_id = self._queue.popleft()
                job = self._jobs.get(job_id)
                if job is not None and job.status == JobStatus.QUEUED:
                    return job
            return None

    def mark_running(self, job_id: str) -> JobRecord:
        """Mark a queued job running."""

        with self._lock:
            job = self._require_job_locked(job_id)
            now = self.clock()
            job.status = JobStatus.RUNNING
            job.started_at = now
            job.updated_at = now
            job.progress = 0.1
            return job

    def mark_completed(self, job_id: str, result: dict[str, Any]) -> JobRecord:
        """Mark a job completed and retain its result."""

        with self._lock:
            job = self._require_job_locked(job_id)
            now = self.clock()
            job.status = JobStatus.COMPLETED
            job.completed_at = now
            job.updated_at = now
            job.progress = 1.0
            job.result = result
            job.error = None
            job.expires_at = now + self.ttl
            self._enforce_retention_locked()
            return job

    def mark_failed(self, job_id: str, error: dict[str, Any]) -> JobRecord:
        """Mark a job failed and retain concise error information."""

        with self._lock:
            job = self._require_job_locked(job_id)
            now = self.clock()
            job.status = JobStatus.FAILED
            job.completed_at = now
            job.updated_at = now
            job.error = dict(error)
            job.expires_at = now + self.ttl
            self._enforce_retention_locked()
            return job

    def request_cancel(self, job_id: str) -> JobRecord:
        """Request cancellation using approved best-effort semantics."""

        with self._lock:
            job = self._require_job_locked(job_id)
            now = self.clock()
            if job.status == JobStatus.QUEUED:
                job.status = JobStatus.CANCELLED
                job.completed_at = now
                job.expires_at = now + self.ttl
            elif job.status == JobStatus.RUNNING:
                job.status = JobStatus.CANCEL_REQUESTED
            job.updated_at = now
            return job

    def mark_cancelled(self, job_id: str) -> JobRecord:
        """Mark a job cancelled after a safe checkpoint."""

        with self._lock:
            job = self._require_job_locked(job_id)
            now = self.clock()
            job.status = JobStatus.CANCELLED
            job.completed_at = now
            job.updated_at = now
            job.expires_at = now + self.ttl
            return job

    def retry(self, job_id: str) -> JobRecord:
        """Retry a retained failed, cancelled, or expired job."""

        with self._lock:
            job = self._require_job_locked(job_id)
            if not job.retry_supported:
                raise RuntimeError("Job cannot be retried")
            if len(self._queue) >= self.queue_capacity:
                raise RuntimeError("Job queue is full")
            now = self.clock()
            job.status = JobStatus.QUEUED
            job.attempt += 1
            job.updated_at = now
            job.started_at = None
            job.completed_at = None
            job.expires_at = None
            job.progress = 0.0
            job.result = None
            self._queue.append(job.job_id)
            return job

    def cleanup(self) -> None:
        """Expire retained terminal jobs."""

        with self._lock:
            self._cleanup_locked()

    def remove(self, job_id: str) -> JobRecord:
        """Remove a retained job from process memory."""

        with self._lock:
            job = self._require_job_locked(job_id)
            self._jobs.pop(job_id, None)
            self._queue = deque(queued_id for queued_id in self._queue if queued_id != job_id)
            return job

    def _cleanup_locked(self) -> None:
        now = self.clock()
        expired = [
            job_id
            for job_id, job in self._jobs.items()
            if job.expires_at is not None and job.expires_at <= now
        ]
        for job_id in expired:
            self._jobs.pop(job_id, None)
        self._queue = deque(job_id for job_id in self._queue if job_id in self._jobs)

    def _enforce_retention_locked(self) -> None:
        while len(self._jobs) > self.max_retained_jobs:
            for job_id, job in list(self._jobs.items()):
                if job.status in {
                    JobStatus.COMPLETED,
                    JobStatus.FAILED,
                    JobStatus.CANCELLED,
                    JobStatus.EXPIRED,
                }:
                    self._jobs.pop(job_id, None)
                    break
            else:
                break

    def _require_job_locked(self, job_id: str) -> JobRecord:
        job = self._jobs.get(job_id)
        if job is None:
            raise KeyError("Job not found")
        return job


class JobRunner:
    """Single-worker in-process runner."""

    def __init__(self, store: JobStore, worker_count: int = DEFAULT_WORKER_COUNT) -> None:
        if worker_count < 1:
            raise ValueError("worker_count must be at least 1")
        self.store = store
        self.worker_count = worker_count
        self._workers: list[Thread] = []
        self._worker_lock = Lock()

    def run_available(self) -> None:
        """Run queued jobs synchronously until the queue is empty."""

        while True:
            job = self.store.pop_next_queued()
            if job is None:
                return
            self.store.mark_running(job.job_id)
            try:
                result = job.work()
            except Exception as exc:  # noqa: BLE001 - boundary converts to concise stored error.
                self.store.mark_failed(
                    job.job_id,
                    {
                        "code": "internal_job_error",
                        "message": "Job failed unexpectedly.",
                        "details": {"type": type(exc).__name__},
                    },
                )
            else:
                current = self.store.get_job(job.job_id)
                if current is not None and current.status == JobStatus.CANCEL_REQUESTED:
                    self.store.mark_cancelled(job.job_id)
                else:
                    self.store.mark_completed(job.job_id, result)

    def start_available(self) -> None:
        """Start daemon workers for queued jobs up to the configured limit."""

        with self._worker_lock:
            self._workers = [worker for worker in self._workers if worker.is_alive()]
            if len(self._workers) >= self.worker_count:
                return
            worker = Thread(target=self.run_available, daemon=True)
            self._workers.append(worker)
            worker.start()


default_store = JobStore()
default_runner = JobRunner(default_store)
