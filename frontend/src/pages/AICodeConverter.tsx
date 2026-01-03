import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Loader2, Copy, Check, Eye, Code, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { MainLayout } from '@/components/layout/MainLayout';

export default function AICodeConverter() {
  const navigate = useNavigate();
  const [inputCode, setInputCode] = useState('');
  const [outputCode, setOutputCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [hasConverted, setHasConverted] = useState(false);

  const handleConvert = async () => {
    if (!inputCode.trim() || isLoading) return;

    setIsLoading(true);
    setOutputCode('');
    setHasConverted(false);

    // Simulate API call to Python-to-Quantum converter backend
    setTimeout(() => {
      const mockOutput = `from qiskit import QuantumCircuit

# Quantum circuit generated from Python code
qc = QuantumCircuit(2, 2)

# Apply quantum gates
qc.h(0)  # Hadamard gate on qubit 0
qc.h(1)  # Hadamard gate on qubit 1
qc.x(0)  # X gate (NOT) on qubit 0
qc.cx(0, 1)  # CNOT gate with control=0, target=1

# Measure qubits
qc.measure([0, 1], [0, 1])`;
      setOutputCode(mockOutput);
      setHasConverted(true);
      setIsLoading(false);
    }, 2000);
  };

  const viewDetailedAnalysis = () => {
    navigate('/conversion-results');
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(outputCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <MainLayout title="Python to Quantum Converter" description="Convert classical Python code to quantum circuits using Qiskit">
      <div className="space-y-4 md:space-y-6">
        {/* Conversion Header */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-4">
                <div className="glow-card flex h-12 w-12 items-center justify-center rounded-lg bg-card border">
                  <Code className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-lg">Python Code</CardTitle>
                  <CardDescription>Classical implementation</CardDescription>
                </div>
              </div>
              
              <ArrowRight className="h-6 w-6 text-quantum" />
              
              <div className="flex items-center gap-4">
                <div className="glow-quantum flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                  <Zap className="h-6 w-6 text-quantum" />
                </div>
                <div>
                  <CardTitle className="text-lg">Quantum Circuit</CardTitle>
                  <CardDescription>Qiskit implementation</CardDescription>
                </div>
              </div>

              <Button
                onClick={handleConvert}
                disabled={!inputCode.trim() || isLoading}
                size="lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Converting...
                  </>
                ) : (
                  <>
                    <Zap className="mr-2 h-4 w-4" />
                    Convert to Quantum
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
        </Card>

        {/* Code Input and Output */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
          {/* Input */}
          <Card className="flex flex-col">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Code className="h-5 w-5 text-primary" />
                <CardTitle>Python Code Input</CardTitle>
              </div>
              <CardDescription>
                Paste your classical Python code here (functions, logic gates, algorithms)
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1 p-0">
              <Textarea
                value={inputCode}
                onChange={(e) => setInputCode(e.target.value)}
                placeholder={`# Paste your Python code here...\n# Example: Logic gates, mathematical functions, etc.\n\ndef nor_gate(a, b):\n    return 1 - (a | b)\n\ndef and_gate(a, b):\n    return a & b`}
                className="min-h-[500px] border-0 rounded-none font-mono text-sm resize-none focus-visible:ring-0"
              />
            </CardContent>
          </Card>

          {/* Output */}
          <Card className="flex flex-col">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <Zap className="h-5 w-5 text-quantum" />
                    <CardTitle>Quantum Circuit Output</CardTitle>
                  </div>
                  <CardDescription>
                    Generated Qiskit quantum circuit code
                  </CardDescription>
                </div>
                {outputCode && (
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={copyToClipboard}
                    >
                      {copied ? (
                        <>
                          <Check className="mr-2 h-4 w-4" />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy className="mr-2 h-4 w-4" />
                          Copy
                        </>
                      )}
                    </Button>
                    {hasConverted && (
                      <Button
                        size="sm"
                        onClick={viewDetailedAnalysis}
                      >
                        <Eye className="mr-2 h-4 w-4" />
                        View Analysis
                      </Button>
                    )}
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent className="flex-1 p-4">
              {isLoading ? (
                <div className="flex items-center justify-center h-[500px]">
                  <div className="text-center">
                    <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-quantum" />
                    <p className="text-sm text-muted-foreground">Converting Python to Quantum Circuit...</p>
                    <p className="text-xs text-muted-foreground mt-2">Analyzing code structure and generating quantum gates</p>
                  </div>
                </div>
              ) : outputCode ? (
                <pre className="font-mono text-sm overflow-auto h-[500px] rounded-lg bg-muted/50 p-4">
                  <code>{outputCode}</code>
                </pre>
              ) : (
                <div className="flex items-center justify-center h-[500px] text-center">
                  <div className="text-muted-foreground space-y-3">
                    <div className="glow-quantum mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                      <Zap className="h-8 w-8 text-quantum" />
                    </div>
                    <p className="font-medium">Your quantum circuit will appear here</p>
                    <p className="text-sm">Paste Python code and click "Convert to Quantum" to begin</p>
                    <div className="text-xs mt-4 p-3 bg-muted rounded-lg border">
                      <p className="font-medium mb-1">Supported conversions:</p>
                      <p>Logic gates (AND, OR, NOR, XOR) • Mathematical functions • Boolean operations</p>
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
