/**
 * Pipeline Execution
 * Execution step with live job status polling.
 */

import { useState } from "react";
import {
  Play,
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
  Server,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useJobStatus } from "@/hooks/useJobStatus";
import { hardwareService } from "@/services/hardware-service";
import { HardwareType } from "@/types/decision-engine.tp";

interface PipelineExecutionProps {
  recommendedHardware: string;
  code: string;
}

export function PipelineExecution({
  recommendedHardware,
  code,
}: PipelineExecutionProps) {
  const [jobId, setJobId] = useState<string | null>(null);
  const [provider, setProvider] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const jobStatus = useJobStatus({
    provider: provider ?? "",
    jobId: jobId ?? "",
    enabled: !!provider && !!jobId,
  });

  const isQuantum = recommendedHardware === HardwareType.QUANTUM;

  const handleExecute = async () => {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      if (isQuantum) {
        // Submit as Python code to quantum backend
        const result = await hardwareService.submitPythonCode({
          code,
          device_name: "aer_simulator",
          shots: 1024,
        });
        setProvider(result.provider ?? "ibm-quantum");
        setJobId(result.job_id);
      } else {
        // Submit to classical backend
        const result = await hardwareService.submitClassicalTask("local", {
          code,
          language: "python",
        });
        setProvider(result.provider ?? "local");
        setJobId(result.job_id);
      }
    } catch (err: any) {
      setSubmitError(err.message || "Failed to submit job");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Not submitted yet
  if (!jobId) {
    return (
      <Card variant="glass" className="animate-fade-in">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5 text-primary" />
            Execute on {recommendedHardware} Backend
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Ready to execute your code on the recommended{" "}
            <Badge variant={isQuantum ? "quantum" : "classical"}>
              {recommendedHardware}
            </Badge>{" "}
            backend.
          </p>

          {submitError && (
            <div className="mb-4 rounded-lg border border-destructive/50 bg-destructive/10 p-3">
              <p className="text-sm text-destructive">{submitError}</p>
            </div>
          )}

          <Button
            variant="quantum"
            onClick={handleExecute}
            disabled={isSubmitting}
            className="gap-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Execute Code
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Job submitted — show status
  const statusIcon = () => {
    if (jobStatus.status === "COMPLETED" || jobStatus.status === "completed") {
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    }
    if (jobStatus.status === "FAILED" || jobStatus.status === "failed") {
      return <XCircle className="h-5 w-5 text-destructive" />;
    }
    return <Loader2 className="h-5 w-5 animate-spin text-primary" />;
  };

  return (
    <Card variant="glass" className="animate-fade-in">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            {statusIcon()}
            Job Status
          </CardTitle>
          <Badge variant="outline" className="font-mono text-xs">
            {jobId}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-lg border border-border bg-secondary/20 p-3">
            <span className="text-sm text-muted-foreground">Status</span>
            <Badge
              variant={
                jobStatus.status === "COMPLETED" || jobStatus.status === "completed"
                  ? "quantum"
                  : jobStatus.status === "FAILED" || jobStatus.status === "failed"
                    ? "destructive"
                    : "outline"
              }
            >
              {jobStatus.status || "SUBMITTING"}
            </Badge>
          </div>

          <div className="flex items-center justify-between rounded-lg border border-border bg-secondary/20 p-3">
            <span className="text-sm text-muted-foreground">Provider</span>
            <span className="font-mono text-sm">{provider}</span>
          </div>

          {jobStatus.isPolling && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3.5 w-3.5 animate-pulse" />
              Polling every 5 seconds...
            </div>
          )}

          {jobStatus.error && (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3">
              <p className="text-sm text-destructive">{jobStatus.error}</p>
            </div>
          )}

          {jobStatus.result && (
            <div className="rounded-lg border border-primary/30 bg-primary/5 p-3">
              <p className="text-sm font-medium mb-2">Execution Results</p>
              <pre className="overflow-x-auto text-xs font-mono">
                {JSON.stringify(jobStatus.result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
