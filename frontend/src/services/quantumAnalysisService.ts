import api from '@/lib/axios';
import { AnalysisResponse } from '@/types/code-converstion.tp';
import { toast } from 'sonner';


class QuantumAnalysisService {
  async analyzeCode(code: string, includeCode: boolean = false): Promise<AnalysisResponse> {
    try {
      toast.info('Analyzing code for quantum patterns...');

      const response = await api.post<AnalysisResponse>('/quantum/analyze', {
        code,
        include_code: includeCode,
      });

      if (!response.data.success) {
        throw new Error(response.data.error || 'Analysis failed');
      }

      toast.success('Analysis completed!');
      return response.data;
    } catch (error: any) {
      console.error('Analysis error:', error);
      toast.error(`Error: ${error.message || 'Failed to analyze code'}`);
      throw error;
    }
  }
}

// Export as singleton instance
export default new QuantumAnalysisService();