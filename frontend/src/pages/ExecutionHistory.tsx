import { useState, useEffect, useCallback } from "react";
import {
  Calendar,
  Search,
  Download,
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
} from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { decisionEngineService } from "@/services/decision-engine-service";
import type {
  DecisionLogEntry,
  AccuracyStats,
} from "@/types/decision-engine.tp";

const statusConfig: Record<
  string,
  { icon: any; color: string; badge: "success" | "destructive" | "warning" }
> = {
  executed: { icon: CheckCircle, color: "text-success", badge: "success" },
  failed: { icon: XCircle, color: "text-destructive", badge: "destructive" },
  predicted: { icon: Clock, color: "text-warning", badge: "warning" },
};

export default function ExecutionHistory() {
  // State
  const [decisions, setDecisions] = useState<DecisionLogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const [limit] = useState(10);
  const [hardwareFilter, setHardwareFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [accuracyStats, setAccuracyStats] = useState<AccuracyStats | null>(
    null,
  );
  const [isLoadingStats, setIsLoadingStats] = useState(false);

  // Fetch history
  const fetchHistory = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await decisionEngineService.getHistory({
        limit,
        offset,
        hardware: hardwareFilter !== "all" ? hardwareFilter : undefined,
        status: statusFilter !== "all" ? statusFilter : undefined,
      });
      setDecisions(result.decisions);
      setTotal(result.total);
    } catch (err: any) {
      setError(
        err.response?.data?.error || err.message || "Failed to fetch history",
      );
      setDecisions([]);
      setTotal(0);
    } finally {
      setIsLoading(false);
    }
  }, [limit, offset, hardwareFilter, statusFilter]);

  // Fetch accuracy stats
  const fetchStats = useCallback(async () => {
    setIsLoadingStats(true);
    try {
      const stats = await decisionEngineService.getAccuracyStats();
      setAccuracyStats(stats);
    } catch {
      // Stats are non-critical, silently fail
    } finally {
      setIsLoadingStats(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  // Reset page when filters change
  useEffect(() => {
    setOffset(0);
  }, [hardwareFilter, statusFilter]);

  const hasMore = offset + limit < total;
  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  // Format date
  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  // Filter by search locally (on top of server-side filters)
  const filteredDecisions = searchQuery
    ? decisions.filter(
        (d) =>
          d.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          d.input.problem_type
            .toLowerCase()
            .includes(searchQuery.toLowerCase()) ||
          d.prediction.recommended_hardware
            .toLowerCase()
            .includes(searchQuery.toLowerCase()),
      )
    : decisions;

  return (
    <MainLayout
      title="Execution History"
      description="Decision logs and performance tracking powered by Firestore"
    >
      <div className="space-y-4 md:space-y-6">
        {/* Accuracy Stats Cards */}
        {accuracyStats && accuracyStats.totalPredictions > 0 && (
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4 md:gap-4">
            <Card variant="glass">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
                  <Database className="h-3.5 w-3.5" />
                  Total Predictions
                </div>
                <p className="text-2xl font-bold font-mono">
                  {accuracyStats.totalPredictions}
                </p>
              </CardContent>
            </Card>
            <Card variant="glass">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
                  <BarChart3 className="h-3.5 w-3.5" />
                  Accuracy
                </div>
                <p className="text-2xl font-bold font-mono">
                  {accuracyStats.totalWithFeedback > 0
                    ? `${accuracyStats.accuracy}%`
                    : "N/A"}
                </p>
                <p className="text-xs text-muted-foreground">
                  {accuracyStats.correctPredictions}/
                  {accuracyStats.totalWithFeedback} correct
                </p>
              </CardContent>
            </Card>
            <Card variant="glass">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
                  <MessageSquarePlus className="h-3.5 w-3.5" />
                  With Feedback
                </div>
                <p className="text-2xl font-bold font-mono">
                  {accuracyStats.totalWithFeedback}
                </p>
              </CardContent>
            </Card>
            <Card variant="glass">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
                  <Clock className="h-3.5 w-3.5" />
                  Avg Time Delta
                </div>
                <p className="text-2xl font-bold font-mono">
                  {accuracyStats.averageTimeDelta !== 0
                    ? `${accuracyStats.averageTimeDelta > 0 ? "+" : ""}${accuracyStats.averageTimeDelta}ms`
                    : "N/A"}
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Filters */}
        <Card variant="glass">
          <CardContent className="flex flex-col gap-3 p-4 sm:flex-row sm:flex-wrap sm:items-center sm:gap-4">
            <div className="relative w-full flex-1 sm:min-w-[200px]">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by ID, problem type, hardware..."
                className="pl-10 bg-secondary/30"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={hardwareFilter} onValueChange={setHardwareFilter}>
              <SelectTrigger className="w-[150px] bg-secondary/30">
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
              <SelectTrigger className="w-[150px] bg-secondary/30">
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
                fetchHistory();
                fetchStats();
              }}
              disabled={isLoading}
            >
              <RefreshCw
                className={cn("h-4 w-4", isLoading && "animate-spin")}
              />
              Refresh
            </Button>
          </CardContent>
        </Card>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <span className="ml-3 text-muted-foreground">
              Loading decision history...
            </span>
          </div>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <Card variant="glass" className="border-destructive/30">
            <CardContent className="p-6 text-center">
              <XCircle className="h-8 w-8 text-destructive mx-auto mb-2" />
              <p className="text-destructive font-medium">{error}</p>
              <Button variant="outline" className="mt-4" onClick={fetchHistory}>
                Try Again
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Empty State */}
        {!isLoading && !error && filteredDecisions.length === 0 && (
          <Card variant="glass">
            <CardContent className="p-12 text-center">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium mb-1">No decisions found</h3>
              <p className="text-sm text-muted-foreground">
                {total === 0
                  ? "Make your first prediction in the Decision Engine to see it here."
                  : "No results match your current filters."}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Decision List */}
        {!isLoading && !error && filteredDecisions.length > 0 && (
          <div className="space-y-3">
            {filteredDecisions.map((decision) => {
              const statusInfo =
                statusConfig[decision.status] || statusConfig.predicted;
              const StatusIcon = statusInfo.icon;
              const isExpanded = expandedId === decision.id;

              const predictedTime = decision.estimated_execution_time_ms
                ? `${(decision.estimated_execution_time_ms / 1000).toFixed(1)}s`
                : "—";
              const predictedCost = decision.estimated_cost_usd
                ? `$${decision.estimated_cost_usd.toFixed(4)}`
                : "—";
              const actualTime =
                decision.feedback?.actual_execution_time_ms !== null &&
                decision.feedback?.actual_execution_time_ms !== undefined
                  ? `${(decision.feedback.actual_execution_time_ms / 1000).toFixed(1)}s`
                  : "—";
              const actualCost =
                decision.feedback?.actual_cost_usd !== null &&
                decision.feedback?.actual_cost_usd !== undefined
                  ? `$${decision.feedback.actual_cost_usd.toFixed(4)}`
                  : "—";

              return (
                <Card
                  key={decision.id}
                  variant="glass"
                  className="transition-all hover:border-primary/30"
                >
                  <CardContent className="p-4">
                    {/* Main Row */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <StatusIcon
                          className={cn("h-5 w-5", statusInfo.color)}
                        />
                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <p className="font-mono text-sm font-medium">
                              {decision.id.substring(0, 8)}...
                            </p>
                            <Badge
                              variant={
                                decision.prediction.recommended_hardware.toLowerCase() as
                                  | "quantum"
                                  | "classical"
                                  | "hybrid"
                              }
                              className="capitalize"
                            >
                              {decision.prediction.recommended_hardware}
                            </Badge>
                            <Badge
                              variant="outline"
                              className="text-xs capitalize"
                            >
                              {decision.input.problem_type.replace("_", " ")}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {formatDate(decision.createdAt)}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 md:gap-8">
                        <div className="text-center hidden sm:block">
                          <p className="text-xs text-muted-foreground">
                            Confidence
                          </p>
                          <p className="font-mono font-medium">
                            {(decision.prediction.confidence * 100).toFixed(0)}%
                          </p>
                        </div>
                        <div className="text-center hidden md:block">
                          <p className="text-xs text-muted-foreground">Time</p>
                          <p className="font-mono font-medium text-sm">
                            <span className="text-muted-foreground">
                              {predictedTime}
                            </span>
                            {decision.feedback && (
                              <>
                                <span className="mx-1">→</span>
                                <span
                                  className={
                                    actualTime !== "—"
                                      ? "text-success"
                                      : "text-muted-foreground"
                                  }
                                >
                                  {actualTime}
                                </span>
                              </>
                            )}
                          </p>
                        </div>
                        <div className="text-center hidden md:block">
                          <p className="text-xs text-muted-foreground">Cost</p>
                          <p className="font-mono font-medium text-sm">
                            <span className="text-muted-foreground">
                              {predictedCost}
                            </span>
                            {decision.feedback && (
                              <>
                                <span className="mx-1">→</span>
                                <span
                                  className={
                                    actualCost !== "—"
                                      ? "text-success"
                                      : "text-muted-foreground"
                                  }
                                >
                                  {actualCost}
                                </span>
                              </>
                            )}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="gap-1"
                          onClick={() =>
                            setExpandedId(isExpanded ? null : decision.id)
                          }
                        >
                          <FileText className="h-4 w-4" />
                          Details
                          {isExpanded ? (
                            <ChevronUp className="h-3 w-3" />
                          ) : (
                            <ChevronDown className="h-3 w-3" />
                          )}
                        </Button>
                      </div>
                    </div>

                    {/* Expanded Details */}
                    {isExpanded && (
                      <div className="mt-4 pt-4 border-t border-border/50 space-y-4">
                        {/* Input Parameters */}
                        <div>
                          <h4 className="text-sm font-medium text-muted-foreground mb-2">
                            Input Parameters
                          </h4>
                          <div className="grid grid-cols-2 gap-2 md:grid-cols-5 text-sm">
                            <div>
                              <span className="text-muted-foreground">
                                Problem Size:
                              </span>{" "}
                              <span className="font-mono">
                                {decision.input.problem_size}
                              </span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">
                                Qubits:
                              </span>{" "}
                              <span className="font-mono">
                                {decision.input.qubits_required}
                              </span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">
                                Circuit Depth:
                              </span>{" "}
                              <span className="font-mono">
                                {decision.input.circuit_depth}
                              </span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">
                                Gate Count:
                              </span>{" "}
                              <span className="font-mono">
                                {decision.input.gate_count}
                              </span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">
                                CX Ratio:
                              </span>{" "}
                              <span className="font-mono">
                                {decision.input.cx_gate_ratio}
                              </span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">
                                Superposition:
                              </span>{" "}
                              <span className="font-mono">
                                {decision.input.superposition_score}
                              </span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">
                                Entanglement:
                              </span>{" "}
                              <span className="font-mono">
                                {decision.input.entanglement_score}
                              </span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">
                                Complexity:
                              </span>{" "}
                              <span className="font-mono capitalize">
                                {decision.input.time_complexity.replace(
                                  "_",
                                  " ",
                                )}
                              </span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">
                                Memory:
                              </span>{" "}
                              <span className="font-mono">
                                {decision.input.memory_requirement_mb}MB
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Rationale */}
                        <div>
                          <h4 className="text-sm font-medium text-muted-foreground mb-1">
                            Rationale
                          </h4>
                          <p className="text-sm bg-secondary/30 rounded-md p-3">
                            {decision.prediction.rationale}
                          </p>
                        </div>

                        {/* Probabilities */}
                        <div className="flex gap-4">
                          <div className="flex-1">
                            <p className="text-xs text-muted-foreground mb-1">
                              Quantum Probability
                            </p>
                            <div className="h-2 bg-secondary rounded-full overflow-hidden">
                              <div
                                className="h-full bg-primary rounded-full transition-all"
                                style={{
                                  width: `${decision.prediction.quantum_probability * 100}%`,
                                }}
                              />
                            </div>
                            <p className="text-xs font-mono mt-1">
                              {(
                                decision.prediction.quantum_probability * 100
                              ).toFixed(1)}
                              %
                            </p>
                          </div>
                          <div className="flex-1">
                            <p className="text-xs text-muted-foreground mb-1">
                              Classical Probability
                            </p>
                            <div className="h-2 bg-secondary rounded-full overflow-hidden">
                              <div
                                className="h-full bg-blue-500 rounded-full transition-all"
                                style={{
                                  width: `${decision.prediction.classical_probability * 100}%`,
                                }}
                              />
                            </div>
                            <p className="text-xs font-mono mt-1">
                              {(
                                decision.prediction.classical_probability * 100
                              ).toFixed(1)}
                              %
                            </p>
                          </div>
                        </div>

                        {/* Feedback */}
                        {decision.feedback && (
                          <div className="bg-secondary/20 rounded-md p-3">
                            <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                              <MessageSquarePlus className="h-4 w-4" />
                              Execution Feedback
                            </h4>
                            <div className="grid grid-cols-2 gap-2 md:grid-cols-4 text-sm">
                              <div>
                                <span className="text-muted-foreground">
                                  Hardware Used:
                                </span>{" "}
                                <span className="font-mono">
                                  {decision.feedback.actual_hardware_used}
                                </span>
                              </div>
                              <div>
                                <span className="text-muted-foreground">
                                  Actual Time:
                                </span>{" "}
                                <span className="font-mono">{actualTime}</span>
                              </div>
                              <div>
                                <span className="text-muted-foreground">
                                  Actual Cost:
                                </span>{" "}
                                <span className="font-mono">{actualCost}</span>
                              </div>
                              <div>
                                <span className="text-muted-foreground">
                                  Correct?
                                </span>{" "}
                                <span
                                  className={cn(
                                    "font-mono",
                                    decision.feedback.prediction_correct
                                      ? "text-success"
                                      : "text-destructive",
                                  )}
                                >
                                  {decision.feedback.prediction_correct
                                    ? "Yes ✓"
                                    : "No ✗"}
                                </span>
                              </div>
                            </div>
                            {decision.feedback.notes && (
                              <p className="text-sm text-muted-foreground mt-2 italic">
                                {decision.feedback.notes}
                              </p>
                            )}
                          </div>
                        )}

                        {/* Full Decision ID */}
                        <div className="text-xs text-muted-foreground font-mono">
                          Decision ID: {decision.id}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Pagination */}
        {!isLoading && total > 0 && (
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Showing {offset + 1}-{Math.min(offset + limit, total)} of {total}{" "}
              decisions
              {totalPages > 1 && ` (Page ${currentPage} of ${totalPages})`}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - limit))}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={!hasMore}
                onClick={() => setOffset(offset + limit)}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
