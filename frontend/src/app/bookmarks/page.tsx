"use client";
import { BottomNav } from "@/components/layout/BottomNav";
import { ArticleModal } from "@/components/feed/ArticleModal";
import { useNewsStore } from "@/store/useNewsStore";
import { useFeed } from "@/hooks/useFeed";
import { FeedCard } from "@/components/feed/FeedCard";
import { AnimatePresence } from "framer-motion";

export default function BookmarksPage() {
  const { selectedArticle } = useNewsStore();
  const { articles, isLoading, mutate } = useFeed({ bookmarked: true });

  return (
    <div className="min-h-dvh flex flex-col">
      <header className="sticky top-0 z-40 glass-bright border-b border-white/8 safe-top">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl accent-bg flex items-center justify-center text-white font-bold text-sm">N</div>
          <h1 className="font-bold text-lg">Zapisane ♥</h1>
          {!isLoading && (
            <span className="ml-auto text-xs font-mono text-[var(--text-muted)]">{articles.length} artykułów</span>
          )}
        </div>
      </header>

      <main className="flex-1 max-w-2xl w-full mx-auto p-4 pb-24">
        {isLoading ? (
          <div className="flex flex-col gap-3">
            {Array.from({ length: 3 }).map((_, i) => <div key={i} className="glass rounded-2xl h-28 animate-pulse" />)}
          </div>
        ) : articles.length === 0 ? (
          <div className="py-20 text-center space-y-3">
            <p className="text-5xl">♡</p>
            <p className="text-[var(--text-muted)] font-medium">Brak zapisanych artykułów</p>
            <p className="text-xs text-[var(--text-dim)]">Kliknij ♡ na karcie artykułu aby go zapisać</p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            <AnimatePresence initial={false}>
              {articles.map((article) => (
                <FeedCard key={article.id} article={article as import("@/types").Article} onMutate={mutate} />
              ))}
            </AnimatePresence>
          </div>
        )}
      </main>

      <BottomNav />
      {selectedArticle && <ArticleModal />}
    </div>
  );
}
