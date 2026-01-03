/**
 * Quantum Metrics Display Component
 */

import {
  Cpu,
  Layers,
  Zap,
  Activity,
  Box,
  Clock,
  Sparkles,
  Link,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { MetricCard } from "./MetricCard";
import type { QuantumMetrics } from "@/types/codeAnalysis";

interface QuantumMetricsProps {
  metrics: QuantumMetrics;
  detectedAlgorithms: string[];
}

export function QuantumMetricsDisplay({
  metrics,
  detectedAlgorithms,
}: QuantumMetricsProps) {
  const getScoreColor = (score: number): "default" | "success" | "warning" => {
    if (score >= 0.7) return "success";
    if (score >= 0.4) return "default";
    return "warning";
  };

  return (
    <div className="space-y-4">
      {/* Header Card */}
      <Card variant="glass" className="border-purple-500/30 bg-purple-500/5">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-purple-400">
            <Cpu className="h-5 w-5" />
            Quantum Circuit Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {metrics.has_superposition && (
              <Badge variant="quantum" className="gap-1">
                <Sparkles className="h-3 w-3" />
                Superposition
              </Badge>
            )}
            {metrics.has_entanglement && (
              <Badge variant="quantum" className="gap-1">
                <Link className="h-3 w-3" />
                Entanglement
              </Badge>
            )}
            {detectedAlgorithms.length > 0 && (
              <Badge
                variant="outline"
                className="border-purple-400/30 text-purple-400"
              >
                {detectedAlgorithms.join(", ")}
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Core Quantum Metrics */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
        <MetricCard
          icon={Cpu}
          label="Qubits Required"
          value={metrics.qubits_required}
          subtitle="Quantum registers"
          variant="quantum"
          animate
        />

        <MetricCard
          icon={Layers}
          label="Circuit Depth"
          value={metrics.circuit_depth}
          subtitle="Gate layers"
          variant="quantum"
          animate
        />

        <MetricCard
          icon={Zap}
          label="Total Gates"
          value={metrics.gate_count}
          subtitle={`${metrics.single_qubit_gates} single, ${metrics.two_qubit_gates} two-qubit`}
          variant="quantum"
          animate
        />

        <MetricCard
          icon={Activity}
          label="CX Gate Ratio"
          value={`${(metrics.cx_gate_ratio * 100).toFixed(1)}%`}
          subtitle={`${metrics.cx_gate_count} CNOT gates`}
          variant={getScoreColor(metrics.cx_gate_ratio)}
          animate
        />

        <MetricCard
          icon={Box}
          label="Quantum Volume"
          value={metrics.quantum_volume ?? "N/A"}
          subtitle="Resource scale"
          variant="quantum"
          animate
        />

        <MetricCard
          icon={Clock}
          label="Est. Runtime"
          value={
            metrics.estimated_runtime_ms
              ? `${metrics.estimated_runtime_ms.toFixed(3)}ms`
              : "N/A"
          }
          subtitle="Execution time"
          variant="quantum"
          animate
        />
      </div>

      {/* Quantum Characteristics */}
      <Card variant="glass">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Quantum Characteristics</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Superposition Score */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-purple-400" />
                <span className="text-muted-foreground">
                  Superposition Potential
                </span>
              </div>
              <span className="font-mono font-semibold">
                {(metrics.superposition_score * 100).toFixed(1)}%
              </span>
            </div>
            <Progress
              value={metrics.superposition_score * 100}
              className="h-2"
            />
          </div>

          {/* Entanglement Score */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <Link className="h-4 w-4 text-purple-400" />
                <span className="text-muted-foreground">
                  Entanglement Complexity
                </span>
              </div>
              <span className="font-mono font-semibold">
                {(metrics.entanglement_score * 100).toFixed(1)}%
              </span>
            </div>
            <Progress
              value={metrics.entanglement_score * 100}
              className="h-2"
            />
          </div>
        </CardContent>
      </Card>

      {/* Gate Distribution */}
      <Card variant="glass">
        <CardContent className="pt-6">
          <div className="space-y-2 text-sm">
            <p className="text-muted-foreground">
              <span className="font-semibold text-foreground">
                Gate Composition:
              </span>{" "}
              Circuit contains {metrics.single_qubit_gates} single-qubit gates
              and {metrics.two_qubit_gates} two-qubit entangling gates.
            </p>
            <p className="text-muted-foreground">
              <span className="font-semibold text-foreground">
                Quantum Volume:
              </span>{" "}
              {metrics.quantum_volume
                ? `${metrics.quantum_volume} - indicates the circuit's computational power and error resilience.`
                : "Not calculated for this circuit."}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
