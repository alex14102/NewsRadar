"use client";
import useSWR from "swr";
import { useMemo } from "react";
import type { Article, FeedStats, Category } from "@/types";
import { API_BASE } from "@/lib/api";
import { useNewsStore } from "@/store/useNewsStore";

const STATIC_DATA_URL =
  "https://raw.githubusercontent.com/alex14102/NewsRadar/refs/heads/data/articles.json";

const isStatic = !API_BASE;

const fetcher = (url: string) => fetch(url).then((r) => r.json());

interface UseFeedOptions {
  category?: Category;
  sourceId?: number;
  unreadOnly?: boolean;
  bookmarked?: boolean;
  search?: string;
  page?: number;
}

export function useFeed(opts: UseFeedOptions = {}) {
  const { readIds, bookmarkedIds } = useNewsStore();

  const apiUrl = isStatic
    ? STATIC_DATA_URL
    : (() => {
        const params = new URLSearchParams();
        if (opts.category && opts.category !== "all") params.set("category", opts.category);
        if (opts.sourceId) params.set("source_id", String(opts.sourceId));
        if (opts.unreadOnly) params.set("unread_only", "true");
        if (opts.bookmarked) params.set("bookmarked", "true");
        if (opts.search) params.set("search", opts.search);
        if (opts.page) params.set("page", String(opts.page));
        return `${API_BASE}/api/feed?${params.toString()}`;
      })();

  const { data: rawData, error, isLoading, mutate } = useSWR<Article[]>(
    apiUrl,
    fetcher,
    { refreshInterval: isStatic ? 20 * 60 * 1000 : 5 * 60 * 1000, revalidateOnFocus: false }
  );

  const articles = useMemo(() => {
    if (!rawData) return [];
    let list = rawData.map((a) => ({
      ...a,
      is_read: readIds.includes(a.id) || a.is_read,
      is_bookmarked: bookmarkedIds.includes(a.id) || a.is_bookmarked,
    }));

    if (!isStatic) return list;

    // Client-side filters in static mode
    if (opts.category && opts.category !== "all") {
      list = list.filter((a) => (a as any).category === opts.category);
    }
    if (opts.bookmarked) {
      list = list.filter((a) => bookmarkedIds.includes(a.id));
    }
    if (opts.unreadOnly) {
      list = list.filter((a) => !readIds.includes(a.id));
    }
    if (opts.search) {
      const q = opts.search.toLowerCase();
      list = list.filter(
        (a) => a.title.toLowerCase().includes(q) || a.summary?.toLowerCase().includes(q)
      );
    }
    return list;
  }, [rawData, readIds, bookmarkedIds, opts.category, opts.bookmarked, opts.unreadOnly, opts.search]);

  return { articles, error, isLoading, mutate };
}

export function useFeedStats() {
  const { readIds, bookmarkedIds } = useNewsStore();
  const { data } = useSWR<Article[]>(
    isStatic ? STATIC_DATA_URL : `${API_BASE}/api/feed/stats`,
    fetcher,
    { refreshInterval: 60_000 }
  );

  if (isStatic) {
    const total = data?.length ?? 0;
    return {
      total,
      unread: total - readIds.length,
      bookmarked: bookmarkedIds.length,
    };
  }
  return (data as unknown as FeedStats) ?? { total: 0, unread: 0, bookmarked: 0 };
}

export async function markRead(id: number) {
  useNewsStore.getState().markRead(id);
  if (!isStatic) {
    await fetch(`${API_BASE}/api/feed/${id}/read`, { method: "PATCH" });
  }
}

export async function toggleBookmark(id: number) {
  const bookmarked = useNewsStore.getState().toggleBookmark(id);
  if (!isStatic) {
    const res = await fetch(`${API_BASE}/api/feed/${id}/bookmark`, { method: "PATCH" });
    return res.json();
  }
  return { bookmarked };
}

export async function refreshFeed(sourceId?: number) {
  if (isStatic) return { new_articles: 0 };
  const url = sourceId
    ? `${API_BASE}/api/feed/refresh?source_id=${sourceId}`
    : `${API_BASE}/api/feed/refresh`;
  const res = await fetch(url, { method: "POST" });
  return res.json();
}
