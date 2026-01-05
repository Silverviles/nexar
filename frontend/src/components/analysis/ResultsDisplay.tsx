/**
 * Analysis Results Display Component
 */

import { useState, useEffect } from "react";
import { CheckCircle, Cpu, Code, BarChart3, Terminal } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ClassicalMetricsDisplay } from "./ClassicalMetrics";
import { QuantumMetricsDisplay } from "./QuantumMetrics";
import { EnvironmentRecommendation } from "./EnvironmentRecommendation";
import type { AnalysisResult } from "@/types/codeAnalysis";
import { getLanguageDisplayName } from "@/lib/languageDetection";
import { cn } from "@/lib/utils";

interface ResultsDisplayProps {
  result: AnalysisResult;
}

export function ResultsDisplay({ result }: ResultsDisplayProps) {
  const [terminalText, setTerminalText] = useState("");
  const isQuantum = result.is_quantum_eligible;
  const primaryColor = isQuantum ? "purple" : "cyan";

  // Typewriter effect for analysis notes
  useEffect(() => {
    setTerminalText("");
    let index = 0;
    const text = result.analysis_notes;

    const interval = setInterval(() => {
      if (index < text.length) {
        setTerminalText((prev) => prev + text[index]);
        index++;
      } else {
        clearInterval(interval);
      }
    }, 20);

    return () => clearInterval(interval);
  }, [result.analysis_notes]);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header - Routing Verdict */}
      <Card
        variant={isQuantum ? "quantum" : "glass"}
        className={cn(
          "border-2 transition-all duration-500",
          isQuantum
            ? "border-purple-500/50 bg-gradient-to-br from-purple-500/10 to-transparent"
            : "border-cyan-500/50 bg-gradient-to-br from-cyan-500/10 to-transparent"
        )}
      >
        <CardHeader>
          <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
            <div className="text-center sm:text-left">
              <CardTitle className="flex items-center justify-center gap-2 sm:justify-start">
                <CheckCircle className="h-6 w-6 text-success" />
                Analysis Complete
              </CardTitle>
              <p className="mt-2 text-sm text-muted-foreground">
                Language: {getLanguageDisplayName(result.detected_language)} •{" "}
                Confidence: {(result.confidence_score * 100).toFixed(1)}%
              </p>
            </div>

            <div className="flex flex-col items-center gap-2">
              <div
                className={cn(
                  "flex h-24 w-24 items-center justify-center rounded-full border-4",
                  isQuantum
                    ? "border-purple-500 bg-purple-500/20"
                    : "border-cyan-500 bg-cyan-500/20"
                )}
              >
                <div className="text-center">
                  <div
                    className={cn(
                      "text-2xl font-bold",
                      isQuantum ? "text-purple-400" : "text-cyan-400"
                    )}
                  >
                    {(result.confidence_score * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Confidence
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <div className="space-y-3">
            {/* Routing Decision */}
            <div className="rounded-lg border border-border/50 bg-secondary/20 p-4">
              <div className="flex items-center gap-2">
                {isQuantum ? (
                  <Cpu className="h-5 w-5 text-purple-400" />
                ) : (
                  <Code className="h-5 w-5 text-cyan-400" />
                )}
                <span className="text-lg font-semibold">
                  {isQuantum
                    ? "QUANTUM ELIGIBLE - NEURAL ROUTING RECOMMENDED"
                    : "OPTIMIZED FOR CLASSICAL EXECUTION"}
                </span>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">
                Problem Type: {result.problem_type.toUpperCase()} • Size:{" "}
                {result.problem_size} • Complexity: {result.time_complexity}
              </p>
            </div>

            {/* Key Metrics Summary */}
            <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
              <div className="rounded border border-border/50 bg-secondary/10 p-3">
                <div className="text-xs text-muted-foreground">Memory</div>
                <div className="mt-1 font-mono text-sm font-semibold">
                  {result.memory_requirement_mb.toFixed(3)} MB
                </div>
              </div>

              {isQuantum && (
                <>
                  <div className="rounded border border-border/50 bg-secondary/10 p-3">
                    <div className="text-xs text-muted-foreground">Qubits</div>
                    <div className="mt-1 font-mono text-sm font-semibold">
                      {result.qubits_required}
                    </div>
                  </div>

                  <div className="rounded border border-border/50 bg-secondary/10 p-3">
                    <div className="text-xs text-muted-foreground">
                      Circuit Depth
                    </div>
                    <div className="mt-1 font-mono text-sm font-semibold">
                      {result.circuit_depth}
                    </div>
                  </div>

                  <div className="rounded border border-border/50 bg-secondary/10 p-3">
                    <div className="text-xs text-muted-foreground">Gates</div>
                    <div className="mt-1 font-mono text-sm font-semibold">
                      {result.gate_count}
                    </div>
                  </div>
                </>
              )}

              {!isQuantum && result.classical_metrics && (
                <>
                  <div className="rounded border border-border/50 bg-secondary/10 p-3">
                    <div className="text-xs text-muted-foreground">
                      Complexity
                    </div>
                    <div className="mt-1 font-mono text-sm font-semibold">
                      {result.classical_metrics.cyclomatic_complexity}
                    </div>
                  </div>

                  <div className="rounded border border-border/50 bg-secondary/10 p-3">
                    <div className="text-xs text-muted-foreground">LOC</div>
                    <div className="mt-1 font-mono text-sm font-semibold">
                      {result.classical_metrics.lines_of_code}
                    </div>
                  </div>

                  <div className="rounded border border-border/50 bg-secondary/10 p-3">
                    <div className="text-xs text-muted-foreground">
                      Functions
                    </div>
                    <div className="mt-1 font-mono text-sm font-semibold">
                      {result.classical_metrics.function_count}
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Detected Algorithms */}
            {result.detected_algorithms.length > 0 && (
              <div className="rounded-lg border border-purple-500/30 bg-purple-500/5 p-4">
                <div className="flex items-center gap-2 text-sm font-semibold text-purple-400">
                  <BarChart3 className="h-4 w-4" />
                  Detected Algorithms
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {result.detected_algorithms.map((algo) => (
                    <Badge key={algo} variant="quantum">
                      {algo.replace(/_/g, " ").toUpperCase()}
                    </Badge>
                  ))}
                  {result.algorithm_detection_source && (
                    <Badge variant="outline" className="text-xs opacity-70">
                      {result.algorithm_detection_source}
                    </Badge>
                  )}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Detailed Metrics */}
      {result.quantum_metrics && (
        <QuantumMetricsDisplay
          metrics={result.quantum_metrics}
          detectedAlgorithms={result.detected_algorithms}
        />
      )}

      {result.classical_metrics && (
        <ClassicalMetricsDisplay
          metrics={result.classical_metrics}
          problemSize={result.problem_size}
        />
      )}

      {/* Terminal Output */}
      <Card variant="glass" className="border-border/50 bg-black/20">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base font-mono">
            <Terminal className="h-4 w-4" />
            Analysis Log
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md bg-black/40 p-4 font-mono text-xs">
            <div className="flex items-start gap-2">
              <span className="text-success">$</span>
              <div className="flex-1">
                <p className="text-success">{terminalText}</p>
                <span className="inline-block h-4 w-2 animate-pulse bg-success" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Environment Recommendation Section */}
      <EnvironmentRecommendation analysisResult={result} />
    </div>
  );
}
