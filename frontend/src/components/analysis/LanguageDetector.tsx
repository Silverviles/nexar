/**
 * Language Detector HUD Component
 * Real-time language detection display
 */

import { useEffect, useState } from "react";
import { Code2, Loader2, CheckCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  getLanguageDisplayName,
  getLanguageColor,
} from "@/lib/languageDetection";
import type { LanguageDetectionResponse } from "@/types/codeAnalysis";
import { cn } from "@/lib/utils";
import { codeAnalysisAPI } from "@/services/codeAnalysisApi";

interface LanguageDetectorProps {
  code: string;
  className?: string;
}

export function LanguageDetector({ code, className }: LanguageDetectorProps) {
  const [detection, setDetection] = useState<LanguageDetectionResponse>({
    language: "unknown",
    confidence: 0,
    is_supported: false,
    details: "Type code to detect language",
    method: "error",
  });
  const [isScanning, setIsScanning] = useState(false);

  useEffect(() => {
    const trimmedCode = code.trim();

    if (!trimmedCode) {
      setDetection({
        language: "unknown",
        confidence: 0,
        is_supported: false,
        details: "Type code to detect language",
        method: "error",
      });
      setIsScanning(false);
      return;
    }

    // Avoid noisy requests while user is still typing very short snippets.
    if (trimmedCode.length < 20) {
      setDetection({
        language: "unknown",
        confidence: 0,
        is_supported: false,
        details: "Add a bit more code for reliable detection",
        method: "error",
      });
      setIsScanning(true);
      return;
    }

    let canceled = false;
    const timer = window.setTimeout(async () => {
      try {
        setIsScanning(true);
        const result = await codeAnalysisAPI.detectLanguage({
          code: trimmedCode,
        });
        if (!canceled) {
          setDetection(result);
        }
      } catch (error) {
        if (!canceled) {
          setDetection({
            language: "unknown",
            confidence: 0,
            is_supported: false,
            details:
              error instanceof Error
                ? error.message
                : "Language detection unavailable",
            method: "error",
          });
        }
      } finally {
        if (!canceled) {
          setIsScanning(false);
        }
      }
    }, 450);

    return () => {
      canceled = true;
      window.clearTimeout(timer);
    };
  }, [code]);

  const { language, confidence, method } = detection;

  return (
    <div className={cn("flex items-center gap-2", className)}>
      {isScanning ? (
        <>
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          <span className="text-sm text-muted-foreground">
            Scanning patterns...
          </span>
        </>
      ) : language !== "unknown" ? (
        <>
          <CheckCircle className="h-4 w-4 text-success" />
          <Badge
            variant="outline"
            className={cn(
              "gap-1.5 border-primary/30 bg-primary/5",
              getLanguageColor(language),
            )}
          >
            <Code2 className="h-3 w-3" />
            {getLanguageDisplayName(language)}
            <span className="text-xs opacity-70">
              {(confidence * 100).toFixed(0)}%
            </span>
            <span className="text-[10px] uppercase tracking-wide opacity-70">
              {method}
            </span>
          </Badge>
        </>
      ) : (
        <>
          <Code2 className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">
            Language not detected
          </span>
        </>
      )}
    </div>
  );
}
