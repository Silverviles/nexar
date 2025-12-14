import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    positive: boolean;
  };
  variant?: "default" | "quantum" | "success" | "warning";
}

const variantStyles = {
  default: "text-primary",
  quantum: "text-quantum",
  success: "text-success",
  warning: "text-warning",
};

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = "default",
}: MetricCardProps) {
  return (
    <Card variant="glass" className="group hover:border-primary/30 transition-all duration-300">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-secondary group-hover:bg-primary/10 transition-colors">
            <Icon className={cn("h-5 w-5 transition-colors", variantStyles[variant])} />
          </div>
          {trend && (
            <span
              className={cn(
                "flex items-center text-xs font-medium",
                trend.positive ? "text-success" : "text-destructive"
              )}
            >
              {trend.positive ? "↑" : "↓"} {trend.value}
            </span>
          )}
        </div>
        <div className="mt-4">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className={cn("mt-1 font-mono text-2xl font-bold", variantStyles[variant])}>
            {value}
          </p>
          {subtitle && <p className="mt-0.5 text-xs text-muted-foreground">{subtitle}</p>}
        </div>
      </CardContent>
    </Card>
  );
}
