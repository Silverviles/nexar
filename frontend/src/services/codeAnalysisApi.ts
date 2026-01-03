/**
 * API Service for Code Analysis Engine
 */

import type {
  AnalysisResult,
  CodeSubmission,
  SupportedLanguagesResponse,
} from "@/types/codeAnalysis";

const API_BASE_URL =
  import.meta.env.VITE_CODE_ANALYSIS_ENGINE_API_BASE ||
  "http://localhost:8002/api/v1";

class CodeAnalysisAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get list of supported programming languages
   */
  async getSupportedLanguages(): Promise<SupportedLanguagesResponse> {
    const response = await fetch(`${this.baseUrl}/supported-languages`);

    if (!response.ok) {
      throw new Error(
        `Failed to fetch supported languages: ${response.statusText}`
      );
    }

    return response.json();
  }

  /**
   * Analyze submitted code
   */
  async analyzeCode(submission: CodeSubmission): Promise<AnalysisResult> {
    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(submission),
    });

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || "Failed to analyze code");
    }

    return response.json();
  }

  /**
   * Check API health
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await fetch(`${this.baseUrl}/health`);

    if (!response.ok) {
      throw new Error("Service is unavailable");
    }

    return response.json();
  }
}

// Export singleton instance
export const codeAnalysisAPI = new CodeAnalysisAPI();

// Export class for testing
export default CodeAnalysisAPI;
