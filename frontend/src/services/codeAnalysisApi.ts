/**
 * API Service for Code Analysis Engine
 */

import api from "@/lib/axios";
import type {
  AnalysisResult,
  CodeSubmission,
  LanguageDetectionResponse,
  SupportedLanguagesResponse,
} from "@/types/codeAnalysis";

const API_BASE_URL = "/v1/code-analysis-engine";

class CodeAnalysisAPI {
  private baseUrl: string;
  private languageCache = new Map<
    string,
    { data: LanguageDetectionResponse; expiresAt: number }
  >();
  private inFlightLanguageRequests = new Map<
    string,
    Promise<LanguageDetectionResponse>
  >();

  private static readonly LANGUAGE_CACHE_TTL_MS = 30_000;
  private static readonly LANGUAGE_CACHE_MAX_ENTRIES = 100;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private buildLanguageCacheKey(code: string): string {
    const normalized = code.trim();
    const snippet = normalized.slice(0, 4096);
    return `${snippet.length}:${snippet}`;
  }

  private setLanguageCache(
    key: string,
    value: LanguageDetectionResponse,
  ): void {
    if (this.languageCache.size >= CodeAnalysisAPI.LANGUAGE_CACHE_MAX_ENTRIES) {
      const firstKey = this.languageCache.keys().next().value as
        | string
        | undefined;
      if (firstKey) {
        this.languageCache.delete(firstKey);
      }
    }

    this.languageCache.set(key, {
      data: value,
      expiresAt: Date.now() + CodeAnalysisAPI.LANGUAGE_CACHE_TTL_MS,
    });
  }

  /**
   * Get list of supported programming languages
   */
  async getSupportedLanguages(): Promise<SupportedLanguagesResponse> {
    try {
      const response = await api.get(`${this.baseUrl}/supported-languages`);

      if (response.status !== 200) {
        throw new Error(
          `Failed to fetch supported languages: ${response.statusText}`,
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
   * Detect language using backend ML/fallback pipeline.
   * Includes short-lived cache and in-flight deduplication to avoid repeated calls.
   */
  async detectLanguage(
    submission: Pick<CodeSubmission, "code">,
  ): Promise<LanguageDetectionResponse> {
    const code = submission.code ?? "";

    if (!code.trim()) {
      return {
        language: "unknown",
        confidence: 0,
        is_supported: false,
        details: "Empty code provided",
        method: "error",
      };
    }

    const cacheKey = this.buildLanguageCacheKey(code);
    const cached = this.languageCache.get(cacheKey);
    if (cached && cached.expiresAt > Date.now()) {
      return cached.data;
    }

    const existingRequest = this.inFlightLanguageRequests.get(cacheKey);
    if (existingRequest) {
      return existingRequest;
    }

    const request = api
      .post(`${this.baseUrl}/detect-language`, { code })
      .then((response) => {
        if (response.status !== 200) {
          throw new Error(`Failed to detect language: ${response.statusText}`);
        }

        const data = response.data as LanguageDetectionResponse;
        this.setLanguageCache(cacheKey, data);
        return data;
      })
      .catch((error) => {
        throw new Error(error.message || "Failed to detect language");
      })
      .finally(() => {
        this.inFlightLanguageRequests.delete(cacheKey);
      });

    this.inFlightLanguageRequests.set(cacheKey, request);
    return request;
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
