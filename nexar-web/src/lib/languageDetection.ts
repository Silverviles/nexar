/**
 * Language presentation helpers
 * Detection is intentionally delegated to backend /detect-language endpoint.
 */

import type { SupportedLanguage } from '@/types/codeAnalysis'

export function getLanguageDisplayName(language: SupportedLanguage | 'unknown'): string {
  const names: Record<SupportedLanguage | 'unknown', string> = {
    python: 'Python',
    qiskit: 'Qiskit',
    qsharp: 'Q#',
    cirq: 'Cirq',
    openqasm: 'OpenQASM',
    unknown: 'Unknown',
  }
  return names[language]
}

/**
 * All languages render in the same neutral ink-muted tone -- Carbon reserves
 * chromatic color for the primary accent and semantic states, not per-language
 * tagging, so frontend's per-language rainbow (blue/purple/indigo/cyan/teal)
 * collapses to one consistent color here.
 */
export function getLanguageColor(_language: SupportedLanguage | 'unknown'): string {
  return 'text-ink-muted'
}
