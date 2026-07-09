"""ReportManager: persists and retrieves JSON reports for every erase
operation performed by the tool."""

import json
import os
import uuid
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import List, Optional


class ReportManager:
    def __init__(self, settings, logger):
        self.settings = settings
        self.logger = logger
        os.makedirs(self.settings.reports_path, exist_ok=True)

    def _to_dict(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, dict):
            return obj
        return {"value": obj}

    def save(self, erase_result, disk_info: Optional[dict] = None, smart_info: Optional[dict] = None) -> str:
        report_id = str(uuid.uuid4())
        report = {
            "id": report_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "erase": self._to_dict(erase_result),
            "disk": disk_info or {},
            "smart": smart_info or {},
        }
        path = os.path.join(self.settings.reports_path, f"report_{report_id}.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        self.logger.info("report_saved", f"Report saved to {path}", report_id=report_id, path=path)
        return path

    def list_reports(self) -> List[dict]:
        reports = []
        if not os.path.isdir(self.settings.reports_path):
            return reports
        for name in sorted(os.listdir(self.settings.reports_path)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(self.settings.reports_path, name)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    reports.append(json.load(fh))
            except (OSError, json.JSONDecodeError) as exc:
                self.logger.exception("report_load_failed", exc)
        reports.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        return reports

    def get_report(self, report_id: str) -> Optional[dict]:
        path = os.path.join(self.settings.reports_path, f"report_{report_id}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def delete_report(self, report_id: str) -> bool:
        path = os.path.join(self.settings.reports_path, f"report_{report_id}.json")
        if os.path.exists(path):
            os.remove(path)
            self.logger.info("report_deleted", f"Deleted report {report_id}")
            return True
        return False
