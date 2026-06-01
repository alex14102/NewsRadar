"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNewsStore } from "@/store/useNewsStore";
import { API_BASE } from "@/lib/api";

export function ArticleModal() {
  const { selectedArticle, setSelectedArticle } = useNewsStore();
  const [bypassContent, setBypassContent] = useState<string | null>(null);
  const [bypassLoading, setBypassLoading] = useState(false);
  const [bypassUrls, setBypassUrls] = useState<{ service: string; url: string }[]>([]);

  const close = () => {
    setSelectedArticle(null);
    setBypassContent(null);
    setBypassUrls([]);
  };

  const fetchBypassUrls = async () => {
    if (!selectedArticle) return;
    const res = await fetch(`${API_BASE}/api/paywall/bypass`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: selectedArticle.url }),
    });
    const data = await res.json();
    setBypassUrls(data.bypass_urls ?? []);
  };

  const fetchFullContent = async () => {
    if (!selectedArticle) return;
    setBypassLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/paywall/fetch?url=${encodeURIComponent(selectedArticle.url)}`);
      const data = await res.json();
      setBypassContent(data.content ?? "Nie udało się pobrać treści.");
    } finally {
      setBypassLoading(false);
    }
  };

  if (!selectedArticle) return null;

  return (
    <AnimatePresence>
      <motion.div
        key="backdrop"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center p-0 sm:p-4"
        onClick={close}
      >
        <motion.div
          initial={{ y: "100%" }}
          animate={{ y: 0 }}
          exit={{ y: "100%" }}
          transition={{ type: "spring", damping: 30, stiffness: 300 }}
          className="w-full sm:max-w-2xl glass-bright rounded-t-3xl sm:rounded-3xl overflow-hidden max-h-[90dvh] flex flex-col"
          onClick={(e: React.MouseEvent) => e.stopPropagation()}
        >
          {/* Handle */}
          <div className="w-12 h-1 rounded-full bg-white/20 mx-auto mt-3 mb-1 sm:hidden" />

          {/* Header */}
          <div className="p-5 border-b border-white/8">
            <div className="flex items-start gap-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className="text-xs font-semibold px-2 py-0.5 rounded-full"
                    style={{
                      background: selectedArticle.source_color ? selectedArticle.source_color + "33" : "var(--accent-glow)",
                      color: selectedArticle.source_color || "var(--accent)",
                    }}
                  >
                    {selectedArticle.source_name}
                  </span>
                  {selectedArticle.is_paywalled && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400">
                      🔒 Paywall
                    </span>
                  )}
                </div>
                <h2 className="text-base font-bold leading-snug">{selectedArticle.title}</h2>
                {selectedArticle.author && (
                  <p className="text-xs text-[var(--text-muted)] mt-1">{selectedArticle.author}</p>
                )}
              </div>
              <button onClick={close} className="w-8 h-8 rounded-xl glass flex items-center justify-center text-[var(--text-muted)] hover:text-white">
                ×
              </button>
            </div>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {bypassContent ? (
              <div className="text-sm leading-relaxed space-y-3 text-[var(--text)]">
                {bypassContent.split("\n\n").map((p, i) => (
                  <p key={i}>{p}</p>
                ))}
              </div>
            ) : (
              <>
                {selectedArticle.summary && (
                  <p className="text-sm text-[var(--text-muted)] leading-relaxed">
                    {selectedArticle.summary}
                  </p>
                )}

                {/* Paywall bypass options */}
                {selectedArticle.is_paywalled && (
                  <div className="glass rounded-xl p-4 space-y-3">
                    <p className="text-xs font-semibold text-yellow-400">Artykuł za paywallem</p>
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={fetchFullContent}
                        disabled={bypassLoading}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium accent-bg text-white disabled:opacity-50"
                      >
                        {bypassLoading ? "Pobieranie..." : "📖 Odczytaj treść"}
                      </button>
                      <button
                        onClick={fetchBypassUrls}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium glass hover:text-white"
                      >
                        🔗 Pokaż linki bypass
                      </button>
                    </div>
                    {bypassUrls.length > 0 && (
                      <div className="flex flex-col gap-1">
                        {bypassUrls.map(({ service, url }) => (
                          <a
                            key={service}
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-[var(--accent)] hover:underline"
                          >
                            → Otwórz przez {service}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-white/8 flex gap-2">
            <a
              href={selectedArticle.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 py-2.5 rounded-xl accent-bg text-white text-sm font-semibold text-center"
            >
              Otwórz artykuł →
            </a>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
