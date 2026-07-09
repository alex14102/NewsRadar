#!/usr/bin/env python3
"""Disk Erasure Utility - entry point.

Interactive mode (default): launches the Rich-based MainMenu.
Non-interactive mode: scriptable subcommands for scan/smart/crypto/erase/reports.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.crypto_detector import CryptoDetector  # noqa: E402
from app.disk_scanner import DiskScanner, human_size  # noqa: E402
from app.erase_manager import ALL_METHODS, EraseManager, SecurityError  # noqa: E402
from app.logger import JsonLogger  # noqa: E402
from app.main_menu import MainMenu  # noqa: E402
from app.monitor import Monitor  # noqa: E402
from app.report_manager import ReportManager  # noqa: E402
from app.settings import Settings  # noqa: E402
from app.smart_manager import SmartManager  # noqa: E402


def build_context(args):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    settings = Settings(config_path=args.config, base_dir=base_dir)
    logger = JsonLogger(settings.log_path, level=settings.log_level)
    disk_scanner = DiskScanner(logger)
    return settings, logger, disk_scanner


def cmd_scan(args):
    settings, logger, disk_scanner = build_context(args)
    disks = disk_scanner.scan()
    for disk in disks:
        print(f"{disk.path}\t{disk.model or '-'}\t{human_size(disk.size)}\t{disk.disk_type}")


def cmd_smart(args):
    settings, logger, disk_scanner = build_context(args)
    smart_manager = SmartManager(logger, settings.smartctl_path)
    report = smart_manager.get_smart_data(args.device)
    print(report)


def cmd_crypto(args):
    settings, logger, disk_scanner = build_context(args)
    crypto_detector = CryptoDetector(logger, settings.blkid_path, settings.cryptsetup_path)
    info = crypto_detector.detect(args.device)
    print(info)


def cmd_erase(args):
    settings, logger, disk_scanner = build_context(args)
    erase_manager = EraseManager(settings, logger, disk_scanner)
    report_manager = ReportManager(settings, logger)
    monitor = Monitor(settings)

    try:
        erase_manager.assert_safe_to_erase(args.device)
    except SecurityError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        sys.exit(2)

    if not args.yes:
        confirm = input(f"Type WYMAZ to permanently erase {args.device} with method '{args.method}': ")
        if confirm.strip() != "WYMAZ":
            print("Aborted.")
            sys.exit(1)

    result = erase_manager.erase(args.device, args.method, progress_callback=monitor.progress_callback)
    report_manager.save(result)
    print(f"Status: {result.status}, duration: {result.duration_sec:.1f}s")
    sys.exit(0 if result.status == "success" else 1)


def cmd_reports(args):
    settings, logger, disk_scanner = build_context(args)
    report_manager = ReportManager(settings, logger)
    for report in report_manager.list_reports():
        erase = report.get("erase", {})
        print(f"{report['id']}\t{report['created_at']}\t{erase.get('device')}\t{erase.get('status')}")


def cmd_menu(args):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    MainMenu(base_dir=base_dir, config_path=args.config).run()


def build_parser():
    parser = argparse.ArgumentParser(description="Disk Erasure Utility")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("menu", help="Launch the interactive menu (default)").set_defaults(func=cmd_menu)

    scan_parser = subparsers.add_parser("scan", help="List block devices")
    scan_parser.set_defaults(func=cmd_scan)

    smart_parser = subparsers.add_parser("smart", help="Show SMART data for a device")
    smart_parser.add_argument("device")
    smart_parser.set_defaults(func=cmd_smart)

    crypto_parser = subparsers.add_parser("crypto", help="Detect encryption on a device")
    crypto_parser.add_argument("device")
    crypto_parser.set_defaults(func=cmd_crypto)

    erase_parser = subparsers.add_parser("erase", help="Erase a device")
    erase_parser.add_argument("device")
    erase_parser.add_argument("--method", default="zero", choices=list(ALL_METHODS))
    erase_parser.add_argument("--yes", action="store_true", help="Skip interactive confirmation")
    erase_parser.set_defaults(func=cmd_erase)

    reports_parser = subparsers.add_parser("reports", help="List saved reports")
    reports_parser.set_defaults(func=cmd_reports)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        args.func = cmd_menu
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
