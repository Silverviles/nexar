import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Info, Loader2, Sparkles } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import {
  decisionEngineService,
  getProblemTypeLabel,
  getTimeComplexityLabel,
  fieldDescriptions
} from '@/services/decision-engine-service';
import {
  ProblemType,
  TimeComplexity,
  type CodeAnalysisInput
} from '@/types/decision-engine.tp';

export default function DecisionEngine() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState<CodeAnalysisInput>({
    problem_type: ProblemType.OPTIMIZATION,
    problem_size: 1000,
    qubits_required: 10,
    circuit_depth: 150,
    gate_count: 500,
    cx_gate_ratio: 0.33,
    superposition_score: 0.75,
    entanglement_score: 0.70,
    time_complexity: TimeComplexity.POLYNOMIAL,
    memory_requirement_mb: 256
  });

  const handleInputChange = (field: keyof CodeAnalysisInput, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: typeof value === 'string' && !isNaN(Number(value)) ? Number(value) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await decisionEngineService.predict(formData);
      
      if (result.success && result.recommendation) {
        toast({
          title: 'Decision Complete',
          description: `Recommended: ${result.recommendation.recommended_hardware}`,
        });
        
        // Navigate to results page with the result data
        navigate('/decision-results', { state: { result } });
      } else {
        toast({
          title: 'Error',
          description: result.error || 'Failed to get recommendation',
          variant: 'destructive'
        });
      }
    } catch (error: any) {
      toast({
        title: 'Request Failed',
        description: error.response?.data?.message || error.message || 'Failed to connect to decision engine',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout title="Decision Engine" description="Get hardware recommendations based on problem parameters">
      <div className="mx-auto max-w-4xl">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-quantum" />
              Hardware Decision Parameters
            </CardTitle>
            <CardDescription>
              Enter the characteristics of your computational problem to receive optimal hardware recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <TooltipProvider>
                {/* Problem Type */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Label htmlFor="problem_type">Problem Type</Label>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                      </TooltipTrigger>
                      <TooltipContent className="max-w-xs">
                        <p>{fieldDescriptions.problem_type}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <Select
                    value={formData.problem_type}
                    onValueChange={(value) => handleInputChange('problem_type', value as ProblemType)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.values(ProblemType).map(type => (
                        <SelectItem key={type} value={type}>
                          {getProblemTypeLabel(type)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Time Complexity */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Label htmlFor="time_complexity">Time Complexity</Label>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                      </TooltipTrigger>
                      <TooltipContent className="max-w-xs">
                        <p>{fieldDescriptions.time_complexity}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <Select
                    value={formData.time_complexity}
                    onValueChange={(value) => handleInputChange('time_complexity', value as TimeComplexity)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.values(TimeComplexity).map(complexity => (
                        <SelectItem key={complexity} value={complexity}>
                          {getTimeComplexityLabel(complexity)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Problem Size */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="problem_size">Problem Size</Label>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-xs">
                          <p>{fieldDescriptions.problem_size}</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Input
                      id="problem_size"
                      type="number"
                      min="1"
                      value={formData.problem_size}
                      onChange={(e) => handleInputChange('problem_size', e.target.value)}
                      required
                    />
                  </div>

                  {/* Qubits Required */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="qubits_required">Qubits Required</Label>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-xs">
                          <p>{fieldDescriptions.qubits_required}</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Input
                      id="qubits_required"
                      type="number"
                      min="0"
                      value={formData.qubits_required}
                      onChange={(e) => handleInputChange('qubits_required', e.target.value)}
                      required
                    />
                  </div>

                  {/* Circuit Depth */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="circuit_depth">Circuit Depth</Label>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-xs">
                          <p>{fieldDescriptions.circuit_depth}</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Input
                      id="circuit_depth"
                      type="number"
                      min="0"
                      value={formData.circuit_depth}
                      onChange={(e) => handleInputChange('circuit_depth', e.target.value)}
                      required
                    />
                  </div>

                  {/* Gate Count */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="gate_count">Gate Count</Label>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-xs">
                          <p>{fieldDescriptions.gate_count}</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Input
                      id="gate_count"
                      type="number"
                      min="0"
                      value={formData.gate_count}
                      onChange={(e) => handleInputChange('gate_count', e.target.value)}
                      required
                    />
                  </div>

                  {/* CX Gate Ratio */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="cx_gate_ratio">CX Gate Ratio</Label>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-xs">
                          <p>{fieldDescriptions.cx_gate_ratio}</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Input
                      id="cx_gate_ratio"
                      type="number"
                      min="0"
                      max="1"
                      step="0.01"
                      value={formData.cx_gate_ratio}
                      onChange={(e) => handleInputChange('cx_gate_ratio', e.target.value)}
                      required
                    />
                  </div>

                  {/* Superposition Score */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="superposition_score">Superposition Score</Label>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-xs">
                          <p>{fieldDescriptions.superposition_score}</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Input
                      id="superposition_score"
                      type="number"
                      min="0"
                      max="1"
                      step="0.01"
                      value={formData.superposition_score}
                      onChange={(e) => handleInputChange('superposition_score', e.target.value)}
                      required
                    />
                  </div>

                  {/* Entanglement Score */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="entanglement_score">Entanglement Score</Label>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-xs">
                          <p>{fieldDescriptions.entanglement_score}</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Input
                      id="entanglement_score"
                      type="number"
                      min="0"
                      max="1"
                      step="0.01"
                      value={formData.entanglement_score}
                      onChange={(e) => handleInputChange('entanglement_score', e.target.value)}
                      required
                    />
                  </div>

                  {/* Memory Requirement */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="memory_requirement_mb">Memory Requirement (MB)</Label>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-xs">
                          <p>{fieldDescriptions.memory_requirement_mb}</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Input
                      id="memory_requirement_mb"
                      type="number"
                      min="0"
                      step="0.1"
                      value={formData.memory_requirement_mb}
                      onChange={(e) => handleInputChange('memory_requirement_mb', e.target.value)}
                      required
                    />
                  </div>
                </div>
              </TooltipProvider>

              <div className="flex gap-4">
                <Button type="submit" disabled={loading} className="flex-1">
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-4 w-4" />
                      Get Recommendation
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/dashboard')}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
