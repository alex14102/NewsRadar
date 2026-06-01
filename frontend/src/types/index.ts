export interface Article {
  id: number;
  source_id: number;
  source_name: string;
  source_color: string | null;
  source_type: string;
  category?: Category;
  title: string;
  url: string;
  summary: string | null;
  full_content: string | null;
  image_url: string | null;
  author: string | null;
  published_at: string | null;
  fetched_at: string;
  is_read: boolean;
  is_bookmarked: boolean;
  is_paywalled: boolean;
  tags: string[] | null;
}

export interface Source {
  id: number;
  name: string;
  url: string;
  source_type: "rss" | "x" | "spotify" | "youtube";
  category: string;
  enabled: boolean;
  notify: boolean;
  icon_url: string | null;
  color: string | null;
  fetch_interval: number;
  last_fetched: string | null;
}

export interface UserSettings {
  id: number;
  theme: "dark" | "light";
  accent_hue: number;
  font_size: "sm" | "md" | "lg";
  language: string;
  notifications_enabled: boolean;
  refresh_interval: number;
}

export interface FeedStats {
  total: number;
  unread: number;
  bookmarked: number;
}

export type Category = "all" | "news" | "gospodarka" | "biznes" | "geopolityka" | "nauka" | "technologia" | "video" | "social" | "podcast" | "general";
