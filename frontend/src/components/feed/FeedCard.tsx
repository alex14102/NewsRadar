"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import type { Article } from "@/types";
import { timeAgo } from "@/lib/utils";
import { markRead, toggleBookmark } from "@/hooks/useFeed";
import { useNewsStore } from "@/store/useNewsStore";

interface FeedCardProps {
  article: Article;
  onMutate: () => void;
}

const CATEGORY_COLOR: Record<string, string> = {
  news: "#e63946",
  bizweek: "#3a86ff",
  tech: "#7c3aed",
  social: "#0f9",
  video: "#ff0000",
  podcast: "#f77f00",
  general: "#6b7280",
};

export function FeedCard({ article, onMutate }: FeedCardProps) {
  const { setSelectedArticle } = useNewsStore();
  const [bookmarked, setBookmarked] = useState(article.is_bookmarked);
  const [read, setRead] = useState(article.is_read);

  const accentColor = article.source_color || "var(--accent)";
  const isVideo = article.source_type === "youtube";
  const isX = article.source_type === "x";

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

  return (
    <motion.article
      initial={{ opacity: 0 }}
      animate={{ opacity: read ? 0.5 : 1 }}
      transition={{ duration: 0.2 }}
      onClick={handleOpen}
      className="card rounded-xl overflow-hidden cursor-pointer"
      style={{ "--card-accent": accentColor } as React.CSSProperties}
    >
      <div className="flex gap-0">
        {/* Main content */}
        <div className="flex-1 min-w-0 px-4 pt-3 pb-3">
          {/* Source + time row */}
          <div className="flex items-center justify-between mb-2 gap-2">
            <div className="flex items-center gap-2 min-w-0">
              {isVideo && (
                <span className="shrink-0 text-[10px] font-mono px-1.5 py-0.5 rounded bg-red-600/20 text-red-400 border border-red-600/30">
                  ▶ YT
                </span>
              )}
              {isX && (
                <span className="shrink-0 text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-600/20 text-emerald-400 border border-emerald-600/30">
                  𝕏
                </span>
              )}
              <span
                className="source-tag truncate"
                style={{ color: accentColor }}
              >
                {article.source_name}
              </span>
            </div>
            <span className="label shrink-0 text-[var(--text-dim)]">
              {timeAgo(article.published_at || article.fetched_at)}
            </span>
          </div>

          {/* Headline */}
          <h3 className="headline text-[15px] leading-[1.35] mb-2 line-clamp-2 text-[#d8dcf0]">
            {article.title}
          </h3>

          {/* Summary — only if no image or for video */}
          {article.summary && !article.image_url && (
            <p className="text-[13px] text-[#5e6080] line-clamp-2 leading-relaxed mb-2">
              {article.summary}
            </p>
          )}

          {/* Footer row */}
          <div className="flex items-center gap-1.5 flex-wrap">
            {article.is_paywalled && (
              <span className="cat-badge text-[var(--yellow)]">
                🔒 paywall
              </span>
            )}
            {article.tags?.slice(0, 2).map((tag) => (
              <span key={tag} className="label px-1.5 py-0.5 rounded bg-white/5">
                {tag}
              </span>
            ))}
            <div className="ml-auto flex items-center gap-3">
              {!read && (
                <span
                  className="w-1.5 h-1.5 rounded-full shrink-0"
                  style={{ background: accentColor }}
                />
              )}
              <button
                onClick={handleBookmark}
                className="text-[14px] transition-colors leading-none"
                style={{ color: bookmarked ? accentColor : "var(--text-dim)" }}
              >
                {bookmarked ? "♥" : "♡"}
              </button>
            </div>
          </div>
        </div>

        {/* Thumbnail — right side */}
        {article.image_url && (
          <div className="shrink-0 w-[88px] sm:w-[104px] self-stretch overflow-hidden">
            <Image
              src={article.image_url}
              alt=""
              width={104}
              height={80}
              className="w-full h-full object-cover"
              unoptimized
            />
          </div>
        )}
      </div>
    </motion.article>
  );
}
