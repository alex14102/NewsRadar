"use client";
import { Header } from "@/components/layout/Header";
import { BottomNav } from "@/components/layout/BottomNav";
import { FeedFilters } from "@/components/feed/FeedFilters";
import { FeedList } from "@/components/feed/FeedList";
import { ArticleModal } from "@/components/feed/ArticleModal";
import { useNewsStore } from "@/store/useNewsStore";

export default function HomePage() {
  const { selectedArticle } = useNewsStore();

  return (
    <div className="min-h-dvh flex flex-col relative">
      <Header />

      <main className="flex-1 max-w-2xl w-full mx-auto">
        <FeedFilters />
        <FeedList />
        <div className="h-24" /> {/* bottom nav spacer */}
      </main>

      <BottomNav />
      {selectedArticle && <ArticleModal />}
    </div>
  );
}
