"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSources, updateSource, deleteSource, addPresets } from "@/hooks/useSources";
import { AddSourceModal } from "./AddSourceModal";
import { sourceTypeIcon } from "@/lib/utils";
import type { Source } from "@/types";

export function SourceManager() {
  const { sources, isLoading, mutate } = useSources();
  const [showAdd, setShowAdd] = useState(false);
  const [addingPresets, setAddingPresets] = useState(false);

  const handleToggle = async (source: Source) => {
    await updateSource(source.id, { enabled: !source.enabled });
    mutate();
  };

  const handleNotify = async (source: Source) => {
    await updateSource(source.id, { notify: !source.notify });
    mutate();
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Usunąć to źródło?")) return;
    await deleteSource(id);
    mutate();
  };

  const handleAddPresets = async () => {
    setAddingPresets(true);
    const res = await addPresets();
    mutate();
    setAddingPresets(false);
    alert(`Dodano ${res.added?.length ?? 0} polskich źródeł`);
  };

  const groupedByCategory = sources.reduce<Record<string, Source[]>>((acc: Record<string, Source[]>, s: Source) => {
    if (!acc[s.category]) acc[s.category] = [];
    acc[s.category].push(s);
    return acc;
  }, {});

  if (isLoading) {
    return (
      <div className="flex flex-col gap-3 p-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="glass rounded-xl h-16 animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <>
      <div className="p-4 space-y-6 pb-24">
        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={() => setShowAdd(true)}
            className="flex-1 py-2.5 rounded-xl accent-bg text-white text-sm font-semibold"
          >
            + Dodaj źródło
          </button>
          <button
            onClick={handleAddPresets}
            disabled={addingPresets}
            className="px-4 py-2.5 rounded-xl glass text-sm font-medium hover:text-white disabled:opacity-50"
          >
            {addingPresets ? "..." : "🇵🇱 Presety PL"}
          </button>
        </div>

        {/* Sources grouped by category */}
        {Object.entries(groupedByCategory).map(([category, items]) => (
          <div key={category}>
            <h3 className="text-xs font-mono font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2 px-1">
              {category}
            </h3>
            <div className="flex flex-col gap-2">
              <AnimatePresence>
                {items.map((source) => (
                  <motion.div
                    key={source.id}
                    layout
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    className={`glass rounded-xl p-3 flex items-center gap-3 ${!source.enabled ? "opacity-40" : ""}`}
                  >
                    {/* Color dot */}
                    <div
                      className="w-3 h-3 rounded-full shrink-0"
                      style={{ background: source.color || "var(--accent)" }}
                    />

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs">{sourceTypeIcon(source.source_type)}</span>
                        <span className="text-sm font-medium truncate">{source.name}</span>
                      </div>
                      <p className="text-[10px] font-mono text-[var(--text-dim)] truncate mt-0.5">
                        {source.url}
                      </p>
                    </div>

                    {/* Controls */}
                    <div className="flex items-center gap-1.5 shrink-0">
                      <button
                        onClick={() => handleNotify(source)}
                        className={`text-base transition-colors ${source.notify ? "text-[var(--accent)]" : "text-[var(--text-dim)] hover:text-white"}`}
                        title="Powiadomienia"
                      >
                        {source.notify ? "🔔" : "🔕"}
                      </button>
                      <button
                        onClick={() => handleToggle(source)}
                        className={`w-10 h-5 rounded-full transition-colors relative ${source.enabled ? "accent-bg" : "bg-white/10"}`}
                      >
                        <span
                          className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${source.enabled ? "translate-x-5" : "translate-x-0.5"}`}
                        />
                      </button>
                      <button
                        onClick={() => handleDelete(source.id)}
                        className="text-[var(--text-dim)] hover:text-red-400 transition-colors text-lg leading-none"
                      >
                        ×
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>
        ))}

        {sources.length === 0 && (
          <div className="py-12 text-center space-y-3">
            <p className="text-4xl">📡</p>
            <p className="text-sm text-[var(--text-muted)]">Brak źródeł</p>
            <p className="text-xs text-[var(--text-dim)]">Dodaj źródła lub załaduj polskie presety</p>
          </div>
        )}
      </div>

      {showAdd && <AddSourceModal onClose={() => { setShowAdd(false); mutate(); }} />}
    </>
  );
}
