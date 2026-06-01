"use client";
import { cn } from "@/lib/utils";

interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
  bright?: boolean;
  onClick?: () => void;
}

export function GlassPanel({ children, className, bright, onClick }: GlassPanelProps) {
  return (
    <div
      className={cn(
        "rounded-2xl",
        bright ? "glass-bright" : "glass",
        onClick && "cursor-pointer transition-all duration-200 hover:scale-[1.01] active:scale-[0.99]",
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
}
