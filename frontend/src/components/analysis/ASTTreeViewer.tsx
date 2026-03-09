/**
 * AST Tree Viewer Component
 * Interactive visualization of code structure
 */

import { useState } from "react";
import {
  ChevronRight,
  Layers,
  Code,
  Braces,
  Container,
  GitBranch,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { ASTNode } from "@/types/codeAnalysis";
import { cn } from "@/lib/utils";

interface ASTTreeViewerProps {
  ast: ASTNode;
}

export function ASTTreeViewer({ ast }: ASTTreeViewerProps) {
  return (
    <Card variant="glass" className="border-green-500/30 bg-green-500/5">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-green-400">
          <GitBranch className="h-5 w-5" />
          Code Structure
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-1 text-sm">
          <TreeNode node={ast} level={0} />
        </div>
      </CardContent>
    </Card>
  );
}

function TreeNode({ node, level }: { node: ASTNode; level: number }) {
  const [isExpanded, setIsExpanded] = useState(level < 2); // Expand first 2 levels
  const complexityScore =
    typeof node.complexity_score === "number" &&
    Number.isFinite(node.complexity_score)
      ? node.complexity_score
      : null;
  const lineNumber =
    typeof node.line_number === "number" && Number.isFinite(node.line_number)
      ? node.line_number
      : null;
  const attributes =
    node.attributes && typeof node.attributes === "object"
      ? node.attributes
      : null;

  const getNodeIcon = (type: string) => {
    const iconMap: Record<string, React.ReactNode> = {
      program: <Container className="h-4 w-4 text-blue-400" />,
      imports: <Code className="h-4 w-4 text-purple-400" />,
      import: <Code className="h-4 w-4 text-purple-400" />,
      functions: <Braces className="h-4 w-4 text-cyan-400" />,
      function: <Braces className="h-4 w-4 text-cyan-400" />,
      control_flow: <GitBranch className="h-4 w-4 text-yellow-400" />,
      loop: <Icon.Loop className="h-4 w-4 text-orange-400" />,
      conditional: <Icon.Conditional className="h-4 w-4 text-pink-400" />,
      quantum_circuit: <Icon.Quantum className="h-4 w-4 text-purple-400" />,
      gate: <Icon.Gate className="h-4 w-4 text-purple-400" />,
    };
    return (
      iconMap[type] || <Layers className="h-4 w-4 text-muted-foreground" />
    );
  };

  const getComplexityColor = (score: number | null) => {
    if (score === null) return "text-muted-foreground";
    if (score < 0.3) return "text-success";
    if (score < 0.6) return "text-cyan-400";
    if (score < 0.8) return "text-yellow-500";
    return "text-destructive";
  };

  const hasChildren = Array.isArray(node.children) && node.children.length > 0;
  const indent = level * 16;

  return (
    <div>
      <div
        className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-secondary/30 cursor-pointer group transition-colors"
        style={{ paddingLeft: `${indent}px` }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {hasChildren && (
          <ChevronRight
            className={cn(
              "h-3.5 w-3.5 transition-transform text-muted-foreground",
              isExpanded && "rotate-90",
            )}
          />
        )}
        {!hasChildren && <div className="w-3.5" />}

        {getNodeIcon(node.type)}

        <div className="flex-1 flex items-center gap-2 min-w-0">
          <span className="font-mono text-xs font-semibold">{node.type}</span>
          {node.name && (
            <span className="text-xs text-muted-foreground truncate">
              {node.name}
            </span>
          )}

          {attributes && Object.keys(attributes).length > 0 && (
            <div className="flex gap-1 flex-wrap">
              {Object.entries(attributes).map(([key, value]) => (
                <Badge
                  key={key}
                  variant="outline"
                  className="text-xs px-1.5 py-0 h-5 border-border/50"
                >
                  {typeof value === "object" ? key : `${key}: ${value}`}
                </Badge>
              ))}
            </div>
          )}

          {complexityScore !== null && (
            <div
              className={cn(
                "text-xs font-mono",
                getComplexityColor(complexityScore),
              )}
            >
              (complexity: {complexityScore.toFixed(2)})
            </div>
          )}

          {lineNumber !== null && (
            <span className="text-xs text-muted-foreground ml-auto">
              L{lineNumber}
            </span>
          )}
        </div>
      </div>

      {hasChildren && isExpanded && (
        <div>
          {node.children.map((child, idx) => (
            <TreeNode key={idx} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

// Helper icons
namespace Icon {
  export function Loop(props: any) {
    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        {...props}
      >
        <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
        <path d="M21 3v5h-5" />
        <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
        <path d="M3 21v-5h5" />
      </svg>
    );
  }

  export function Conditional(props: any) {
    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        {...props}
      >
        <path d="M12 3L22 8v8l-10 5-10-5V8l10-5z" />
        <path d="M12 12v5" />
      </svg>
    );
  }

  export function Quantum(props: any) {
    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        {...props}
      >
        <circle cx="12" cy="12" r="1" />
        <circle cx="19" cy="5" r="1" />
        <circle cx="5" cy="5" r="1" />
        <circle cx="19" cy="19" r="1" />
        <circle cx="5" cy="19" r="1" />
        <path d="M12 12L19 5M12 12L5 5M12 12L19 19M12 12L5 19" />
      </svg>
    );
  }

  export function Gate(props: any) {
    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        {...props}
      >
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <line x1="9" y1="3" x2="9" y2="21" />
        <line x1="15" y1="3" x2="15" y2="21" />
      </svg>
    );
  }
}
