"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { addSource } from "@/hooks/useSources";

interface AddSourceModalProps {
  onClose: () => void;
}

// Quick-add templates for creators
const CREATOR_TEMPLATES = [
  {
    label: "Kanał YouTube",
    icon: "▶",
    source_type: "youtube",
    category: "video",
    color: "#ff0000",
    placeholder: "https://youtube.com/feeds/videos.xml?channel_id=UC...",
    hint: "Wklej URL kanału YouTube lub RSS XML feed",
  },
  {
    label: "Profil X / Twitter",
    icon: "𝕏",
    source_type: "x",
    category: "social",
    color: "#00ff99",
    placeholder: "https://x.com/NazwaUżytkownika",
    hint: "Wklej URL profilu X/Twitter",
  },
  {
    label: "RSS / Artykuły",
    icon: "📡",
    source_type: "rss",
    category: "news",
    color: "#e63946",
    placeholder: "https://strona.pl/feed.xml",
    hint: "Wklej adres RSS/Atom dowolnej strony",
  },
  {
    label: "Podcast",
    icon: "🎧",
    source_type: "spotify",
    category: "podcast",
    color: "#f77f00",
    placeholder: "https://open.spotify.com/show/... lub RSS",
    hint: "Spotify show URL lub bezpośredni RSS podcastu",
  },
];

const CATEGORIES = [
  { id: "news",    label: "WIADOMOŚCI" },
  { id: "bizweek", label: "BIZWEEK" },
  { id: "tech",    label: "TECH" },
  { id: "video",   label: "VIDEO" },
  { id: "social",  label: "SOCIAL" },
  { id: "podcast", label: "PODCAST" },
  { id: "general", label: "OGÓLNE" },
];

const COLORS = ["#e63946","#c1121f","#3a86ff","#1d6fa4","#7c3aed","#4361ee","#ff0000","#f77f00","#00ff99","#ffd166","#06d6a0","#e4e4f0"];

export function AddSourceModal({ onClose }: AddSourceModalProps) {
  const [template, setTemplate] = useState(CREATOR_TEMPLATES[0]);
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
    source_type: "youtube",
    category: "video",
    notify: false,
    color: "#ff0000",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const setF = (key: string, val: any) => setForm((f) => ({ ...f, [key]: val }));

  const applyTemplate = (t: typeof CREATOR_TEMPLATES[0]) => {
    setTemplate(t);
    setF("source_type", t.source_type);
    setF("category", t.category);
    setF("color", t.color);
  };

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
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/70 backdrop-blur-sm p-0 sm:p-4">
      <motion.div
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        exit={{ y: "100%" }}
        transition={{ type: "spring", damping: 28, stiffness: 280 }}
        className="w-full sm:max-w-md glass-bright rounded-t-2xl sm:rounded-2xl overflow-hidden max-h-[92dvh] flex flex-col"
      >
        {/* Handle */}
        <div className="w-10 h-1 rounded-full bg-white/20 mx-auto mt-3 mb-1 sm:hidden shrink-0" />

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border)] shrink-0">
          <div>
            <p className="label mb-0.5">NOWE ŹRÓDŁO</p>
            <h2 className="headline text-base">Dodaj twórcę lub kanał</h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 glass rounded-lg flex items-center justify-center text-[var(--text-muted)] hover:text-white label text-base"
          >
            ×
          </button>
        </div>

        <div className="overflow-y-auto flex-1 p-5">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Type templates */}
            <div>
              <p className="label mb-2">TYP TREŚCI</p>
              <div className="grid grid-cols-2 gap-2">
                {CREATOR_TEMPLATES.map((t) => (
                  <button
                    key={t.source_type + t.category}
                    type="button"
                    onClick={() => applyTemplate(t)}
                    className={`flex items-center gap-2 p-3 rounded-xl text-sm font-medium border transition-all ${
                      template.source_type === t.source_type && template.category === t.category
                        ? "border-[var(--accent)] text-white"
                        : "border-[var(--border)] text-[var(--text-muted)] hover:border-[var(--border-bright)] hover:text-white"
                    }`}
                    style={
                      template.source_type === t.source_type && template.category === t.category
                        ? { background: `${t.color}15`, borderColor: t.color }
                        : {}
                    }
                  >
                    <span
                      className="text-base w-7 h-7 rounded flex items-center justify-center shrink-0"
                      style={{ background: t.color + "22", color: t.color }}
                    >
                      {t.icon}
                    </span>
                    <span className="text-xs font-semibold leading-tight">{t.label}</span>
                  </button>
                ))}
              </div>
              {template.hint && (
                <p className="label mt-1.5 text-[var(--text-dim)]">{template.hint}</p>
              )}
            </div>

            {/* URL */}
            <div>
              <label className="label mb-1.5 block">URL *</label>
              <input
                value={form.url}
                onChange={(e) => setF("url", e.target.value)}
                placeholder={template.placeholder}
                className="w-full glass rounded-xl px-4 py-2.5 text-sm outline-none border border-[var(--border)] focus:border-[var(--accent)] transition-colors font-mono"
              />
            </div>

            {/* Name */}
            <div>
              <label className="label mb-1.5 block">NAZWA</label>
              <input
                value={form.name}
                onChange={(e) => setF("name", e.target.value)}
                placeholder="np. Damian Olszewski"
                className="w-full glass rounded-xl px-4 py-2.5 text-sm outline-none border border-[var(--border)] focus:border-[var(--accent)] transition-colors"
              />
            </div>

            {/* Category */}
            <div>
              <label className="label mb-1.5 block">KATEGORIA</label>
              <div className="flex flex-wrap gap-1.5">
                {CATEGORIES.map(({ id, label }) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => setF("category", id)}
                    className={`label px-3 py-1.5 rounded border transition-colors ${
                      form.category === id
                        ? "border-[var(--accent)] text-[var(--accent)] bg-[var(--accent-glow)]"
                        : "border-[var(--border)] text-[var(--text-muted)] hover:border-[var(--border-bright)]"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Color */}
            <div>
              <label className="label mb-1.5 block">KOLOR</label>
              <div className="flex gap-2 flex-wrap">
                {COLORS.map((c) => (
                  <button
                    key={c}
                    type="button"
                    onClick={() => setF("color", c)}
                    className={`w-7 h-7 rounded-md transition-transform ${
                      form.color === c ? "scale-125 ring-2 ring-white ring-offset-1 ring-offset-[var(--bg)]" : "hover:scale-110"
                    }`}
                    style={{ background: c }}
                  />
                ))}
              </div>
            </div>

            {/* Notify toggle */}
            <label className="flex items-center gap-3 cursor-pointer">
              <div
                onClick={() => setF("notify", !form.notify)}
                className={`w-11 h-6 rounded-full transition-colors relative shrink-0 ${form.notify ? "accent-bg" : "bg-white/10"}`}
              >
                <span className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ${form.notify ? "translate-x-5.5" : "translate-x-0.5"}`} />
              </div>
              <div>
                <span className="text-sm font-medium">Powiadomienia push</span>
                <p className="label text-[var(--text-dim)]">Natychmiastowe alerty z tego źródła</p>
              </div>
            </label>

            {error && (
              <p className="text-xs font-mono text-red-400 px-1">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl accent-bg text-white font-semibold text-sm disabled:opacity-50 transition-opacity"
            >
              {loading ? "DODAWANIE..." : "DODAJ ŹRÓDŁO"}
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}
