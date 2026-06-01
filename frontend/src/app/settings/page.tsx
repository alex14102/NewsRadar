"use client";
import { BottomNav } from "@/components/layout/BottomNav";
import { ThemePicker } from "@/components/ui/ThemePicker";
import { useSettings } from "@/hooks/useSettings";
import { useFeedStats } from "@/hooks/useFeed";
import { useSources } from "@/hooks/useSources";

export default function SettingsPage() {
  const { settings, saveSettings } = useSettings();
  const stats = useFeedStats();
  const { sources } = useSources();

  return (
    <div className="min-h-dvh flex flex-col">
      <header className="sticky top-0 z-40 glass-bright border-b border-white/8 safe-top">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl accent-bg flex items-center justify-center text-white font-bold text-sm">N</div>
          <h1 className="font-bold text-lg">Ustawienia</h1>
        </div>
      </header>

      <main className="flex-1 max-w-2xl w-full mx-auto p-4 pb-24 space-y-6">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: "Artykułów", val: stats.total },
            { label: "Źródeł", val: sources.length },
            { label: "Nieprzecz.", val: stats.unread },
          ].map(({ label, val }) => (
            <div key={label} className="glass rounded-xl p-3 text-center">
              <p className="text-2xl font-bold font-mono accent">{val}</p>
              <p className="text-[10px] text-[var(--text-muted)] mt-0.5">{label}</p>
            </div>
          ))}
        </div>

        {/* Theme */}
        <div className="glass rounded-2xl p-5">
          <ThemePicker />
        </div>

        {/* Notification interval */}
        <div className="glass rounded-2xl p-5">
          <label className="text-xs font-mono text-[var(--text-muted)] mb-3 block uppercase tracking-wider">
            Odświeżanie co
          </label>
          <div className="flex gap-2">
            {([300, 600, 900, 1800] as const).map((interval) => (
              <button
                key={interval}
                onClick={() => saveSettings({ refresh_interval: interval })}
                className={`flex-1 py-2 rounded-xl text-xs font-medium transition-colors ${
                  settings.refresh_interval === interval ? "accent-bg text-white" : "glass hover:text-white"
                }`}
              >
                {interval === 300 ? "5 min" : interval === 600 ? "10 min" : interval === 900 ? "15 min" : "30 min"}
              </button>
            ))}
          </div>
        </div>

        {/* About */}
        <div className="glass rounded-2xl p-5 space-y-2">
          <p className="text-xs font-mono text-[var(--text-muted)] uppercase tracking-wider mb-3">O aplikacji</p>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl accent-bg flex items-center justify-center text-white font-bold">N</div>
            <div>
              <p className="font-bold">NewsRadar</p>
              <p className="text-xs text-[var(--text-muted)]">v1.0.0 · Agregator informacji</p>
            </div>
          </div>
          <p className="text-xs text-[var(--text-dim)] leading-relaxed mt-3">
            Prywatny agregator newsów z obsługą RSS, X (Twitter), Spotify, bypass paywall i push notyfikacjami.
          </p>
          <a
            href="https://github.com/twoj-nick/newsradar"
            target="_blank"
            rel="noopener noreferrer"
            className="block mt-2 text-xs text-[var(--accent)] hover:underline"
          >
            → GitHub Repo
          </a>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
