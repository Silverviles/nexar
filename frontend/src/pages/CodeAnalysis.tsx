import { useState } from "react";
import { Code, Upload, Play, Settings, Sliders, DollarSign, Loader2, BarChart3, Layers, CheckCircle } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

const sampleCode = `def quantum_grover_search(oracle, n_qubits):
    """
    Implements Grover's search algorithm
    for finding marked items in an unsorted database.
    """
    qc = QuantumCircuit(n_qubits)
    
    # Apply Hadamard to all qubits
    qc.h(range(n_qubits))
    
    # Apply Grover iterations
    iterations = int(np.pi/4 * np.sqrt(2**n_qubits))
    for _ in range(iterations):
        oracle(qc)
        diffuser(qc, n_qubits)
    
    return qc`;

export default function CodeAnalysis() {
  const [code, setCode] = useState(sampleCode);
  const [optimization, setOptimization] = useState("balanced");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisComplete, setAnalysisComplete] = useState(false);

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    setAnalysisProgress(0);
    setAnalysisComplete(false);

    const interval = setInterval(() => {
      setAnalysisProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsAnalyzing(false);
          setAnalysisComplete(true);
          return 100;
        }
        return prev + 10;
      });
    }, 300);
  };

  return (
    <MainLayout title="Code Analysis" description="Submit code for quantum-classical routing decision">
      <div className="grid grid-cols-1 gap-4 md:gap-6 lg:grid-cols-3">
        {/* Code Editor Panel */}
        <Card variant="glass" className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Code className="h-5 w-5 text-primary" />
                  Code Input
                </CardTitle>
                <CardDescription>Paste or upload your code for analysis</CardDescription>
              </div>
              <Button variant="outline" size="sm" className="gap-2">
                <Upload className="h-4 w-4" />
                Upload File
              </Button>
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
              <RadioGroup value={optimization} onValueChange={setOptimization}>
                {[
                  { value: "cost", label: "Cost-Optimized", desc: "Minimize execution costs" },
                  { value: "performance", label: "Performance-Optimized", desc: "Fastest execution time" },
                  { value: "balanced", label: "Balanced", desc: "Optimal cost-performance ratio" },
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
                      <p className="text-xs text-muted-foreground">{option.desc}</p>
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
                  <Label className="text-xs text-muted-foreground">Max Cost per Execution</Label>
                  <Input
                    type="number"
                    placeholder="$10.00"
                    className="mt-1 bg-secondary/30"
                  />
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">Priority Level</Label>
                  <select className="mt-1 w-full rounded-md border border-border bg-secondary/30 px-3 py-2 text-sm">
                    <option>Normal</option>
                    <option>High</option>
                    <option>Critical</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Analysis Results */}
        {(isAnalyzing || analysisComplete) && (
          <Card variant={analysisComplete ? "quantum" : "glass"} className="animate-fade-in lg:col-span-3">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {analysisComplete ? (
                  <>
                    <CheckCircle className="h-5 w-5 text-success" />
                    Analysis Complete
                  </>
                ) : (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin text-primary" />
                    Analyzing Code...
                  </>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isAnalyzing && (
                <div className="space-y-4">
                  <Progress value={analysisProgress} className="h-2" />
                  <p className="text-sm text-muted-foreground">
                    {analysisProgress < 30 && "Parsing code structure..."}
                    {analysisProgress >= 30 && analysisProgress < 60 && "Detecting algorithm patterns..."}
                    {analysisProgress >= 60 && analysisProgress < 90 && "Evaluating resource requirements..."}
                    {analysisProgress >= 90 && "Generating routing recommendation..."}
                  </p>
                </div>
              )}

              {analysisComplete && (
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 md:gap-4">
                  <div className="rounded-lg border border-border bg-secondary/20 p-4">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <BarChart3 className="h-4 w-4" />
                      Complexity Score
                    </div>
                    <p className="mt-2 font-mono text-2xl font-bold text-quantum">8.4 / 10</p>
                    <p className="text-xs text-muted-foreground">High quantum suitability</p>
                  </div>
                  <div className="rounded-lg border border-border bg-secondary/20 p-4">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Layers className="h-4 w-4" />
                      Pattern Detected
                    </div>
                    <Badge variant="quantum" className="mt-2">Grover's Algorithm</Badge>
                    <p className="mt-1 text-xs text-muted-foreground">Search optimization</p>
                  </div>
                  <div className="rounded-lg border border-border bg-secondary/20 p-4">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Settings className="h-4 w-4" />
                      Recommended Hardware
                    </div>
                    <Badge variant="quantum" className="mt-2">Quantum</Badge>
                    <p className="mt-1 text-xs text-muted-foreground">IBM Quantum - 94% confidence</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </MainLayout>
  );
}
