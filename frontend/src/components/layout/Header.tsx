"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNewsStore } from "@/store/useNewsStore";
import { useFeedStats, refreshFeed } from "@/hooks/useFeed";
import { NotifBell } from "@/components/notifications/NotifBell";

function UtcClock() {
  const [time, setTime] = useState("");

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      setTime(
        now.toUTCString().slice(17, 25) + " UTC"
      );
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <span className="label text-[var(--text-dim)] hidden sm:block">{time}</span>
  );
}

export function Header() {
  const { searchQuery, setSearchQuery } = useNewsStore();
  const stats = useFeedStats();
  const [refreshing, setRefreshing] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    await refreshFeed();
    setRefreshing(false);
    window.location.reload();
  };

  return (
    <header className="sticky top-0 z-40 glass-bright border-b border-[var(--border-bright)] safe-top">
      {/* Live accent bar */}
      <div className="live-bar" />

      <div className="max-w-3xl mx-auto px-4 h-14 flex items-center gap-3">
        {/* Wordmark */}
        {!searchOpen && (
          <div className="flex items-center gap-2.5 shrink-0 min-w-0">
            <div
              className="w-7 h-7 rounded flex items-center justify-center accent-bg shrink-0"
              style={{ fontFamily: "'Barlow Condensed',sans-serif", fontWeight: 700, fontSize: 14 }}
            >
              N
            </div>
            <div className="hidden sm:flex flex-col leading-none">
              <span
                className="text-[13px] font-bold tracking-[0.12em] text-white"
                style={{ fontFamily: "'Barlow Condensed',sans-serif" }}
              >
                NEWSRADAR
              </span>
              <span className="label text-[8px]">INTELLIGENCE FEED</span>
            </div>
          </div>
        )}

        {/* Search — expands on mobile tap */}
        <AnimatePresence>
          {searchOpen ? (
            <motion.div
              key="search-open"
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: "100%" }}
              exit={{ opacity: 0, width: 0 }}
              className="flex-1 flex items-center gap-2"
            >
              <input
                autoFocus
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="SZUKAJ ARTYKUŁÓW..."
                className="flex-1 glass rounded-lg px-3 py-2 text-[13px] font-mono outline-none border border-transparent focus:border-[var(--accent)] transition-colors placeholder:text-[var(--text-muted)] placeholder:tracking-widest"
              />
              <button
                onClick={() => { setSearchOpen(false); setSearchQuery(""); }}
                className="label text-[var(--text-muted)] hover:text-white px-1"
              >
                ESC
              </button>
            </motion.div>
          ) : (
            <motion.div key="search-closed" className="flex-1 flex items-center gap-2 min-w-0">
              {/* UTC clock */}
              <UtcClock />

              {/* Unread badge */}
              {stats.unread > 0 && (
                <span className="label px-2 py-0.5 rounded border border-[var(--accent)]/40 text-[var(--accent)] ml-auto">
                  {stats.unread} NOWYCH
                </span>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Actions */}
        <div className="flex items-center gap-1.5 shrink-0">
          <button
            onClick={() => setSearchOpen(true)}
            className="w-8 h-8 rounded flex items-center justify-center text-[var(--text-muted)] hover:text-white transition-colors glass"
            title="Szukaj"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
          </button>

          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="w-8 h-8 rounded flex items-center justify-center text-[var(--text-muted)] hover:text-white transition-colors glass"
            title="Odśwież"
          >
            <motion.svg
              width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
              animate={{ rotate: refreshing ? 360 : 0 }}
              transition={{ duration: 0.8, repeat: refreshing ? Infinity : 0, ease: "linear" }}
            >
              <path d="M23 4v6h-6"/><path d="M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </motion.svg>
          </button>

          <NotifBell />
        </div>
      </div>
    </header>
  );
}
