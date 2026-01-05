import torch
from transformers import AutoTokenizer, T5ForConditionalGeneration

MODEL_PATH = "C:/Users/black/OneDrive/Desktop/research/nexar/ai-code-converter/codet5-quantum-best"

class AIService:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        self.model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)
        self.model.eval()
    
    def generate_quantum_code(self, python_code: str, max_length: int = 300) -> str:
        """Generate quantum code from Python code using AI model"""
        inputs = self.tokenizer(
            f"Translate Python to quantum circuit:\n{python_code}",
            return_tensors="pt",
            truncation=True,
            max_length=256
        )
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=3,
                do_sample=True
            )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

# Singleton instance
ai_service = AIService()