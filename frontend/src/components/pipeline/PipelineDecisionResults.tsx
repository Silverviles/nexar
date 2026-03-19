/**
 * Pipeline Decision Results
 * Displays the Decision Engine recommendation within the pipeline flow.
 */

import { useState } from "react";
import {
  Award,
  Clock,
  DollarSign,
  Gauge,
  Brain,
  GitBranch,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  ArrowRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  type DecisionEngineResponse,
  type CodeAnalysisInput,
  HardwareType,
} from "@/types/decision-engine.tp";
import { cn } from "@/lib/utils";

/** Format execution time (ms) into a readable string */
function formatTime(ms: number | null | undefined): string {
  if (ms == null) return "N/A";
  if (ms > 1e15) return "Infeasible";
  const s = ms / 1000;
  if (s < 1) return `${ms.toFixed(0)}ms`;
  if (s < 60) return `${s.toFixed(2)}s`;
  if (s < 3600) return `${Math.floor(s / 60)}m ${Math.round(s % 60)}s`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ${Math.round((s % 3600) / 60)}m`;
  const days = s / 86400;
  if (days < 365) return `${days.toFixed(1)} days`;
  return `${(days / 365).toFixed(1)} years`;
}

/** Format cost (USD) into a readable string */
function formatCost(usd: number | null | undefined): string {
  if (usd == null) return "N/A";
  if (usd > 1e12) return "Infeasible";
  if (usd < 0.01) return `$${usd.toFixed(6)}`;
  if (usd < 1000) return `$${usd.toFixed(2)}`;
  if (usd < 1e6) return `$${(usd / 1000).toFixed(1)}K`;
  if (usd < 1e9) return `$${(usd / 1e6).toFixed(1)}M`;
  return `$${(usd / 1e9).toFixed(1)}B`;
}

interface PipelineDecisionResultsProps {
  result: DecisionEngineResponse;
  mappedInput: CodeAnalysisInput | null;
}

export function PipelineDecisionResults({
  result,
  mappedInput,
}: PipelineDecisionResultsProps) {
  const [showMappedInput, setShowMappedInput] = useState(false);

  if (!result.recommendation) {
    return (
      <Card variant="glass" className="animate-fade-in">
        <CardContent className="py-6">
          <p className="text-sm text-muted-foreground">
            Decision Engine did not return a recommendation.
            {result.error && ` Error: ${result.error}`}
          </p>
        </CardContent>
      </Card>
    );
  }

  const { recommendation, alternatives, estimated_execution_time_ms, estimated_cost_usd } = result;
  const isQuantum = recommendation.recommended_hardware === HardwareType.QUANTUM;
  const confidencePercent = Math.round(recommendation.confidence * 100);

  const getBadgeVariant = (hardware: string) => {
    if (hardware === "Quantum") return "quantum" as const;
    if (hardware === "Classical") return "classical" as const;
    return "hybrid" as const;
  };

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Primary Recommendation */}
      <Card variant={isQuantum ? "quantum" : "glass"}>
        <CardHeader>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5" />
              Hardware Recommendation
            </CardTitle>
            <Badge
              variant={getBadgeVariant(recommendation.recommended_hardware)}
              className="animate-pulse-glow"
            >
              {recommendation.recommended_hardware} Execution
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {/* Confidence */}
            <div className="text-center">
              <div className="relative mx-auto h-20 w-20">
                <svg className="h-20 w-20 -rotate-90 transform">
                  <circle
                    cx="40" cy="40" r="34"
                    stroke="hsl(var(--border))"
                    strokeWidth="6" fill="none"
                  />
                  <circle
                    cx="40" cy="40" r="34"
                    stroke={isQuantum ? "hsl(var(--quantum))" : "hsl(var(--classical))"}
                    strokeWidth="6" fill="none"
                    strokeDasharray={`${confidencePercent * 2.136} ${100 * 2.136}`}
                    strokeLinecap="round"
                  />
                </svg>
                <span className="absolute inset-0 flex items-center justify-center font-mono text-xl font-bold">
                  {confidencePercent}%
                </span>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">Confidence</p>
            </div>

            {/* Time */}
            <div className="flex flex-col justify-center">
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Clock className="h-3.5 w-3.5" />
                <span className="text-xs">Expected Time</span>
              </div>
              <p className="mt-1 font-mono text-xl font-bold">
                {formatTime(estimated_execution_time_ms)}
              </p>
            </div>

            {/* Cost */}
            <div className="flex flex-col justify-center">
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <DollarSign className="h-3.5 w-3.5" />
                <span className="text-xs">Estimated Cost</span>
              </div>
              <p className="mt-1 font-mono text-xl font-bold">
                {formatCost(estimated_cost_usd)}
              </p>
            </div>

            {/* Probabilities */}
            <div className="flex flex-col justify-center">
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Gauge className="h-3.5 w-3.5" />
                <span className="text-xs">Quantum Prob.</span>
              </div>
              <p
                className={cn(
                  "mt-1 font-mono text-xl font-bold",
                  isQuantum && "text-quantum"
                )}
              >
                {Math.round(recommendation.quantum_probability * 100)}%
              </p>
              <p className="text-xs text-muted-foreground">
                Classical: {Math.round(recommendation.classical_probability * 100)}%
              </p>
            </div>
          </div>

          {/* Rationale */}
          <div className="mt-4 rounded-lg border border-border bg-secondary/20 p-3">
            <div className="flex items-center gap-2 mb-2">
              <MessageSquare className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium">Rationale</span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {recommendation.rationale}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Alternatives */}
      {alternatives && alternatives.length > 0 && (
        <Card variant="glass">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <GitBranch className="h-4 w-4 text-warning" />
              Alternatives
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alternatives.map((alt, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between rounded-lg border border-border bg-secondary/20 p-3"
                >
                  <div className="flex items-center gap-3">
                    <Badge variant={getBadgeVariant(alt.hardware)}>
                      {alt.hardware}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {alt.trade_off}
                    </span>
                  </div>
                  <span className="font-mono text-sm">
                    {(alt.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Mapped Input (debug/transparency) */}
      {mappedInput && (
        <div className="rounded-lg border border-border bg-secondary/10 p-3">
          <button
            onClick={() => setShowMappedInput(!showMappedInput)}
            className="flex w-full items-center justify-between text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            <span className="flex items-center gap-1.5">
              <Brain className="h-3.5 w-3.5" />
              View mapped parameters sent to Decision Engine
            </span>
            {showMappedInput ? (
              <ChevronUp className="h-3.5 w-3.5" />
            ) : (
              <ChevronDown className="h-3.5 w-3.5" />
            )}
          </button>
          {showMappedInput && (
            <pre className="mt-2 overflow-x-auto rounded bg-secondary/30 p-3 text-xs font-mono">
              {JSON.stringify(mappedInput, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
