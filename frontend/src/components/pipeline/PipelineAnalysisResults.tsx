/**
 * Pipeline Analysis Results
 * Displays code analysis results inline within the pipeline flow.
 */

import {
  CheckCircle,
  Cpu,
  Code,
  BarChart3,
  Zap,
  Clock,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { AnalysisResult } from "@/types/codeAnalysis";
import { cn } from "@/lib/utils";

interface PipelineAnalysisResultsProps {
  result: AnalysisResult;
}

export function PipelineAnalysisResults({
  result,
}: PipelineAnalysisResultsProps) {
  const isQuantum = result.is_quantum;

  return (
    <Card variant="glass" className="animate-fade-in">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            Analysis Complete
          </CardTitle>
          <div className="flex gap-2">
            <Badge variant={isQuantum ? "quantum" : "classical"}>
              {isQuantum ? "Quantum" : "Classical"} Code
            </Badge>
            <Badge variant="outline">
              {result.detected_language}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <MetricCard
            icon={Code}
            label="Language"
            value={result.detected_language}
            subtext={`${(result.language_confidence * 100).toFixed(0)}% confidence`}
          />
          <MetricCard
            icon={BarChart3}
            label="Problem Type"
            value={result.problem_type}
            subtext={`Size: ${result.problem_size}`}
          />
          <MetricCard
            icon={Cpu}
            label="Qubits"
            value={String(result.qubits_required)}
            subtext={`Depth: ${result.circuit_depth}`}
          />
          <MetricCard
            icon={Zap}
            label="Gates"
            value={String(result.gate_count)}
            subtext={`CX ratio: ${(result.cx_gate_ratio * 100).toFixed(0)}%`}
          />
          <MetricCard
            icon={BarChart3}
            label="Superposition"
            value={`${(result.superposition_score * 100).toFixed(0)}%`}
            subtext={`Entanglement: ${(result.entanglement_score * 100).toFixed(0)}%`}
          />
          <MetricCard
            icon={Clock}
            label="Complexity"
            value={result.time_complexity}
            subtext={`${result.memory_requirement_mb.toFixed(1)} MB`}
          />
        </div>

        {result.detected_algorithms.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="text-xs text-muted-foreground">Detected algorithms:</span>
            {result.detected_algorithms.map((algo, i) => (
              <Badge key={i} variant="outline" className="text-xs">
                {algo}
              </Badge>
            ))}
          </div>
        )}

        {result.analysis_notes && (
          <div className="mt-3 rounded-lg bg-secondary/30 p-3">
            <p className="text-xs text-muted-foreground font-mono">
              {result.analysis_notes}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  subtext,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  subtext: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-secondary/20 p-3">
      <div className="flex items-center gap-1.5 text-muted-foreground mb-1">
        <Icon className="h-3.5 w-3.5" />
        <span className="text-xs">{label}</span>
      </div>
      <p className="font-mono text-sm font-bold truncate">{value}</p>
      <p className="text-xs text-muted-foreground truncate">{subtext}</p>
    </div>
  );
}
