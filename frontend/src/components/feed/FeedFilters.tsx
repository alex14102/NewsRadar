"use client";
import { motion } from "framer-motion";
import { useNewsStore } from "@/store/useNewsStore";
import type { Category } from "@/types";
import { cn } from "@/lib/utils";

const CATEGORIES: { id: Category; label: string; icon: string }[] = [
  { id: "all", label: "Wszystko", icon: "◉" },
  { id: "news", label: "Wiadomości", icon: "📰" },
  { id: "tech", label: "Technologia", icon: "⚡" },
  { id: "business", label: "Biznes", icon: "📊" },
  { id: "social", label: "Social", icon: "𝕏" },
  { id: "podcast", label: "Podcasty", icon: "🎧" },
];

export function FeedFilters() {
  const { activeCategory, setActiveCategory, unreadOnly, toggleUnreadOnly } = useNewsStore();

  return (
    <div className="flex flex-col gap-2 px-4 py-3">
      {/* Category tabs */}
      <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1">
        {CATEGORIES.map(({ id, label, icon }) => {
          const active = activeCategory === id;
          return (
            <button
              key={id}
              onClick={() => setActiveCategory(id)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all duration-200 shrink-0 relative",
                active
                  ? "text-white"
                  : "glass text-[var(--text-muted)] hover:text-white"
              )}
            >
              {active && (
                <motion.span
                  layoutId="filter-active"
                  className="absolute inset-0 rounded-xl accent-bg opacity-90"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.4 }}
                />
              )}
              <span className="relative">{icon}</span>
              <span className="relative">{label}</span>
            </button>
          );
        })}
      </div>

      {/* Unread toggle */}
      <div className="flex items-center gap-2">
        <button
          onClick={toggleUnreadOnly}
          className={cn(
            "flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-colors",
            unreadOnly ? "accent-bg text-white" : "glass text-[var(--text-muted)] hover:text-white"
          )}
        >
          <span>●</span> Tylko nieprzeczytane
        </button>
      </div>
    </div>
  );
}
