import { useState, useEffect, useCallback, type ElementType } from 'react'
import {
  Search,
  FileText,
  ChevronDown,
  ChevronUp,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  Loader2,
  MessageSquarePlus,
  BarChart3,
  Database,
} from 'lucide-react'
import { MainLayout } from '@/components/layout/MainLayout'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { cn } from '@/lib/utils'
import { formatDurationMs, formatSignedMilliseconds } from '@/lib/number-format'
import { decisionEngineService } from '@/services/decision-engine-service'
import type { DecisionLogEntry, AccuracyStats } from '@/types/decision-engine.tp'

const statusConfig: Record<string, { icon: ElementType; color: string }> = {
  executed: { icon: CheckCircle, color: 'text-success' },
  failed: { icon: XCircle, color: 'text-error' },
  predicted: { icon: Clock, color: 'text-ink' },
}

export default function ExecutionHistory() {
  const [decisions, setDecisions] = useState<DecisionLogEntry[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [offset, setOffset] = useState(0)
  const [limit] = useState(10)
  const [hardwareFilter, setHardwareFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [accuracyStats, setAccuracyStats] = useState<AccuracyStats | null>(null)

  const fetchHistory = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await decisionEngineService.getHistory({
        limit,
        offset,
        hardware: hardwareFilter !== 'all' ? hardwareFilter : undefined,
        status: statusFilter !== 'all' ? statusFilter : undefined,
      })
      setDecisions(result.decisions)
      setTotal(result.total)
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to fetch history')
      setDecisions([])
      setTotal(0)
    } finally {
      setIsLoading(false)
    }
  }, [limit, offset, hardwareFilter, statusFilter])

  const fetchStats = useCallback(async () => {
    try {
      const stats = await decisionEngineService.getAccuracyStats()
      setAccuracyStats(stats)
    } catch {
      // Stats are non-critical, silently fail
    }
  }, [])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  useEffect(() => {
    fetchStats()
  }, [fetchStats])

  useEffect(() => {
    setOffset(0)
  }, [hardwareFilter, statusFilter])

  const hasMore = offset + limit < total
  const currentPage = Math.floor(offset / limit) + 1
  const totalPages = Math.ceil(total / limit)

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr)
      return d.toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })
    } catch {
      return dateStr
    }
  }

  const filteredDecisions = searchQuery
    ? decisions.filter(
        (d) =>
          d.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          d.input.problem_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
          d.prediction.recommended_hardware.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : decisions

  return (
    <MainLayout title="Execution History" description="Decision logs and performance tracking powered by Firestore">
      <div className="space-y-4 md:space-y-6">
        {accuracyStats && accuracyStats.totalPredictions > 0 && (
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4 md:gap-4">
            <Card variant="glass">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-ink-muted text-xs mb-1">
                  <Database className="h-3.5 w-3.5" />
                  Total Predictions
                </div>
                <p className="text-2xl font-semibold font-mono text-ink">{accuracyStats.totalPredictions}</p>
              </CardContent>
            </Card>
            <Card variant="glass">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-ink-muted text-xs mb-1">
                  <BarChart3 className="h-3.5 w-3.5" />
                  Accuracy
                </div>
                <p className="text-2xl font-semibold font-mono text-ink">
                  {accuracyStats.totalWithFeedback > 0 ? `${accuracyStats.accuracy}%` : 'N/A'}
                </p>
                <p className="text-xs text-ink-muted">
                  {accuracyStats.correctPredictions}/{accuracyStats.totalWithFeedback} correct
                </p>
              </CardContent>
            </Card>
            <Card variant="glass">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-ink-muted text-xs mb-1">
                  <MessageSquarePlus className="h-3.5 w-3.5" />
                  With Feedback
                </div>
                <p className="text-2xl font-semibold font-mono text-ink">{accuracyStats.totalWithFeedback}</p>
              </CardContent>
            </Card>
            <Card variant="glass">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-ink-muted text-xs mb-1">
                  <Clock className="h-3.5 w-3.5" />
                  Avg Time Delta
                </div>
                <p className="text-2xl font-semibold font-mono text-ink">{formatSignedMilliseconds(accuracyStats.averageTimeDelta)}</p>
              </CardContent>
            </Card>
          </div>
        )}

        <Card variant="glass">
          <CardContent className="flex flex-col gap-3 p-4 sm:flex-row sm:flex-wrap sm:items-center sm:gap-4">
            <div className="relative w-full flex-1 sm:min-w-[200px]">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-subtle" />
              <Input placeholder="Search by ID, problem type, hardware..." className="pl-10" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
            </div>
            <Select value={hardwareFilter} onValueChange={setHardwareFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Hardware" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Hardware</SelectItem>
                <SelectItem value="Quantum">Quantum</SelectItem>
                <SelectItem value="Classical">Classical</SelectItem>
                <SelectItem value="Hybrid">Hybrid</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="predicted">Predicted</SelectItem>
                <SelectItem value="executed">Executed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              className="gap-2"
              onClick={() => {
                fetchHistory()
                fetchStats()
              }}
              disabled={isLoading}
            >
              <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
              Refresh
            </Button>
          </CardContent>
        </Card>

        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <span className="ml-3 text-ink-muted">Loading decision history...</span>
          </div>
        )}

        {error && !isLoading && (
          <Card variant="glass" className="border-error/40">
            <CardContent className="p-6 text-center">
              <XCircle className="h-8 w-8 text-error mx-auto mb-2" />
              <p className="text-error font-medium">{error}</p>
              <Button variant="outline" className="mt-4" onClick={fetchHistory}>
                Try Again
              </Button>
            </CardContent>
          </Card>
        )}

        {!isLoading && !error && filteredDecisions.length === 0 && (
          <Card variant="glass">
            <CardContent className="p-12 text-center">
              <FileText className="h-12 w-12 text-ink-subtle mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-1 text-ink">No decisions found</h3>
              <p className="text-sm text-ink-muted">
                {total === 0 ? 'Make your first prediction in the Decision Engine to see it here.' : 'No results match your current filters.'}
              </p>
            </CardContent>
          </Card>
        )}

        {!isLoading && !error && filteredDecisions.length > 0 && (
          <div className="space-y-3">
            {filteredDecisions.map((decision) => {
              const statusInfo = statusConfig[decision.status] || statusConfig.predicted
              const StatusIcon = statusInfo.icon
              const isExpanded = expandedId === decision.id

              const predictedTime = decision.estimated_execution_time_ms ? formatDurationMs(decision.estimated_execution_time_ms) : '—'
              const predictedCost = decision.estimated_cost_usd ? `$${decision.estimated_cost_usd.toFixed(4)}` : '—'
              const actualTime =
                decision.feedback?.actual_execution_time_ms !== null && decision.feedback?.actual_execution_time_ms !== undefined
                  ? formatDurationMs(decision.feedback.actual_execution_time_ms)
                  : '—'
              const actualCost =
                decision.feedback?.actual_cost_usd !== null && decision.feedback?.actual_cost_usd !== undefined
                  ? `$${decision.feedback.actual_cost_usd.toFixed(4)}`
                  : '—'

              return (
                <Card key={decision.id} variant="glass" className="transition-colors hover:border-primary/40">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <StatusIcon className={cn('h-5 w-5', statusInfo.color)} />
                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <p className="font-mono text-sm font-medium text-ink">{decision.id.substring(0, 8)}...</p>
                            <Badge
                              variant={decision.prediction.recommended_hardware.toLowerCase() as 'quantum' | 'classical' | 'hybrid'}
                              className="capitalize"
                            >
                              {decision.prediction.recommended_hardware}
                            </Badge>
                            <Badge variant="outline" className="text-xs capitalize">
                              {decision.input.problem_type.replace('_', ' ')}
                            </Badge>
                          </div>
                          <p className="text-sm text-ink-muted">{formatDate(decision.createdAt)}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 md:gap-8">
                        <div className="text-center hidden sm:block">
                          <p className="text-xs text-ink-muted">Confidence</p>
                          <p className="font-mono font-medium text-ink">{(decision.prediction.confidence * 100).toFixed(0)}%</p>
                        </div>
                        <div className="text-center hidden md:block">
                          <p className="text-xs text-ink-muted">Time</p>
                          <p className="font-mono font-medium text-sm">
                            <span className="text-ink-muted">{predictedTime}</span>
                            {decision.feedback && (
                              <>
                                <span className="mx-1">→</span>
                                <span className={actualTime !== '—' ? 'text-success' : 'text-ink-muted'}>{actualTime}</span>
                              </>
                            )}
                          </p>
                        </div>
                        <div className="text-center hidden md:block">
                          <p className="text-xs text-ink-muted">Cost</p>
                          <p className="font-mono font-medium text-sm">
                            <span className="text-ink-muted">{predictedCost}</span>
                            {decision.feedback && (
                              <>
                                <span className="mx-1">→</span>
                                <span className={actualCost !== '—' ? 'text-success' : 'text-ink-muted'}>{actualCost}</span>
                              </>
                            )}
                          </p>
                        </div>
                        <Button variant="ghost" size="sm" className="gap-1" onClick={() => setExpandedId(isExpanded ? null : decision.id)}>
                          <FileText className="h-4 w-4" />
                          Details
                          {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                        </Button>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="mt-4 pt-4 border-t border-hairline space-y-4">
                        <div>
                          <h4 className="text-sm font-medium text-ink-muted mb-2">Input Parameters</h4>
                          <div className="grid grid-cols-2 gap-2 md:grid-cols-5 text-sm">
                            <div>
                              <span className="text-ink-muted">Problem Size:</span> <span className="font-mono text-ink">{decision.input.problem_size}</span>
                            </div>
                            <div>
                              <span className="text-ink-muted">Qubits:</span> <span className="font-mono text-ink">{decision.input.qubits_required}</span>
                            </div>
                            <div>
                              <span className="text-ink-muted">Circuit Depth:</span> <span className="font-mono text-ink">{decision.input.circuit_depth}</span>
                            </div>
                            <div>
                              <span className="text-ink-muted">Gate Count:</span> <span className="font-mono text-ink">{decision.input.gate_count}</span>
                            </div>
                            <div>
                              <span className="text-ink-muted">CX Ratio:</span> <span className="font-mono text-ink">{decision.input.cx_gate_ratio}</span>
                            </div>
                            <div>
                              <span className="text-ink-muted">Superposition:</span>{' '}
                              <span className="font-mono text-ink">{decision.input.superposition_score}</span>
                            </div>
                            <div>
                              <span className="text-ink-muted">Entanglement:</span>{' '}
                              <span className="font-mono text-ink">{decision.input.entanglement_score}</span>
                            </div>
                            <div>
                              <span className="text-ink-muted">Complexity:</span>{' '}
                              <span className="font-mono capitalize text-ink">{decision.input.time_complexity.replace('_', ' ')}</span>
                            </div>
                            <div>
                              <span className="text-ink-muted">Memory:</span> <span className="font-mono text-ink">{decision.input.memory_requirement_mb}MB</span>
                            </div>
                          </div>
                        </div>

                        <div>
                          <h4 className="text-sm font-medium text-ink-muted mb-1">Rationale</h4>
                          <p className="text-sm bg-surface-1 border border-hairline p-3 text-ink">{decision.prediction.rationale}</p>
                        </div>

                        <div className="flex gap-4">
                          <div className="flex-1">
                            <p className="text-xs text-ink-muted mb-1">Quantum Probability</p>
                            <div className="h-2 bg-surface-2 overflow-hidden">
                              <div className="h-full bg-quantum transition-all" style={{ width: `${decision.prediction.quantum_probability * 100}%` }} />
                            </div>
                            <p className="text-xs font-mono mt-1 text-ink">{(decision.prediction.quantum_probability * 100).toFixed(1)}%</p>
                          </div>
                          <div className="flex-1">
                            <p className="text-xs text-ink-muted mb-1">Classical Probability</p>
                            <div className="h-2 bg-surface-2 overflow-hidden">
                              <div className="h-full bg-classical transition-all" style={{ width: `${decision.prediction.classical_probability * 100}%` }} />
                            </div>
                            <p className="text-xs font-mono mt-1 text-ink">{(decision.prediction.classical_probability * 100).toFixed(1)}%</p>
                          </div>
                        </div>

                        {decision.feedback && (
                          <div className="bg-surface-1 border border-hairline p-3">
                            <h4 className="text-sm font-medium mb-2 flex items-center gap-2 text-ink">
                              <MessageSquarePlus className="h-4 w-4" />
                              Execution Feedback
                            </h4>
                            <div className="grid grid-cols-2 gap-2 md:grid-cols-4 text-sm">
                              <div>
                                <span className="text-ink-muted">Hardware Used:</span>{' '}
                                <span className="font-mono text-ink">{decision.feedback.actual_hardware_used}</span>
                              </div>
                              <div>
                                <span className="text-ink-muted">Actual Time:</span> <span className="font-mono text-ink">{actualTime}</span>
                              </div>
                              <div>
                                <span className="text-ink-muted">Actual Cost:</span> <span className="font-mono text-ink">{actualCost}</span>
                              </div>
                              <div>
                                <span className="text-ink-muted">Correct?</span>{' '}
                                <span className={cn('font-mono', decision.feedback.prediction_correct ? 'text-success' : 'text-error')}>
                                  {decision.feedback.prediction_correct ? 'Yes ✓' : 'No ✗'}
                                </span>
                              </div>
                            </div>
                            {decision.feedback.notes && <p className="text-sm text-ink-muted mt-2 italic">{decision.feedback.notes}</p>}
                          </div>
                        )}

                        <div className="text-xs text-ink-muted font-mono">Decision ID: {decision.id}</div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}

        {!isLoading && total > 0 && (
          <div className="flex items-center justify-between">
            <p className="text-sm text-ink-muted">
              Showing {offset + 1}-{Math.min(offset + limit, total)} of {total} decisions
              {totalPages > 1 && ` (Page ${currentPage} of ${totalPages})`}
            </p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - limit))}>
                Previous
              </Button>
              <Button variant="outline" size="sm" disabled={!hasMore} onClick={() => setOffset(offset + limit)}>
                Next
              </Button>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  )
}
