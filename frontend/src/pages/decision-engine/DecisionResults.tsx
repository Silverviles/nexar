import { useLocation, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Award, Clock, DollarSign, Gauge, Brain, GitBranch, MessageSquare, ArrowLeft, Sparkles } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { type DecisionEngineResponse, HardwareType } from '@/types/decision-engine.tp';

export default function DecisionResults() {
  const location = useLocation();
  const navigate = useNavigate();
  const [result, setResult] = useState<DecisionEngineResponse | null>(null);

  useEffect(() => {
    // Get result from navigation state
    if (location.state?.result) {
      setResult(location.state.result);
    } else {
      // No result data, redirect back
      navigate('/decision-engine');
    }
  }, [location, navigate]);

  if (!result || !result.recommendation) {
    return (
      <MainLayout title="Decision Results" description="Hardware recommendation results">
        <Alert>
          <AlertDescription>
            No decision data available. Please submit a decision request first.
          </AlertDescription>
        </Alert>
        <Button onClick={() => navigate('/decision-engine')} className="mt-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Decision Engine
        </Button>
      </MainLayout>
    );
  }

  const { recommendation, alternatives, estimated_execution_time_ms, estimated_cost_usd } = result;
  const isQuantum = recommendation.recommended_hardware === HardwareType.QUANTUM;
  const isClassical = recommendation.recommended_hardware === HardwareType.CLASSICAL;
  const isHybrid = recommendation.recommended_hardware === HardwareType.HYBRID;

  const getBadgeVariant = () => {
    if (isQuantum) return "quantum";
    if (isClassical) return "classical";
    return "hybrid";
  };

  const confidencePercent = Math.round(recommendation.confidence * 100);

  return (
    <MainLayout title="Decision Results" description="Comprehensive routing recommendation">
      <div className="space-y-4 md:space-y-6">
        {/* Back Button */}
        <Button variant="outline" onClick={() => navigate('/decision-engine')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          New Decision
        </Button>

        {/* Primary Recommendation */}
        <Card variant={isQuantum ? "quantum" : "glass"} className="animate-scale-in">
          <CardHeader>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <CardTitle className="flex items-center gap-2">
                <Award className="h-5 w-5" />
                Primary Recommendation
              </CardTitle>
              <Badge variant={getBadgeVariant()} className="animate-pulse-glow">
                {recommendation.recommended_hardware} Execution
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:gap-6 lg:grid-cols-4">
              {/* Confidence Score */}
              <div className="text-center">
                <div className="relative mx-auto h-24 w-24">
                  <svg className="h-24 w-24 -rotate-90 transform">
                    <circle cx="48" cy="48" r="40" stroke="hsl(var(--border))" strokeWidth="8" fill="none" />
                    <circle
                      cx="48" cy="48" r="40"
                      stroke={isQuantum ? "hsl(var(--quantum))" : isClassical ? "hsl(var(--classical))" : "hsl(var(--hybrid))"}
                      strokeWidth="8"
                      fill="none"
                      strokeDasharray={`${confidencePercent * 2.51} ${100 * 2.51}`}
                      strokeLinecap="round"
                      className={isQuantum ? "drop-shadow-[0_0_8px_hsl(var(--quantum))]" : ""}
                    />
                  </svg>
                  <span className="absolute inset-0 flex items-center justify-center font-mono text-2xl font-bold">
                    {confidencePercent}%
                  </span>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">Confidence Score</p>
              </div>

              {/* Expected Time */}
              <div className="flex flex-col justify-center">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  <span className="text-sm">Expected Time</span>
                </div>
                <p className="mt-1 font-mono text-2xl font-bold">
                  {estimated_execution_time_ms 
                    ? `${(estimated_execution_time_ms / 1000).toFixed(2)}s`
                    : 'N/A'}
                </p>
                <p className="text-xs text-muted-foreground">Estimated execution</p>
              </div>

              {/* Estimated Cost */}
              <div className="flex flex-col justify-center">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <DollarSign className="h-4 w-4" />
                  <span className="text-sm">Estimated Cost</span>
                </div>
                <p className="mt-1 font-mono text-2xl font-bold">
                  ${estimated_cost_usd?.toFixed(4) || 'N/A'}
                </p>
                <p className="text-xs text-muted-foreground">Per execution</p>
              </div>

              {/* Probabilities */}
              <div className="flex flex-col justify-center">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Gauge className="h-4 w-4" />
                  <span className="text-sm">Quantum Probability</span>
                </div>
                <p className={`mt-1 font-mono text-2xl font-bold ${isQuantum ? 'text-quantum' : ''}`}>
                  {Math.round(recommendation.quantum_probability * 100)}%
                </p>
                <p className="text-xs text-muted-foreground">
                  Classical: {Math.round(recommendation.classical_probability * 100)}%
                </p>
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
                Model Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-lg border border-border bg-secondary/20 p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Recommended Hardware</span>
                  <Badge variant={getBadgeVariant()}>
                    {recommendation.recommended_hardware}
                  </Badge>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Quantum Probability</span>
                    <span className="font-mono">{(recommendation.quantum_probability * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Classical Probability</span>
                    <span className="font-mono">{(recommendation.classical_probability * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Confidence</span>
                    <span className="font-mono font-bold">{(recommendation.confidence * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Alternative Options */}
          {alternatives && alternatives.length > 0 && (
            <Card variant="glass">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GitBranch className="h-5 w-5 text-warning" />
                  Alternative Options
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {alternatives.map((alt, idx) => (
                  <div key={idx} className="rounded-lg border border-border bg-secondary/20 p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Badge variant={
                        alt.hardware === 'Quantum' ? 'quantum' : 
                        alt.hardware === 'Classical' ? 'classical' : 
                        'hybrid'
                      }>
                        {alt.hardware}
                      </Badge>
                      <span className="font-mono text-sm">{(alt.confidence * 100).toFixed(0)}% confidence</span>
                    </div>
                    <p className="text-xs text-muted-foreground">{alt.trade_off}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Decision Explanation */}
        <Card variant="glow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-primary" />
              Decision Rationale
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg border border-border bg-secondary/20 p-4">
              <p className="text-sm leading-relaxed">
                {recommendation.rationale}
              </p>
              
              {estimated_cost_usd && estimated_execution_time_ms && (
                <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span>Estimated time: <strong>{(estimated_execution_time_ms / 1000).toFixed(2)}s</strong></span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                    <span>Estimated cost: <strong>${estimated_cost_usd.toFixed(4)}</strong></span>
                  </div>
                </div>
              )}
            </div>
            
            <div className="mt-4 flex gap-3 flex-wrap">

              <Button variant="outline" onClick={() => navigate('/decision-engine')}>
                Try Different Parameters
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
