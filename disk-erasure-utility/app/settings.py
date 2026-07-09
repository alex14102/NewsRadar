"""Settings: loads and exposes configuration from config.yaml."""

import os
import copy
import threading

import yaml

DEFAULT_CONFIG = {
    "logging": {
        "level": "INFO",
        "path": "logs/app.jsonl",
    },
    "reports": {
        "path": "reports",
        "formats": ["json"],
    },
    "erase": {
        "default_method": "zero",
        "threads": 2,
        "chunk_size_mb": 4,
        "verify": True,
        "confirm_required": True,
    },
    "smart": {
        "enabled": True,
        "smartctl_path": "smartctl",
    },
    "crypto": {
        "enabled": True,
        "blkid_path": "blkid",
        "cryptsetup_path": "cryptsetup",
    },
    "safety": {
        "protected_extra": [],
        "block_virtual_devices": True,
    },
    "monitor": {
        "refresh_per_second": 4,
        "smart_poll_seconds": 5,
    },
}


class Settings:
    """Loads config.yaml (creating a default one if missing) and exposes
    typed accessors used across the application. Thread-safe for reads."""

    def __init__(self, config_path="config.yaml", base_dir=None):
        self._lock = threading.Lock()
        self.base_dir = base_dir or os.getcwd()
        self.config_path = (
            config_path
            if os.path.isabs(config_path)
            else os.path.join(self.base_dir, config_path)
        )
        self._data = {}
        self.load()

    def load(self):
        with self._lock:
            if not os.path.exists(self.config_path):
                self._data = copy.deepcopy(DEFAULT_CONFIG)
                self._write(self._data)
            else:
                with open(self.config_path, "r", encoding="utf-8") as fh:
                    loaded = yaml.safe_load(fh) or {}
                self._data = self._merge_defaults(loaded)
        return self._data

    def _merge_defaults(self, loaded):
        merged = copy.deepcopy(DEFAULT_CONFIG)
        for section, values in loaded.items():
            if isinstance(values, dict) and isinstance(merged.get(section), dict):
                merged[section].update(values)
            else:
                merged[section] = values
        return merged

    def _write(self, data):
        os.makedirs(os.path.dirname(self.config_path) or ".", exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True)

    def save(self):
        with self._lock:
            self._write(self._data)

    def get(self, dotted_key, default=None):
        node = self._data
        for part in dotted_key.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return node

    def set(self, dotted_key, value):
        with self._lock:
            parts = dotted_key.split(".")
            node = self._data
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = value

    def resolve_path(self, relative_or_absolute):
        if os.path.isabs(relative_or_absolute):
            return relative_or_absolute
        return os.path.join(self.base_dir, relative_or_absolute)

    @property
    def log_path(self):
        return self.resolve_path(self.get("logging.path", "logs/app.jsonl"))

    @property
    def log_level(self):
        return str(self.get("logging.level", "INFO")).upper()

    @property
    def reports_path(self):
        return self.resolve_path(self.get("reports.path", "reports"))

    @property
    def default_method(self):
        return self.get("erase.default_method", "zero")

    @property
    def threads(self):
        return int(self.get("erase.threads", 2))

    @property
    def chunk_size_bytes(self):
        return int(self.get("erase.chunk_size_mb", 4)) * 1024 * 1024

    @property
    def verify(self):
        return bool(self.get("erase.verify", True))

    @property
    def confirm_required(self):
        return bool(self.get("erase.confirm_required", True))

    @property
    def smartctl_path(self):
        return self.get("smart.smartctl_path", "smartctl")

    @property
    def blkid_path(self):
        return self.get("crypto.blkid_path", "blkid")

    @property
    def cryptsetup_path(self):
        return self.get("crypto.cryptsetup_path", "cryptsetup")

    @property
    def protected_extra(self):
        return list(self.get("safety.protected_extra", []) or [])

    @property
    def block_virtual_devices(self):
        return bool(self.get("safety.block_virtual_devices", True))

    @property
    def monitor_refresh_per_second(self):
        return float(self.get("monitor.refresh_per_second", 4))

    @property
    def smart_poll_seconds(self):
        return float(self.get("monitor.smart_poll_seconds", 5))
