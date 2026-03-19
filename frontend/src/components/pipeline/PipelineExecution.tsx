/**
 * Pipeline Execution
 * Execution step with live job status polling.
 * Routes to IBM Quantum or Local Classical based on the decision engine recommendation.
 */

import { useState } from "react";
import {
  Play,
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
  Server,
  Cpu,
  Atom,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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

  // IBM Quantum settings
  const [deviceName, setDeviceName] = useState("ibm_sherbrooke");
  const [shots, setShots] = useState(1024);

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
        // Submit to IBM Quantum via execute-python endpoint
        // The code must define a `circuit` variable (QuantumCircuit)
        const result = await hardwareService.submitPythonCode({
          code,
          device_name: deviceName,
          shots,
        });
        setProvider(result.provider ?? "ibm-quantum");
        setJobId(result.job_id);
      } else {
        // Submit to local classical Python executor
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

  // Not submitted yet — show execution config
  if (!jobId) {
    return (
      <Card variant="glass" className="animate-fade-in">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {isQuantum ? (
              <Atom className="h-5 w-5 text-quantum" />
            ) : (
              <Cpu className="h-5 w-5 text-primary" />
            )}
            Execute on {isQuantum ? "IBM Quantum" : "Local Classical"} Backend
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {isQuantum ? (
              <>
                <p className="text-sm text-muted-foreground">
                  Your code will be submitted to{" "}
                  <Badge variant="quantum">IBM Quantum</Badge> via the Qiskit
                  Runtime. The code must define a{" "}
                  <code className="rounded bg-secondary/50 px-1.5 py-0.5 font-mono text-xs">
                    circuit
                  </code>{" "}
                  variable (QuantumCircuit).
                </p>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label className="text-xs text-muted-foreground">
                      Device
                    </Label>
                    <select
                      value={deviceName}
                      onChange={(e) => setDeviceName(e.target.value)}
                      className="mt-1 w-full rounded-md border border-border bg-secondary/30 px-3 py-2 text-sm font-mono"
                    >
                      <optgroup label="Real Quantum Hardware">
                        <option value="ibm_sherbrooke">ibm_sherbrooke (127 qubits)</option>
                        <option value="ibm_brisbane">ibm_brisbane (127 qubits)</option>
                        <option value="ibm_kyiv">ibm_kyiv (127 qubits)</option>
                        <option value="ibm_nazca">ibm_nazca (127 qubits)</option>
                      </optgroup>
                      <optgroup label="Simulators">
                        <option value="ibmq_qasm_simulator">ibmq_qasm_simulator</option>
                      </optgroup>
                    </select>
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">
                      Shots
                    </Label>
                    <Input
                      type="number"
                      value={shots}
                      onChange={(e) =>
                        setShots(Math.max(1, parseInt(e.target.value) || 1024))
                      }
                      min={1}
                      max={100000}
                      className="mt-1 bg-secondary/30 font-mono"
                    />
                  </div>
                </div>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">
                Your code will be executed on the{" "}
                <Badge variant="classical">Local Classical</Badge> Python
                runtime. All standard Python libraries and installed packages are
                available.
              </p>
            )}

            {submitError && (
              <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3">
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
                  Submitting to {isQuantum ? "IBM Quantum" : "Local"}...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Execute on {isQuantum ? "IBM Quantum" : "Local Python"}
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Job submitted — show live status
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
            <span className="text-sm text-muted-foreground">Provider</span>
            <Badge variant={isQuantum ? "quantum" : "classical"}>
              {provider === "ibm-quantum" ? "IBM Quantum" : "Local Classical"}
            </Badge>
          </div>

          {isQuantum && (
            <div className="flex items-center justify-between rounded-lg border border-border bg-secondary/20 p-3">
              <span className="text-sm text-muted-foreground">Device</span>
              <span className="font-mono text-sm">{deviceName}</span>
            </div>
          )}

          <div className="flex items-center justify-between rounded-lg border border-border bg-secondary/20 p-3">
            <span className="text-sm text-muted-foreground">Status</span>
            <Badge
              variant={
                jobStatus.status === "COMPLETED" ||
                jobStatus.status === "completed"
                  ? "quantum"
                  : jobStatus.status === "FAILED" ||
                      jobStatus.status === "failed"
                    ? "destructive"
                    : "outline"
              }
            >
              {jobStatus.status || "SUBMITTING"}
            </Badge>
          </div>

          {jobStatus.isPolling && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3.5 w-3.5 animate-pulse" />
              {isQuantum
                ? "Waiting for IBM Quantum (may take minutes in queue)..."
                : "Polling every 5 seconds..."}
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
