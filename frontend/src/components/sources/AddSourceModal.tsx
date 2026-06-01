"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { addSource } from "@/hooks/useSources";

interface AddSourceModalProps {
  onClose: () => void;
}

const SOURCE_TYPES = [
  { id: "rss", label: "RSS / Atom", icon: "📡" },
  { id: "x", label: "Profil X (Twitter)", icon: "𝕏" },
  { id: "spotify", label: "Podcast / Spotify", icon: "🎧" },
  { id: "youtube", label: "YouTube RSS", icon: "▶" },
];

const CATEGORIES = ["news", "tech", "business", "social", "podcast", "general"];
const COLORS = ["#e63946", "#457b9d", "#2a9d8f", "#e9c46a", "#7209b7", "#4361ee", "#f77f00", "#06d6a0"];

export function AddSourceModal({ onClose }: AddSourceModalProps) {
  const [form, setForm] = useState<{
    name: string;
    url: string;
    source_type: "rss" | "x" | "spotify" | "youtube";
    category: string;
    notify: boolean;
    color: string;
  }>({
    name: "",
    url: "",
    source_type: "rss",
    category: "news",
    notify: false,
    color: COLORS[0],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const set = (key: string, val: any) => setForm((f) => ({ ...f, [key]: val }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.url) { setError("URL jest wymagany"); return; }
    setLoading(true);
    setError("");
    try {
      const res = await addSource(form);
      if (res.detail) { setError(res.detail); return; }
      onClose();
    } catch {
      setError("Błąd podczas dodawania źródła");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm p-0 sm:p-4">
      <motion.div
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        exit={{ y: "100%" }}
        transition={{ type: "spring", damping: 30, stiffness: 300 }}
        className="w-full sm:max-w-md glass-bright rounded-t-3xl sm:rounded-3xl overflow-hidden"
      >
        <div className="w-12 h-1 rounded-full bg-white/20 mx-auto mt-3 mb-4 sm:hidden" />

        <div className="p-5">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-bold text-lg">Dodaj źródło</h2>
            <button onClick={onClose} className="w-8 h-8 glass rounded-xl flex items-center justify-center text-[var(--text-muted)] hover:text-white">×</button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Source type */}
            <div>
              <label className="text-xs font-mono text-[var(--text-muted)] mb-1.5 block">Typ źródła</label>
              <div className="grid grid-cols-2 gap-1.5">
                {SOURCE_TYPES.map(({ id, label, icon }) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => set("source_type", id)}
                    className={`py-2 px-3 rounded-xl text-xs font-medium flex items-center gap-1.5 transition-colors ${
                      form.source_type === id ? "accent-bg text-white" : "glass hover:text-white"
                    }`}
                  >
                    <span>{icon}</span> {label}
                  </button>
                ))}
              </div>
            </div>

            {/* URL */}
            <div>
              <label className="text-xs font-mono text-[var(--text-muted)] mb-1.5 block">URL źródła *</label>
              <input
                value={form.url}
                onChange={(e) => set("url", e.target.value)}
                placeholder={
                  form.source_type === "x" ? "https://x.com/username" :
                  form.source_type === "spotify" ? "https://open.spotify.com/show/..." :
                  "https://example.com/feed.xml"
                }
                className="w-full glass rounded-xl px-4 py-2.5 text-sm outline-none focus:border-[var(--accent)] border border-transparent transition-colors"
              />
            </div>

            {/* Name */}
            <div>
              <label className="text-xs font-mono text-[var(--text-muted)] mb-1.5 block">Nazwa (opcjonalna)</label>
              <input
                value={form.name}
                onChange={(e) => set("name", e.target.value)}
                placeholder="Moje źródło"
                className="w-full glass rounded-xl px-4 py-2.5 text-sm outline-none focus:border-[var(--accent)] border border-transparent"
              />
            </div>

            {/* Category + Color */}
            <div className="flex gap-3">
              <div className="flex-1">
                <label className="text-xs font-mono text-[var(--text-muted)] mb-1.5 block">Kategoria</label>
                <select
                  value={form.category}
                  onChange={(e) => set("category", e.target.value)}
                  className="w-full glass rounded-xl px-3 py-2.5 text-sm outline-none"
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c} className="bg-[var(--bg)]">{c}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs font-mono text-[var(--text-muted)] mb-1.5 block">Kolor</label>
                <div className="flex gap-1 flex-wrap">
                  {COLORS.map((c) => (
                    <button
                      key={c}
                      type="button"
                      onClick={() => set("color", c)}
                      className={`w-6 h-6 rounded-full transition-transform ${form.color === c ? "scale-125 ring-2 ring-white" : "hover:scale-110"}`}
                      style={{ background: c }}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* Notify */}
            <label className="flex items-center gap-2 cursor-pointer">
              <div
                onClick={() => set("notify", !form.notify)}
                className={`w-10 h-5 rounded-full transition-colors relative ${form.notify ? "accent-bg" : "bg-white/10"}`}
              >
                <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${form.notify ? "translate-x-5" : "translate-x-0.5"}`} />
              </div>
              <span className="text-sm">Powiadomienia push</span>
            </label>

            {error && <p className="text-xs text-red-400">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl accent-bg text-white font-semibold text-sm disabled:opacity-50"
            >
              {loading ? "Dodawanie..." : "Dodaj źródło"}
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}
