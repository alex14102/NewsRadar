"use client";
import { AnimatePresence, motion } from "framer-motion";
import { useFeed } from "@/hooks/useFeed";
import { useNewsStore } from "@/store/useNewsStore";
import { FeedCard } from "./FeedCard";

export function FeedList() {
  const { activeCategory, searchQuery, unreadOnly } = useNewsStore();
  const { articles, isLoading, error, mutate } = useFeed({
    category: activeCategory,
    search: searchQuery || undefined,
    unreadOnly,
  });

  if (isLoading) {
    return (
      <div className="flex flex-col gap-3 px-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="glass rounded-2xl h-28 animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-4 py-12 text-center">
        <p className="text-[var(--text-muted)] text-sm">Błąd połączenia z backendem</p>
        <p className="text-xs text-[var(--text-dim)] mt-1">Sprawdź czy backend działa na porcie 8000</p>
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div className="px-4 py-16 text-center space-y-3">
        <p className="text-4xl">📡</p>
        <p className="text-[var(--text-muted)] text-sm font-medium">Brak artykułów</p>
        <p className="text-xs text-[var(--text-dim)]">
          {searchQuery ? "Zmień frazę wyszukiwania" : "Dodaj źródła i odśwież feed"}
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 px-4 pb-2">
      <AnimatePresence initial={false}>
        {articles.map((article: import("@/types").Article) => (
          <FeedCard key={article.id} article={article} onMutate={mutate} />
        ))}
      </AnimatePresence>
    </div>
  );
}
