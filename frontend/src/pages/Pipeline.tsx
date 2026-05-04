/**
 * Unified Pipeline Page
 *
 * Drop code → Analyze → Decide → Execute
 * Uses async Firestore-backed pipeline with polling for progressive results.
 */

import { useState } from "react";
import { Loader2, AlertCircle } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { PipelineStepper } from "@/components/pipeline/PipelineStepper";
import { PipelineCodeInput } from "@/components/pipeline/PipelineCodeInput";
import { PipelineAnalysisResults } from "@/components/pipeline/PipelineAnalysisResults";
import { PipelineDecisionResults } from "@/components/pipeline/PipelineDecisionResults";
import { PipelineExecution } from "@/components/pipeline/PipelineExecution";
import { pipelineService } from "@/services/pipeline-service";
import { usePipelineStatus } from "@/hooks/usePipelineStatus";
import type { PipelineStage } from "@/types/pipeline";
import type { AnalysisResult } from "@/types/codeAnalysis";
import type { DecisionEngineResponse, CodeAnalysisInput } from "@/types/decision-engine.tp";

export default function Pipeline() {
  const [code, setCode] = useState("");
  const [pipelineId, setPipelineId] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Poll for status once we have a pipeline ID
  const pipelineStatus = usePipelineStatus({
    pipelineId: pipelineId ?? "",
    enabled: !!pipelineId,
  });

  // Map backend status to UI stage
  const getStage = (): PipelineStage => {
    if (!pipelineId) return "idle";
    if (isSubmitting) return "processing";
    if (!pipelineStatus.status) return "processing";

    switch (pipelineStatus.status) {
      case "processing":
        return "processing";
      case "analyzing":
        return "analyzing";
      case "deciding":
        return "deciding";
      case "completed":
        return "complete";
      case "failed":
        return "error";
      default:
        return "processing";
    }
  };

  const stage = getStage();

  const handleRunPipeline = async () => {
    if (!code.trim()) return;

    setSubmitError(null);
    setPipelineId(null);
    setIsSubmitting(true);

    try {
      const { pipeline_id } = await pipelineService.run({ code });
      setPipelineId(pipeline_id);
    } catch (err: any) {
      setSubmitError(err.message || "Failed to start pipeline");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setPipelineId(null);
    setSubmitError(null);
    setIsSubmitting(false);
  };

  const isRunning = stage === "processing" || stage === "analyzing" || stage === "deciding";

  // Get typed results from polling state
  const analysisResult = pipelineStatus.analysis as AnalysisResult | null;
  const decisionResult = pipelineStatus.decision as DecisionEngineResponse | null;
  const mappedInput = pipelineStatus.mappedInput as CodeAnalysisInput | null;
  const error = pipelineStatus.error || submitError;

  return (
    <MainLayout
      title="Run Pipeline"
      description="Analyze code and get hardware recommendations in one step"
    >
      <div className="space-y-6">
        {/* Stepper */}
        <Card variant="glass" className="p-4">
          <PipelineStepper currentStage={stage} />
        </Card>

        {/* Code Input */}
        <PipelineCodeInput
          code={code}
          onCodeChange={setCode}
          onSubmit={handleRunPipeline}
          isRunning={isRunning || isSubmitting}
        />

        {/* Progress indicator while running */}
        {isRunning && (
          <Card variant="glass" className="animate-fade-in">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                {stage === "analyzing" && "Analyzing code..."}
                {stage === "deciding" && "Getting hardware recommendation..."}
                {stage === "processing" && "Starting pipeline..."}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Progress
                value={
                  stage === "analyzing" ? 40 :
                  stage === "deciding" ? 75 :
                  20
                }
                className="h-2"
              />
              <p className="mt-2 text-sm text-muted-foreground">
                {stage === "analyzing" && "Parsing code structure, detecting algorithms, computing metrics..."}
                {stage === "deciding" && "ML model predicting optimal hardware..."}
                {stage === "processing" && "Initializing pipeline..."}
                {pipelineStatus.isPolling && " (polling every 3s)"}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Poll error (network issues) */}
        {pipelineStatus.pollError && !error && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Connection issue: {pipelineStatus.pollError}. Retrying...
            </AlertDescription>
          </Alert>
        )}

        {/* Analysis Results (show as soon as available, even while deciding) */}
        {analysisResult && (
          <PipelineAnalysisResults result={analysisResult} />
        )}

        {/* Decision Results */}
        {decisionResult && !isRunning && (
          <PipelineDecisionResults
            result={decisionResult}
            mappedInput={mappedInput}
          />
        )}

        {/* Execution */}
        {decisionResult?.recommendation && stage === "complete" && (
          <>
            <Separator />
            <PipelineExecution
              recommendedHardware={decisionResult.recommendation.recommended_hardware}
              code={code}
            />
          </>
        )}

        {/* Timing info */}
        {pipelineStatus.timing && !isRunning && (
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            {pipelineStatus.timing.analysis_ms != null && (
              <span>Analysis: {pipelineStatus.timing.analysis_ms}ms</span>
            )}
            {pipelineStatus.timing.decision_ms != null && (
              <span>Decision: {pipelineStatus.timing.decision_ms}ms</span>
            )}
            {pipelineStatus.timing.total_ms != null && (
              <span>Total: {pipelineStatus.timing.total_ms}ms</span>
            )}
          </div>
        )}

        {/* Reset button when pipeline is done */}
        {(stage === "complete" || stage === "error") && (
          <div className="flex justify-center">
            <button
              onClick={handleReset}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors underline"
            >
              Reset and start over
            </button>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
