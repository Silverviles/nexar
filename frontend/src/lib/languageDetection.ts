/**
 * Language presentation helpers
 * Detection is intentionally delegated to backend /detect-language endpoint.
 */

import type { SupportedLanguage } from "@/types/codeAnalysis";

/**
 * Get language display name
 */
export function getLanguageDisplayName(
  language: SupportedLanguage | "unknown",
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
  language: SupportedLanguage | "unknown",
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
