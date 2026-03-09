/**
 * Code Quality Score Component
 * Displays overall code quality metrics with detailed breakdown
 */

import { useState } from "react";
import { AlertCircle, TrendingUp, Zap, Gauge } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import type { CodeQualityMetrics } from "@/types/codeAnalysis";
import { cn } from "@/lib/utils";

interface CodeQualityScoreProps {
  metrics: CodeQualityMetrics;
}

export function CodeQualityScore({ metrics }: CodeQualityScoreProps) {
  const [open, setOpen] = useState(false);

  const getScoreColor = (score: number): string => {
    if (score >= 80) return "text-success";
    if (score >= 60) return "text-cyan-400";
    if (score >= 40) return "text-yellow-500";
    return "text-destructive";
  };

  const getScoreBgColor = (score: number): string => {
    if (score >= 80) return "bg-success/10 border-success/30";
    if (score >= 60) return "bg-cyan-500/10 border-cyan-500/30";
    if (score >= 40) return "bg-yellow-500/10 border-yellow-500/30";
    return "bg-destructive/10 border-destructive/30";
  };

  const getCertaintyLevel = (
    score: number,
  ): "Excellent" | "Good" | "Fair" | "Poor" => {
    if (score >= 80) return "Excellent";
    if (score >= 60) return "Good";
    if (score >= 40) return "Fair";
    return "Poor";
  };

  return (
    <Card variant="glass" className="border-blue-500/30 bg-blue-500/5">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-blue-400">
            <Gauge className="h-5 w-5" />
            Code Quality Assessment
          </div>
          <Badge variant="outline" className="border-blue-400/30 text-blue-400">
            {getCertaintyLevel(metrics.overall_score)}
          </Badge>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Overall Score - Large */}
        <div className="flex items-center justify-between rounded-lg border border-border/50 bg-secondary/10 p-4">
          <div>
            <p className="text-xs text-muted-foreground">Overall Score</p>
            <p
              className={cn(
                "text-3xl font-bold",
                getScoreColor(metrics.overall_score),
              )}
            >
              {metrics.overall_score.toFixed(1)}/100
            </p>
          </div>
          <div
            className={cn(
              "flex h-20 w-20 items-center justify-center rounded-full border-2",
              getScoreBgColor(metrics.overall_score).split(" ").slice(0, 1)[0],
              "border-blue-500",
            )}
          >
            <div className="text-center">
              <div className="text-xl font-bold text-blue-400">
                {metrics.overall_score.toFixed(0)}%
              </div>
            </div>
          </div>
        </div>

        {/* Individual Metrics */}
        <div className="space-y-3">
          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-muted-foreground">Maintainability</span>
              <span className="font-mono text-xs font-semibold">
                {metrics.maintainability_score.toFixed(0)}/100
              </span>
            </div>
            <Progress value={metrics.maintainability_score} className="h-2" />
          </div>

          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-muted-foreground">Performance</span>
              <span className="font-mono text-xs font-semibold">
                {metrics.performance_score.toFixed(0)}/100
              </span>
            </div>
            <Progress value={metrics.performance_score} className="h-2" />
          </div>

          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-muted-foreground">Resource Efficiency</span>
              <span className="font-mono text-xs font-semibold">
                {metrics.resource_efficiency_score.toFixed(0)}/100
              </span>
            </div>
            <Progress
              value={metrics.resource_efficiency_score}
              className="h-2"
            />
          </div>

          <div className="flex items-center gap-2 rounded-lg border border-border/50 bg-secondary/10 p-3">
            <AlertCircle className="h-4 w-4 text-yellow-500" />
            <div>
              <p className="text-xs text-muted-foreground">Complexity Rating</p>
              <p className="font-semibold">{metrics.code_complexity_rating}</p>
            </div>
          </div>
        </div>

        {/* Detailed View Button */}
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" className="w-full gap-2" size="sm">
              <TrendingUp className="h-4 w-4" />
              View Detailed Analysis
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Quality Metrics Breakdown</DialogTitle>
              <DialogDescription>
                Detailed analysis of code quality indicators
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="rounded-lg border border-border p-4">
                <h4 className="font-semibold mb-2">
                  Maintainability ({metrics.maintainability_score.toFixed(1)}
                  /100)
                </h4>
                <p className="text-xs text-muted-foreground mb-2">
                  Measures how easy the code is to understand and modify.
                  Affected by cyclomatic complexity and nesting depth.
                </p>
                <Progress
                  value={metrics.maintainability_score}
                  className="h-2"
                />
              </div>

              <div className="rounded-lg border border-border p-4">
                <h4 className="font-semibold mb-2">
                  Performance ({metrics.performance_score.toFixed(1)}/100)
                </h4>
                <p className="text-xs text-muted-foreground mb-2">
                  Evaluates algorithm efficiency and resource utilization. Lower
                  time complexity indicates better performance.
                </p>
                <Progress value={metrics.performance_score} className="h-2" />
              </div>

              <div className="rounded-lg border border-border p-4">
                <h4 className="font-semibold mb-2">
                  Resource Efficiency (
                  {metrics.resource_efficiency_score.toFixed(1)}/100)
                </h4>
                <p className="text-xs text-muted-foreground mb-2">
                  Assessment of memory and computational resource usage. Lower
                  space complexity is better.
                </p>
                <Progress
                  value={metrics.resource_efficiency_score}
                  className="h-2"
                />
              </div>

              <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/5 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="h-4 w-4 text-yellow-500" />
                  <h4 className="font-semibold">Complexity Rating</h4>
                </div>
                <p className="text-sm">{metrics.code_complexity_rating}</p>
                <p className="text-xs text-muted-foreground mt-2">
                  {metrics.code_complexity_rating === "Very High"
                    ? "Consider refactoring: High complexity increases bug risk and maintenance effort."
                    : metrics.code_complexity_rating === "High"
                      ? "Monitor complexity: Consider structural improvements for better maintainability."
                      : "Good complexity level for this code type."}
                </p>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
}
