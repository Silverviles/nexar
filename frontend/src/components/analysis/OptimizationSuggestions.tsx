/**
 * Optimization Suggestions Component
 * Displays actionable optimization recommendations
 */

import { useState } from "react";
import {
  Lightbulb,
  AlertTriangle,
  AlertCircle,
  Info,
  ChevronDown,
  CheckCircle,
  Zap,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { OptimizationSuggestion } from "@/types/codeAnalysis";
import { cn } from "@/lib/utils";

interface OptimizationSuggestionsProps {
  suggestions: OptimizationSuggestion[];
}

export function OptimizationSuggestions({
  suggestions,
}: OptimizationSuggestionsProps) {
  const [expandedId, setExpandedId] = useState<number | null>(
    suggestions.length > 0 ? 0 : null,
  );

  if (!suggestions || suggestions.length === 0) {
    return (
      <Card variant="glass" className="border-success/30 bg-success/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-success">
            <CheckCircle className="h-5 w-5" />
            Code Optimization
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            ✓ No major optimization opportunities detected. Your code is
            well-structured!
          </p>
        </CardContent>
      </Card>
    );
  }

  const severityIcon = {
    high: <AlertTriangle className="h-4 w-4" />,
    medium: <AlertCircle className="h-4 w-4" />,
    low: <Info className="h-4 w-4" />,
  };

  const severityColor = {
    high: "border-destructive/30 bg-destructive/5 text-destructive",
    medium: "border-yellow-500/30 bg-yellow-500/5 text-yellow-500",
    low: "border-cyan-500/30 bg-cyan-500/5 text-cyan-500",
  };

  const highSuggestions = suggestions.filter((s) => s.severity === "high");
  const mediumSuggestions = suggestions.filter((s) => s.severity === "medium");
  const lowSuggestions = suggestions.filter((s) => s.severity === "low");

  return (
    <div className="space-y-3">
      <Card variant="glass">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-yellow-400" />
              Optimization Opportunities
            </div>
            <Badge variant="outline" className="gap-1">
              <Zap className="h-3 w-3" />
              {suggestions.length} suggestions
            </Badge>
          </CardTitle>
        </CardHeader>
      </Card>

      {/* High Severity */}
      {highSuggestions.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase text-destructive/80 px-2">
            High Priority ({highSuggestions.length})
          </h3>
          {highSuggestions.map((suggestion, idx) => (
            <SuggestionCard
              key={`high-${idx}`}
              suggestion={suggestion}
              index={suggestions.indexOf(suggestion)}
              isExpanded={expandedId === suggestions.indexOf(suggestion)}
              onToggle={() =>
                setExpandedId(
                  expandedId === suggestions.indexOf(suggestion)
                    ? null
                    : suggestions.indexOf(suggestion),
                )
              }
            />
          ))}
        </div>
      )}

      {/* Medium Severity */}
      {mediumSuggestions.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase text-yellow-500/80 px-2">
            Medium Priority ({mediumSuggestions.length})
          </h3>
          {mediumSuggestions.map((suggestion, idx) => (
            <SuggestionCard
              key={`medium-${idx}`}
              suggestion={suggestion}
              index={suggestions.indexOf(suggestion)}
              isExpanded={expandedId === suggestions.indexOf(suggestion)}
              onToggle={() =>
                setExpandedId(
                  expandedId === suggestions.indexOf(suggestion)
                    ? null
                    : suggestions.indexOf(suggestion),
                )
              }
            />
          ))}
        </div>
      )}

      {/* Low Severity */}
      {lowSuggestions.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase text-cyan-500/80 px-2">
            Low Priority ({lowSuggestions.length})
          </h3>
          {lowSuggestions.map((suggestion, idx) => (
            <SuggestionCard
              key={`low-${idx}`}
              suggestion={suggestion}
              index={suggestions.indexOf(suggestion)}
              isExpanded={expandedId === suggestions.indexOf(suggestion)}
              onToggle={() =>
                setExpandedId(
                  expandedId === suggestions.indexOf(suggestion)
                    ? null
                    : suggestions.indexOf(suggestion),
                )
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}

function SuggestionCard({
  suggestion,
  index,
  isExpanded,
  onToggle,
}: {
  suggestion: OptimizationSuggestion;
  index: number;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const severityColor = {
    high: "border-destructive/30 bg-destructive/5",
    medium: "border-yellow-500/30 bg-yellow-500/5",
    low: "border-cyan-500/30 bg-cyan-500/5",
  };

  const severityIcon = {
    high: <AlertTriangle className="h-4 w-4 text-destructive" />,
    medium: <AlertCircle className="h-4 w-4 text-yellow-500" />,
    low: <Info className="h-4 w-4 text-cyan-500" />,
  };

  const categoryColors: Record<string, string> = {
    performance: "bg-purple-500/20 text-purple-400 border-purple-500/30",
    resources: "bg-orange-500/20 text-orange-400 border-orange-500/30",
    structure: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  };

  return (
    <div
      className={cn(
        "rounded-lg border transition-all",
        severityColor[suggestion.severity as keyof typeof severityColor],
      )}
    >
      <Button
        variant="ghost"
        className="w-full justify-between h-auto p-4 hover:bg-transparent"
        onClick={onToggle}
      >
        <div className="flex items-start gap-3 text-left flex-1">
          <div className="mt-0.5">
            {severityIcon[suggestion.severity as keyof typeof severityIcon]}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <p className="font-semibold text-sm">{suggestion.description}</p>
              <Badge
                variant="outline"
                className={
                  categoryColors[
                    suggestion.category as keyof typeof categoryColors
                  ]
                }
              >
                {suggestion.category}
              </Badge>
            </div>
            {isExpanded && (
              <p className="text-xs text-muted-foreground mt-1">
                {suggestion.expected_improvement}
              </p>
            )}
          </div>
        </div>
        <ChevronDown
          className={cn(
            "h-4 w-4 transition-transform",
            isExpanded && "rotate-180",
          )}
        />
      </Button>

      {isExpanded && (
        <div className="border-t border-current/20 px-4 py-3 space-y-2">
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase mb-1">
              Expected Improvement
            </p>
            <p className="text-sm">{suggestion.expected_improvement}</p>
          </div>

          {suggestion.estimated_savings && (
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase mb-2">
                Potential Savings
              </p>
              <div className="space-y-1">
                {Object.entries(suggestion.estimated_savings).map(
                  ([key, value]) => (
                    <div key={key} className="text-xs flex justify-between">
                      <span className="text-muted-foreground capitalize">
                        {key.replace(/_/g, " ")}:
                      </span>
                      <span className="font-mono font-semibold">
                        {typeof value === "object"
                          ? JSON.stringify(value)
                          : String(value)}
                      </span>
                    </div>
                  ),
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
