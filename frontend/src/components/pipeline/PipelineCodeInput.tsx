/**
 * Pipeline Code Input
 * Code textarea with file upload for the pipeline page.
 */

import { Code, Upload, Play, Loader2 } from "lucide-react";
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
import { Input } from "@/components/ui/input";

const sampleCode = `from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)

# 1. Create superposition
qc.h(0)
qc.h(1)

# 2. Oracle: phase flip on |11⟩
qc.cz(0, 1)

# 3. Diffusion operator
qc.h(0)
qc.h(1)

qc.x(0)
qc.x(1)

qc.cz(0, 1)

qc.x(0)
qc.x(1)

qc.h(0)
qc.h(1)

qc.draw("mpl")`;

interface PipelineCodeInputProps {
  code: string;
  onCodeChange: (code: string) => void;
  onSubmit: () => void;
  isRunning: boolean;
}

export function PipelineCodeInput({
  code,
  onCodeChange,
  onSubmit,
  isRunning,
}: PipelineCodeInputProps) {
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      onCodeChange(content);
    };
    reader.readAsText(file);
  };

  const handleLoadSample = () => {
    onCodeChange(sampleCode);
  };

  return (
    <Card variant="glass">
      <CardHeader>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Code className="h-5 w-5 text-primary" />
              Code Input
            </CardTitle>
            <CardDescription>
              Paste your code or upload a file — the pipeline will analyze it and recommend the best backend
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleLoadSample}>
              Load Sample
            </Button>
            <Label htmlFor="pipeline-file-upload" className="cursor-pointer">
              <div className="flex items-center gap-2 rounded-md border border-border bg-background px-3 py-2 text-sm hover:bg-accent">
                <Upload className="h-4 w-4" />
                Upload
              </div>
              <Input
                id="pipeline-file-upload"
                type="file"
                accept=".py,.qs,.qasm,.txt"
                className="hidden"
                onChange={handleFileUpload}
              />
            </Label>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <Textarea
          value={code}
          onChange={(e) => onCodeChange(e.target.value)}
          className="min-h-[200px] font-mono text-xs bg-secondary/30 border-border resize-none md:min-h-[300px] md:text-sm"
          placeholder="Paste your quantum or classical code here..."
          disabled={isRunning}
        />

        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4 text-xs text-muted-foreground md:text-sm">
            <span>{code.split("\n").length} lines</span>
            <span>{code.length} characters</span>
          </div>

          <Button
            variant="quantum"
            size="lg"
            className="w-full gap-2 sm:w-auto"
            onClick={onSubmit}
            disabled={isRunning || !code.trim()}
          >
            {isRunning ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Running Pipeline...
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Run Pipeline
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
