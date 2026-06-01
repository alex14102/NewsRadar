"use client";
import useSWR from "swr";
import type { Source } from "@/types";
import { API_BASE } from "@/lib/api";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export function useSources() {
  const { data, error, isLoading, mutate } = useSWR<Source[]>(`${API_BASE}/api/sources`, fetcher);
  return { sources: data ?? [], error, isLoading, mutate };
}

export async function addSource(data: Partial<Source>) {
  const res = await fetch(`${API_BASE}/api/sources`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateSource(id: number, data: Partial<Source>) {
  const res = await fetch(`${API_BASE}/api/sources/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteSource(id: number) {
  await fetch(`${API_BASE}/api/sources/${id}`, { method: "DELETE" });
}

export async function addPresets() {
  const res = await fetch(`${API_BASE}/api/sources/presets`, { method: "POST" });
  return res.json();
}
