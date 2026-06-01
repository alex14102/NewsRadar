"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useFeedStats } from "@/hooks/useFeed";

const NAV_ITEMS = [
  { href: "/", icon: "⌂", label: "Feed" },
  { href: "/sources", icon: "⊕", label: "Źródła" },
  { href: "/bookmarks", icon: "♥", label: "Zapisane" },
  { href: "/settings", icon: "⚙", label: "Ustawienia" },
] as const;

export function BottomNav() {
  const pathname = usePathname();
  const stats = useFeedStats();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 glass-bright border-t border-white/8 safe-bottom">
      <div className="max-w-2xl mx-auto flex items-center">
        {NAV_ITEMS.map(({ href, icon, label }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex-1 flex flex-col items-center gap-1 py-3 text-xs transition-colors relative",
                active ? "text-[var(--accent)]" : "text-[var(--text-muted)] hover:text-white"
              )}
            >
              <span className="text-xl leading-none">{icon}</span>
              <span className="font-medium">{label}</span>
              {href === "/" && stats.unread > 0 && (
                <span className="absolute top-2 right-[calc(50%-14px)] w-4 h-4 rounded-full accent-bg text-white text-[9px] flex items-center justify-center font-bold">
                  {stats.unread > 9 ? "9+" : stats.unread}
                </span>
              )}
              {active && (
                <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-8 h-0.5 rounded-full accent-bg" />
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
