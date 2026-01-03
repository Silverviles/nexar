import { CheckCircle, XCircle, Clock, History } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface Decision {
  id: string;
  timestamp: string;
  hardware: "quantum" | "classical" | "hybrid";
  confidence: number;
  status: "completed" | "failed" | "pending";
  cost: string;
}

const recentDecisions: Decision[] = [
  { id: "DEC-001", timestamp: "2 min ago", hardware: "quantum", confidence: 94, status: "completed", cost: "$0.42" },
  { id: "DEC-002", timestamp: "5 min ago", hardware: "classical", confidence: 88, status: "completed", cost: "$0.08" },
  { id: "DEC-003", timestamp: "12 min ago", hardware: "hybrid", confidence: 91, status: "completed", cost: "$0.25" },
  { id: "DEC-004", timestamp: "18 min ago", hardware: "quantum", confidence: 76, status: "failed", cost: "$0.00" },
  { id: "DEC-005", timestamp: "23 min ago", hardware: "classical", confidence: 97, status: "completed", cost: "$0.05" },
];

const hardwareBadge = {
  quantum: "quantum",
  classical: "classical",
  hybrid: "hybrid",
} as const;

const statusIcon = {
  completed: CheckCircle,
  failed: XCircle,
  pending: Clock,
};

const statusColor = {
  completed: "text-success",
  failed: "text-destructive",
  pending: "text-warning",
};

export function RecentDecisions() {
  return (
    <Card variant="glass" className="col-span-2">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <History className="h-5 w-5 text-primary" />
          Recent Decisions
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {recentDecisions.map((decision) => {
            const StatusIcon = statusIcon[decision.status];
            return (
              <div
                key={decision.id}
                className="flex flex-col gap-3 rounded-lg border border-border bg-secondary/20 p-3 transition-all hover:border-primary/30 hover:bg-secondary/40 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="flex items-center gap-3 sm:gap-4">
                  <StatusIcon className={cn("h-4 w-4 sm:h-5 sm:w-5", statusColor[decision.status])} />
                  <div>
                    <p className="font-mono text-xs font-medium sm:text-sm">{decision.id}</p>
                    <p className="text-xs text-muted-foreground">{decision.timestamp}</p>
                  </div>
                </div>
                <div className="flex items-center justify-between gap-2 sm:gap-4">
                  <Badge variant={hardwareBadge[decision.hardware]} className="capitalize text-xs">
                    {decision.hardware}
                  </Badge>
                  <div className="text-right">
                    <p className="font-mono text-xs font-bold sm:text-sm">{decision.confidence}%</p>
                    <p className="text-xs text-muted-foreground">confidence</p>
                  </div>
                  <p className="w-12 text-right font-mono text-xs text-muted-foreground sm:w-16 sm:text-sm">
                    {decision.cost}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
