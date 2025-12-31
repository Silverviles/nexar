import { Award, Clock, DollarSign, Gauge, Brain, Network, TrendingUp, Shield, CheckSquare, AlertTriangle, PieChart, BarChart, GitBranch, MessageSquare, Info } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";

export default function DecisionResults() {
  return (
    <MainLayout title="Decision Results" description="Comprehensive routing recommendation">
      <div className="space-y-4 md:space-y-6">
        {/* Primary Recommendation */}
        <Card variant="quantum" className="animate-scale-in">
          <CardHeader>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <CardTitle className="flex items-center gap-2">
                <Award className="h-5 w-5 text-quantum" />
                Primary Recommendation
              </CardTitle>
              <Badge variant="quantum" className="animate-pulse-glow">Quantum Execution</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:gap-6 lg:grid-cols-4">
              <div className="text-center">
                <div className="relative mx-auto h-24 w-24">
                  <svg className="h-24 w-24 -rotate-90 transform">
                    <circle cx="48" cy="48" r="40" stroke="hsl(var(--border))" strokeWidth="8" fill="none" />
                    <circle
                      cx="48" cy="48" r="40"
                      stroke="hsl(var(--quantum))"
                      strokeWidth="8"
                      fill="none"
                      strokeDasharray={`${94 * 2.51} ${100 * 2.51}`}
                      strokeLinecap="round"
                      className="drop-shadow-[0_0_8px_hsl(var(--quantum))]"
                    />
                  </svg>
                  <span className="absolute inset-0 flex items-center justify-center font-mono text-2xl font-bold">94%</span>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">Confidence Score</p>
              </div>
              <div className="flex flex-col justify-center">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  <span className="text-sm">Expected Time</span>
                </div>
                <p className="mt-1 font-mono text-2xl font-bold">2.4s</p>
                <p className="text-xs text-success">83% faster than classical</p>
              </div>
              <div className="flex flex-col justify-center">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <DollarSign className="h-4 w-4" />
                  <span className="text-sm">Estimated Cost</span>
                </div>
                <p className="mt-1 font-mono text-2xl font-bold">$0.42</p>
                <p className="text-xs text-muted-foreground">Within budget</p>
              </div>
              <div className="flex flex-col justify-center">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Gauge className="h-4 w-4" />
                  <span className="text-sm">Quantum Advantage</span>
                </div>
                <p className="mt-1 font-mono text-2xl font-bold text-quantum">4.2x</p>
                <p className="text-xs text-muted-foreground">vs. classical</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 gap-4 md:gap-6 lg:grid-cols-2">
          {/* ML Model Predictions */}
          <Card variant="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-primary" />
                ML Model Predictions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { name: "Random Forest", prediction: "Quantum", confidence: 92 },
                { name: "XGBoost", prediction: "Quantum", confidence: 96 },
                { name: "Neural Network", prediction: "Quantum", confidence: 94 },
              ].map((model) => (
                <div key={model.name} className="flex items-center justify-between rounded-lg border border-border bg-secondary/20 p-3">
                  <div className="flex items-center gap-3">
                    <Network className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{model.name}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant="quantum">{model.prediction}</Badge>
                    <span className="font-mono text-sm">{model.confidence}%</span>
                  </div>
                </div>
              ))}
              <div className="mt-4 rounded-lg border border-primary/30 bg-primary/5 p-3">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Ensemble Confidence</span>
                  <span className="font-mono text-lg font-bold text-primary">94%</span>
                </div>
                <Progress value={94} className="mt-2 h-2" />
              </div>
            </CardContent>
          </Card>

          {/* Rule-Based Validation */}
          <Card variant="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-success" />
                Rule-Based Validation
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { check: "Qubit threshold (≥20)", passed: true },
                { check: "Coherence time requirement", passed: true },
                { check: "Error rate tolerance (<1%)", passed: true },
                { check: "Gate compatibility", passed: true },
                { check: "Budget constraint", passed: true },
              ].map((rule) => (
                <div key={rule.check} className="flex items-center justify-between rounded-lg border border-border bg-secondary/20 p-3">
                  <div className="flex items-center gap-2">
                    {rule.passed ? (
                      <CheckSquare className="h-4 w-4 text-success" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-warning" />
                    )}
                    <span className="text-sm">{rule.check}</span>
                  </div>
                  <Badge variant={rule.passed ? "success" : "warning"}>
                    {rule.passed ? "Passed" : "Warning"}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Cost-Benefit Analysis */}
          <Card variant="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="h-5 w-5 text-success" />
                Cost-Benefit Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="rounded-lg border border-quantum/30 bg-quantum/5 p-4 text-center">
                    <p className="text-sm text-muted-foreground">Quantum Cost</p>
                    <p className="font-mono text-xl font-bold text-quantum">$0.42</p>
                  </div>
                  <div className="rounded-lg border border-classical/30 bg-classical/5 p-4 text-center">
                    <p className="text-sm text-muted-foreground">Classical Cost</p>
                    <p className="font-mono text-xl font-bold text-classical">$0.08</p>
                  </div>
                </div>
                <div className="rounded-lg border border-success/30 bg-success/5 p-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">ROI Calculation</span>
                    <span className="font-mono font-bold text-success">+$12.50</span>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Based on time savings and quantum advantage factor
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Alternative Options */}
          <Card variant="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="h-5 w-5 text-warning" />
                Alternative Options
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="rounded-lg border border-border bg-secondary/20 p-4">
                <div className="flex items-center justify-between">
                  <Badge variant="classical">Classical GPU</Badge>
                  <span className="font-mono text-sm">78% confidence</span>
                </div>
                <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                  <span>Time: 14.2s</span>
                  <span>Cost: $0.08</span>
                </div>
              </div>
              <div className="rounded-lg border border-border bg-secondary/20 p-4">
                <div className="flex items-center justify-between">
                  <Badge variant="hybrid">Hybrid</Badge>
                  <span className="font-mono text-sm">85% confidence</span>
                </div>
                <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                  <span>Time: 5.8s</span>
                  <span>Cost: $0.25</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Decision Explanation */}
        <Card variant="glow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-primary" />
              Decision Explanation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg border border-border bg-secondary/20 p-4">
              <p className="text-sm leading-relaxed text-muted-foreground">
                <strong className="text-foreground">Quantum execution is recommended</strong> for this Grover's search implementation 
                due to the algorithm's inherent quantum speedup characteristics. The code exhibits O(√N) complexity 
                patterns that demonstrate a <strong className="text-quantum">4.2x quantum advantage</strong> over classical alternatives. 
                All hardware compatibility checks passed, and the estimated cost of <strong className="text-foreground">$0.42</strong> falls 
                within your specified budget constraint.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <Badge variant="outline" className="gap-1">
                  <Info className="h-3 w-3" /> Grover's Algorithm Detected
                </Badge>
                <Badge variant="outline" className="gap-1">
                  <TrendingUp className="h-3 w-3" /> High Quantum Suitability
                </Badge>
                <Badge variant="outline" className="gap-1">
                  <DollarSign className="h-3 w-3" /> Within Budget
                </Badge>
              </div>
            </div>
            <div className="mt-4 flex gap-3">
              <Button variant="quantum" className="gap-2">
                Execute on Quantum
              </Button>
              <Button variant="outline">View Alternatives</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
