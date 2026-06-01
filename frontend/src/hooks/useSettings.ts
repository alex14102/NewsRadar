"use client";
import { useEffect } from "react";
import useSWR from "swr";
import { useNewsStore } from "@/store/useNewsStore";
import type { UserSettings } from "@/types";
import { API_BASE } from "@/lib/api";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export function useSettings() {
  const { settings, updateSettings, applyTheme } = useNewsStore();
  const { data: remote } = useSWR<UserSettings>(`${API_BASE}/api/settings`, fetcher);

  useEffect(() => {
    if (remote) {
      updateSettings(remote);
    }
  }, [remote]);

  useEffect(() => {
    applyTheme(settings);
  }, []);

  const saveSettings = async (updates: Partial<UserSettings>) => {
    updateSettings(updates);
    await fetch(`${API_BASE}/api/settings`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
  };

  return { settings, saveSettings };
}
