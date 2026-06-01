"use client";
import useSWR from "swr";
import type { Article, FeedStats, Category } from "@/types";
import { API_BASE } from "@/lib/api";

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
  const params = new URLSearchParams();
  if (opts.category && opts.category !== "all") params.set("category", opts.category);
  if (opts.sourceId) params.set("source_id", String(opts.sourceId));
  if (opts.unreadOnly) params.set("unread_only", "true");
  if (opts.bookmarked) params.set("bookmarked", "true");
  if (opts.search) params.set("search", opts.search);
  if (opts.page) params.set("page", String(opts.page));

  const { data, error, isLoading, mutate } = useSWR<Article[]>(
    `${API_BASE}/api/feed?${params.toString()}`,
    fetcher,
    { refreshInterval: 5 * 60 * 1000, revalidateOnFocus: false }
  );

  return { articles: data ?? [], error, isLoading, mutate };
}

export function useFeedStats() {
  const { data } = useSWR<FeedStats>(`${API_BASE}/api/feed/stats`, fetcher, {
    refreshInterval: 60_000,
  });
  return data ?? { total: 0, unread: 0, bookmarked: 0 };
}

export async function markRead(id: number) {
  await fetch(`${API_BASE}/api/feed/${id}/read`, { method: "PATCH" });
}

export async function toggleBookmark(id: number) {
  const res = await fetch(`${API_BASE}/api/feed/${id}/bookmark`, { method: "PATCH" });
  return res.json();
}

export async function refreshFeed(sourceId?: number) {
  const url = sourceId
    ? `${API_BASE}/api/feed/refresh?source_id=${sourceId}`
    : `${API_BASE}/api/feed/refresh`;
  const res = await fetch(url, { method: "POST" });
  return res.json();
}
