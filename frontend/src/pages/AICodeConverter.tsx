import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowRight,
  Loader2,
  Copy,
  Check,
  Eye,
  Code,
  Zap,
  Download,
  BarChart,
  Cpu,
  Play,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { MainLayout } from "@/components/layout/MainLayout";
import { toast } from "sonner";

export default function AICodeConverter() {
  const navigate = useNavigate();
  const [inputCode, setInputCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [copied, setCopied] = useState(false);

  // Single execution function - like your test script
  const executeFullFlow = async () => {
    if (!inputCode.trim() || isLoading) return;

    setIsLoading(true);
    setResults(null);

    try {
      toast.info("Starting full conversion flow...");

      // Step 1: Translate Python to Quantum
      toast.info("Translating Python to quantum code...");
      const translateResponse = await fetch("http://localhost:3000/translate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          python_code: inputCode,
        }),
      });

      if (!translateResponse.ok) {
        throw new Error(`Translation failed: ${translateResponse.status}`);
      }

      const translation = await translateResponse.json();
      const quantumCode = translation.quantum_code;

      // Add imports if needed
      const quantumCodeWithImports = quantumCode.startsWith("from qiskit")
        ? quantumCode
        : `from qiskit import QuantumCircuit\n${quantumCode}`;

      toast.success("Translation successful!");

      // Step 2: Execute Quantum Circuit
      toast.info("Executing quantum circuit...");
      const executeResponse = await fetch("http://localhost:3000/execute", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          quantum_code: quantumCodeWithImports,
          gate_type: "auto", // Auto-detect
          shots: 1000,
        }),
      });

      if (!executeResponse.ok) {
        throw new Error(`Execution failed: ${executeResponse.status}`);
      }

      const execution = await executeResponse.json();

      if (!execution.success) {
        throw new Error("Quantum execution failed");
      }

      toast.success("Execution successful!");

      // Step 3: Estimate Python performance
      toast.info("Analyzing performance...");
      let pythonPerformance = null;
      try {
        // Simple estimation based on gate type
        const estimatedOpsPerSecond = 10_000_000; // 10M ops/sec
        const estimatedPerOp = 0.0001; // 0.1µs per operation

        // Calculate quantum stats
        const quantumTime =
          execution.performance?.execution_time_seconds * 1000 || 0; // ms
        const quantumPerShot = quantumTime / 1000; // ms per shot

        pythonPerformance = {
          estimatedOpsPerSecond,
          estimatedPerOp,
          speedDifference: quantumPerShot / estimatedPerOp,
        };
      } catch (e) {
        console.log("Performance estimation skipped:", e);
      }

      // Step 4: Prepare complete results
      const completeResults = {
        metadata: {
          timestamp: new Date().toISOString(),
          shots: 1000,
          gateType: "Auto-detected",
        },
        pythonCode: inputCode,
        quantumCode: quantumCodeWithImports,
        executionResults: execution,
        pythonPerformance,
      };

      setResults(completeResults);
      toast.success("Full flow completed!");
    } catch (error: any) {
      console.error("Full flow error:", error);
      toast.error(`Error: ${error.message || "Failed to complete conversion"}`);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      toast.success(`${type} copied to clipboard`);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error("Failed to copy to clipboard");
    }
  };

  const viewDetailedAnalysis = () => {
    if (results) {
      navigate("/conversion-results", {
        state: { results },
      });
    }
  };

  const exportResults = () => {
    if (!results) return;

    const exportData = {
      ...results,
      export_timestamp: new Date().toISOString(),
      export_format: "JSON v1.0",
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `quantum_conversion_${new Date().getTime()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    toast.success("Results exported as JSON");
  };

  // Reset and start over
  const resetConverter = () => {
    setInputCode("");
    setResults(null);
    toast.info("Converter reset. Paste new Python code.");
  };

  return (
    <MainLayout
      title="Python to Quantum Converter"
      description="Convert and execute Python code as quantum circuits"
    >
      <div className="space-y-4 md:space-y-6">
        {/* Header Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-4">
                <div className="glow-card flex h-12 w-12 items-center justify-center rounded-lg bg-card border">
                  <Code className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle>Single-Step Conversion</CardTitle>
                  <CardDescription>
                    Paste Python code, click once, get full results
                  </CardDescription>
                </div>
              </div>

              <div className="flex gap-2">
                {results && (
                  <Button variant="outline" onClick={resetConverter}>
                    New Conversion
                  </Button>
                )}
                <Button
                  onClick={executeFullFlow}
                  disabled={!inputCode.trim() || isLoading}
                  size="lg"
                  className="min-w-[180px]"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Running Full Flow...
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4" />
                      Convert & Execute
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
          {/* Left Panel: Input */}
          <Card className="flex flex-col">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Code className="h-5 w-5 text-primary" />
                <CardTitle>Python Code Input</CardTitle>
              </div>
              <CardDescription>
                Paste your Python code (logic gates, functions, algorithms)
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1 p-0">
              <Textarea
                value={inputCode}
                onChange={(e) => setInputCode(e.target.value)}
                placeholder={`# Paste your Python code here...\n# Example logic gates:\n\ndef xor_gate(a, b):\n    return a ^ b\n\ndef nor_gate(a, b):\n    return 1 - (a | b)\n\ndef complex_logic(a, b, c):\n    return (a and b) or (not c)`}
                className="min-h-[500px] border-0 rounded-none font-mono text-sm resize-none focus-visible:ring-0"
                disabled={isLoading}
              />
            </CardContent>
          </Card>

          {/* Right Panel: Results or Placeholder */}
          <Card className="flex flex-col">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-quantum" />
                  <CardTitle>Results</CardTitle>
                </div>
                {results && (
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        copyToClipboard(results.quantumCode, "Quantum code")
                      }
                    >
                      {copied ? (
                        <>
                          <Check className="mr-2 h-4 w-4" />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy className="mr-2 h-4 w-4" />
                          Copy Code
                        </>
                      )}
                    </Button>
                    <Button size="sm" onClick={viewDetailedAnalysis}>
                      <Eye className="mr-2 h-4 w-4" />
                      Details
                    </Button>
                  </div>
                )}
              </div>
              <CardDescription>
                {results
                  ? "Conversion and execution results"
                  : "Results will appear here"}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1 p-4">
              {isLoading ? (
                <div className="flex flex-col items-center justify-center h-[500px] space-y-4">
                  <Loader2 className="h-12 w-12 animate-spin text-quantum" />
                  <div className="text-center space-y-2">
                    <p className="font-medium">
                      Running Full Conversion Flow...
                    </p>
                    <div className="space-y-1 text-sm text-muted-foreground">
                      <p>✓ 1. Translating Python to quantum code</p>
                      <p>✓ 2. Executing quantum circuit (1000 shots)</p>
                      <p>→ 3. Analyzing results and performance</p>
                    </div>
                    <p className="text-xs text-muted-foreground mt-4">
                      This may take a few seconds...
                    </p>
                  </div>
                </div>
              ) : results ? (
                <div className="space-y-6 h-[500px] overflow-y-auto pr-2">
                  {/* Quantum Code Preview */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Zap className="h-4 w-4 text-quantum" />
                      <h3 className="font-medium">Generated Quantum Code</h3>
                    </div>
                    <pre className="text-xs font-mono bg-muted/50 p-3 rounded-lg overflow-auto max-h-[150px]">
                      <code>{results.quantumCode}</code>
                    </pre>
                  </div>

                  {/* Execution Summary */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <BarChart className="h-4 w-4 text-quantum" />
                      <h3 className="font-medium">Execution Summary</h3>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 bg-muted/30 rounded-lg">
                        <div className="text-sm text-muted-foreground">
                          Total Shots
                        </div>
                        <div className="text-2xl font-bold">1,000</div>
                      </div>
                      <div className="p-3 bg-muted/30 rounded-lg">
                        <div className="text-sm text-muted-foreground">
                          Circuit Depth
                        </div>
                        <div className="text-2xl font-bold">
                          {results.executionResults.performance?.depth || "N/A"}
                        </div>
                      </div>
                      <div className="p-3 bg-muted/30 rounded-lg">
                        <div className="text-sm text-muted-foreground">
                          Qubits
                        </div>
                        <div className="text-2xl font-bold">
                          {results.executionResults.performance?.num_qubits ||
                            "N/A"}
                        </div>
                      </div>
                      <div className="p-3 bg-muted/30 rounded-lg">
                        <div className="text-sm text-muted-foreground">
                          Execution Time
                        </div>
                        <div className="text-lg font-bold">
                          {results.executionResults.performance
                            ?.execution_time_seconds
                            ? `${(
                                results.executionResults.performance
                                  .execution_time_seconds * 1000
                              ).toFixed(1)} ms`
                            : "N/A"}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Measurement Results */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium flex items-center gap-2">
                        <BarChart className="h-4 w-4" />
                        Measurement Results
                      </h3>
                      <span className="text-sm text-muted-foreground">
                        {
                          Object.keys(results.executionResults.counts || {})
                            .length
                        }{" "}
                        states
                      </span>
                    </div>
                    <div className="space-y-2">
                      {Object.entries(
                        results.executionResults.counts || {}
                      ).map(([state, count]: [string, any]) => {
                        const probability = count / 1000;
                        return (
                          <div key={state} className="space-y-1">
                            <div className="flex justify-between text-sm">
                              <span className="font-mono">|{state}⟩</span>
                              <span>
                                {count} shots ({(probability * 100).toFixed(1)}
                                %)
                              </span>
                            </div>
                            <div className="h-2 bg-muted rounded-full overflow-hidden">
                              <div
                                className="h-full bg-quantum rounded-full transition-all duration-500"
                                style={{ width: `${probability * 100}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Quick Performance Comparison */}
                  {results.pythonPerformance && (
                    <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border">
                      <div className="flex items-center gap-2 mb-2">
                        <Cpu className="h-4 w-4" />
                        <h3 className="font-medium">Performance Insight</h3>
                      </div>
                      <p className="text-sm">
                        Python execution would be approximately{" "}
                        <span className="font-bold">
                          {Math.round(
                            results.pythonPerformance.speedDifference
                          ).toLocaleString()}
                          × faster
                        </span>{" "}
                        for the same operations.
                      </p>
                      <p className="text-xs text-muted-foreground mt-2">
                        Quantum simulation is for algorithm verification, not
                        performance comparison.
                      </p>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-2 pt-4 border-t">
                    <Button
                      variant="outline"
                      className="flex-1"
                      onClick={exportResults}
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Export JSON
                    </Button>
                    <Button className="flex-1" onClick={viewDetailedAnalysis}>
                      <Eye className="mr-2 h-4 w-4" />
                      View Full Analysis
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-[500px] text-center space-y-6">
                  <div className="space-y-3">
                    <div className="glow-quantum mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                      <Zap className="h-8 w-8 text-quantum" />
                    </div>
                    <div>
                      <p className="font-medium">Ready to Convert</p>
                      <p className="text-sm text-muted-foreground">
                        Paste Python code and click "Convert & Execute"
                      </p>
                    </div>
                  </div>

                  <div className="w-full max-w-md space-y-4">
                    <div className="text-sm font-medium">Example Code:</div>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        onClick={() =>
                          setInputCode(`def xor_gate(a, b):\n    return a ^ b`)
                        }
                        className="p-3 text-left text-xs font-mono bg-muted/50 rounded-lg border hover:bg-muted/80 transition-colors"
                      >
                        XOR Gate
                      </button>
                      <button
                        onClick={() =>
                          setInputCode(
                            `def nor_gate(a, b):\n    return 1 - (a | b)`
                          )
                        }
                        className="p-3 text-left text-xs font-mono bg-muted/50 rounded-lg border hover:bg-muted/80 transition-colors"
                      >
                        NOR Gate
                      </button>
                      <button
                        onClick={() =>
                          setInputCode(`def and_gate(a, b):\n    return a & b`)
                        }
                        className="p-3 text-left text-xs font-mono bg-muted/50 rounded-lg border hover:bg-muted/80 transition-colors"
                      >
                        AND Gate
                      </button>
                      <button
                        onClick={() =>
                          setInputCode(
                            `def logic_func(a, b, c):\n    return (a and b) or (not c)`
                          )
                        }
                        className="p-3 text-left text-xs font-mono bg-muted/50 rounded-lg border hover:bg-muted/80 transition-colors"
                      >
                        Complex Logic
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Info Card */}
        <Card>
          <CardHeader>
            <CardTitle>How It Works</CardTitle>
            <CardDescription>Single-step conversion process</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Code className="h-5 w-5 text-primary" />
                </div>
                <h4 className="font-medium">1. Paste Python</h4>
                <p className="text-sm text-muted-foreground">
                  Paste any Python code with logic operations
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <ArrowRight className="h-5 w-5 text-primary" />
                </div>
                <h4 className="font-medium">2. AI Translation</h4>
                <p className="text-sm text-muted-foreground">
                  AI model converts to quantum circuit code
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Play className="h-5 w-5 text-primary" />
                </div>
                <h4 className="font-medium">3. Execute</h4>
                <p className="text-sm text-muted-foreground">
                  Circuit runs with 1000 shots on simulator
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <BarChart className="h-5 w-5 text-primary" />
                </div>
                <h4 className="font-medium">4. Results</h4>
                <p className="text-sm text-muted-foreground">
                  Get complete analysis and performance metrics
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
