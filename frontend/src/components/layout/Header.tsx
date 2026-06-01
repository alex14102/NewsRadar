"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { useNewsStore } from "@/store/useNewsStore";
import { useFeedStats, refreshFeed } from "@/hooks/useFeed";
import { NotifBell } from "@/components/notifications/NotifBell";

export function Header() {
  const { searchQuery, setSearchQuery } = useNewsStore();
  const stats = useFeedStats();
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    await refreshFeed();
    setRefreshing(false);
    window.location.reload();
  };

  return (
    <header className="sticky top-0 z-40 glass-bright border-b border-white/8 safe-top">
      <div className="max-w-2xl mx-auto px-4 py-3 flex items-center gap-3">
        {/* Logo */}
        <div className="flex items-center gap-2 shrink-0">
          <div className="w-8 h-8 rounded-xl accent-bg flex items-center justify-center text-white font-bold text-sm">N</div>
          <span className="font-semibold text-sm tracking-wide hidden sm:block">NewsRadar</span>
        </div>

        {/* Search */}
        <div className="flex-1 relative">
          <input
            type="search"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Szukaj w artykułach..."
            className="w-full glass rounded-xl px-4 py-2 text-sm outline-none focus:border-[var(--accent)] transition-colors placeholder:text-[var(--text-muted)] border border-transparent"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-white text-lg"
            >
              ×
            </button>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 shrink-0">
          {stats.unread > 0 && (
            <span className="font-mono text-xs px-2 py-1 rounded-full glass text-[var(--accent)] border border-[var(--accent)]/30">
              {stats.unread}
            </span>
          )}
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="w-9 h-9 rounded-xl glass flex items-center justify-center text-[var(--text-muted)] hover:text-white transition-colors"
            title="Odśwież"
          >
            <motion.span
              animate={{ rotate: refreshing ? 360 : 0 }}
              transition={{ duration: 1, repeat: refreshing ? Infinity : 0, ease: "linear" }}
              className="text-lg"
            >
              ↻
            </motion.span>
          </button>
          <NotifBell />
        </div>
      </div>
    </header>
  );
}
