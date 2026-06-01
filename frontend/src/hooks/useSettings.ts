"use client";
import { useEffect } from "react";
import useSWR from "swr";
import { useNewsStore } from "@/store/useNewsStore";
import type { UserSettings } from "@/types";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export function useSettings() {
  const { settings, updateSettings, applyTheme } = useNewsStore();
  const { data: remote } = useSWR<UserSettings>("/api/settings", fetcher);

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
    await fetch("/api/settings", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
  };

  return { settings, saveSettings };
}
