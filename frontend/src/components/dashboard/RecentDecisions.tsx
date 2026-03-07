import { CheckCircle, XCircle, Clock, History, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface RecentDecision {
  id: string;
  hardware: string;
  confidence: number;
  status: string;
  cost: number | null;
  createdAt: string;
}

interface RecentDecisionsProps {
  decisions: RecentDecision[];
  isLoading: boolean;
}

const hardwareBadge: Record<string, "quantum" | "classical" | "hybrid"> = {
  quantum: "quantum",
  classical: "classical",
  hybrid: "hybrid",
};

const statusIcon: Record<string, typeof CheckCircle> = {
  executed: CheckCircle,
  failed: XCircle,
  predicted: Clock,
};

const statusColor: Record<string, string> = {
  executed: "text-success",
  failed: "text-destructive",
  predicted: "text-warning",
};

function timeAgo(dateStr: string): string {
  if (!dateStr) return "";
  const now = new Date();
  const date = new Date(dateStr);
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export function RecentDecisions({
  decisions,
  isLoading,
}: RecentDecisionsProps) {
  return (
    <Card variant="glass" className="col-span-2">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <History className="h-5 w-5 text-primary" />
          Recent Decisions
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
            <span className="ml-2 text-sm text-muted-foreground">
              Loading...
            </span>
          </div>
        ) : decisions.length === 0 ? (
          <div className="py-8 text-center text-sm text-muted-foreground">
            No decisions yet. Make your first prediction to see it here.
          </div>
        ) : (
          <div className="space-y-2">
            {decisions.map((decision) => {
              const StatusIcon = statusIcon[decision.status] || Clock;
              const badgeVariant = hardwareBadge[decision.hardware] || "hybrid";
              return (
                <div
                  key={decision.id}
                  className="flex flex-col gap-3 rounded-lg border border-border bg-secondary/20 p-3 transition-all hover:border-primary/30 hover:bg-secondary/40 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="flex items-center gap-3 sm:gap-4">
                    <StatusIcon
                      className={cn(
                        "h-4 w-4 sm:h-5 sm:w-5",
                        statusColor[decision.status] || "text-muted-foreground",
                      )}
                    />
                    <div>
                      <p className="font-mono text-xs font-medium sm:text-sm">
                        {decision.id.substring(0, 8)}...
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {timeAgo(decision.createdAt)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between gap-2 sm:gap-4">
                    <Badge
                      variant={badgeVariant}
                      className="capitalize text-xs"
                    >
                      {decision.hardware}
                    </Badge>
                    <div className="text-right">
                      <p className="font-mono text-xs font-bold sm:text-sm">
                        {decision.confidence}%
                      </p>
                      <p className="text-xs text-muted-foreground">
                        confidence
                      </p>
                    </div>
                    <p className="w-12 text-right font-mono text-xs text-muted-foreground sm:w-16 sm:text-sm">
                      {decision.cost !== null
                        ? `$${decision.cost.toFixed(2)}`
                        : "—"}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
