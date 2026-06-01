"use client";
import { useMemo } from "react";
import useSWR from "swr";
import { motion } from "framer-motion";
import { useNewsStore } from "@/store/useNewsStore";
import type { Article } from "@/types";
import { API_BASE } from "@/lib/api";

const STATIC_DATA_URL =
  "https://raw.githubusercontent.com/alex14102/NewsRadar/refs/heads/data/articles.json";
const isStatic = !API_BASE;

const fetcher = (url: string) => fetch(url).then((r) => r.json());

interface DerivedSource {
  name: string;
  color: string | null;
  category: string;
  count: number;
}

const CATEGORY_LABELS: Record<string, string> = {
  news: "WIADOMOŚCI",
  geopolityka: "GEOPOLITYKA",
  gospodarka: "GOSPODARKA",
  biznes: "BIZNES",
  nauka: "NAUKA",
  technologia: "TECHNOLOGIA",
  video: "VIDEO",
  social: "SOCIAL",
  podcast: "PODCAST",
  general: "OGÓLNE",
};

export function SourceManager() {
  const { disabledSources, toggleSourceEnabled, setAllSourcesEnabled } = useNewsStore();
  const { data, isLoading } = useSWR<Article[]>(
    isStatic ? STATIC_DATA_URL : null,
    fetcher,
    { revalidateOnFocus: false }
  );

  const sources: DerivedSource[] = useMemo(() => {
    if (!data) return [];
    const map = new Map<string, DerivedSource>();
    for (const a of data) {
      const existing = map.get(a.source_name);
      if (existing) {
        existing.count++;
      } else {
        map.set(a.source_name, {
          name: a.source_name,
          color: a.source_color,
          category: a.category ?? "general",
          count: 1,
        });
      }
    }
    return Array.from(map.values()).sort((a, b) => a.name.localeCompare(b.name));
  }, [data]);

  const grouped = useMemo(() => {
    const g: Record<string, DerivedSource[]> = {};
    for (const s of sources) {
      if (!g[s.category]) g[s.category] = [];
      g[s.category].push(s);
    }
    return g;
  }, [sources]);

  if (isLoading || !data) {
    return (
      <div className="flex flex-col gap-3 p-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="glass rounded-xl h-16 animate-pulse" />
        ))}
      </div>
    );
  }

  const allNames = sources.map((s) => s.name);
  const allEnabled = disabledSources.length === 0;
  const allDisabled = disabledSources.length === sources.length;

  return (
    <div className="p-4 space-y-6 pb-24">
      <div className="space-y-2">
        <p className="label text-[var(--text-muted)]">
          {sources.length - disabledSources.length}/{sources.length} aktywnych źródeł
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => setAllSourcesEnabled(allNames, true)}
            disabled={allEnabled}
            className="flex-1 py-2 rounded-lg glass text-xs label hover:text-white disabled:opacity-40 disabled:cursor-not-allowed"
          >
            ZAZNACZ WSZYSTKO
          </button>
          <button
            onClick={() => setAllSourcesEnabled(allNames, false)}
            disabled={allDisabled}
            className="flex-1 py-2 rounded-lg glass text-xs label hover:text-white disabled:opacity-40 disabled:cursor-not-allowed"
          >
            ODZNACZ WSZYSTKO
          </button>
        </div>
      </div>

      {Object.entries(grouped).map(([category, items]) => {
        const categoryNames = items.map((s) => s.name);
        const categoryAllEnabled = categoryNames.every((n) => !disabledSources.includes(n));
        return (
          <div key={category}>
            <div className="flex items-center justify-between mb-2 px-1">
              <h3 className="text-xs font-mono font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                {CATEGORY_LABELS[category] ?? category.toUpperCase()}
              </h3>
              <button
                onClick={() => setAllSourcesEnabled(categoryNames, !categoryAllEnabled)}
                className="text-[10px] font-mono text-[var(--text-dim)] hover:text-white"
              >
                {categoryAllEnabled ? "wszystkie ✓" : "włącz wszystkie"}
              </button>
            </div>
            <div className="flex flex-col gap-2">
              {items.map((source) => {
                const enabled = !disabledSources.includes(source.name);
                return (
                  <motion.button
                    key={source.name}
                    layout
                    onClick={() => toggleSourceEnabled(source.name)}
                    className={`glass rounded-xl p-3 flex items-center gap-3 text-left transition-opacity ${
                      enabled ? "" : "opacity-40"
                    }`}
                  >
                    <div
                      className="w-3 h-3 rounded-full shrink-0"
                      style={{ background: source.color || "var(--accent)" }}
                    />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">{source.name}</div>
                      <p className="text-[10px] font-mono text-[var(--text-dim)] mt-0.5">
                        {source.count} artykułów
                      </p>
                    </div>
                    <div
                      className={`w-10 h-5 rounded-full transition-colors relative shrink-0 ${
                        enabled ? "accent-bg" : "bg-white/10"
                      }`}
                    >
                      <span
                        className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                          enabled ? "translate-x-5" : "translate-x-0.5"
                        }`}
                      />
                    </div>
                  </motion.button>
                );
              })}
            </div>
          </div>
        );
      })}

      <div className="pt-4 border-t border-[var(--border)]">
        <p className="text-[11px] font-mono text-[var(--text-dim)] leading-relaxed">
          Lista źródeł jest zarządzana z pliku{" "}
          <span className="text-[var(--text-muted)]">scripts/fetch_feeds.py</span> w repo.
          Aby dodać nowe źródło napisz nazwę + URL RSS i dorzucimy je do skryptu.
        </p>
      </div>
    </div>
  );
}
