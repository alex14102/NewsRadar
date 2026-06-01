"use client";
import { useMemo } from "react";
import { useFeed } from "@/hooks/useFeed";
import { useNewsStore } from "@/store/useNewsStore";
import { FeedCard } from "./FeedCard";
import type { Article } from "@/types";

export function FeedList() {
  const { activeCategory, searchQuery, unreadOnly, sortOrder } = useNewsStore();
  const { articles, isLoading, error, mutate } = useFeed({
    category: activeCategory,
    search: searchQuery || undefined,
    unreadOnly,
  });

  const sorted = useMemo(() => {
    const arr = [...(articles as Article[])];
    if (sortOrder === "date_asc") {
      return arr.sort((a, b) =>
        new Date(a.published_at || a.fetched_at).getTime() -
        new Date(b.published_at || b.fetched_at).getTime()
      );
    }
    if (sortOrder === "source") {
      return arr.sort((a, b) => a.source_name.localeCompare(b.source_name));
    }
    return arr;
  }, [articles, sortOrder]);

  if (isLoading) {
    return (
      <div className="flex flex-col gap-1 px-4 pt-2">
        {Array.from({ length: 7 }).map((_, i) => (
          <div
            key={i}
            className="relative rounded-xl overflow-hidden"
            style={{ height: 86, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)" }}
          >
            <div className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-sm" style={{ background: "rgba(255,255,255,0.12)" }} />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-4 py-16 text-center space-y-2">
        <p className="label" style={{ color: "var(--red)" }}>BŁĄD POŁĄCZENIA</p>
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>Backend niedostępny na porcie 8000</p>
      </div>
    );
  }

  if (sorted.length === 0) {
    return (
      <div className="px-4 py-20 text-center space-y-3">
        <p className="text-3xl" style={{ opacity: 0.3 }}>◉</p>
        <p className="label" style={{ color: "var(--text-muted)" }}>BRAK ARTYKUŁÓW</p>
        <p className="text-sm" style={{ color: "var(--text-dim)" }}>
          {searchQuery ? "Zmień frazę wyszukiwania" : "Dodaj źródła i odśwież feed"}
        </p>
      </div>
    );
  }

  // Group by source for "source" sort
  if (sortOrder === "source") {
    const groups: Record<string, Article[]> = {};
    for (const a of sorted) {
      if (!groups[a.source_name]) groups[a.source_name] = [];
      groups[a.source_name].push(a);
    }
    return (
      <div className="pb-2" style={{ position: "relative", zIndex: 10 }}>
        {Object.entries(groups).map(([sourceName, items]) => (
          <div key={sourceName}>
            <div className="px-4 py-2" style={{ background: "var(--bg-panel)", position: "sticky", top: 57, zIndex: 20 }}>
              <p className="label">{sourceName.toUpperCase()}</p>
            </div>
            <div className="flex flex-col gap-1 px-4">
              {items.map((article) => (
                <FeedCard key={article.id} article={article} onMutate={mutate} />
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Date-sorted with separator rows
  return (
    <div className="flex flex-col gap-1 px-4 pt-2 pb-2" style={{ position: "relative", zIndex: 10 }}>
      {sorted.map((article: Article, i: number) => {
        const date = article.published_at
          ? new Date(article.published_at).toLocaleDateString("pl-PL", { day: "numeric", month: "long" })
          : null;
        const prevDate =
          i > 0 && sorted[i - 1].published_at
            ? new Date(sorted[i - 1].published_at!).toLocaleDateString("pl-PL", { day: "numeric", month: "long" })
            : null;
        const showDate = date && date !== prevDate;

        return (
          <div key={article.id}>
            {showDate && (
              <div className="py-2 flex items-center gap-3">
                <span className="label" style={{ color: "var(--text-dim)" }}>{date}</span>
                <span className="flex-1" style={{ height: 1, background: "var(--border)" }} />
              </div>
            )}
            <FeedCard article={article} onMutate={mutate} />
          </div>
        );
      })}
    </div>
  );
}
