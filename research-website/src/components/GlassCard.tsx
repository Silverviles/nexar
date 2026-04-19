import * as React from "react";
import { cn } from "@/lib/utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  glow?: "cyan" | "violet" | "none";
}

export const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-2xl border border-border bg-card p-6 transition-all duration-300 hover:border-foreground/20",
        className,
      )}
      {...props}
    />
  ),
);
GlassCard.displayName = "GlassCard";
