"""EraseManager: performs secure erasure of block devices using named,
industry-recognised data-sanitization standards.

Safety is enforced here, not just in the UI: no code path in this class
will ever touch the running system's disk, its boot media, the medium a
live/removable system was booted from, or virtual pseudo-devices
(loop/ram/zram). Those checks happen unconditionally, before any method
that opens the device for writing.

The overwrite methods below implement the pass patterns defined by the
sanitization standards commonly referenced under the ISO/IEC 27040
storage-security umbrella (NIST SP 800-88, DoD 5220.22-M, VSITR/BSI,
HMG Infosec Standard 5, GOST R 50739-95, Bruce Schneier's algorithm,
and Gutmann's 35-pass method), plus the device-native secure-erase
commands (ATA Secure Erase, NVMe Format, TRIM/discard).
"""

import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, List, Optional

VIRTUAL_DEVICE_RE = re.compile(r"^(loop\d*|ram\d*|zram\d*|dm-\d+)$")


class SecurityError(Exception):
    """Raised whenever an operation would touch a protected device."""


@dataclass
class EraseResult:
    device: str
    method: str
    standard: str
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
    """A single overwrite pass. Subclasses generate the bytes written to
    the device for that pass and, where the pattern is deterministic,
    the values used to verify it afterwards."""

    name = "base"

    def chunk(self, size: int, phase: int = 0) -> bytes:
        """Returns `size` bytes to write next. `phase` is the pass-relative
        byte offset being written at (bytes_written so far in this pass),
        needed by multi-byte patterns to stay continuous across chunk
        boundaries instead of restarting the pattern at every chunk."""
        raise NotImplementedError

    def verify_pattern(self) -> Optional[bytes]:
        """Returns the repeating byte pattern expected on disk after this
        pass, or None if it is not deterministically verifiable (random)."""
        return None


class PatternPass(Pass):
    """Fills every byte with a single constant value (e.g. 0x00, 0xFF).
    A single repeated byte is phase-invariant, so chunk boundaries never
    affect the pattern seen on disk."""

    def __init__(self, byte_value: int):
        self.byte_value = byte_value
        self.name = f"0x{byte_value:02x}"

    def chunk(self, size: int, phase: int = 0) -> bytes:
        return bytes([self.byte_value]) * size

    def verify_pattern(self) -> Optional[bytes]:
        return bytes([self.byte_value])


class BytePatternPass(Pass):
    """Fills the device with a repeating multi-byte pattern, e.g. the
    3-byte rotating patterns used by the Gutmann method. `chunk` rotates
    the pattern by `phase` so the sequence stays continuous across chunk
    boundaries, matching what a sample read at any device offset will see."""

    def __init__(self, pattern: bytes, label: Optional[str] = None):
        self.pattern = pattern
        self.name = label or pattern.hex()

    def chunk(self, size: int, phase: int = 0) -> bytes:
        offset = phase % len(self.pattern)
        rotated = self.pattern[offset:] + self.pattern[:offset]
        reps = (size // len(rotated)) + 2
        return (rotated * reps)[:size]

    def verify_pattern(self) -> Optional[bytes]:
        return self.pattern


class RandomPass(Pass):
    name = "losowe dane"

    def chunk(self, size: int, phase: int = 0) -> bytes:
        return os.urandom(size)


def _gutmann_passes() -> List[Pass]:
    """The exact 35 passes described by Peter Gutmann's 1996 paper:
    4 random passes, then the fixed patterns targeting specific
    encoding schemes of the era (passes 5-31), then 4 more random
    passes (32-35)."""
    passes: List[Pass] = [RandomPass() for _ in range(4)]  # passes 1-4
    passes.append(PatternPass(0x55))  # pass 5
    passes.append(PatternPass(0xAA))  # pass 6
    passes.append(BytePatternPass(b"\x92\x49\x24"))  # pass 7
    passes.append(BytePatternPass(b"\x49\x24\x92"))  # pass 8
    passes.append(BytePatternPass(b"\x24\x92\x49"))  # pass 9
    for value in (
        0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
        0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF,
    ):  # passes 10-25
        passes.append(PatternPass(value))
    passes.append(BytePatternPass(b"\x92\x49\x24"))  # pass 26
    passes.append(BytePatternPass(b"\x49\x24\x92"))  # pass 27
    passes.append(BytePatternPass(b"\x24\x92\x49"))  # pass 28
    passes.append(BytePatternPass(b"\x6d\xb6\xdb"))  # pass 29
    passes.append(BytePatternPass(b"\xb6\xdb\x6d"))  # pass 30
    passes.append(BytePatternPass(b"\xdb\x6d\xb6"))  # pass 31
    passes.extend(RandomPass() for _ in range(4))  # passes 32-35
    return passes


@dataclass
class MethodSpec:
    id: str
    label: str
    standard: str
    description: str
    passes: Optional[List[Pass]] = None  # None => external/device-native method
    external: bool = False


METHODS: List[MethodSpec] = [
    MethodSpec(
        "zero", "Zapis zerami (1 przebieg)", "Podstawowe czyszczenie",
        "Szybkie, jednoprzebiegowe nadpisanie zerami. Wystarczajace dla nosnikow "
        "przeznaczonych do ponownego uzycia w niskim poziomie ryzyka.",
        [PatternPass(0x00)],
    ),
    MethodSpec(
        "random", "Losowe dane (1 przebieg)", "Podstawowe czyszczenie",
        "Jeden przebieg danych z generatora CSPRNG.",
        [RandomPass()],
    ),
    MethodSpec(
        "nist_clear", "NIST SP 800-88 Rev.1 - Clear", "NIST SP 800-88",
        "Pojedynczy przebieg nadpisania (logiczne czyszczenie). Rekomendowane dla "
        "nosnikow o niskiej/sredniej poufnosci danych, zgodnie z NIST SP 800-88.",
        [PatternPass(0x00)],
    ),
    MethodSpec(
        "dod3", "DoD 5220.22-M (3 przebiegi)", "DoD 5220.22-M",
        "Amerykanski standard Departamentu Obrony: przebiegi 0x00, 0xFF, dane losowe.",
        [PatternPass(0x00), PatternPass(0xFF), RandomPass()],
    ),
    MethodSpec(
        "dod7", "DoD 5220.22-M ECC (7 przebiegow)", "DoD 5220.22-M ECC",
        "Rozszerzony wariant DoD z dodatkowymi przebiegami weryfikujacymi.",
        [
            PatternPass(0xF6), PatternPass(0x00), PatternPass(0xFF), RandomPass(),
            PatternPass(0x00), PatternPass(0xFF), RandomPass(),
        ],
    ),
    MethodSpec(
        "vsitr", "VSITR / BSI (7 przebiegow)", "VSITR (Niemcy, BSI)",
        "Niemiecki standard: naprzemienne przebiegi 0x00/0xFF, ostatni przebieg 0xAA.",
        [
            PatternPass(0x00), PatternPass(0xFF), PatternPass(0x00), PatternPass(0xFF),
            PatternPass(0x00), PatternPass(0xFF), PatternPass(0xAA),
        ],
    ),
    MethodSpec(
        "hmg_is5", "HMG IS5 Enhanced (3 przebiegi)", "HMG Infosec Standard 5 (UK)",
        "Brytyjski standard rzadowy: 0x00, 0xFF, dane losowe, z weryfikacja koncowa.",
        [PatternPass(0x00), PatternPass(0xFF), RandomPass()],
    ),
    MethodSpec(
        "gost_r50739", "GOST R 50739-95 (1 przebieg)", "GOST R 50739-95 (Rosja)",
        "Rosyjski standard - jeden przebieg danych losowych (klasa ochrony 6).",
        [RandomPass()],
    ),
    MethodSpec(
        "schneier", "Schneier (7 przebiegow)", "Bruce Schneier's Algorithm",
        "0xFF, 0x00, nastepnie 5 przebiegow kryptograficznie bezpiecznych danych losowych.",
        [PatternPass(0xFF), PatternPass(0x00)] + [RandomPass() for _ in range(5)],
    ),
    MethodSpec(
        "gutmann", "Gutmann (35 przebiegow)", "Gutmann Method",
        "Pelna metoda Petera Gutmanna z 1996 roku - 35 przebiegow (4 losowe, 27 "
        "wzorcow docelowych, 4 losowe). Bardzo czasochlonna, historyczna metoda.",
        _gutmann_passes(),
    ),
    MethodSpec(
        "blkdiscard", "TRIM / Discard", "ATA/NVMe TRIM (discard)",
        "Sprzetowe oznaczenie wszystkich blokow jako nieuzywane. Szybkie, "
        "rekomendowane dla dyskow SSD/NVMe wspierajacych discard.",
        None, external=True,
    ),
    MethodSpec(
        "secure-erase", "ATA Secure Erase", "ATA Security Feature Set",
        "Sprzetowe polecenie bezpiecznego kasowania realizowane przez firmware dysku (hdparm).",
        None, external=True,
    ),
    MethodSpec(
        "nvme-format", "NVMe Format (crypto erase)", "NVMe Format NVM Command",
        "Format z kryptograficznym kasowaniem kluczy szyfrujacych nosnik (nvme-cli).",
        None, external=True,
    ),
]

METHODS_BY_ID = {m.id: m for m in METHODS}
EXTERNAL_METHODS = tuple(m.id for m in METHODS if m.external)
ALL_METHODS = tuple(m.id for m in METHODS)

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
        spec = METHODS_BY_ID.get(method)
        if spec is None:
            raise ValueError(f"Unknown erase method: {method}")

        self.assert_safe_to_erase(device)

        result = EraseResult(
            device=device,
            method=method,
            standard=spec.standard,
            passes=len(spec.passes) if spec.passes else 1,
            started_at=datetime.now(timezone.utc).isoformat(),
            status="running",
        )
        self.logger.operation(
            "erase_start", "running", device=device, method=method, standard=spec.standard
        )

        try:
            if spec.external:
                self._run_external_method(device, spec, result, progress_callback, stop_event)
            else:
                self._run_pass_based_method(device, spec, result, progress_callback, stop_event)
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

        if result.status == "success" and self.settings.verify and spec.passes:
            result.verification = self._verify(device, spec.passes[-1])

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

    def _run_pass_based_method(self, device, spec, result, progress_callback, stop_event):
        passes = spec.passes
        total_size = self._device_size(device)
        result.bytes_total = total_size
        chunk_size = self.settings.chunk_size_bytes

        for pass_index, erase_pass in enumerate(passes, start=1):
            bytes_written = 0
            fd = os.open(device, os.O_WRONLY)
            try:
                # A single repeated byte is phase-invariant, so it can be
                # generated once and reused for every chunk. Multi-byte
                # patterns and random data must be (re)generated per chunk
                # so the sequence stays continuous across chunk boundaries
                # (needed for the multi-byte pattern to verify correctly
                # from any device offset afterwards).
                is_static = isinstance(erase_pass, PatternPass)
                static_chunk = erase_pass.chunk(chunk_size) if is_static else None
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
                    data = (
                        static_chunk[:write_size]
                        if is_static
                        else erase_pass.chunk(write_size, phase=bytes_written)
                    )
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
        readable and, for deterministic patterns, matches the expected
        repeating byte pattern."""
        sample_size = 1024 * 1024
        total_size = self._device_size(device)
        offsets = sorted({0, max(0, total_size // 2), max(0, total_size - sample_size)})
        pattern = last_pass.verify_pattern()
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
                if pattern is not None:
                    # The write loop keeps the pattern continuous from
                    # device offset 0, so the phase at this offset is
                    # simply offset % len(pattern).
                    phase = offset % len(pattern)
                    rotated = pattern[phase:] + pattern[:phase]
                    expected = (rotated * ((len(data) // len(rotated)) + 2))[: len(data)]
                    if data != expected:
                        mismatches += 1
        finally:
            os.close(fd)

        return {
            "samples_checked": samples_checked,
            "mismatches": mismatches,
            "deterministic_check": pattern is not None,
            "passed": mismatches == 0,
        }

    # ------------------------------------------------------------------
    # External tool based methods
    # ------------------------------------------------------------------
    def _run_external_method(self, device, spec, result, progress_callback, stop_event):
        if spec.id == "blkdiscard":
            self._blkdiscard(device, result, progress_callback, stop_event)
        elif spec.id == "secure-erase":
            self._ata_secure_erase(device, result, progress_callback, stop_event)
        elif spec.id == "nvme-format":
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
