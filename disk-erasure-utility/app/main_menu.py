"""MainMenu: interactive Rich-based CLI tying every manager together."""

import signal
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .crypto_detector import CryptoDetector
from .disk_scanner import DiskScanner, human_size
from .erase_manager import ALL_METHODS, METHODS, METHODS_BY_ID, EraseManager, SecurityError
from .logger import JsonLogger
from .monitor import Monitor
from .report_manager import ReportManager
from .settings import Settings
from .smart_manager import SmartManager


class MainMenu:
    def __init__(self, base_dir=None, config_path="config.yaml"):
        self.console = Console()
        self.settings = Settings(config_path=config_path, base_dir=base_dir)
        self.logger = JsonLogger(
            self.settings.log_path, level=self.settings.log_level, console=self.console
        )
        self.disk_scanner = DiskScanner(self.logger)
        self.smart_manager = SmartManager(self.logger, self.settings.smartctl_path)
        self.crypto_detector = CryptoDetector(
            self.logger, self.settings.blkid_path, self.settings.cryptsetup_path
        )
        self.erase_manager = EraseManager(self.settings, self.logger, self.disk_scanner)
        self.report_manager = ReportManager(self.settings, self.logger)
        self.monitor = Monitor(self.settings, self.smart_manager)

        self._stop_event = threading.Event()
        self._previous_sigint = None
        self._disks_cache = []

    # ------------------------------------------------------------------
    # Signal handling / lifecycle
    # ------------------------------------------------------------------
    def _install_signal_handler(self):
        self._previous_sigint = signal.getsignal(signal.SIGINT)

        def handler(signum, frame):  # noqa: ARG001
            self._stop_event.set()
            self.logger.warning("sigint", "Ctrl+C received, requesting safe stop")

        signal.signal(signal.SIGINT, handler)

    def _restore_signal_handler(self):
        if self._previous_sigint is not None:
            signal.signal(signal.SIGINT, self._previous_sigint)

    def run(self):
        self._install_signal_handler()
        try:
            self._loop()
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Przerwano przez uzytkownika.[/yellow]")
        finally:
            self._restore_signal_handler()
            self.console.print("[dim]Zamykanie aplikacji...[/dim]")

    def _loop(self):
        while True:
            self._stop_event.clear()
            self.console.print(self._header_panel())
            choice = Prompt.ask(
                "Wybierz opcje",
                choices=["1", "2", "3", "4", "5", "6", "0"],
                default="1",
            )
            try:
                if choice == "1":
                    self._show_disks()
                elif choice == "2":
                    self._show_smart()
                elif choice == "3":
                    self._show_crypto()
                elif choice == "4":
                    self._erase_flow()
                elif choice == "5":
                    self._show_reports()
                elif choice == "6":
                    self._settings_menu()
                elif choice == "0":
                    break
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Operacja przerwana. Powrot do menu.[/yellow]")
            except Exception as exc:  # noqa: BLE001
                self.logger.exception("menu_error", exc)
                self.console.print(f"[bold red]Blad:[/bold red] {exc}")

    def _header_panel(self):
        return Panel(
            "[1] Skanuj dyski   [2] SMART   [3] Wykryj szyfrowanie\n"
            "[4] Wymaz dysk     [5] Raporty [6] Ustawienia\n"
            "[0] Wyjscie",
            title="Disk Erasure Utility",
            subtitle="Bezpieczne narzedzie do trwalego kasowania danych",
        )

    # ------------------------------------------------------------------
    # Disk listing
    # ------------------------------------------------------------------
    def _scan(self):
        self._disks_cache = self.disk_scanner.scan()
        return self._disks_cache

    def _disks_table(self, disks):
        protected = set(self.erase_manager.get_protected_devices())
        table = Table(title="Wykryte urzadzenia blokowe")
        table.add_column("#", justify="right")
        table.add_column("Urzadzenie")
        table.add_column("Model")
        table.add_column("Rozmiar")
        table.add_column("Typ")
        table.add_column("Wymienny")
        table.add_column("Zamontowany")
        table.add_column("Chroniony")

        for idx, disk in enumerate(disks, start=1):
            is_protected = (
                disk.path in protected
                or disk.is_virtual
                or any(p.path in protected for p in disk.partitions)
            )
            mounts = ", ".join(m for p in disk.partitions for m in p.mountpoints) or "-"
            table.add_row(
                str(idx),
                disk.path,
                disk.model or "-",
                human_size(disk.size),
                disk.disk_type,
                "tak" if disk.removable else "nie",
                mounts,
                "[bold red]TAK[/bold red]" if is_protected else "nie",
            )
        return table

    def _show_disks(self):
        disks = self._scan()
        self.console.print(self._disks_table(disks))

    def _select_disks(self, disks, prompt_text="Wybierz numer dysku (lub 'all')"):
        raw = Prompt.ask(prompt_text, default="")
        if not raw:
            return []
        if raw.strip().lower() == "all":
            return list(disks)
        selected = []
        for token in raw.split(","):
            token = token.strip()
            if not token.isdigit():
                continue
            index = int(token) - 1
            if 0 <= index < len(disks):
                selected.append(disks[index])
        return selected

    # ------------------------------------------------------------------
    # SMART
    # ------------------------------------------------------------------
    def _show_smart(self):
        disks = self._scan()
        self.console.print(self._disks_table(disks))
        selected = self._select_disks(disks)
        if not selected:
            return
        table = Table(title="Status S.M.A.R.T.")
        table.add_column("Urzadzenie")
        table.add_column("Zdrowie")
        table.add_column("Temp.")
        table.add_column("Godziny pracy")
        table.add_column("Sektory zrealokowane")
        table.add_column("Typ nosnika")
        for disk in selected:
            report = self.smart_manager.get_smart_data(disk.path)
            if not report.available:
                table.add_row(disk.path, f"niedostepne ({report.error})", "-", "-", "-", "-")
                continue
            health = "OK" if report.healthy else "UWAGA" if report.healthy is False else "?"
            media = "SSD" if report.is_ssd else "HDD" if report.is_ssd is False else "?"
            table.add_row(
                disk.path,
                health,
                f"{report.temperature_c}C" if report.temperature_c is not None else "-",
                str(report.power_on_hours) if report.power_on_hours is not None else "-",
                str(report.reallocated_sectors) if report.reallocated_sectors is not None else "-",
                media,
            )
        self.console.print(table)

    # ------------------------------------------------------------------
    # Crypto detection
    # ------------------------------------------------------------------
    def _show_crypto(self):
        disks = self._scan()
        self.console.print(self._disks_table(disks))
        selected = self._select_disks(disks)
        if not selected:
            return
        table = Table(title="Wykrywanie szyfrowania")
        table.add_column("Urzadzenie")
        table.add_column("Zaszyfrowany")
        table.add_column("Schemat")
        for disk in selected:
            devices = [disk.path] + [p.path for p in disk.partitions]
            for device in devices:
                info = self.crypto_detector.detect(device)
                table.add_row(
                    device,
                    "TAK" if info.encrypted else "nie",
                    info.scheme or "-",
                )
        self.console.print(table)

    # ------------------------------------------------------------------
    # Erase methods (ISO/IEC 27040-referenced sanitization standards)
    # ------------------------------------------------------------------
    def _methods_table(self):
        table = Table(title="Metody wymazywania (normy niszczenia danych)", expand=True)
        table.add_column("ID", no_wrap=True)
        table.add_column("Nazwa", no_wrap=True)
        table.add_column("Norma / standard", no_wrap=True)
        table.add_column("Przebiegi", justify="right", no_wrap=True)
        table.add_column("Opis", overflow="ellipsis", max_width=48)
        for spec in METHODS:
            passes = str(len(spec.passes)) if spec.passes else "sprzetowo"
            table.add_row(spec.id, spec.label, spec.standard, passes, spec.description)
        return table

    # ------------------------------------------------------------------
    # Erase flow
    # ------------------------------------------------------------------
    def _erase_flow(self):
        disks = self._scan()
        self.console.print(self._disks_table(disks))
        selected = self._select_disks(disks, "Wybierz numer dysku do wymazania (lub 'all')")
        if not selected:
            self.console.print("[yellow]Nie wybrano zadnego dysku.[/yellow]")
            return

        blocked = []
        allowed = []
        for disk in selected:
            try:
                self.erase_manager.assert_safe_to_erase(disk.path)
                allowed.append(disk)
            except SecurityError as exc:
                blocked.append((disk, str(exc)))

        for disk, reason in blocked:
            self.console.print(Panel(reason, title=f"[bold red]Zablokowano {disk.path}[/bold red]"))

        if not allowed:
            return

        self.console.print(self._methods_table())
        method = Prompt.ask(
            "Wybierz metode wymazywania (ID)", choices=list(ALL_METHODS), default=self.settings.default_method
        )
        spec = METHODS_BY_ID[method]
        self.console.print(
            Panel(
                f"{spec.label}\nNorma: {spec.standard}\n{spec.description}",
                title="Wybrana metoda",
                style="cyan",
            )
        )

        self.console.print(
            Panel(
                "\n".join(f"- {d.path} ({d.model or 'unknown'}, {human_size(d.size)})" for d in allowed),
                title="[bold yellow]Dyski do trwalego wymazania[/bold yellow]",
            )
        )
        if self.settings.confirm_required:
            confirmation = Prompt.ask(
                "Wpisz WYMAZ aby potwierdzic nieodwracalna operacje", default=""
            )
            if confirmation.strip() != "WYMAZ":
                self.console.print("[yellow]Anulowano.[/yellow]")
                return

        self._run_erase_jobs(allowed, method)

    def _run_erase_jobs(self, disks, method):
        spec = METHODS_BY_ID[method]
        self.monitor.reset()
        for disk in disks:
            self.monitor.register_job(disk.path, method, standard=spec.standard, total_passes=spec.passes and len(spec.passes) or 1)
        self.monitor.start_smart_polling([d.path for d in disks])

        results = {}
        try:
            with self.monitor.live():
                with ThreadPoolExecutor(max_workers=max(1, self.settings.threads)) as executor:
                    futures = {
                        executor.submit(self._erase_one, disk, method): disk for disk in disks
                    }
                    for future in as_completed(futures):
                        disk = futures[future]
                        try:
                            results[disk.path] = future.result()
                        except Exception as exc:  # noqa: BLE001
                            self.logger.exception("erase_job_failed", exc)
        finally:
            self.monitor.stop_smart_polling()

        for disk in disks:
            result = results.get(disk.path)
            if result is None:
                continue
            smart_info = vars(self.smart_manager.get_smart_data(disk.path))
            self.report_manager.save(result, disk_info=vars(disk), smart_info=smart_info)

        succeeded = sum(1 for r in results.values() if r.status == "success")
        self.console.print(
            f"[green]Zakonczono: {succeeded}/{len(disks)} operacji zakonczonych sukcesem.[/green]"
        )

    def _erase_one(self, disk, method):
        try:
            result = self.erase_manager.erase(
                disk.path,
                method,
                progress_callback=self.monitor.progress_callback,
                stop_event=self._stop_event,
            )
        except SecurityError as exc:
            self.monitor.finish_job(disk.path, "blocked")
            raise
        self.monitor.finish_job(disk.path, result.status)
        return result

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------
    def _show_reports(self):
        reports = self.report_manager.list_reports()
        if not reports:
            self.console.print("[dim]Brak zapisanych raportow.[/dim]")
            return
        table = Table(title="Raporty wymazywania")
        table.add_column("ID")
        table.add_column("Data")
        table.add_column("Urzadzenie")
        table.add_column("Metoda")
        table.add_column("Status")
        table.add_column("Czas [s]")
        for report in reports:
            erase = report.get("erase", {})
            table.add_row(
                report.get("id", "")[:8],
                report.get("created_at", ""),
                erase.get("device", "-"),
                erase.get("method", "-"),
                erase.get("status", "-"),
                f"{erase.get('duration_sec', 0):.1f}" if erase.get("duration_sec") is not None else "-",
            )
        self.console.print(table)

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------
    def _settings_menu(self):
        self.console.print(
            Panel(
                f"Metoda domyslna: {self.settings.default_method}\n"
                f"Watki: {self.settings.threads}\n"
                f"Rozmiar fragmentu: {self.settings.chunk_size_bytes // (1024*1024)} MB\n"
                f"Sciezka logow: {self.settings.log_path}\n"
                f"Sciezka raportow: {self.settings.reports_path}\n"
                f"Poziom logowania: {self.settings.log_level}\n"
                f"Weryfikacja po zapisie: {self.settings.verify}\n"
                f"Wymagane potwierdzenie: {self.settings.confirm_required}",
                title="Ustawienia (config.yaml)",
            )
        )
        if Confirm.ask("Zmienic metode domyslna?", default=False):
            method = Prompt.ask("Nowa metoda domyslna", choices=list(ALL_METHODS))
            self.settings.set("erase.default_method", method)
            self.settings.save()
            self.console.print("[green]Zapisano ustawienia.[/green]")
