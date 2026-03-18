/**
 * Unified Pipeline Page
 *
 * Drop code → Analyze → Decide → Execute
 * Single page that chains all Nexar services into one coherent flow.
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
import type { PipelineResponse, PipelineStage } from "@/types/pipeline";
import type { AnalysisResult } from "@/types/codeAnalysis";
import type { DecisionEngineResponse, CodeAnalysisInput } from "@/types/decision-engine.tp";

export default function Pipeline() {
  const [code, setCode] = useState("");
  const [stage, setStage] = useState<PipelineStage>("idle");
  const [error, setError] = useState<string | null>(null);

  // Results from each pipeline step
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [decisionResult, setDecisionResult] = useState<DecisionEngineResponse | null>(null);
  const [mappedInput, setMappedInput] = useState<CodeAnalysisInput | null>(null);
  const [timing, setTiming] = useState<PipelineResponse["timing"] | null>(null);

  const handleRunPipeline = async () => {
    if (!code.trim()) return;

    // Reset state
    setStage("running");
    setError(null);
    setAnalysisResult(null);
    setDecisionResult(null);
    setMappedInput(null);
    setTiming(null);

    // Show analyzing stage briefly for UX
    setStage("analyzing");

    try {
      const response = await pipelineService.run({ code });

      setTiming(response.timing);

      if (response.analysis) {
        setAnalysisResult(response.analysis as AnalysisResult);
      }

      // Brief delay to show the analysis step before decision
      if (response.status === "completed" || response.status === "partial") {
        setStage("deciding");

        // Small delay for visual feedback
        await new Promise((resolve) => setTimeout(resolve, 300));

        if (response.decision) {
          setDecisionResult(response.decision as DecisionEngineResponse);
        }
        if (response.mapped_input) {
          setMappedInput(response.mapped_input as CodeAnalysisInput);
        }
      }

      if (response.status === "completed") {
        setStage("complete");
      } else if (response.status === "partial") {
        // Partial — show what we have + error
        setStage("complete");
        if (response.error) {
          setError(response.error);
        }
      } else {
        setStage("error");
        setError(response.error || "Pipeline failed");
      }
    } catch (err: any) {
      setStage("error");
      setError(err.message || "Pipeline request failed");
    }
  };

  const handleReset = () => {
    setStage("idle");
    setError(null);
    setAnalysisResult(null);
    setDecisionResult(null);
    setMappedInput(null);
    setTiming(null);
  };

  const isRunning = stage === "running" || stage === "analyzing" || stage === "deciding";

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
          isRunning={isRunning}
        />

        {/* Progress indicator while running */}
        {isRunning && (
          <Card variant="glass" className="animate-fade-in">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                {stage === "analyzing" && "Analyzing code..."}
                {stage === "deciding" && "Getting hardware recommendation..."}
                {stage === "running" && "Starting pipeline..."}
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
                {stage === "analyzing" && "Parsing code structure and detecting algorithms..."}
                {stage === "deciding" && "ML model predicting optimal hardware..."}
                {stage === "running" && "Initializing pipeline..."}
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

        {/* Analysis Results */}
        {analysisResult && !isRunning && (
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
        {timing && !isRunning && (
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            {timing.analysis_ms != null && (
              <span>Analysis: {timing.analysis_ms}ms</span>
            )}
            {timing.decision_ms != null && (
              <span>Decision: {timing.decision_ms}ms</span>
            )}
            <span>Total: {timing.total_ms}ms</span>
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
