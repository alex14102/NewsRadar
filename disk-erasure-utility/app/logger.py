"""Logger: structured JSON-lines logging for every operation, error and
command executed by the application."""

import json
import os
import sys
import threading
import uuid
from datetime import datetime, timezone

from rich.console import Console


class JsonLogger:
    """Writes one JSON object per line to a log file, and mirrors
    human-readable messages to the console via Rich."""

    LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}

    def __init__(self, log_path, level="INFO", console=None):
        self.log_path = log_path
        self.level = level.upper()
        self.console = console or Console()
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(self.log_path) or ".", exist_ok=True)
        if not os.path.exists(self.log_path):
            open(self.log_path, "a", encoding="utf-8").close()

    def _should_emit(self, level):
        return self.LEVELS.get(level, 0) >= self.LEVELS.get(self.level, 0)

    def _write(self, record):
        with self._lock:
            with open(self.log_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _emit(self, level, event, message, **extra):
        record = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "event": event,
            "message": message,
        }
        if extra:
            record["data"] = extra
        self._write(record)
        if self._should_emit(level):
            self._print(level, event, message)
        return record

    def _print(self, level, event, message):
        colors = {
            "DEBUG": "dim",
            "INFO": "cyan",
            "WARNING": "yellow",
            "ERROR": "bold red",
            "CRITICAL": "bold white on red",
        }
        color = colors.get(level, "white")
        self.console.print(f"[{color}][{level}][/{color}] {event}: {message}")

    def debug(self, event, message, **extra):
        return self._emit("DEBUG", event, message, **extra)

    def info(self, event, message, **extra):
        return self._emit("INFO", event, message, **extra)

    def warning(self, event, message, **extra):
        return self._emit("WARNING", event, message, **extra)

    def error(self, event, message, **extra):
        return self._emit("ERROR", event, message, **extra)

    def critical(self, event, message, **extra):
        return self._emit("CRITICAL", event, message, **extra)

    def command(self, argv, returncode=None, duration_sec=None, **extra):
        """Logs every external command executed by the tool."""
        return self._emit(
            "INFO",
            "command",
            " ".join(argv) if isinstance(argv, (list, tuple)) else str(argv),
            argv=list(argv) if isinstance(argv, (list, tuple)) else [str(argv)],
            returncode=returncode,
            duration_sec=duration_sec,
            **extra,
        )

    def operation(self, name, status, **extra):
        """Logs a high level operation (scan, erase, report, ...)."""
        level = "ERROR" if status == "failed" else "INFO"
        return self._emit(level, "operation", f"{name}: {status}", operation=name, status=status, **extra)

    def exception(self, event, exc):
        return self._emit("ERROR", event, str(exc), exception_type=type(exc).__name__)

    def tail(self, n=50):
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
        out = []
        for line in lines[-n:]:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out
