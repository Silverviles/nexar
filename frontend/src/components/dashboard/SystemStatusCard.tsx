import { Activity, Cloud, Cpu, Server } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface SystemStatus {
  name: string;
  status: "online" | "offline" | "maintenance";
  queueLength?: number;
  icon: typeof Activity;
}

const systems: SystemStatus[] = [
  { name: "IBM Quantum", status: "online", queueLength: 12, icon: Cloud },
  { name: "Amazon Braket", status: "online", queueLength: 5, icon: Cloud },
  { name: "Classical GPU", status: "online", queueLength: 3, icon: Cpu },
  { name: "Classical CPU", status: "maintenance", queueLength: 0, icon: Server },
];

const statusConfig = {
  online: { color: "bg-success", text: "Online", badge: "success" as const },
  offline: { color: "bg-destructive", text: "Offline", badge: "destructive" as const },
  maintenance: { color: "bg-warning", text: "Maintenance", badge: "warning" as const },
};

export function SystemStatusCard() {
  return (
    <Card variant="glass" className="col-span-2">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            System Status
          </CardTitle>
          <Badge variant="quantum" className="animate-pulse-glow">
            Real-time
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 sm:grid-cols-2">
          {systems.map((system) => {
            const config = statusConfig[system.status];
            const Icon = system.icon;
            return (
              <div
                key={system.name}
                className="flex items-center justify-between rounded-lg border border-border bg-secondary/30 p-3 transition-all hover:border-primary/30"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
                    <Icon className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">{system.name}</p>
                    <div className="flex items-center gap-1.5">
                      <div
                        className={cn(
                          "h-2 w-2 rounded-full",
                          config.color,
                          system.status === "online" && "animate-pulse"
                        )}
                      />
                      <span className="text-xs text-muted-foreground">{config.text}</span>
                    </div>
                  </div>
                </div>
                {system.queueLength !== undefined && system.status === "online" && (
                  <div className="text-right">
                    <p className="font-mono text-lg font-bold text-foreground">
                      {system.queueLength}
                    </p>
                    <p className="text-xs text-muted-foreground">in queue</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
