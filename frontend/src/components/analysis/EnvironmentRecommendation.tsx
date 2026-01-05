/**
 * Environment Recommendation Component
 * Takes code analysis results and gets hardware recommendations from the decision engine
 */

import { useState } from "react";
import {
  Cpu,
  Zap,
  DollarSign,
  Clock,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Gauge,
  Lightbulb,
  ArrowRight,
  Sparkles,
  Server,
  GitBranch,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { decisionEngineService } from "@/services/decision-engine-service";
import type { AnalysisResult } from "@/types/codeAnalysis";
import {
  ProblemType,
  TimeComplexity,
  HardwareType,
  type CodeAnalysisInput,
  type DecisionEngineResponse,
} from "@/types/decision-engine.tp";

interface EnvironmentRecommendationProps {
  analysisResult: AnalysisResult;
}

// Map analysis result problem type to decision engine problem type
function mapProblemType(type: string): ProblemType {
  const mapping: Record<string, ProblemType> = {
    search: ProblemType.SEARCH,
    optimization: ProblemType.OPTIMIZATION,
    simulation: ProblemType.SIMULATION,
    machine_learning: ProblemType.MATRIX_OPS,
    factorization: ProblemType.FACTORIZATION,
    cryptography: ProblemType.FACTORIZATION,
    sampling: ProblemType.RANDOM_CIRCUIT,
    classical: ProblemType.SORTING,
    unknown: ProblemType.OPTIMIZATION,
  };
  return mapping[type] || ProblemType.OPTIMIZATION;
}

// Map time complexity string to decision engine enum
function mapTimeComplexity(complexity: string): TimeComplexity {
  const mapping: Record<string, TimeComplexity> = {
    "O(1)": TimeComplexity.POLYNOMIAL,
    "O(log n)": TimeComplexity.POLYNOMIAL,
    "O(n)": TimeComplexity.POLYNOMIAL,
    "O(n log n)": TimeComplexity.NLOGN,
    "O(n^2)": TimeComplexity.POLYNOMIAL,
    "O(n^3)": TimeComplexity.POLYNOMIAL,
    "O(2^n)": TimeComplexity.EXPONENTIAL,
    "O(n!)": TimeComplexity.EXPONENTIAL,
    "O(n^k)": TimeComplexity.POLYNOMIAL,
    "O(sqrt(n))": TimeComplexity.QUADRATIC_SPEEDUP,
    unknown: TimeComplexity.POLYNOMIAL,
  };
  return mapping[complexity] || TimeComplexity.POLYNOMIAL;
}

export function EnvironmentRecommendation({ analysisResult }: EnvironmentRecommendationProps) {
  const [budgetLimit, setBudgetLimit] = useState<string>("10.00");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendation, setRecommendation] = useState<DecisionEngineResponse | null>(null);

  const handleGetRecommendation = async () => {
    setIsLoading(true);
    setError(null);

    // Build the CodeAnalysisInput from the analysis result
    const input: CodeAnalysisInput = {
      problem_type: mapProblemType(analysisResult.problem_type),
      problem_size: analysisResult.problem_size,
      qubits_required: analysisResult.qubits_required,
      circuit_depth: analysisResult.circuit_depth,
      gate_count: analysisResult.gate_count,
      cx_gate_ratio: analysisResult.cx_gate_ratio,
      superposition_score: analysisResult.superposition_score,
      entanglement_score: analysisResult.entanglement_score,
      time_complexity: mapTimeComplexity(analysisResult.time_complexity),
      memory_requirement_mb: analysisResult.memory_requirement_mb,
    };

    try {
      const budget = parseFloat(budgetLimit) || undefined;
      const result = await decisionEngineService.predict(input, budget);
      setRecommendation(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get recommendation");
    } finally {
      setIsLoading(false);
    }
  };

  const getHardwareIcon = (hardware: HardwareType) => {
    switch (hardware) {
      case HardwareType.QUANTUM:
        return <Zap className="h-5 w-5" />;
      case HardwareType.CLASSICAL:
        return <Server className="h-5 w-5" />;
      case HardwareType.HYBRID:
        return <Cpu className="h-5 w-5" />;
    }
  };

  const getHardwareColor = (hardware: HardwareType) => {
    switch (hardware) {
      case HardwareType.QUANTUM:
        return "text-purple-400";
      case HardwareType.CLASSICAL:
        return "text-cyan-400";
      case HardwareType.HYBRID:
        return "text-amber-400";
    }
  };

  const getHardwareBadgeVariant = (hardware: HardwareType | string) => {
    if (hardware === HardwareType.QUANTUM || hardware === "Quantum") return "quantum";
    if (hardware === HardwareType.CLASSICAL || hardware === "Classical") return "default";
    return "warning";
  };

  return (
    <div className="space-y-4">
      <Separator />

      {/* Request Section */}
      <Card variant="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5 text-primary" />
            Environment Recommendation
          </CardTitle>
          <CardDescription>
            Get an AI-powered hardware recommendation based on your code analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
            <div className="flex-1">
              <Label className="text-sm text-muted-foreground">Budget Limit (USD)</Label>
              <div className="relative mt-1">
                <DollarSign className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={budgetLimit}
                  onChange={(e) => setBudgetLimit(e.target.value)}
                  placeholder="10.00"
                  className="bg-secondary/30 pl-9"
                />
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                Optional: Set a maximum cost per execution
              </p>
            </div>
            <Button
              variant="quantum"
              onClick={handleGetRecommendation}
              disabled={isLoading}
              className="gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Get Recommendation
                </>
              )}
            </Button>
          </div>

          {/* Input Parameters Preview */}
          <div className="mt-4 rounded-lg border border-border/50 bg-secondary/10 p-3">
            <p className="text-xs font-medium text-muted-foreground mb-2">Analysis Parameters</p>
            <div className="grid grid-cols-2 gap-2 text-xs sm:grid-cols-3 md:grid-cols-5">
              <div>
                <span className="text-muted-foreground">Problem: </span>
                <span className="font-mono">{analysisResult.problem_type}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Size: </span>
                <span className="font-mono">{analysisResult.problem_size}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Qubits: </span>
                <span className="font-mono">{analysisResult.qubits_required}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Depth: </span>
                <span className="font-mono">{analysisResult.circuit_depth}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Memory: </span>
                <span className="font-mono">{analysisResult.memory_requirement_mb.toFixed(2)}MB</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Recommendation Results */}
      {recommendation && recommendation.recommendation && (
        <div className="space-y-4 animate-fade-in">
          {/* Primary Recommendation Card */}
          <Card
            variant={recommendation.recommendation.recommended_hardware === HardwareType.QUANTUM ? "quantum" : "glass"}
            className={cn(
              "border-2 transition-all duration-500",
              recommendation.recommendation.recommended_hardware === HardwareType.QUANTUM
                ? "border-purple-500/50"
                : recommendation.recommendation.recommended_hardware === HardwareType.CLASSICAL
                ? "border-cyan-500/50"
                : "border-amber-500/50"
            )}
          >
            <CardHeader>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  Hardware Recommendation
                </CardTitle>
                <Badge
                  variant={getHardwareBadgeVariant(recommendation.recommendation.recommended_hardware)}
                  className="w-fit animate-pulse"
                >
                  {recommendation.recommendation.recommended_hardware} Execution
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {/* Confidence Score */}
                <div className="text-center">
                  <div className="relative mx-auto h-20 w-20">
                    <svg className="h-20 w-20 -rotate-90 transform">
                      <circle
                        cx="40"
                        cy="40"
                        r="32"
                        stroke="hsl(var(--border))"
                        strokeWidth="6"
                        fill="none"
                      />
                      <circle
                        cx="40"
                        cy="40"
                        r="32"
                        stroke={
                          recommendation.recommendation.recommended_hardware === HardwareType.QUANTUM
                            ? "hsl(var(--quantum))"
                            : "hsl(var(--primary))"
                        }
                        strokeWidth="6"
                        fill="none"
                        strokeDasharray={`${recommendation.recommendation.confidence * 100 * 2.01} ${100 * 2.01}`}
                        strokeLinecap="round"
                        className="transition-all duration-1000"
                      />
                    </svg>
                    <span className="absolute inset-0 flex items-center justify-center font-mono text-lg font-bold">
                      {Math.round(recommendation.recommendation.confidence * 100)}%
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">Confidence</p>
                </div>

                {/* Execution Time */}
                <div className="flex flex-col justify-center rounded-lg border border-border/50 bg-secondary/10 p-3">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    <span className="text-xs">Est. Execution Time</span>
                  </div>
                  <p className="mt-1 font-mono text-xl font-bold">
                    {recommendation.estimated_execution_time_ms
                      ? `${(recommendation.estimated_execution_time_ms / 1000).toFixed(2)}s`
                      : "N/A"}
                  </p>
                </div>

                {/* Cost */}
                <div className="flex flex-col justify-center rounded-lg border border-border/50 bg-secondary/10 p-3">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <DollarSign className="h-4 w-4" />
                    <span className="text-xs">Est. Cost</span>
                  </div>
                  <p className="mt-1 font-mono text-xl font-bold text-success">
                    ${recommendation.estimated_cost_usd?.toFixed(4) || "N/A"}
                  </p>
                </div>

                {/* Probabilities */}
                <div className="flex flex-col justify-center rounded-lg border border-border/50 bg-secondary/10 p-3">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Gauge className="h-4 w-4" />
                    <span className="text-xs">Quantum Probability</span>
                  </div>
                  <p className="mt-1 font-mono text-xl font-bold text-purple-400">
                    {Math.round(recommendation.recommendation.quantum_probability * 100)}%
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Classical: {Math.round(recommendation.recommendation.classical_probability * 100)}%
                  </p>
                </div>
              </div>

              {/* Rationale */}
              <div className="mt-4 rounded-lg border border-border/50 bg-secondary/20 p-4">
                <div className="flex items-center gap-2 text-sm font-semibold">
                  <Lightbulb className="h-4 w-4 text-amber-400" />
                  Decision Rationale
                </div>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                  {recommendation.recommendation.rationale}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Alternatives */}
          {recommendation.alternatives && recommendation.alternatives.length > 0 && (
            <Card variant="glass">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <GitBranch className="h-4 w-4 text-warning" />
                  Alternative Options
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  {recommendation.alternatives.map((alt, idx) => (
                    <div
                      key={idx}
                      className="rounded-lg border border-border/50 bg-secondary/10 p-4 transition-all hover:bg-secondary/20"
                    >
                      <div className="flex items-center justify-between">
                        <Badge variant={getHardwareBadgeVariant(alt.hardware)}>
                          {alt.hardware}
                        </Badge>
                        <span className="font-mono text-sm">
                          {Math.round(alt.confidence * 100)}% confidence
                        </span>
                      </div>
                      <p className="mt-2 text-xs text-muted-foreground">{alt.trade_off}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* No Recommendation Available */}
      {recommendation && !recommendation.recommendation && recommendation.error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{recommendation.error}</AlertDescription>
        </Alert>
      )}
    </div>
  );
}
