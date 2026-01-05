// File: `api/src/config/endpoints.ts`
export type Endpoints = {
    decisionEngine: {
        base: string;
        health: string;
        predict: string;
    };
    codeAnalysis: {
        base: string;
        health: string;
        analyze: string;
        detectLanguage: string;
        supportedLanguages: string;
    };
    aiCodeConverter: {
        base: string;
    };
    hardware: {
        base: string;
        status: string;
    };
};

export const ENDPOINTS: Endpoints = {
    decisionEngine: {
        base: '/api/v1/decision-engine',
        health: '/api/v1/decision-engine/health',
        predict: '/api/v1/decision-engine/predict',
    },
    codeAnalysis: {
        base: '/api/v1/code-analysis-engine',
        health: '/api/v1/code-analysis-engine/health',
        analyze: '/api/v1/code-analysis-engine/analyze',
        detectLanguage: '/api/v1/code-analysis-engine/detect-language',
        supportedLanguages: '/api/v1/code-analysis-engine/supported-languages',
    },
    aiCodeConverter: {
        base: '/api/v1/ai-code-converter',
    },
    hardware: {
        base: '/api/v1/hardware',
        status: '/api/v1/hardware/status',
    },
};

export function getEndpoint<K extends keyof Endpoints>(group: K, key?: string) {
    const g = ENDPOINTS[group] as any;
    return key ? (g[key] as string | undefined) : g.base;
}
