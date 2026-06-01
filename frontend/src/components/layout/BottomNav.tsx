"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useFeedStats } from "@/hooks/useFeed";

const NAV_ITEMS = [
  {
    href: "/", label: "FEED",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      </svg>
    ),
  },
  {
    href: "/sources", label: "ŹRÓDŁA",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <circle cx="12" cy="12" r="3"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3m-4.22-7.78-2.12 2.12M7.1 16.9l-2.12 2.12m14.14 0-2.12-2.12M7.1 7.1 4.98 4.98"/>
      </svg>
    ),
  },
  {
    href: "/bookmarks", label: "ZAPISANE",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
      </svg>
    ),
  },
  {
    href: "/settings", label: "USTAWIENIA",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
      </svg>
    ),
  },
] as const;

export function BottomNav() {
  const pathname = usePathname();
  const stats = useFeedStats();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 glass-bright border-t border-[var(--border-bright)] safe-bottom">
      <div className="max-w-3xl mx-auto flex items-center">
        {NAV_ITEMS.map(({ href, label, icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex-1 flex flex-col items-center gap-1 py-3 transition-colors relative",
                active ? "text-[var(--accent)]" : "text-[var(--text-muted)] hover:text-white"
              )}
            >
              {icon}
              <span
                className="label text-[9px]"
                style={{ color: "inherit" }}
              >
                {label}
              </span>
              {href === "/" && stats.unread > 0 && (
                <span className="absolute top-1.5 right-[calc(50%-18px)] min-w-[16px] h-4 px-0.5 rounded-sm accent-bg text-white text-[8px] font-mono flex items-center justify-center">
                  {stats.unread > 99 ? "99+" : stats.unread}
                </span>
              )}
              {active && (
                <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-6 h-[2px] rounded-sm accent-bg" />
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
