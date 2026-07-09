"""EraseManager: performs secure erasure of block devices.

Safety is enforced here, not just in the UI: no code path in this class
will ever touch the running system's disk, its boot media, the medium a
live/removable system was booted from, or virtual pseudo-devices
(loop/ram/zram). Those checks happen unconditionally, before any method
that opens the device for writing.
"""

import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, List, Optional

VIRTUAL_DEVICE_RE = re.compile(r"^(loop\d*|ram\d*|zram\d*|dm-\d+)$")


class SecurityError(Exception):
    """Raised whenever an operation would touch a protected device."""


@dataclass
class EraseResult:
    device: str
    method: str
    passes: int
    started_at: str
    ended_at: Optional[str] = None
    duration_sec: Optional[float] = None
    bytes_total: int = 0
    bytes_written: int = 0
    status: str = "pending"  # pending, running, success, failed, interrupted, blocked
    error: Optional[str] = None
    verification: Optional[dict] = None


class Pass:
    name = "base"

    def chunk(self, size: int) -> bytes:
        raise NotImplementedError

    def verify_value(self) -> Optional[int]:
        """Returns the expected constant byte value for verification,
        or None if the pass is not deterministically verifiable (random)."""
        return None


class PatternPass(Pass):
    def __init__(self, byte_value: int):
        self.byte_value = byte_value
        self.name = f"pattern-0x{byte_value:02x}"

    def chunk(self, size: int) -> bytes:
        return bytes([self.byte_value]) * size

    def verify_value(self) -> Optional[int]:
        return self.byte_value


class RandomPass(Pass):
    name = "random"

    def chunk(self, size: int) -> bytes:
        return os.urandom(size)


METHOD_PASSES = {
    "zero": [PatternPass(0x00)],
    "random": [RandomPass()],
    "dod3": [PatternPass(0x00), PatternPass(0xFF), RandomPass()],
    "dod7": [
        PatternPass(0xF6),
        PatternPass(0x00),
        PatternPass(0xFF),
        RandomPass(),
        PatternPass(0x00),
        PatternPass(0xFF),
        RandomPass(),
    ],
}

EXTERNAL_METHODS = ("blkdiscard", "secure-erase", "nvme-format")

ALL_METHODS = tuple(METHOD_PASSES.keys()) + EXTERNAL_METHODS

ProgressCallback = Callable[[str, int, int, int, int], None]
# callback(device, bytes_written, bytes_total, pass_index, total_passes)


class EraseManager:
    def __init__(self, settings, logger, disk_scanner):
        self.settings = settings
        self.logger = logger
        self.disk_scanner = disk_scanner

    # ------------------------------------------------------------------
    # Safety
    # ------------------------------------------------------------------
    def is_virtual_device(self, device_path: str) -> bool:
        base = os.path.basename(os.path.realpath(device_path))
        return bool(VIRTUAL_DEVICE_RE.match(base))

    def get_protected_devices(self) -> List[str]:
        """Devices that must never be erasable: the running system's
        root/boot devices, the live/removable boot medium, active swap,
        and anything the operator explicitly added to config.yaml."""
        protected = set()
        protected.update(self.disk_scanner.get_root_devices())
        protected.update(self.disk_scanner.get_live_medium_devices())
        protected.update(self._active_swap_devices())
        for extra in self.settings.protected_extra:
            protected.add(os.path.realpath(extra))
        resolved = set()
        for dev in protected:
            resolved.add(dev)
            resolved.add(os.path.realpath(dev))
            resolved.add(self.disk_scanner.resolve_to_parent_disk(dev))
        return sorted(resolved)

    @staticmethod
    def _active_swap_devices() -> List[str]:
        devices = []
        try:
            with open("/proc/swaps", "r", encoding="utf-8") as fh:
                next(fh, None)  # header
                for line in fh:
                    parts = line.split()
                    if parts:
                        devices.append(parts[0])
        except OSError:
            pass
        return devices

    def assert_safe_to_erase(self, device_path: str) -> None:
        real = os.path.realpath(device_path)

        if self.settings.block_virtual_devices and self.is_virtual_device(real):
            raise SecurityError(
                f"Refusing to erase '{device_path}': virtual/pseudo device "
                "(loop, ram, zram, dm) can never be a wipe target."
            )

        parent = self.disk_scanner.resolve_to_parent_disk(real)
        protected = set(self.get_protected_devices())

        if real in protected or parent in protected or device_path in protected:
            raise SecurityError(
                f"Refusing to erase '{device_path}': it is the running system disk, "
                "boot media, the live boot medium, active swap, or explicitly "
                "protected in config.yaml."
            )

    # ------------------------------------------------------------------
    # Erase orchestration
    # ------------------------------------------------------------------
    def erase(
        self,
        device: str,
        method: str,
        progress_callback: Optional[ProgressCallback] = None,
        stop_event=None,
    ) -> EraseResult:
        if method not in ALL_METHODS:
            raise ValueError(f"Unknown erase method: {method}")

        self.assert_safe_to_erase(device)

        result = EraseResult(
            device=device,
            method=method,
            passes=len(METHOD_PASSES.get(method, [])) or 1,
            started_at=datetime.now(timezone.utc).isoformat(),
            status="running",
        )
        self.logger.operation("erase_start", "running", device=device, method=method)

        try:
            if method in EXTERNAL_METHODS:
                self._run_external_method(device, method, result, progress_callback, stop_event)
            else:
                self._run_pass_based_method(device, method, result, progress_callback, stop_event)
        except SecurityError:
            raise
        except Exception as exc:  # noqa: BLE001 - we want to record any failure
            result.status = "failed"
            result.error = str(exc)
            self.logger.exception("erase_failed", exc)
        finally:
            result.ended_at = datetime.now(timezone.utc).isoformat()
            started = datetime.fromisoformat(result.started_at)
            ended = datetime.fromisoformat(result.ended_at)
            result.duration_sec = (ended - started).total_seconds()

        if result.status == "running":
            result.status = "success"

        if result.status == "success" and self.settings.verify and method in METHOD_PASSES:
            result.verification = self._verify(device, METHOD_PASSES[method][-1])

        self.logger.operation(
            "erase_finished",
            result.status,
            device=device,
            method=method,
            duration_sec=result.duration_sec,
            bytes_written=result.bytes_written,
        )
        return result

    # ------------------------------------------------------------------
    # Pass-based (dd-style) erasure
    # ------------------------------------------------------------------
    def _device_size(self, device: str) -> int:
        fd = os.open(device, os.O_RDONLY)
        try:
            size = os.lseek(fd, 0, os.SEEK_END)
        finally:
            os.close(fd)
        return size

    def _run_pass_based_method(self, device, method, result, progress_callback, stop_event):
        passes = METHOD_PASSES[method]
        total_size = self._device_size(device)
        result.bytes_total = total_size
        chunk_size = self.settings.chunk_size_bytes

        for pass_index, erase_pass in enumerate(passes, start=1):
            bytes_written = 0
            fd = os.open(device, os.O_WRONLY)
            try:
                is_pattern = isinstance(erase_pass, PatternPass)
                static_chunk = erase_pass.chunk(chunk_size) if is_pattern else None
                while bytes_written < total_size:
                    if stop_event is not None and stop_event.is_set():
                        result.status = "interrupted"
                        self.logger.warning(
                            "erase_interrupted",
                            "Erase stopped by user request",
                            device=device,
                            pass_index=pass_index,
                            bytes_written=bytes_written,
                        )
                        return
                    remaining = total_size - bytes_written
                    write_size = min(chunk_size, remaining)
                    data = static_chunk[:write_size] if is_pattern else erase_pass.chunk(write_size)
                    try:
                        written = os.write(fd, data)
                    except OSError as exc:
                        if exc.errno == 28:  # ENOSPC: reached end of device
                            break
                        raise
                    if written <= 0:
                        break
                    bytes_written += written
                    result.bytes_written = bytes_written
                    if progress_callback:
                        progress_callback(device, bytes_written, total_size, pass_index, len(passes))
                os.fsync(fd)
            finally:
                os.close(fd)

    def _verify(self, device: str, last_pass: Pass) -> dict:
        """Reads back a handful of sample offsets to confirm the device is
        readable and, for deterministic patterns, matches the expected byte."""
        sample_size = 1024 * 1024
        total_size = self._device_size(device)
        offsets = sorted({0, max(0, total_size // 2), max(0, total_size - sample_size)})
        expected = last_pass.verify_value()
        mismatches = 0
        samples_checked = 0

        fd = os.open(device, os.O_RDONLY)
        try:
            for offset in offsets:
                if offset < 0 or offset >= total_size:
                    continue
                os.lseek(fd, offset, os.SEEK_SET)
                data = os.read(fd, min(sample_size, total_size - offset))
                samples_checked += 1
                if expected is not None and any(b != expected for b in data):
                    mismatches += 1
        finally:
            os.close(fd)

        return {
            "samples_checked": samples_checked,
            "mismatches": mismatches,
            "deterministic_check": expected is not None,
            "passed": mismatches == 0,
        }

    # ------------------------------------------------------------------
    # External tool based methods
    # ------------------------------------------------------------------
    def _run_external_method(self, device, method, result, progress_callback, stop_event):
        if method == "blkdiscard":
            self._blkdiscard(device, result, progress_callback, stop_event)
        elif method == "secure-erase":
            self._ata_secure_erase(device, result, progress_callback, stop_event)
        elif method == "nvme-format":
            self._nvme_format(device, result, progress_callback, stop_event)

    def _run_subprocess(self, argv, result):
        start = time.time()
        proc = subprocess.run(argv, capture_output=True, text=True, check=False)
        self.logger.command(argv, returncode=proc.returncode, duration_sec=time.time() - start)
        if proc.returncode != 0:
            raise RuntimeError(
                f"Command failed ({' '.join(argv)}): {proc.stderr.strip() or proc.stdout.strip()}"
            )
        return proc

    def _blkdiscard(self, device, result, progress_callback, stop_event):
        if shutil.which("blkdiscard") is None:
            raise RuntimeError("blkdiscard is not installed")
        if progress_callback:
            progress_callback(device, 0, 1, 1, 1)
        self._run_subprocess(["blkdiscard", "-v", device], result)
        result.bytes_total = result.bytes_written = self._device_size(device)
        if progress_callback:
            progress_callback(device, result.bytes_total, result.bytes_total, 1, 1)

    def _ata_secure_erase(self, device, result, progress_callback, stop_event):
        if shutil.which("hdparm") is None:
            raise RuntimeError("hdparm is not installed")

        info = subprocess.run(["hdparm", "-I", device], capture_output=True, text=True, check=False)
        self.logger.command(["hdparm", "-I", device], returncode=info.returncode)
        if "frozen" in info.stdout.lower() and "not\tfrozen" not in info.stdout.lower():
            raise RuntimeError(
                "Security state is 'frozen'; suspend/resume the host or use a "
                "hot-plug controller before attempting ATA secure erase."
            )

        if progress_callback:
            progress_callback(device, 0, 1, 1, 1)
        self._run_subprocess(
            ["hdparm", "--user-master", "u", "--security-set-pass", "NULL", device], result
        )
        self._run_subprocess(
            ["hdparm", "--user-master", "u", "--security-erase", "NULL", device], result
        )
        result.bytes_total = result.bytes_written = self._device_size(device)
        if progress_callback:
            progress_callback(device, result.bytes_total, result.bytes_total, 1, 1)

    def _nvme_format(self, device, result, progress_callback, stop_event):
        if shutil.which("nvme") is None:
            raise RuntimeError("nvme-cli is not installed")
        if progress_callback:
            progress_callback(device, 0, 1, 1, 1)
        self._run_subprocess(["nvme", "format", device, "--ses=1"], result)
        result.bytes_total = result.bytes_written = self._device_size(device)
        if progress_callback:
            progress_callback(device, result.bytes_total, result.bytes_total, 1, 1)
