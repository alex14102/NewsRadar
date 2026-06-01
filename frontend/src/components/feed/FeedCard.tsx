"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import type { Article } from "@/types";
import { timeAgo, sourceTypeIcon } from "@/lib/utils";
import { markRead, toggleBookmark } from "@/hooks/useFeed";
import { useNewsStore } from "@/store/useNewsStore";

interface FeedCardProps {
  article: Article;
  onMutate: () => void;
}

export function FeedCard({ article, onMutate }: FeedCardProps) {
  const { setSelectedArticle } = useNewsStore();
  const [bookmarked, setBookmarked] = useState(article.is_bookmarked);
  const [read, setRead] = useState(article.is_read);

  const handleOpen = async () => {
    if (!read) {
      setRead(true);
      await markRead(article.id);
      onMutate();
    }
    setSelectedArticle(article);
  };

  const handleBookmark = async (e: React.MouseEvent) => {
    e.stopPropagation();
    const res = await toggleBookmark(article.id);
    setBookmarked(res.bookmarked);
    onMutate();
  };

  const accentColor = article.source_color || "var(--accent)";

  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      className={`glass rounded-2xl overflow-hidden cursor-pointer transition-all duration-200 hover:scale-[1.01] active:scale-[0.99] ${read ? "opacity-60" : ""}`}
      onClick={handleOpen}
    >
      {/* Source bar */}
      <div
        className="h-0.5 w-full"
        style={{ background: `linear-gradient(90deg, ${accentColor}, transparent)` }}
      />

      <div className="p-4 flex gap-3">
        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Source + time */}
          <div className="flex items-center gap-1.5 mb-1.5">
            <span className="text-xs font-mono text-[var(--text-muted)]">
              {sourceTypeIcon(article.source_type)}
            </span>
            <span
              className="text-xs font-semibold truncate"
              style={{ color: accentColor }}
            >
              {article.source_name}
            </span>
            <span className="text-[10px] font-mono text-[var(--text-dim)] ml-auto shrink-0">
              {timeAgo(article.published_at || article.fetched_at)}
            </span>
          </div>

          {/* Title */}
          <h3 className="text-sm font-semibold leading-snug line-clamp-2 mb-1">
            {article.title}
          </h3>

          {/* Summary */}
          {article.summary && (
            <p className="text-xs text-[var(--text-muted)] line-clamp-2 leading-relaxed">
              {article.summary}
            </p>
          )}

          {/* Tags row */}
          <div className="flex items-center gap-1.5 mt-2 flex-wrap">
            {article.is_paywalled && (
              <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-yellow-500/15 text-yellow-400 border border-yellow-500/20">
                🔒 PAYWALL
              </span>
            )}
            {article.tags?.slice(0, 2).map((tag) => (
              <span key={tag} className="px-1.5 py-0.5 rounded text-[9px] font-mono glass text-[var(--text-muted)]">
                #{tag}
              </span>
            ))}
            {!read && (
              <span className="w-1.5 h-1.5 rounded-full accent-bg ml-auto shrink-0" />
            )}
          </div>
        </div>

        {/* Thumbnail */}
        <div className="flex flex-col items-end gap-2 shrink-0">
          {article.image_url && (
            <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-xl overflow-hidden glass shrink-0">
              <Image
                src={article.image_url}
                alt=""
                width={80}
                height={80}
                className="w-full h-full object-cover"
                unoptimized
              />
            </div>
          )}
          <button
            onClick={handleBookmark}
            className={`text-lg transition-all duration-150 ${bookmarked ? "text-[var(--accent)]" : "text-[var(--text-dim)] hover:text-white"}`}
            title={bookmarked ? "Usuń z zakładek" : "Dodaj do zakładek"}
          >
            {bookmarked ? "♥" : "♡"}
          </button>
        </div>
      </div>
    </motion.article>
  );
}
