"use client";
import { useNewsStore } from "@/store/useNewsStore";
import type { SortOrder } from "@/store/useNewsStore";
import type { Category } from "@/types";
import { cn } from "@/lib/utils";

const SORT_OPTIONS: { id: SortOrder; label: string }[] = [
  { id: "date_desc", label: "NAJNOWSZE" },
  { id: "date_asc",  label: "NAJSTARSZE" },
  { id: "source",    label: "ŹRÓDŁO" },
];

const CATEGORIES: { id: Category; label: string; dot?: string }[] = [
  { id: "all",     label: "WSZYSTKO" },
  { id: "news",    label: "WIADOMOŚCI", dot: "#e63946" },
  { id: "bizweek", label: "BIZWEEK",    dot: "#3a86ff" },
  { id: "tech",    label: "TECH",       dot: "#7c3aed" },
  { id: "video",   label: "VIDEO",      dot: "#ff0000" },
  { id: "social",  label: "SOCIAL",     dot: "#00ff99" },
  { id: "podcast", label: "PODCAST",    dot: "#f77f00" },
];

export function FeedFilters() {
  const { activeCategory, setActiveCategory, unreadOnly, toggleUnreadOnly, sortOrder, setSortOrder } = useNewsStore();

  return (
    <div className="relative z-10 border-b border-[var(--border)]">
      {/* Category nav */}
      <div className="flex overflow-x-auto scrollbar-hide">
        {CATEGORIES.map(({ id, label, dot }) => {
          const active = activeCategory === id;
          return (
            <button
              key={id}
              onClick={() => setActiveCategory(id)}
              className={cn(
                "relative flex items-center gap-1.5 px-4 py-3 text-[11px] font-mono font-medium tracking-[0.07em] whitespace-nowrap shrink-0 transition-colors duration-150 border-b-2",
                active
                  ? "text-white border-[var(--accent)]"
                  : "text-[var(--text-muted)] border-transparent hover:text-white hover:border-white/20"
              )}
            >
              {dot && (
                <span
                  className="w-1.5 h-1.5 rounded-full shrink-0"
                  style={{ background: dot }}
                />
              )}
              {label}
            </button>
          );
        })}
      </div>

      {/* Sub-row: unread + sort */}
      <div className="flex items-center gap-2 px-4 py-2 overflow-x-auto scrollbar-hide">
        <button
          onClick={toggleUnreadOnly}
          className={cn(
            "label flex items-center gap-1.5 px-2.5 py-1 rounded border transition-colors shrink-0",
            unreadOnly
              ? "border-[var(--accent)] text-[var(--accent)] bg-[var(--accent-glow)]"
              : "border-[var(--border)] text-[var(--text-muted)] hover:border-[var(--border-bright)]"
          )}
        >
          <span className={cn("w-1.5 h-1.5 rounded-full", unreadOnly ? "bg-[var(--accent)]" : "bg-[var(--text-muted)]")} />
          NIEPRZECZYTANE
        </button>

        <span className="label text-[var(--border-bright)] mx-1 shrink-0">|</span>
        <span className="label text-[var(--text-dim)] shrink-0">SORTUJ:</span>

        {SORT_OPTIONS.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setSortOrder(id)}
            className={cn(
              "label px-2.5 py-1 rounded border transition-colors shrink-0",
              sortOrder === id
                ? "border-[var(--accent)] text-[var(--accent)] bg-[var(--accent-glow)]"
                : "border-transparent text-[var(--text-muted)] hover:text-white"
            )}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}
