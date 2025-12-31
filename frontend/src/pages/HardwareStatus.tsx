import { Atom, Server, Cpu, Clock, Wrench, Activity, DollarSign, Heart, AlertCircle, CheckCircle } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

interface SystemCard {
  name: string;
  type: "quantum" | "classical";
  status: "online" | "offline" | "maintenance";
  provider?: string;
  queueTime: string;
  qubits?: number;
  load?: number;
  costPerOp: string;
  uptime: string;
  errorRate: string;
}

const quantumSystems: SystemCard[] = [
  {
    name: "IBM Eagle R3",
    type: "quantum",
    status: "online",
    provider: "IBM Quantum",
    queueTime: "2m 15s",
    qubits: 127,
    costPerOp: "$0.42",
    uptime: "99.7%",
    errorRate: "0.3%",
  },
  {
    name: "IBM Heron",
    type: "quantum",
    status: "online",
    provider: "IBM Quantum",
    queueTime: "5m 30s",
    qubits: 133,
    costPerOp: "$0.58",
    uptime: "99.2%",
    errorRate: "0.5%",
  },
  {
    name: "Amazon IonQ Aria",
    type: "quantum",
    status: "online",
    provider: "Amazon Braket",
    queueTime: "1m 45s",
    qubits: 25,
    costPerOp: "$0.35",
    uptime: "99.9%",
    errorRate: "0.1%",
  },
  {
    name: "Amazon Rigetti Ankaa",
    type: "quantum",
    status: "maintenance",
    provider: "Amazon Braket",
    queueTime: "—",
    qubits: 84,
    costPerOp: "$0.28",
    uptime: "—",
    errorRate: "—",
  },
];

const classicalSystems: SystemCard[] = [
  {
    name: "GPU Cluster A",
    type: "classical",
    status: "online",
    queueTime: "30s",
    load: 67,
    costPerOp: "$0.08",
    uptime: "99.99%",
    errorRate: "0.01%",
  },
  {
    name: "GPU Cluster B",
    type: "classical",
    status: "online",
    queueTime: "15s",
    load: 42,
    costPerOp: "$0.08",
    uptime: "99.95%",
    errorRate: "0.02%",
  },
  {
    name: "CPU Pool - General",
    type: "classical",
    status: "online",
    queueTime: "5s",
    load: 28,
    costPerOp: "$0.02",
    uptime: "100%",
    errorRate: "0.00%",
  },
  {
    name: "CPU Pool - High Memory",
    type: "classical",
    status: "offline",
    queueTime: "—",
    load: 0,
    costPerOp: "$0.05",
    uptime: "—",
    errorRate: "—",
  },
];

const statusConfig = {
  online: { icon: CheckCircle, color: "text-success", bg: "bg-success/10" },
  offline: { icon: AlertCircle, color: "text-destructive", bg: "bg-destructive/10" },
  maintenance: { icon: Wrench, color: "text-warning", bg: "bg-warning/10" },
};

function SystemCardComponent({ system }: { system: SystemCard }) {
  const status = statusConfig[system.status];
  const StatusIcon = status.icon;

  return (
    <Card variant="glass" className={cn("transition-all hover:border-primary/30", system.status !== "online" && "opacity-60")}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={cn("flex h-10 w-10 items-center justify-center rounded-lg", system.type === "quantum" ? "bg-quantum/10" : "bg-classical/10")}>
              {system.type === "quantum" ? (
                <Atom className="h-5 w-5 text-quantum" />
              ) : system.name.includes("GPU") ? (
                <Cpu className="h-5 w-5 text-classical" />
              ) : (
                <Server className="h-5 w-5 text-classical" />
              )}
            </div>
            <div>
              <CardTitle className="text-base">{system.name}</CardTitle>
              {system.provider && (
                <CardDescription className="text-xs">{system.provider}</CardDescription>
              )}
            </div>
          </div>
          <Badge className={cn("gap-1", status.bg, status.color)} variant="outline">
            <StatusIcon className="h-3 w-3" />
            {system.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground flex items-center gap-1">
              <Clock className="h-3 w-3" /> Queue Time
            </p>
            <p className="font-mono font-medium">{system.queueTime}</p>
          </div>
          {system.qubits && (
            <div>
              <p className="text-muted-foreground">Qubits</p>
              <p className="font-mono font-medium">{system.qubits}</p>
            </div>
          )}
          {system.load !== undefined && (
            <div className="col-span-2">
              <p className="text-muted-foreground mb-1">Load</p>
              <div className="flex items-center gap-2">
                <Progress value={system.load} className="h-2" />
                <span className="font-mono text-xs">{system.load}%</span>
              </div>
            </div>
          )}
          <div>
            <p className="text-muted-foreground flex items-center gap-1">
              <DollarSign className="h-3 w-3" /> Cost/Op
            </p>
            <p className="font-mono font-medium text-success">{system.costPerOp}</p>
          </div>
          <div>
            <p className="text-muted-foreground flex items-center gap-1">
              <Heart className="h-3 w-3" /> Uptime
            </p>
            <p className="font-mono font-medium">{system.uptime}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function HardwareStatus() {
  return (
    <MainLayout title="Hardware Status" description="Real-time monitoring of quantum and classical systems">
      <div className="space-y-4 md:space-y-6">
        {/* Quantum Systems */}
        <section>
          <div className="mb-4 flex items-center gap-2">
            <Atom className="h-5 w-5 text-quantum" />
            <h2 className="text-lg font-semibold">Quantum Systems</h2>
            <Badge variant="quantum" className="ml-2">
              {quantumSystems.filter((s) => s.status === "online").length} / {quantumSystems.length} Online
            </Badge>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {quantumSystems.map((system) => (
              <SystemCardComponent key={system.name} system={system} />
            ))}
          </div>
        </section>

        {/* Classical Systems */}
        <section>
          <div className="mb-4 flex items-center gap-2">
            <Server className="h-5 w-5 text-classical" />
            <h2 className="text-lg font-semibold">Classical Systems</h2>
            <Badge variant="classical" className="ml-2">
              {classicalSystems.filter((s) => s.status === "online").length} / {classicalSystems.length} Online
            </Badge>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {classicalSystems.map((system) => (
              <SystemCardComponent key={system.name} system={system} />
            ))}
          </div>
        </section>

        {/* Live Pricing */}
        <section>
          <Card variant="glow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-primary" />
                Live Pricing Trends
              </CardTitle>
              <CardDescription>Current market rates for quantum and classical compute</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="rounded-lg border border-quantum/30 bg-quantum/5 p-4">
                  <p className="text-sm text-muted-foreground">Quantum Avg.</p>
                  <p className="font-mono text-2xl font-bold text-quantum">$0.41</p>
                  <p className="text-xs text-success">↓ 5% from yesterday</p>
                </div>
                <div className="rounded-lg border border-classical/30 bg-classical/5 p-4">
                  <p className="text-sm text-muted-foreground">GPU Avg.</p>
                  <p className="font-mono text-2xl font-bold text-classical">$0.08</p>
                  <p className="text-xs text-muted-foreground">No change</p>
                </div>
                <div className="rounded-lg border border-hybrid/30 bg-hybrid/5 p-4">
                  <p className="text-sm text-muted-foreground">CPU Avg.</p>
                  <p className="font-mono text-2xl font-bold text-hybrid">$0.03</p>
                  <p className="text-xs text-destructive">↑ 2% from yesterday</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>
      </div>
    </MainLayout>
  );
}
