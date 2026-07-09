"""DiskScanner: enumerates block devices on the system and identifies
which ones are safe to operate on."""

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional


VIRTUAL_DEVICE_PATTERNS = (
    re.compile(r"^loop\d*$"),
    re.compile(r"^ram\d*$"),
    re.compile(r"^zram\d*$"),
    re.compile(r"^dm-\d+$"),
)


@dataclass
class Partition:
    name: str
    path: str
    size: int
    fstype: Optional[str]
    mountpoints: List[str] = field(default_factory=list)
    uuid: Optional[str] = None


@dataclass
class Disk:
    name: str
    path: str
    size: int
    model: Optional[str]
    serial: Optional[str]
    vendor: Optional[str]
    disk_type: str  # disk, rom, loop, ram, zram, part, ...
    transport: Optional[str]
    removable: bool
    rotational: Optional[bool]
    mountpoints: List[str] = field(default_factory=list)
    partitions: List[Partition] = field(default_factory=list)

    @property
    def is_virtual(self) -> bool:
        base = os.path.basename(self.path)
        return any(p.match(base) for p in VIRTUAL_DEVICE_PATTERNS)

    @property
    def size_human(self) -> str:
        return human_size(self.size)

    def all_devices(self) -> List[str]:
        """Returns this disk's device path plus every partition path."""
        devices = [self.path]
        devices.extend(p.path for p in self.partitions)
        return devices


def human_size(num_bytes) -> str:
    try:
        num_bytes = float(num_bytes)
    except (TypeError, ValueError):
        return "unknown"
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if num_bytes < 1024.0:
            return f"{num_bytes:3.1f}{unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f}EB"


class DiskScanner:
    """Uses `lsblk` and `/proc/mounts` to build an inventory of block
    devices, and to determine which devices back the running system so
    EraseManager can refuse to touch them."""

    def __init__(self, logger, lsblk_path="lsblk"):
        self.logger = logger
        self.lsblk_path = lsblk_path

    def _run(self, argv):
        result = subprocess.run(argv, capture_output=True, text=True, check=False)
        self.logger.command(argv, returncode=result.returncode)
        return result

    def scan(self) -> List[Disk]:
        """Returns every block device (disks and their partitions)."""
        argv = [
            self.lsblk_path,
            "-b",
            "-J",
            "-O",
        ]
        result = self._run(argv)
        if result.returncode != 0:
            self.logger.error("disk_scan", "lsblk failed", stderr=result.stderr)
            return []
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            self.logger.exception("disk_scan_parse", exc)
            return []

        disks: List[Disk] = []
        for node in data.get("blockdevices", []):
            if node.get("type") not in ("disk", "loop", "rom"):
                continue
            disks.append(self._build_disk(node))
        self.logger.operation("disk_scan", "success", count=len(disks))
        return disks

    def _build_disk(self, node) -> Disk:
        path = node.get("path") or f"/dev/{node.get('name')}"
        disk = Disk(
            name=node.get("name"),
            path=path,
            size=int(node.get("size") or 0),
            model=(node.get("model") or "").strip() or None,
            serial=(node.get("serial") or "").strip() or None,
            vendor=(node.get("vendor") or "").strip() or None,
            disk_type=node.get("type", "disk"),
            transport=node.get("tran"),
            removable=bool(node.get("rm")),
            rotational=self._parse_bool(node.get("rota")),
            mountpoints=self._collect_mountpoints(node),
        )
        for child in node.get("children", []) or []:
            disk.partitions.append(
                Partition(
                    name=child.get("name"),
                    path=child.get("path") or f"/dev/{child.get('name')}",
                    size=int(child.get("size") or 0),
                    fstype=child.get("fstype"),
                    mountpoints=self._collect_mountpoints(child),
                    uuid=child.get("uuid"),
                )
            )
        return disk

    @staticmethod
    def _parse_bool(value):
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        return str(value).strip() in ("1", "true", "True")

    @staticmethod
    def _collect_mountpoints(node) -> List[str]:
        mps = node.get("mountpoints") or node.get("mountpoint")
        if mps is None:
            return []
        if isinstance(mps, list):
            return [m for m in mps if m]
        return [mps] if mps else []

    def erasable_disks(self, disks: Optional[List[Disk]] = None) -> List[Disk]:
        """Filters out virtual devices (loop/ram/zram/rom) that must never
        be presented as erase candidates."""
        disks = disks if disks is not None else self.scan()
        return [d for d in disks if d.disk_type == "disk" and not d.is_virtual]

    def get_root_devices(self) -> List[str]:
        """Returns the parent disk device(s) backing '/', '/boot' and
        '/boot/efi' - these must never be erasable."""
        critical_mounts = ("/", "/boot", "/boot/efi")
        devices = set()
        for mount in critical_mounts:
            dev = self._source_for_mountpoint(mount)
            if dev:
                devices.add(dev)
        return sorted(devices)

    def _source_for_mountpoint(self, mountpoint) -> Optional[str]:
        result = subprocess.run(
            ["findmnt", "-n", "-o", "SOURCE", mountpoint],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return None
        source = result.stdout.strip()
        return source or None

    def get_live_medium_devices(self) -> List[str]:
        """Best-effort detection of the device(s) backing a live/removable
        boot medium (e.g. the USB pendrive the OS was started from)."""
        devices = set()
        try:
            with open("/proc/cmdline", "r", encoding="utf-8") as fh:
                cmdline = fh.read()
        except OSError:
            cmdline = ""

        is_live = any(tok in cmdline for tok in ("boot=live", "boot=casper", "live-media"))

        candidates = ["/run/live/medium", "/cdrom", "/lib/live/mount/medium"]
        for candidate in candidates:
            if os.path.ismount(candidate):
                dev = self._source_for_mountpoint(candidate)
                if dev:
                    devices.add(dev)

        if is_live:
            try:
                with open("/proc/mounts", "r", encoding="utf-8") as fh:
                    for line in fh:
                        parts = line.split()
                        if len(parts) < 3:
                            continue
                        source, target, fstype = parts[0], parts[1], parts[2]
                        if fstype in ("iso9660", "squashfs") or "medium" in target:
                            devices.add(source)
            except OSError:
                pass
        return sorted(devices)

    def resolve_to_parent_disk(self, device_path: str) -> str:
        """Given a partition path (e.g. /dev/sda1), returns its parent
        disk path (/dev/sda). If already a disk, returns it unchanged."""
        real = os.path.realpath(device_path)
        result = subprocess.run(
            ["lsblk", "-no", "PKNAME", real],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            pkname = result.stdout.strip()
            if pkname:
                return f"/dev/{pkname}"
        return real
