import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function timeAgo(dateStr: string | null): string {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "przed chwilą";
  if (m < 60) return `${m} min`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h} godz`;
  const d = Math.floor(h / 24);
  return `${d} dni`;
}

export function sourceTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    rss: "📡",
    x: "𝕏",
    spotify: "🎵",
    youtube: "▶",
  };
  return icons[type] ?? "📰";
}
