/**
 * Optimization Suggestions Component
 * Displays actionable optimization recommendations
 */

import { useState } from 'react'
import { Lightbulb, AlertTriangle, AlertCircle, Info, ChevronDown, CheckCircle, Zap } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { OptimizationSuggestion } from '@/types/codeAnalysis'
import { cn } from '@/lib/utils'

interface OptimizationSuggestionsProps {
  suggestions: OptimizationSuggestion[]
}

export function OptimizationSuggestions({ suggestions }: OptimizationSuggestionsProps) {
  const [expandedId, setExpandedId] = useState<number | null>(suggestions.length > 0 ? 0 : null)

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
          <p className="text-sm text-ink-muted">✓ No major optimization opportunities detected. Your code is well-structured!</p>
        </CardContent>
      </Card>
    )
  }

  const highSuggestions = suggestions.filter((s) => s.severity === 'high')
  const mediumSuggestions = suggestions.filter((s) => s.severity === 'medium')
  const lowSuggestions = suggestions.filter((s) => s.severity === 'low')

  return (
    <div className="space-y-3">
      <Card variant="glass">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-ink">
              <Lightbulb className="h-5 w-5 text-warning" />
              Optimization Opportunities
            </div>
            <Badge variant="outline" className="gap-1">
              <Zap className="h-3 w-3" />
              {suggestions.length} suggestions
            </Badge>
          </CardTitle>
        </CardHeader>
      </Card>

      {highSuggestions.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase text-error/80 px-2">High Priority ({highSuggestions.length})</h3>
          {highSuggestions.map((suggestion) => (
            <SuggestionCard
              key={`high-${suggestions.indexOf(suggestion)}`}
              suggestion={suggestion}
              isExpanded={expandedId === suggestions.indexOf(suggestion)}
              onToggle={() => setExpandedId(expandedId === suggestions.indexOf(suggestion) ? null : suggestions.indexOf(suggestion))}
            />
          ))}
        </div>
      )}

      {mediumSuggestions.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase text-ink px-2">Medium Priority ({mediumSuggestions.length})</h3>
          {mediumSuggestions.map((suggestion) => (
            <SuggestionCard
              key={`medium-${suggestions.indexOf(suggestion)}`}
              suggestion={suggestion}
              isExpanded={expandedId === suggestions.indexOf(suggestion)}
              onToggle={() => setExpandedId(expandedId === suggestions.indexOf(suggestion) ? null : suggestions.indexOf(suggestion))}
            />
          ))}
        </div>
      )}

      {lowSuggestions.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase text-ink-muted px-2">Low Priority ({lowSuggestions.length})</h3>
          {lowSuggestions.map((suggestion) => (
            <SuggestionCard
              key={`low-${suggestions.indexOf(suggestion)}`}
              suggestion={suggestion}
              isExpanded={expandedId === suggestions.indexOf(suggestion)}
              onToggle={() => setExpandedId(expandedId === suggestions.indexOf(suggestion) ? null : suggestions.indexOf(suggestion))}
            />
          ))}
        </div>
      )}
    </div>
  )
}

const severityColor: Record<string, string> = {
  high: 'border-error/40 bg-error/5',
  medium: 'border-warning/50 bg-warning/10',
  low: 'border-hairline bg-surface-1',
}

const severityIcon: Record<string, React.ReactNode> = {
  high: <AlertTriangle className="h-4 w-4 text-error" />,
  medium: <AlertCircle className="h-4 w-4 text-ink" />,
  low: <Info className="h-4 w-4 text-ink-muted" />,
}

const categoryColors: Record<string, string> = {
  performance: 'bg-primary/10 text-primary border-primary/30',
  resources: 'bg-warning/15 text-ink border-warning/40',
  structure: 'bg-classical/10 text-classical border-classical/30',
}

function SuggestionCard({
  suggestion,
  isExpanded,
  onToggle,
}: {
  suggestion: OptimizationSuggestion
  isExpanded: boolean
  onToggle: () => void
}) {
  return (
    <div className={cn('border transition-colors', severityColor[suggestion.severity])}>
      <Button variant="ghost" className="w-full justify-between h-auto p-4 hover:bg-transparent" onClick={onToggle}>
        <div className="flex items-start gap-3 text-left flex-1">
          <div className="mt-0.5">{severityIcon[suggestion.severity]}</div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <p className="font-semibold text-sm text-ink">{suggestion.description}</p>
              <Badge variant="outline" className={categoryColors[suggestion.category]}>
                {suggestion.category}
              </Badge>
            </div>
            {isExpanded && <p className="text-xs text-ink-muted mt-1">{suggestion.expected_improvement}</p>}
          </div>
        </div>
        <ChevronDown className={cn('h-4 w-4 transition-transform', isExpanded && 'rotate-180')} />
      </Button>

      {isExpanded && (
        <div className="border-t border-current/20 px-4 py-3 space-y-2">
          <div>
            <p className="text-xs font-semibold text-ink-muted uppercase mb-1">Expected Improvement</p>
            <p className="text-sm text-ink">{suggestion.expected_improvement}</p>
          </div>

          {suggestion.estimated_savings && (
            <div>
              <p className="text-xs font-semibold text-ink-muted uppercase mb-2">Potential Savings</p>
              <div className="space-y-1">
                {Object.entries(suggestion.estimated_savings).map(([key, value]) => (
                  <div key={key} className="text-xs flex justify-between">
                    <span className="text-ink-muted capitalize">{key.replace(/_/g, ' ')}:</span>
                    <span className="font-mono font-semibold text-ink">
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
