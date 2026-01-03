/**
 * Code Analysis Page - Complete Implementation
 */

import { useState, useEffect } from "react";
import {
  Code,
  Upload,
  Play,
  Sliders,
  DollarSign,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { LanguageDetector } from "@/components/analysis/LanguageDetector";
import { ResultsDisplay } from "@/components/analysis/ResultsDisplay";
import { codeAnalysisAPI } from "@/services/codeAnalysisApi";
import type {
  AnalysisResult,
  OptimizationPreference,
} from "@/types/codeAnalysis";
import { cn } from "@/lib/utils";

const sampleCode = `from qiskit import QuantumCircuit

# Quantum circuit generated from Python code
qc = QuantumCircuit(2, 2)

# Apply quantum gates
qc.h(0)  # Hadamard gate on qubit 0
qc.h(1)  # Hadamard gate on qubit 1
qc.x(0)  # X gate (NOT) on qubit 0
qc.cx(0, 1)  # CNOT gate with control=0, target=1

# Measure qubits
qc.measure([0, 1], [0, 1])`;

export default function CodeAnalysis() {
  const [code, setCode] = useState(sampleCode);
  const [optimization, setOptimization] =
    useState<OptimizationPreference>("balanced");
  const [maxBudget, setMaxBudget] = useState<string>("10.00");
  const [priority, setPriority] = useState<string>("Normal");

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState("");

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Update progress messages based on progress
  useEffect(() => {
    if (!isAnalyzing) return;

    if (analysisProgress < 30) {
      setProgressMessage("Parsing code structure...");
    } else if (analysisProgress < 60) {
      setProgressMessage("Detecting algorithm patterns...");
    } else if (analysisProgress < 90) {
      setProgressMessage("Evaluating resource requirements...");
    } else {
      setProgressMessage("Generating routing recommendation...");
    }
  }, [analysisProgress, isAnalyzing]);

  const handleAnalyze = async () => {
    if (!code.trim()) return;

    setIsAnalyzing(true);
    setAnalysisProgress(0);
    setResult(null);
    setError(null);

    // Simulate progress for better UX
    const progressInterval = setInterval(() => {
      setAnalysisProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 15;
      });
    }, 200);

    try {
      const analysisResult = await codeAnalysisAPI.analyzeCode({ code });

      // Complete progress
      clearInterval(progressInterval);
      setAnalysisProgress(100);

      // Show result after brief delay
      setTimeout(() => {
        setResult(analysisResult);
        setIsAnalyzing(false);
      }, 500);
    } catch (err) {
      clearInterval(progressInterval);
      setIsAnalyzing(false);
      setAnalysisProgress(0);
      setError(err instanceof Error ? err.message : "Analysis failed");
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setCode(content);
    };
    reader.readAsText(file);
  };

  return (
    <MainLayout
      title="Code Analysis"
      description="Submit code for quantum-classical routing decision"
    >
      <div className="grid grid-cols-1 gap-4 md:gap-6 lg:grid-cols-3">
        {/* Code Editor Panel */}
        <Card variant="glass" className="lg:col-span-2">
          <CardHeader>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Code className="h-5 w-5 text-primary" />
                  Code Input
                </CardTitle>
                <CardDescription>
                  Paste or upload your code for analysis
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <Label htmlFor="file-upload" className="cursor-pointer">
                  <div className="flex items-center gap-2 rounded-md border border-border bg-background px-3 py-2 text-sm hover:bg-accent">
                    <Upload className="h-4 w-4" />
                    Upload File
                  </div>
                  <Input
                    id="file-upload"
                    type="file"
                    accept=".py,.qs,.qasm,.txt"
                    className="hidden"
                    onChange={handleFileUpload}
                  />
                </Label>
              </div>
            </div>

            {/* Language Detection HUD */}
            <div className="mt-3 rounded-lg border border-primary/20 bg-primary/5 p-3">
              <LanguageDetector code={code} />
            </div>
          </CardHeader>

          <CardContent>
            <Textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="min-h-[250px] font-mono text-xs bg-secondary/30 border-border resize-none md:min-h-[350px] md:text-sm"
              placeholder="Paste your code here..."
            />

            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3 text-xs text-muted-foreground md:gap-4 md:text-sm">
                <span>{code.split("\n").length} lines</span>
                <span>{code.length} characters</span>
              </div>

              <Button
                variant="quantum"
                size="lg"
                className="w-full gap-2 sm:w-auto"
                onClick={handleAnalyze}
                disabled={isAnalyzing || !code.trim()}
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    Analyze Code
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Configuration Panel */}
        <div className="space-y-4 md:space-y-6">
          <Card variant="glass">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <Sliders className="h-4 w-4 text-primary" />
                Optimization Preference
              </CardTitle>
            </CardHeader>
            <CardContent>
              <RadioGroup
                value={optimization}
                onValueChange={(v) =>
                  setOptimization(v as OptimizationPreference)
                }
              >
                {[
                  {
                    value: "cost",
                    label: "Cost-Optimized",
                    desc: "Minimize execution costs",
                  },
                  {
                    value: "performance",
                    label: "Performance-Optimized",
                    desc: "Fastest execution time",
                  },
                  {
                    value: "balanced",
                    label: "Balanced",
                    desc: "Optimal cost-performance ratio",
                  },
                ].map((option) => (
                  <Label
                    key={option.value}
                    className={cn(
                      "flex items-start gap-3 rounded-lg border p-3 cursor-pointer transition-all",
                      optimization === option.value
                        ? "border-primary/50 bg-primary/5"
                        : "border-border hover:border-primary/30"
                    )}
                  >
                    <RadioGroupItem value={option.value} className="mt-0.5" />
                    <div>
                      <p className="font-medium text-sm">{option.label}</p>
                      <p className="text-xs text-muted-foreground">
                        {option.desc}
                      </p>
                    </div>
                  </Label>
                ))}
              </RadioGroup>
            </CardContent>
          </Card>

          <Card variant="glass">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <DollarSign className="h-4 w-4 text-success" />
                Budget Constraint
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <Label className="text-xs text-muted-foreground">
                    Max Cost per Execution
                  </Label>
                  <Input
                    type="number"
                    value={maxBudget}
                    onChange={(e) => setMaxBudget(e.target.value)}
                    placeholder="$10.00"
                    className="mt-1 bg-secondary/30"
                  />
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">
                    Priority Level
                  </Label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="mt-1 w-full rounded-md border border-border bg-secondary/30 px-3 py-2 text-sm"
                  >
                    <option>Normal</option>
                    <option>High</option>
                    <option>Critical</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Analysis Progress */}
        {isAnalyzing && (
          <Card variant="glass" className="animate-fade-in lg:col-span-3">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                Analyzing Code...
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Progress value={analysisProgress} className="h-2" />
                <p className="text-sm text-muted-foreground">
                  {progressMessage}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {error && (
          <Alert variant="destructive" className="lg:col-span-3">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Analysis Results */}
        {result && !isAnalyzing && (
          <div className="lg:col-span-3">
            <ResultsDisplay result={result} />
          </div>
        )}
      </div>
    </MainLayout>
  );
}
