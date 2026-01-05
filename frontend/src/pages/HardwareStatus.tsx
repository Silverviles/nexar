import {useEffect, useState} from "react";
import {
    Activity,
    AlertCircle,
    Atom,
    CheckCircle,
    Clock,
    Cpu,
    DollarSign,
    Heart,
    Loader2,
    Server,
    Wrench
} from "lucide-react";
import {MainLayout} from "@/components/layout/MainLayout";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card";
import {Badge} from "@/components/ui/badge";
import {Progress} from "@/components/ui/progress";
import {cn} from "@/lib/utils";
import {hardwareService} from "@/services/hardware-service";

interface SystemCard {
    name: string;
    type: "quantum" | "classical";
    status: "online" | "offline" | "maintenance";
    provider?: string;
    description?: string;
    version?: string;
    queueTime: string;
    qubits?: number;
    load?: number;
    costPerOp?: string;
    uptime?: string;
    errorRate?: string;
    basisGates?: string[];
}

const statusConfig = {
    online: {icon: CheckCircle, color: "text-success", bg: "bg-success/10"},
    offline: {icon: AlertCircle, color: "text-destructive", bg: "bg-destructive/10"},
    maintenance: {icon: Wrench, color: "text-warning", bg: "bg-warning/10"},
};

function SystemCardComponent({system}: { system: SystemCard }) {
    const status = statusConfig[system.status];
    const StatusIcon = status.icon;

    return (
        <Card variant="glass"
              className={cn("transition-all hover:border-primary/30", system.status !== "online" && "opacity-60")}>
            <CardHeader className="pb-3">
                <div className="flex justify-end mb-2">
                    <Badge className={cn("gap-1", status.bg, status.color)} variant="outline">
                        <StatusIcon className="h-3 w-3"/>
                        <span className="capitalize">{system.status}</span>
                    </Badge>
                </div>
                <div className="flex items-center gap-3">
                    <div
                        className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-lg", system.type === "quantum" ? "bg-quantum/10" : "bg-classical/10")}>
                        {system.type === "quantum" ? (
                            <Atom className="h-5 w-5 text-quantum"/>
                        ) : system.name.includes("GPU") ? (
                            <Cpu className="h-5 w-5 text-classical"/>
                        ) : (
                            <Server className="h-5 w-5 text-classical"/>
                        )}
                    </div>
                    <div className="min-w-0 flex-1">
                        <CardTitle className="text-base truncate" title={system.name}>{system.name}</CardTitle>
                        <div className="flex items-center gap-1.5 mt-0.5 overflow-hidden">
                            {system.provider && (
                                <CardDescription className="text-[10px] font-medium uppercase tracking-wider truncate shrink-0">{system.provider}</CardDescription>
                            )}
                            {system.version && (
                                <Badge variant="outline" className="text-[9px] px-1 py-0 h-3.5 bg-muted/50 whitespace-nowrap">v{system.version}</Badge>
                            )}
                        </div>
                    </div>
                </div>
                {system.description && (
                     <CardDescription className="text-xs line-clamp-1 mt-3 italic">{system.description}</CardDescription>
                )}
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <p className="text-muted-foreground flex items-center gap-1">
                            <Clock className="h-3 w-3"/> Queue Time
                        </p>
                        <p className="font-mono font-medium">{system.queueTime}</p>
                    </div>
                    {system.qubits !== undefined && system.qubits > 0 && (
                        <div>
                            <p className="text-muted-foreground">Qubits</p>
                            <p className="font-mono font-medium">{system.qubits}</p>
                        </div>
                    )}
                    {system.load !== undefined && (
                        <div className="col-span-2">
                            <p className="text-muted-foreground mb-1">Load</p>
                            <div className="flex items-center gap-2">
                                <Progress value={system.load} className="h-2"/>
                                <span className="font-mono text-xs">{system.load}%</span>
                            </div>
                        </div>
                    )}
                    {system.basisGates && system.basisGates.length > 0 && (
                         <div className="col-span-2">
                             <p className="text-muted-foreground mb-1 text-xs">Basis Gates</p>
                             <div className="flex flex-wrap gap-1">
                                 {system.basisGates.slice(0, 6).map(gate => (
                                     <Badge key={gate} variant="outline" className="text-[10px] px-1.5 py-0 bg-muted/30 border-muted-foreground/20">{gate}</Badge>
                                 ))}
                                 {system.basisGates.length > 6 && (
                                     <span className="text-[10px] text-muted-foreground">+{system.basisGates.length - 6}</span>
                                 )}
                             </div>
                         </div>
                    )}
                    {system.costPerOp && (
                        <div>
                            <p className="text-muted-foreground flex items-center gap-1">
                                <DollarSign className="h-3 w-3"/> Cost/Op
                            </p>
                            <p className="font-mono font-medium text-success">{system.costPerOp}</p>
                        </div>
                    )}
                    {system.uptime && (
                        <div>
                            <p className="text-muted-foreground flex items-center gap-1">
                                <Heart className="h-3 w-3"/> Uptime
                            </p>
                            <p className="font-mono font-medium">{system.uptime}</p>
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}

export default function HardwareStatus() {
    const [quantumSystems, setQuantumSystems] = useState<SystemCard[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchHardware = async () => {
            try {
                setLoading(true);
                const data = await hardwareService.getDevices();

                const mappedSystems: SystemCard[] = data.devices.map(device => {
                    const isQuantum = device.num_qubits !== undefined || device.is_simulator !== undefined;

                    let status: "online" | "offline" | "maintenance" = "online";
                    if (device.is_operational === false || device.status === "inactive" || device.status === "offline") {
                        status = "offline";
                    } else if (device.status === "maintenance") {
                        status = "maintenance";
                    }

                    return {
                        name: device.name.toUpperCase().replace(/_/g, " "),
                        type: isQuantum ? "quantum" : "classical",
                        status,
                        provider: device.provider,
                        description: device.description,
                        version: device.version,
                        queueTime: device.pending_jobs !== undefined && device.pending_jobs >= 0
                            ? `${device.pending_jobs * 2}m`
                            : isQuantum ? "—" : "5s",
                        qubits: device.num_qubits,
                        load: device.pending_jobs !== undefined && device.pending_jobs >= 0
                            ? Math.min(device.pending_jobs * 5, 100)
                            : isQuantum ? undefined : 15,
                        basisGates: device.basis_gates?.map(g => g.name),
                        costPerOp: undefined,
                        uptime: undefined,
                        errorRate: undefined,
                    };
                });

                setQuantumSystems(mappedSystems.filter(s => s.type === "quantum"));
                setError(null);
            } catch (err) {
                console.error("Failed to fetch hardware:", err);
                setError("Failed to load hardware status. Please check if the API is running.");
            } finally {
                setLoading(false);
            }
        };

        fetchHardware();
    }, []);

    return (
        <MainLayout title="Hardware Status" description="Real-time monitoring of quantum and classical systems">
            <div className="space-y-4 md:space-y-6">
                {loading ? (
                    <div className="flex h-64 items-center justify-center">
                        <div className="flex flex-col items-center gap-2">
                            <Loader2 className="h-8 w-8 animate-spin text-primary"/>
                            <p className="text-muted-foreground text-sm">Loading hardware systems...</p>
                        </div>
                    </div>
                ) : error ? (
                    <div className="flex h-64 items-center justify-center">
                        <Card variant="glass" className="border-destructive/30 bg-destructive/5 p-6 text-center">
                            <AlertCircle className="mx-auto mb-2 h-8 w-8 text-destructive"/>
                            <p className="text-destructive font-medium">{error}</p>
                        </Card>
                    </div>
                ) : (
                    <>
                        {/* Quantum Systems */}
                        <section>
                            <div className="mb-4 flex items-center gap-2">
                                <Atom className="h-5 w-5 text-quantum"/>
                                <h2 className="text-lg font-semibold">Quantum Systems</h2>
                                <Badge variant="quantum" className="ml-2">
                                    {quantumSystems.filter((s) => s.status === "online").length} / {quantumSystems.length} Online
                                </Badge>
                            </div>
                            {quantumSystems.length > 0 ? (
                                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                                    {quantumSystems.map((system) => (
                                        <SystemCardComponent key={system.name} system={system}/>
                                    ))}
                                </div>
                            ) : (
                                <div className="rounded-lg border border-dashed p-8 text-center">
                                    <p className="text-muted-foreground">No quantum systems available.</p>
                                </div>
                            )}
                        </section>

                        {/* Classical Systems */}
                        <section>
                            <div className="mb-4 flex items-center gap-2">
                                <Server className="h-5 w-5 text-classical"/>
                                <h2 className="text-lg font-semibold">Classical Systems</h2>
                            </div>
                        </section>
                    </>
                )}

                {/* Live Pricing */}
                <section>
                    <Card variant="glow">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Activity className="h-5 w-5 text-primary"/>
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
