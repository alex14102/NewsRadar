"use client";
import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Article, UserSettings, Category } from "@/types";

export type SortOrder = "date_desc" | "date_asc" | "source";

interface NewsStore {
  activeCategory: Category;
  selectedArticle: Article | null;
  searchQuery: string;
  unreadOnly: boolean;
  sidebarOpen: boolean;
  sortOrder: SortOrder;
  settings: UserSettings;

  setActiveCategory: (cat: Category) => void;
  setSelectedArticle: (article: Article | null) => void;
  setSearchQuery: (q: string) => void;
  toggleUnreadOnly: () => void;
  toggleSidebar: () => void;
  setSortOrder: (order: SortOrder) => void;
  updateSettings: (s: Partial<UserSettings>) => void;
  applyTheme: (settings: UserSettings) => void;
}

const DEFAULT_SETTINGS: UserSettings = {
  id: 1,
  theme: "dark",
  accent_hue: 210,
  font_size: "md",
  language: "pl",
  notifications_enabled: true,
  refresh_interval: 300,
};

export const useNewsStore = create<NewsStore>()(
  persist(
    (set, get) => ({
      activeCategory: "all",
      selectedArticle: null,
      searchQuery: "",
      unreadOnly: false,
      sidebarOpen: false,
      sortOrder: "date_desc",
      settings: DEFAULT_SETTINGS,

      setActiveCategory: (cat) => set({ activeCategory: cat }),
      setSelectedArticle: (article) => set({ selectedArticle: article }),
      setSearchQuery: (q) => set({ searchQuery: q }),
      toggleUnreadOnly: () => set((s) => ({ unreadOnly: !s.unreadOnly })),
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setSortOrder: (order) => set({ sortOrder: order }),

      updateSettings: (updates) => {
        const next = { ...get().settings, ...updates };
        set({ settings: next });
        get().applyTheme(next);
      },

      applyTheme: (s) => {
        const root = document.documentElement;
        root.style.setProperty("--accent-hue", String(s.accent_hue));
        root.classList.toggle("light", s.theme === "light");
        root.classList.toggle("dark", s.theme === "dark");
        document.body.classList.remove("font-sm", "font-md", "font-lg");
        document.body.classList.add(`font-${s.font_size}`);
      },
    }),
    {
      name: "newsradar-store",
      partialize: (s) => ({ settings: s.settings, activeCategory: s.activeCategory, sortOrder: s.sortOrder }),
    }
  )
);
