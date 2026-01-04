import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
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
  Search,
  Target,
  Gauge,
  Sparkles,
  AlertCircle,
  Layers,
  GitCompare,
  Brain,
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
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface PatternInfo {
  pattern: string;
  confidence: number;
  quantum_algo: string;
  speedup: string;
  suitability_score: number;
}

interface QuantumSuitability {
  score: number;
  level: "high" | "medium" | "low";
  message: string;
}

interface CodeMetrics {
  has_function: boolean;
  has_loop: boolean;
  has_condition: boolean;
  line_count: number;
  function_count: number;
  loop_count: number;
  condition_count: number;
}

interface AnalysisResponse {
  success: boolean;
  patterns: PatternInfo[];
  quantum_suitability: QuantumSuitability;
  metrics: CodeMetrics;
  original_code?: string;
  error?: string;
}

export default function QuantumPatternAnalyzer() {
  const navigate = useNavigate();
  const [inputCode, setInputCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<AnalysisResponse | null>(null);
  const [copied, setCopied] = useState(false);
  const [includeCode, setIncludeCode] = useState(false);

  const analyzeCode = async () => {
    if (!inputCode.trim() || isLoading) return;

    setIsLoading(true);
    setResults(null);

    try {
      toast.info("Analyzing code for quantum patterns...");

      const response = await fetch(
        "http://localhost:3000/api/quantum/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            code: inputCode,
            include_code: includeCode,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || `Analysis failed: ${response.status}`
        );
      }

      const data: AnalysisResponse = await response.json();

      if (!data.success) {
        throw new Error(data.error || "Analysis failed");
      }

      setResults(data);
      toast.success("Analysis completed!");
    } catch (error: any) {
      console.error("Analysis error:", error);
      toast.error(`Error: ${error.message || "Failed to analyze code"}`);
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
      navigate("/quantum-analysis-results", {
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
    link.download = `quantum_analysis_${new Date().getTime()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    toast.success("Results exported as JSON");
  };

  const resetAnalyzer = () => {
    setInputCode("");
    setResults(null);
    setIncludeCode(false);
    toast.info("Analyzer reset. Paste new Python code.");
  };

  const getSuitabilityColor = (level: string) => {
    switch (level) {
      case "high":
        return "text-green-600 bg-green-100 border-green-200";
      case "medium":
        return "text-yellow-600 bg-yellow-100 border-yellow-200";
      case "low":
        return "text-red-600 bg-red-100 border-red-200";
      default:
        return "text-gray-600 bg-gray-100 border-gray-200";
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  // Example codes for quick testing
  const exampleCodes = [
    {
      name: "Linear Search",
      code: `def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1`,
    },
    {
      name: "Binary Search",
      code: `def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1`,
    },
    {
      name: "Brute Force",
      code: `def max_product_subarray(arr):
    max_product = float('-inf')
    for i in range(len(arr)):
        for j in range(i, len(arr)):
            product = 1
            for k in range(i, j + 1):
                product *= arr[k]
            max_product = max(max_product, product)
    return max_product`,
    },
    {
      name: "Min/Max Finding",
      code: `def find_min_max(arr):
    min_val = arr[0]
    max_val = arr[0]
    for num in arr:
        if num < min_val:
            min_val = num
        if num > max_val:
            max_val = num
    return min_val, max_val`,
    },
  ];

  return (
    <MainLayout
      title="Quantum Pattern Analyzer"
      description="Analyze Python code for quantum suitability and detect quantum-amenable patterns"
    >
      <div className="space-y-4 md:space-y-6">
        {/* Header Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-4">
                <div className="glow-card flex h-12 w-12 items-center justify-center rounded-lg bg-card border">
                  <Brain className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <CardTitle>Quantum Pattern Recognition</CardTitle>
                  <CardDescription>
                    Detect quantum-amenable algorithms and estimate quantum
                    advantage
                  </CardDescription>
                </div>
              </div>

              <div className="flex gap-2">
                {results && (
                  <Button variant="outline" onClick={resetAnalyzer}>
                    New Analysis
                  </Button>
                )}
                <Button
                  onClick={analyzeCode}
                  disabled={!inputCode.trim() || isLoading}
                  size="lg"
                  className="min-w-[180px] bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Target className="mr-2 h-4 w-4" />
                      Analyze Code
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
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Code className="h-5 w-5 text-primary" />
                  <CardTitle>Python Code Input</CardTitle>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="include-code"
                    checked={includeCode}
                    onChange={(e) => setIncludeCode(e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300"
                  />
                  <label
                    htmlFor="include-code"
                    className="text-sm text-muted-foreground"
                  >
                    Include code in results
                  </label>
                </div>
              </div>
              <CardDescription>
                Paste Python algorithms to analyze quantum suitability
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1 p-0">
              <Textarea
                value={inputCode}
                onChange={(e) => setInputCode(e.target.value)}
                placeholder={`# Paste your Python algorithm here...\n# Example: Search algorithms, optimization problems, etc.\n\ndef search(arr, target):\n    for i in range(len(arr)):\n        if arr[i] == target:\n            return i\n    return -1`}
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
                  <Sparkles className="h-5 w-5 text-purple-600" />
                  <CardTitle>Analysis Results</CardTitle>
                </div>
              </div>
              <CardDescription>
                {results
                  ? "Quantum pattern analysis results"
                  : "Results will appear here"}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1 p-4">
              {isLoading ? (
                <div className="flex flex-col items-center justify-center h-[500px] space-y-4">
                  <Loader2 className="h-12 w-12 animate-spin text-purple-600" />
                  <div className="text-center space-y-2">
                    <p className="font-medium">Analyzing Quantum Patterns...</p>
                    <div className="space-y-1 text-sm text-muted-foreground">
                      <p>✓ 1. Parsing Python AST</p>
                      <p>✓ 2. Detecting algorithm patterns</p>
                      <p>→ 3. Calculating quantum suitability</p>
                      <p>→ 4. Generating recommendations</p>
                    </div>
                    <p className="text-xs text-muted-foreground mt-4">
                      Analyzing code structure and patterns...
                    </p>
                  </div>
                </div>
              ) : results ? (
                <div className="space-y-6 h-[500px] overflow-y-auto pr-2">
                  {/* Suitability Score */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Gauge className="h-5 w-5 text-purple-600" />
                        <h3 className="font-medium">Quantum Suitability</h3>
                      </div>
                      <Badge
                        className={`px-3 py-1 ${getSuitabilityColor(
                          results.quantum_suitability.level
                        )}`}
                      >
                        {results.quantum_suitability.level.toUpperCase()}
                      </Badge>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Suitability Score</span>
                        <span className="font-bold">
                          {results.quantum_suitability.score.toFixed(3)}
                        </span>
                      </div>
                      <Progress
                        value={results.quantum_suitability.score * 100}
                        className="h-2"
                      />
                      <p className="text-sm text-muted-foreground">
                        {results.quantum_suitability.message}
                      </p>
                    </div>
                  </div>

                  {/* Detected Patterns */}
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Layers className="h-5 w-5 text-purple-600" />
                      <h3 className="font-medium">Detected Patterns</h3>
                      <Badge variant="outline" className="ml-auto">
                        {results.patterns.length} patterns
                      </Badge>
                    </div>

                    {results.patterns.length > 0 ? (
                      <div className="space-y-3">
                        {results.patterns.map((pattern, index) => (
                          <Card key={index} className="border shadow-sm">
                            <CardContent className="p-4">
                              <div className="flex items-start justify-between mb-2">
                                <div className="space-y-1">
                                  <div className="flex items-center gap-2">
                                    <h4 className="font-medium capitalize">
                                      {pattern.pattern.replace(/_/g, " ")}
                                    </h4>
                                    <Badge
                                      variant="secondary"
                                      className={`text-xs ${getConfidenceColor(
                                        pattern.confidence
                                      )}`}
                                    >
                                      {Math.round(pattern.confidence * 100)}%
                                      confident
                                    </Badge>
                                  </div>
                                  <h4 className="font-medium capitalize">
                                    {pattern.quantum_algo}
                                  </h4>
                                </div>
                                {/* <Badge className="bg-blue-100 text-blue-800 border-blue-200">
                                  {pattern.speedup}
                                </Badge> */}
                              </div>

                              <div className="grid grid-cols-2 gap-2 mt-3 text-sm">
                                <div className="flex items-center gap-1">
                                  <Sparkles className="h-3 w-3" />
                                  <span className="text-muted-foreground">
                                    Score:
                                  </span>
                                  <span className="font-medium ml-1">
                                    {pattern.suitability_score.toFixed(2)}
                                  </span>
                                </div>
                                {/* <div className="flex items-center gap-1">
                                  <GitCompare className="h-3 w-3" />
                                  <span className="text-muted-foreground">Speedup:</span>
                                  <span className="font-medium ml-1">{pattern.speedup}</span>
                                </div> */}
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 text-center border rounded-lg bg-muted/30">
                        <AlertCircle className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                        <p className="text-sm text-muted-foreground">
                          No quantum-amenable patterns detected in this code
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Code Metrics */}
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <BarChart className="h-5 w-5 text-purple-600" />
                      <h3 className="font-medium">Code Metrics</h3>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      <div className="p-3 bg-muted/30 rounded-lg">
                        <div className="text-sm text-muted-foreground">
                          Lines
                        </div>
                        <div className="text-2xl font-bold">
                          {results.metrics.line_count}
                        </div>
                      </div>
                      <div className="p-3 bg-muted/30 rounded-lg">
                        <div className="text-sm text-muted-foreground">
                          Functions
                        </div>
                        <div className="text-2xl font-bold">
                          {results.metrics.function_count}
                        </div>
                      </div>
                      <div className="p-3 bg-muted/30 rounded-lg">
                        <div className="text-sm text-muted-foreground">
                          Loops
                        </div>
                        <div className="text-2xl font-bold">
                          {results.metrics.loop_count}
                        </div>
                      </div>
                      <div className="p-3 bg-muted/30 rounded-lg">
                        <div className="text-sm text-muted-foreground">
                          Conditions
                        </div>
                        <div className="text-2xl font-bold">
                          {results.metrics.condition_count}
                        </div>
                      </div>
                      <div className="p-3 bg-muted/30 rounded-lg">
                        <div className="text-sm text-muted-foreground">
                          Has Functions
                        </div>
                        <div className="text-lg font-bold">
                          {results.metrics.has_function ? "✓" : "✗"}
                        </div>
                      </div>
                      <div className="p-3 bg-muted/30 rounded-lg">
                        <div className="text-sm text-muted-foreground">
                          Has Loops
                        </div>
                        <div className="text-lg font-bold">
                          {results.metrics.has_loop ? "✓" : "✗"}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Recommendations */}
                  {results.quantum_suitability.level === "high" && (
                    <div className="p-4 bg-gradient-to-r from-black to-purple-900 rounded-lg border">
                      <div className="flex items-center gap-2 mb-2">
                        <Zap className="h-4 w-4 text-purple-600" />
                        <h3 className="font-medium ">Quantum Opportunity</h3>
                      </div>
                      <p className="text-sm mb-3">
                        This code is highly suitable for quantum conversion.
                        Consider:
                      </p>
                      <ul className="space-y-1 text-sm">
                        {results.patterns.map((pattern, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <div className="h-1.5 w-1.5 rounded-full bg-purple-600 mt-1.5 flex-shrink-0" />
                            <span>
                              Convert to{" "}
                              <span className="font-medium">
                                {pattern.quantum_algo}
                              </span>
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Action Buttons */}
                  {/* <div className="flex gap-2 pt-4 border-t">
                    <Button
                      variant="outline"
                      className="flex-1"
                      onClick={exportResults}
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Export JSON
                    </Button>
                    <Button
                      className="flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700"
                      onClick={viewDetailedAnalysis}
                    >
                      <Eye className="mr-2 h-4 w-4" />
                      View Full Analysis
                    </Button>
                  </div> */}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-[500px] text-center space-y-6">
                  <div className="space-y-3">
                    <div className="glow-quantum mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-purple-100">
                      <Search className="h-8 w-8 text-purple-600" />
                    </div>
                    <div>
                      <p className="font-medium">Ready to Analyze</p>
                      <p className="text-sm text-muted-foreground">
                        Paste Python code and click "Analyze Code"
                      </p>
                    </div>
                  </div>

                  <div className="w-full max-w-md space-y-4">
                    <div className="text-sm font-medium">
                      Try Example Algorithms:
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      {exampleCodes.map((example, index) => (
                        <button
                          key={index}
                          onClick={() => setInputCode(example.code)}
                          className="p-3 text-left text-xs font-mono bg-muted/50 rounded-lg border hover:bg-muted/80 transition-colors group"
                        >
                          <div className="font-medium mb-1">{example.name}</div>
                          <div className="text-muted-foreground truncate">
                            {example.code.split("\n")[0]}
                          </div>
                        </button>
                      ))}
                    </div>

                    <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                      <div className="flex items-center gap-2 mb-1">
                        <Target className="h-4 w-4 text-blue-600" />
                        <span className="text-sm font-medium text-blue-800">
                          What we detect:
                        </span>
                      </div>
                      <ul className="text-xs text-blue-700 space-y-1">
                        <li>• Linear/Binary Search algorithms</li>
                        <li>• Brute force optimization problems</li>
                        <li>• Min/Max finding operations</li>
                        <li>• Sorting algorithms</li>
                        <li>• Nested loop patterns</li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
