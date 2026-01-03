/**
 * Classical Metrics Display Component
 */

import { Code, GitBranch, Layers, Repeat, Zap, FileCode } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MetricCard } from "./MetricCard";
import type { ClassicalMetrics } from "@/types/codeAnalysis";

interface ClassicalMetricsProps {
  metrics: ClassicalMetrics;
  problemSize: number;
}

export function ClassicalMetricsDisplay({
  metrics,
  problemSize,
}: ClassicalMetricsProps) {
  const getComplexityColor = (
    complexity: number
  ): "default" | "success" | "warning" => {
    if (complexity <= 5) return "success";
    if (complexity <= 10) return "default";
    return "warning";
  };

  return (
    <div className="space-y-4">
      {/* Header Card */}
      <Card variant="glass" className="border-cyan-500/30 bg-cyan-500/5">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-cyan-400">
            <Code className="h-5 w-5" />
            Classical Code Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Badge
              variant="outline"
              className="border-cyan-400/30 text-cyan-400"
            >
              Problem Size: {problemSize}
            </Badge>
            <Badge
              variant="outline"
              className="border-cyan-400/30 text-cyan-400"
            >
              {metrics.time_complexity}
            </Badge>
            <Badge
              variant="outline"
              className="border-cyan-400/30 text-cyan-400"
            >
              Space: {metrics.space_complexity}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
        <MetricCard
          icon={GitBranch}
          label="Cyclomatic Complexity"
          value={metrics.cyclomatic_complexity}
          subtitle={`Cognitive: ${metrics.cognitive_complexity}`}
          variant={getComplexityColor(metrics.cyclomatic_complexity)}
          animate
        />

        <MetricCard
          icon={FileCode}
          label="Lines of Code"
          value={metrics.lines_of_code}
          subtitle="Analyzed lines"
          variant="classical"
          animate
        />

        <MetricCard
          icon={Repeat}
          label="Loop Count"
          value={metrics.loop_count}
          subtitle="Iterations detected"
          variant="classical"
          animate
        />

        <MetricCard
          icon={GitBranch}
          label="Conditionals"
          value={metrics.conditional_count}
          subtitle="Decision points"
          variant="classical"
          animate
        />

        <MetricCard
          icon={Layers}
          label="Nesting Depth"
          value={metrics.max_nesting_depth}
          subtitle="Maximum depth"
          variant={metrics.max_nesting_depth > 3 ? "warning" : "success"}
          animate
        />

        <MetricCard
          icon={Zap}
          label="Functions"
          value={metrics.function_count}
          subtitle="Defined functions"
          variant="classical"
          animate
        />
      </div>

      {/* Complexity Explanation */}
      <Card variant="glass">
        <CardContent className="pt-6">
          <div className="space-y-2 text-sm">
            <p className="text-muted-foreground">
              <span className="font-semibold text-foreground">
                Time Complexity:
              </span>{" "}
              {metrics.time_complexity} indicates the algorithm's growth rate
              relative to input size.
            </p>
            <p className="text-muted-foreground">
              <span className="font-semibold text-foreground">
                Cyclomatic Complexity:
              </span>{" "}
              {metrics.cyclomatic_complexity <= 5 &&
                "Low complexity - easy to maintain and test."}
              {metrics.cyclomatic_complexity > 5 &&
                metrics.cyclomatic_complexity <= 10 &&
                "Moderate complexity - acceptable maintainability."}
              {metrics.cyclomatic_complexity > 10 &&
                "High complexity - consider refactoring for better maintainability."}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
