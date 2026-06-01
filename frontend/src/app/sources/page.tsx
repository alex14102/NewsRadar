"use client";
import { BottomNav } from "@/components/layout/BottomNav";
import { SourceManager } from "@/components/sources/SourceManager";

export default function SourcesPage() {
  return (
    <div className="min-h-dvh flex flex-col">
      <header className="sticky top-0 z-40 glass-bright border-b border-white/8 safe-top">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl accent-bg flex items-center justify-center text-white font-bold text-sm">N</div>
          <h1 className="font-bold text-lg">Źródła</h1>
        </div>
      </header>

      <main className="flex-1 max-w-2xl w-full mx-auto">
        <SourceManager />
      </main>

      <BottomNav />
    </div>
  );
}
