/**
 * AST Tree Viewer Component
 * Interactive visualization of code structure
 */

import { useState, type ReactNode, type SVGProps } from 'react'
import { ChevronRight, Layers, Code, Braces, Container, GitBranch } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { ASTNode } from '@/types/codeAnalysis'
import { cn } from '@/lib/utils'

interface ASTTreeViewerProps {
  ast: ASTNode
}

export function ASTTreeViewer({ ast }: ASTTreeViewerProps) {
  return (
    <Card variant="glass">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-ink">
          <GitBranch className="h-5 w-5 text-primary" />
          Code Structure
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-1 text-sm">
          <TreeNode node={ast} level={0} />
        </div>
      </CardContent>
    </Card>
  )
}

function TreeNode({ node, level }: { node: ASTNode; level: number }) {
  const [isExpanded, setIsExpanded] = useState(level < 2)
  const complexityScore =
    typeof node.complexity_score === 'number' && Number.isFinite(node.complexity_score) ? node.complexity_score : null
  const lineNumber = typeof node.line_number === 'number' && Number.isFinite(node.line_number) ? node.line_number : null
  const attributes = node.attributes && typeof node.attributes === 'object' ? node.attributes : null

  const getNodeIcon = (type: string) => {
    const iconMap: Record<string, ReactNode> = {
      program: <Container className="h-4 w-4 text-primary" />,
      imports: <Code className="h-4 w-4 text-primary" />,
      import: <Code className="h-4 w-4 text-primary" />,
      functions: <Braces className="h-4 w-4 text-classical" />,
      function: <Braces className="h-4 w-4 text-classical" />,
      control_flow: <GitBranch className="h-4 w-4 text-ink" />,
      loop: <Icon.Loop className="h-4 w-4 text-ink" />,
      conditional: <Icon.Conditional className="h-4 w-4 text-ink" />,
      quantum_circuit: <Icon.Quantum className="h-4 w-4 text-quantum" />,
      gate: <Icon.Gate className="h-4 w-4 text-quantum" />,
    }
    return iconMap[type] || <Layers className="h-4 w-4 text-ink-muted" />
  }

  const getComplexityColor = (score: number | null) => {
    if (score === null) return 'text-ink-muted'
    if (score < 0.3) return 'text-success'
    if (score < 0.6) return 'text-primary'
    if (score < 0.8) return 'text-ink'
    return 'text-error'
  }

  const hasChildren = Array.isArray(node.children) && node.children.length > 0
  const indent = level * 16

  return (
    <div>
      <div
        className="flex items-center gap-2 py-1.5 px-2 hover:bg-surface-1 cursor-pointer group transition-colors"
        style={{ paddingLeft: `${indent}px` }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {hasChildren && <ChevronRight className={cn('h-3.5 w-3.5 transition-transform text-ink-muted', isExpanded && 'rotate-90')} />}
        {!hasChildren && <div className="w-3.5" />}

        {getNodeIcon(node.type)}

        <div className="flex-1 flex items-center gap-2 min-w-0">
          <span className="font-mono text-xs font-semibold text-ink">{node.type}</span>
          {node.name && <span className="text-xs text-ink-muted truncate">{node.name}</span>}

          {attributes && Object.keys(attributes).length > 0 && (
            <div className="flex gap-1 flex-wrap">
              {Object.entries(attributes).map(([key, value]) => (
                <Badge key={key} variant="outline" className="text-xs px-1.5 py-0 h-5">
                  {typeof value === 'object' ? key : `${key}: ${value}`}
                </Badge>
              ))}
            </div>
          )}

          {complexityScore !== null && (
            <div className={cn('text-xs font-mono', getComplexityColor(complexityScore))}>(complexity: {complexityScore.toFixed(2)})</div>
          )}

          {lineNumber !== null && <span className="text-xs text-ink-subtle ml-auto">L{lineNumber}</span>}
        </div>
      </div>

      {hasChildren && isExpanded && (
        <div>
          {node.children!.map((child, idx) => (
            <TreeNode key={idx} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  )
}

/* Plain object of small inline-SVG icons -- a `namespace` here would compile to
   runtime code, which erasableSyntaxOnly forbids, so this uses a const object instead. */
const Icon = {
  Loop: (props: SVGProps<SVGSVGElement>) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
      <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
      <path d="M21 3v5h-5" />
      <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
      <path d="M3 21v-5h5" />
    </svg>
  ),
  Conditional: (props: SVGProps<SVGSVGElement>) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
      <path d="M12 3L22 8v8l-10 5-10-5V8l10-5z" />
      <path d="M12 12v5" />
    </svg>
  ),
  Quantum: (props: SVGProps<SVGSVGElement>) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
      <circle cx="12" cy="12" r="1" />
      <circle cx="19" cy="5" r="1" />
      <circle cx="5" cy="5" r="1" />
      <circle cx="19" cy="19" r="1" />
      <circle cx="5" cy="19" r="1" />
      <path d="M12 12L19 5M12 12L5 5M12 12L19 19M12 12L5 19" />
    </svg>
  ),
  Gate: (props: SVGProps<SVGSVGElement>) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
      <rect x="3" y="3" width="18" height="18" rx="2" />
      <line x1="9" y1="3" x2="9" y2="21" />
      <line x1="15" y1="3" x2="15" y2="21" />
    </svg>
  ),
}
