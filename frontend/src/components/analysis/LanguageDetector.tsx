/**
 * Language Detector HUD Component
 * Real-time language detection display
 */

import { useEffect, useState } from "react";
import { Code2, Loader2, CheckCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  detectLanguage,
  getLanguageDisplayName,
  getLanguageColor,
} from "@/lib/languageDetection";
import type { SupportedLanguage } from "@/types/codeAnalysis";
import { cn } from "@/lib/utils";

interface LanguageDetectorProps {
  code: string;
  className?: string;
}

export function LanguageDetector({ code, className }: LanguageDetectorProps) {
  const [detection, setDetection] = useState(detectLanguage(""));

  useEffect(() => {
    const result = detectLanguage(code);
    setDetection(result);
  }, [code]);

  const { language, confidence, isScanning } = detection;

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
              getLanguageColor(language)
            )}
          >
            <Code2 className="h-3 w-3" />
            {getLanguageDisplayName(language)}
            <span className="text-xs opacity-70">
              {(confidence * 100).toFixed(0)}%
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
