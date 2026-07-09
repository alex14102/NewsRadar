"""Monitor: tracks progress of one or more concurrent erase jobs and
renders a live-updating Rich dashboard (progress bars, speed, ETA, and
periodic SMART temperature polling)."""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

from rich.live import Live
from rich.table import Table

from .disk_scanner import human_size


@dataclass
class JobState:
    device: str
    method: str
    bytes_written: int = 0
    bytes_total: int = 0
    pass_index: int = 1
    total_passes: int = 1
    status: str = "running"
    started_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    last_bytes: int = 0
    speed_bps: float = 0.0
    temperature_c: Optional[int] = None


class Monitor:
    def __init__(self, settings, smart_manager=None):
        self.settings = settings
        self.smart_manager = smart_manager
        self._jobs: Dict[str, JobState] = {}
        self._lock = threading.Lock()
        self._smart_stop = threading.Event()
        self._smart_thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    def register_job(self, device: str, method: str, total_passes: int = 1):
        with self._lock:
            self._jobs[device] = JobState(device=device, method=method, total_passes=total_passes)

    def progress_callback(self, device, bytes_written, bytes_total, pass_index, total_passes):
        with self._lock:
            job = self._jobs.get(device)
            if job is None:
                job = JobState(device=device, method="?", total_passes=total_passes)
                self._jobs[device] = job
            now = time.time()
            elapsed = now - job.last_update
            if elapsed > 0.2:
                delta_bytes = bytes_written - job.last_bytes
                instantaneous = delta_bytes / elapsed if elapsed > 0 else 0
                job.speed_bps = (job.speed_bps * 0.6) + (instantaneous * 0.4)
                job.last_update = now
                job.last_bytes = bytes_written
            job.bytes_written = bytes_written
            job.bytes_total = bytes_total
            job.pass_index = pass_index
            job.total_passes = total_passes

    def finish_job(self, device: str, status: str):
        with self._lock:
            job = self._jobs.get(device)
            if job:
                job.status = status

    def snapshot(self):
        with self._lock:
            return {k: JobState(**vars(v)) for k, v in self._jobs.items()}

    # ------------------------------------------------------------------
    def start_smart_polling(self, devices):
        if not self.smart_manager:
            return
        self._smart_stop.clear()

        def poll():
            while not self._smart_stop.is_set():
                for device in devices:
                    report = self.smart_manager.get_smart_data(device)
                    with self._lock:
                        job = self._jobs.get(device)
                        if job and report.available:
                            job.temperature_c = report.temperature_c
                self._smart_stop.wait(self.settings.smart_poll_seconds)

        self._smart_thread = threading.Thread(target=poll, daemon=True)
        self._smart_thread.start()

    def stop_smart_polling(self):
        self._smart_stop.set()
        if self._smart_thread:
            self._smart_thread.join(timeout=2)

    # ------------------------------------------------------------------
    def render_table(self) -> Table:
        table = Table(title="Postep operacji wymazywania", expand=True)
        table.add_column("Urzadzenie")
        table.add_column("Metoda")
        table.add_column("Przebieg")
        table.add_column("Postep")
        table.add_column("Predkosc")
        table.add_column("ETA")
        table.add_column("Temp.")
        table.add_column("Status")

        for job in self.snapshot().values():
            pct = (job.bytes_written / job.bytes_total * 100) if job.bytes_total else 0.0
            remaining_bytes = max(0, job.bytes_total - job.bytes_written)
            eta = remaining_bytes / job.speed_bps if job.speed_bps > 1 else None
            eta_text = f"{eta:6.0f}s" if eta is not None else "--"
            temp_text = f"{job.temperature_c}C" if job.temperature_c is not None else "--"
            status_style = {
                "running": "cyan",
                "success": "bold green",
                "failed": "bold red",
                "interrupted": "bold yellow",
                "blocked": "bold red",
            }.get(job.status, "white")
            table.add_row(
                job.device,
                job.method,
                f"{job.pass_index}/{job.total_passes}",
                f"{pct:5.1f}% ({human_size(job.bytes_written)}/{human_size(job.bytes_total)})",
                f"{human_size(job.speed_bps)}/s",
                eta_text,
                temp_text,
                f"[{status_style}]{job.status}[/{status_style}]",
            )
        return table

    def live(self) -> Live:
        return Live(
            self.render_table(),
            refresh_per_second=self.settings.monitor_refresh_per_second,
            transient=False,
        )
