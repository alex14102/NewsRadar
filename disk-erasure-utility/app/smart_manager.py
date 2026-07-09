"""SmartManager: retrieves S.M.A.R.T. health information for a device
using smartctl (smartmontools)."""

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SmartReport:
    device: str
    available: bool
    healthy: Optional[bool] = None
    temperature_c: Optional[int] = None
    power_on_hours: Optional[int] = None
    power_cycle_count: Optional[int] = None
    reallocated_sectors: Optional[int] = None
    pending_sectors: Optional[int] = None
    uncorrectable_sectors: Optional[int] = None
    rotation_rate: Optional[int] = None
    is_ssd: Optional[bool] = None
    raw: Dict = field(default_factory=dict)
    error: Optional[str] = None


ATTRIBUTE_IDS = {
    5: "reallocated_sectors",
    9: "power_on_hours",
    12: "power_cycle_count",
    197: "pending_sectors",
    198: "uncorrectable_sectors",
}


class SmartManager:
    """Wraps smartctl to fetch health/attributes for physical disks."""

    def __init__(self, logger, smartctl_path="smartctl"):
        self.logger = logger
        self.smartctl_path = smartctl_path

    def is_smartctl_available(self) -> bool:
        return shutil.which(self.smartctl_path) is not None

    def get_smart_data(self, device: str) -> SmartReport:
        if not self.is_smartctl_available():
            return SmartReport(device=device, available=False, error="smartctl not installed")

        argv = [self.smartctl_path, "-a", "-j", device]
        result = subprocess.run(argv, capture_output=True, text=True, check=False)
        self.logger.command(argv, returncode=result.returncode)

        if not result.stdout:
            return SmartReport(
                device=device,
                available=False,
                error=result.stderr.strip() or "no smartctl output",
            )

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            self.logger.exception("smart_parse", exc)
            return SmartReport(device=device, available=False, error="failed to parse smartctl JSON")

        report = SmartReport(device=device, available=True, raw=data)

        status = data.get("smart_status", {})
        if "passed" in status:
            report.healthy = bool(status["passed"])

        temperature = data.get("temperature", {})
        if "current" in temperature:
            report.temperature_c = temperature["current"]

        rotation_rate = data.get("rotation_rate")
        if rotation_rate is not None:
            report.rotation_rate = rotation_rate
            report.is_ssd = rotation_rate == 0

        for attr in data.get("ata_smart_attributes", {}).get("table", []):
            attr_id = attr.get("id")
            field_name = ATTRIBUTE_IDS.get(attr_id)
            if field_name:
                raw_value = attr.get("raw", {}).get("value")
                setattr(report, field_name, raw_value)

        power_on = data.get("power_on_time", {}).get("hours")
        if power_on is not None:
            report.power_on_hours = power_on

        return report

    def get_health_summary(self, devices: List[str]) -> Dict[str, SmartReport]:
        return {device: self.get_smart_data(device) for device in devices}
