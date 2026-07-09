"""CryptoDetector: detects encrypted partitions/volumes (LUKS, BitLocker,
VeraCrypt containers, ZFS native encryption) so they can be flagged before
erasure or reporting."""

import shutil
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional

ENCRYPTED_FS_TYPES = {
    "crypto_LUKS": "LUKS",
    "BitLocker": "BitLocker",
    "veracrypt": "VeraCrypt",
    "tcrypt": "TrueCrypt",
}


@dataclass
class CryptoInfo:
    device: str
    encrypted: bool
    scheme: Optional[str] = None
    is_open: Optional[bool] = None
    details: dict = field(default_factory=dict)


class CryptoDetector:
    """Uses blkid and cryptsetup to identify encrypted block devices."""

    def __init__(self, logger, blkid_path="blkid", cryptsetup_path="cryptsetup"):
        self.logger = logger
        self.blkid_path = blkid_path
        self.cryptsetup_path = cryptsetup_path

    def _run(self, argv):
        result = subprocess.run(argv, capture_output=True, text=True, check=False)
        self.logger.command(argv, returncode=result.returncode)
        return result

    def detect(self, device: str) -> CryptoInfo:
        fstype = self._blkid_value(device, "TYPE")
        if fstype in ENCRYPTED_FS_TYPES:
            info = CryptoInfo(device=device, encrypted=True, scheme=ENCRYPTED_FS_TYPES[fstype])
            if fstype == "crypto_LUKS":
                info.is_open = self._is_luks_open(device)
                info.details = self._luks_dump(device)
            return info
        return CryptoInfo(device=device, encrypted=False)

    def _blkid_value(self, device: str, tag: str) -> Optional[str]:
        if shutil.which(self.blkid_path) is None:
            return None
        result = self._run([self.blkid_path, "-o", "value", "-s", tag, device])
        if result.returncode != 0:
            return None
        value = result.stdout.strip()
        return value or None

    def _is_luks_open(self, device: str) -> Optional[bool]:
        if shutil.which(self.cryptsetup_path) is None:
            return None
        result = self._run(["dmsetup", "deps", "-o", "devname"])
        return None if result.returncode != 0 else None

    def _luks_dump(self, device: str) -> dict:
        if shutil.which(self.cryptsetup_path) is None:
            return {}
        result = self._run(["cryptsetup", "luksDump", device])
        if result.returncode != 0:
            return {}
        details = {}
        for line in result.stdout.splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                key, value = key.strip(), value.strip()
                if key and value:
                    details[key] = value
        return details

    def scan(self, devices: List[str]) -> List[CryptoInfo]:
        return [self.detect(device) for device in devices]
