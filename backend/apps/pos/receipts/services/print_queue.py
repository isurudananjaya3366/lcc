"""
Print job queue and retry logic.

Task 51: Print job queue with priority.
Task 52: Retry with exponential backoff.
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum

from apps.pos.receipts.services.print_connectivity import (
    NetworkPrinter,
    PrinterConnectionError,
    USBPrinterStub,
)

logger = logging.getLogger(__name__)


class PrintPriority(IntEnum):
    HIGH = 1
    NORMAL = 5
    LOW = 10


class PrintJobStatus:
    PENDING = "pending"
    PRINTING = "printing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class PrintJob:
    """An individual print job."""

    job_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    receipt_id: str | None = None
    data: bytes = b""
    priority: int = PrintPriority.NORMAL
    copies: int = 1
    status: str = PrintJobStatus.PENDING
    attempts: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    error: str | None = None

    # Printer config
    printer_host: str | None = None
    printer_port: int = 9100
    printer_type: str = "network"  # network | usb

    def __lt__(self, other):
        """Lower priority value = higher priority in queue."""
        return self.priority < other.priority


class PrintQueue:
    """
    In-memory print-job queue with priority ordering and retry.

    For production, jobs would be persisted to database or Redis
    and processed by Celery workers. This provides the core logic.

    Usage::

        queue = PrintQueue()
        queue.enqueue(PrintJob(data=raw_bytes, printer_host="192.168.1.100"))
        results = queue.process_all()
    """

    BASE_DELAY = 2  # seconds
    MAX_DELAY = 60  # seconds

    def __init__(self):
        self._jobs: list[PrintJob] = []

    @property
    def size(self) -> int:
        return len(self._jobs)

    def enqueue(self, job: PrintJob) -> str:
        self._jobs.append(job)
        self._jobs.sort()  # By priority
        logger.info("Enqueued print job %s (priority=%d)", job.job_id, job.priority)
        return job.job_id

    def dequeue(self) -> PrintJob | None:
        pending = [j for j in self._jobs if j.status == PrintJobStatus.PENDING]
        if not pending:
            return None
        job = pending[0]
        return job

    def cancel(self, job_id: str) -> bool:
        for job in self._jobs:
            if job.job_id == job_id and job.status == PrintJobStatus.PENDING:
                job.status = PrintJobStatus.CANCELLED
                return True
        return False

    def get_job(self, job_id: str) -> PrintJob | None:
        for job in self._jobs:
            if job.job_id == job_id:
                return job
        return None

    # ── Processing ────────────────────────────────────────

    def process_next(self) -> PrintJob | None:
        job = self.dequeue()
        if not job:
            return None
        self._execute_job(job)
        return job

    def process_all(self) -> list[PrintJob]:
        processed = []
        while True:
            job = self.process_next()
            if not job:
                break
            processed.append(job)
        return processed

    def _execute_job(self, job: PrintJob):
        job.status = PrintJobStatus.PRINTING
        job.attempts += 1

        try:
            printer = self._get_printer(job)
            for _ in range(job.copies):
                printer.send(job.data)
            job.status = PrintJobStatus.COMPLETED
            logger.info("Print job %s completed", job.job_id)
        except PrinterConnectionError as exc:
            job.error = str(exc)
            if job.attempts < job.max_retries:
                job.status = PrintJobStatus.RETRYING
                self._schedule_retry(job)
            else:
                job.status = PrintJobStatus.FAILED
                logger.error("Print job %s failed after %d attempts: %s",
                             job.job_id, job.attempts, exc)

    @staticmethod
    def _get_printer(job: PrintJob):
        if job.printer_type == "usb":
            return USBPrinterStub()
        return NetworkPrinter(
            host=job.printer_host or "127.0.0.1",
            port=job.printer_port,
        )

    # ── Task 52: Retry with exponential backoff ──────────

    def _schedule_retry(self, job: PrintJob):
        delay = min(
            self.BASE_DELAY * (2 ** (job.attempts - 1)),
            self.MAX_DELAY,
        )
        logger.info(
            "Retrying print job %s in %.1fs (attempt %d/%d)",
            job.job_id, delay, job.attempts, job.max_retries,
        )
        # In production this would be a Celery countdown task.
        # For synchronous usage we do a blocking delay.
        time.sleep(delay)
        job.status = PrintJobStatus.PENDING

    # ── Cleanup ───────────────────────────────────────────

    def clear_completed(self):
        self._jobs = [
            j for j in self._jobs
            if j.status not in (PrintJobStatus.COMPLETED, PrintJobStatus.CANCELLED)
        ]

    def get_summary(self) -> dict:
        return {
            "total": len(self._jobs),
            "pending": sum(1 for j in self._jobs if j.status == PrintJobStatus.PENDING),
            "completed": sum(1 for j in self._jobs if j.status == PrintJobStatus.COMPLETED),
            "failed": sum(1 for j in self._jobs if j.status == PrintJobStatus.FAILED),
            "retrying": sum(1 for j in self._jobs if j.status == PrintJobStatus.RETRYING),
        }
