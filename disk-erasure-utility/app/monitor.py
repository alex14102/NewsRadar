"""Monitor: tracks progress of one or more concurrent erase jobs and
renders a live-updating Rich progress bar per device (pass number,
speed, ETA, temperature, status), plus periodic SMART temperature
polling in the background."""

import threading
import time
from typing import Dict, Optional

from rich.progress import (
    BarColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.text import Text

from .disk_scanner import human_size

STATUS_STYLES = {
    "running": "cyan",
    "success": "bold green",
    "failed": "bold red",
    "interrupted": "bold yellow",
    "blocked": "bold red",
}


class PassColumn(ProgressColumn):
    def render(self, task):
        pass_index = task.fields.get("pass_index", 1)
        total_passes = task.fields.get("total_passes", 1)
        return Text(f"przebieg {pass_index}/{total_passes}", style="magenta")


class SpeedColumn(ProgressColumn):
    def render(self, task):
        speed = task.fields.get("speed_bps", 0.0)
        return Text(f"{human_size(speed)}/s", style="cyan")


class TemperatureColumn(ProgressColumn):
    def render(self, task):
        temp = task.fields.get("temperature_c")
        text = f"{temp}C" if temp is not None else "--"
        style = "red" if isinstance(temp, (int, float)) and temp >= 55 else "yellow"
        return Text(text, style=style)


class StatusColumn(ProgressColumn):
    def render(self, task):
        status = task.fields.get("status", "running")
        return Text(status, style=STATUS_STYLES.get(status, "white"))


class Monitor:
    def __init__(self, settings, smart_manager=None):
        self.settings = settings
        self.smart_manager = smart_manager
        self._lock = threading.Lock()
        self._task_ids: Dict[str, int] = {}
        self._last_update: Dict[str, float] = {}
        self._last_bytes: Dict[str, int] = {}
        self._smart_stop = threading.Event()
        self._smart_thread: Optional[threading.Thread] = None

        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold]{task.fields[device]}[/bold]"),
            TextColumn("{task.fields[standard]}"),
            BarColumn(bar_width=30),
            TextColumn("[progress.percentage]{task.percentage:>5.1f}%"),
            PassColumn(),
            SpeedColumn(),
            TimeRemainingColumn(),
            TemperatureColumn(),
            StatusColumn(),
            transient=False,
            refresh_per_second=self.settings.monitor_refresh_per_second,
        )

    # ------------------------------------------------------------------
    def register_job(self, device: str, method: str, standard: str = "", total_passes: int = 1):
        with self._lock:
            task_id = self.progress.add_task(
                device,
                total=1,
                device=device,
                method=method,
                standard=standard,
                pass_index=1,
                total_passes=total_passes,
                speed_bps=0.0,
                temperature_c=None,
                status="running",
            )
            self._task_ids[device] = task_id
            self._last_update[device] = time.time()
            self._last_bytes[device] = 0

    def progress_callback(self, device, bytes_written, bytes_total, pass_index, total_passes):
        with self._lock:
            task_id = self._task_ids.get(device)
            if task_id is None:
                return
            now = time.time()
            elapsed = now - self._last_update.get(device, now)
            speed = None
            if elapsed > 0.2:
                delta_bytes = bytes_written - self._last_bytes.get(device, 0)
                instantaneous = delta_bytes / elapsed if elapsed > 0 else 0.0
                task = self.progress.tasks[task_id]
                previous_speed = task.fields.get("speed_bps", 0.0)
                speed = (previous_speed * 0.6) + (instantaneous * 0.4)
                self._last_update[device] = now
                self._last_bytes[device] = bytes_written

            update_kwargs = dict(
                completed=bytes_written,
                total=max(bytes_total, 1),
                pass_index=pass_index,
                total_passes=total_passes,
            )
            if speed is not None:
                update_kwargs["speed_bps"] = speed
            self.progress.update(task_id, **update_kwargs)

    def finish_job(self, device: str, status: str):
        with self._lock:
            task_id = self._task_ids.get(device)
            if task_id is None:
                return
            task = self.progress.tasks[task_id]
            update_kwargs = {"status": status}
            if status == "success":
                update_kwargs["completed"] = task.total
            self.progress.update(task_id, **update_kwargs)

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
                        task_id = self._task_ids.get(device)
                        if task_id is not None and report.available:
                            self.progress.update(task_id, temperature_c=report.temperature_c)
                self._smart_stop.wait(self.settings.smart_poll_seconds)

        self._smart_thread = threading.Thread(target=poll, daemon=True)
        self._smart_thread.start()

    def stop_smart_polling(self):
        self._smart_stop.set()
        if self._smart_thread:
            self._smart_thread.join(timeout=2)

    # ------------------------------------------------------------------
    def live(self):
        """Returns the underlying rich.progress.Progress instance, which
        is itself a context manager that starts/stops a Live display."""
        return self.progress

    def reset(self):
        with self._lock:
            for task_id in list(self._task_ids.values()):
                self.progress.remove_task(task_id)
            self._task_ids.clear()
            self._last_update.clear()
            self._last_bytes.clear()
