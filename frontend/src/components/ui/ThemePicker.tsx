"use client";
import { useSettings } from "@/hooks/useSettings";

const ACCENT_PRESETS = [
  { label: "Niebieski", hue: 210 },
  { label: "Fioletowy", hue: 270 },
  { label: "Zielony", hue: 145 },
  { label: "Czerwony", hue: 0 },
  { label: "Pomarańczowy", hue: 30 },
  { label: "Różowy", hue: 330 },
  { label: "Turkusowy", hue: 175 },
  { label: "Złoty", hue: 45 },
];

export function ThemePicker() {
  const { settings, saveSettings } = useSettings();

  return (
    <div className="space-y-5">
      {/* Theme toggle */}
      <div>
        <label className="text-xs font-mono text-[var(--text-muted)] mb-2 block uppercase tracking-wider">Motyw</label>
        <div className="flex gap-2">
          {(["dark", "light"] as const).map((t) => (
            <button
              key={t}
              onClick={() => saveSettings({ theme: t })}
              className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                settings.theme === t ? "accent-bg text-white" : "glass hover:text-white"
              }`}
            >
              {t === "dark" ? "🌙 Ciemny" : "☀️ Jasny"}
            </button>
          ))}
        </div>
      </div>

      {/* Accent color */}
      <div>
        <label className="text-xs font-mono text-[var(--text-muted)] mb-2 block uppercase tracking-wider">
          Kolor akcentu
        </label>
        <div className="grid grid-cols-4 gap-2 mb-3">
          {ACCENT_PRESETS.map(({ label, hue }) => (
            <button
              key={hue}
              onClick={() => saveSettings({ accent_hue: hue })}
              className={`flex flex-col items-center gap-1.5 p-2 rounded-xl glass transition-all ${
                settings.accent_hue === hue ? "ring-2 ring-white/40 scale-105" : "hover:scale-105"
              }`}
            >
              <div
                className="w-8 h-8 rounded-full"
                style={{ background: `hsl(${hue} 70% 60%)` }}
              />
              <span className="text-[9px] font-mono text-[var(--text-muted)]">{label}</span>
            </button>
          ))}
        </div>
        <div>
          <label className="text-xs text-[var(--text-muted)] mb-1 block">Własny odcień: {settings.accent_hue}°</label>
          <input
            type="range"
            min={0}
            max={360}
            value={settings.accent_hue}
            onChange={(e) => saveSettings({ accent_hue: Number(e.target.value) })}
            className="w-full h-2 rounded-full cursor-pointer"
            style={{
              background: `linear-gradient(to right, hsl(0,70%,60%), hsl(60,70%,60%), hsl(120,70%,60%), hsl(180,70%,60%), hsl(240,70%,60%), hsl(300,70%,60%), hsl(360,70%,60%))`,
            }}
          />
        </div>
      </div>

      {/* Font size */}
      <div>
        <label className="text-xs font-mono text-[var(--text-muted)] mb-2 block uppercase tracking-wider">Rozmiar czcionki</label>
        <div className="flex gap-2">
          {([["sm", "Mała"], ["md", "Normalna"], ["lg", "Duża"]] as const).map(([size, label]) => (
            <button
              key={size}
              onClick={() => saveSettings({ font_size: size })}
              className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                settings.font_size === size ? "accent-bg text-white" : "glass hover:text-white"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
