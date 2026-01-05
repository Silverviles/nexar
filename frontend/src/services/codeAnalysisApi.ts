/**
 * API Service for Code Analysis Engine
 */

import api from "@/lib/axios";
import type {
  AnalysisResult,
  CodeSubmission,
  SupportedLanguagesResponse,
} from "@/types/codeAnalysis";

const API_BASE_URL = "/v1/code-analysis-engine";

class CodeAnalysisAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get list of supported programming languages
   */
  async getSupportedLanguages(): Promise<SupportedLanguagesResponse> {
    try {
      const response = await api.get(`${this.baseUrl}/supported-languages`);

      if (response.status !== 200) {
        throw new Error(
          `Failed to fetch supported languages: ${response.statusText}`
        );
      }

      return response.data; // No need for response.json(), axios does it for you
    } catch (error) {
      throw new Error(error.message || "Error fetching supported languages");
    }
  }

  /**
   * Analyze submitted code
   */
  async analyzeCode(submission: CodeSubmission): Promise<AnalysisResult> {
    try {
      const response = await api.post(`${this.baseUrl}/analyze`, submission);

      if (response.status !== 200) {
        throw new Error(`Failed to analyze code: ${response.statusText}`);
      }

      return response.data; // The parsed JSON is in response.data
    } catch (error) {
      throw new Error(error.message || "Failed to analyze code");
    }
  }

  /**
   * Check API health
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    try {
      const response = await api.get(`${this.baseUrl}/health`);

      if (response.status !== 200) {
        throw new Error("Service is unavailable");
      }

      return response.data;
    } catch (error) {
      throw new Error(error.message || "Error checking service health");
    }
  }
}

// Export singleton instance
export const codeAnalysisAPI = new CodeAnalysisAPI();

// Export class for testing
export default CodeAnalysisAPI;
