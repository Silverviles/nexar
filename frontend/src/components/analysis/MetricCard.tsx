/**
 * Reusable Metric Card Component
 */

import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  subtitle?: string;
  variant?: "default" | "quantum" | "classical" | "success" | "warning";
  className?: string;
  animate?: boolean;
}

const variantStyles = {
  default: "border-border bg-secondary/20",
  quantum: "border-purple-500/30 bg-purple-500/5",
  classical: "border-cyan-500/30 bg-cyan-500/5",
  success: "border-success/30 bg-success/5",
  warning: "border-warning/30 bg-warning/5",
};

const valueColorStyles = {
  default: "text-foreground",
  quantum: "text-purple-400",
  classical: "text-cyan-400",
  success: "text-success",
  warning: "text-warning",
};

export function MetricCard({
  icon: Icon,
  label,
  value,
  subtitle,
  variant = "default",
  className,
  animate = false,
}: MetricCardProps) {
  return (
    <div
      className={cn(
        "rounded-lg border p-4 transition-all duration-300",
        variantStyles[variant],
        animate && "animate-fade-in",
        className
      )}
    >
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Icon className="h-4 w-4" />
        {label}
      </div>
      <p
        className={cn(
          "mt-2 font-mono text-2xl font-bold",
          valueColorStyles[variant]
        )}
      >
        {value}
      </p>
      {subtitle && (
        <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>
      )}
    </div>
  );
}
