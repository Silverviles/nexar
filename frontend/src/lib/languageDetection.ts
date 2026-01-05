/**
 * Frontend Language Detection Library
 * Heuristic-based detection for supported quantum languages
 */

import type { SupportedLanguage } from "@/types/codeAnalysis";

interface LanguageSignature {
  language: SupportedLanguage;
  patterns: RegExp[];
  weight: number;
}

const LANGUAGE_SIGNATURES: LanguageSignature[] = [
  {
    language: "openqasm",
    patterns: [
      /OPENQASM\s+\d+\.\d+/i,
      /include\s+"qelib1\.inc"/i,
      /qreg\s+\w+\[\d+\]/,
      /creg\s+\w+\[\d+\]/,
      /^\s*gate\s+\w+/m,
    ],
    weight: 3,
  },
  {
    language: "qsharp",
    patterns: [
      /namespace\s+\w+/,
      /operation\s+\w+\s*\(/,
      /using\s*\(/,
      /Microsoft\.Quantum/,
      /body\s*\(\.\.\.\)/,
    ],
    weight: 3,
  },
  {
    language: "qiskit",
    patterns: [
      /from\s+qiskit\s+import/i,
      /import\s+qiskit/i,
      /QuantumCircuit/,
      /QuantumRegister/,
      /ClassicalRegister/,
    ],
    weight: 3,
  },
  {
    language: "cirq",
    patterns: [
      /import\s+cirq/i,
      /from\s+cirq\s+import/i,
      /cirq\.Circuit/,
      /cirq\.LineQubit/,
      /cirq\.GridQubit/,
    ],
    weight: 3,
  },
  {
    language: "python",
    patterns: [
      /def\s+\w+\s*\(/,
      /class\s+\w+/,
      /import\s+\w+/,
      /from\s+\w+\s+import/,
      /if\s+__name__\s*==\s*["']__main__["']/,
    ],
    weight: 1,
  },
];

export interface DetectionResult {
  language: SupportedLanguage | "unknown";
  confidence: number;
  isScanning: boolean;
  matchedPatterns: number;
}

/**
 * Detect programming language from code content
 */
export function detectLanguage(code: string): DetectionResult {
  if (!code || code.trim().length === 0) {
    return {
      language: "unknown",
      confidence: 0,
      isScanning: false,
      matchedPatterns: 0,
    };
  }

  // Check if code is too short to analyze
  if (code.trim().length < 10) {
    return {
      language: "unknown",
      confidence: 0,
      isScanning: true,
      matchedPatterns: 0,
    };
  }

  const scores: Record<SupportedLanguage, number> = {
    python: 0,
    qiskit: 0,
    qsharp: 0,
    cirq: 0,
    openqasm: 0,
  };

  let maxMatches = 0;

  // Calculate scores for each language
  for (const signature of LANGUAGE_SIGNATURES) {
    let matches = 0;
    for (const pattern of signature.patterns) {
      if (pattern.test(code)) {
        matches++;
      }
    }
    scores[signature.language] = matches * signature.weight;
    maxMatches = Math.max(maxMatches, matches);
  }

  // Find language with highest score
  let detectedLanguage: SupportedLanguage | "unknown" = "unknown";
  let maxScore = 0;

  for (const [lang, score] of Object.entries(scores)) {
    if (score > maxScore) {
      maxScore = score;
      detectedLanguage = lang as SupportedLanguage;
    }
  }

  // Calculate confidence (0-1)
  let confidence = 0;
  if (detectedLanguage !== "unknown") {
    const signature = LANGUAGE_SIGNATURES.find(
      (s) => s.language === detectedLanguage
    );
    if (signature) {
      confidence = Math.min(
        maxScore / (signature.patterns.length * signature.weight),
        1
      );
    }
  }

  return {
    language: detectedLanguage,
    confidence: Math.round(confidence * 100) / 100,
    isScanning: confidence < 0.5 && code.length < 100,
    matchedPatterns: maxMatches,
  };
}

/**
 * Get language display name
 */
export function getLanguageDisplayName(
  language: SupportedLanguage | "unknown"
): string {
  const names: Record<SupportedLanguage | "unknown", string> = {
    python: "Python",
    qiskit: "Qiskit",
    qsharp: "Q#",
    cirq: "Cirq",
    openqasm: "OpenQASM",
    unknown: "Unknown",
  };
  return names[language];
}

/**
 * Get language color theme
 */
export function getLanguageColor(
  language: SupportedLanguage | "unknown"
): string {
  const colors: Record<SupportedLanguage | "unknown", string> = {
    python: "text-blue-400",
    qiskit: "text-purple-400",
    qsharp: "text-indigo-400",
    cirq: "text-cyan-400",
    openqasm: "text-teal-400",
    unknown: "text-gray-400",
  };
  return colors[language];
}
