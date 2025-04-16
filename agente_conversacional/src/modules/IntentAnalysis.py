# src/modules/IntentAnalysis.py
from typing import Dict, List, Any  # Adicione esta linha
from ..interfaces.IModule import IModule

class IntentAnalysis(IModule):
    def __init__(self, immutable_memory):
        self.immutable_memory = immutable_memory
        
    def run(self, context: Dict) -> Dict:
        user_message = context['user_message']
        
        # Lógica de análise de intenção usando a memória
        intent = "neutra"
        if any(keyword in user_message.lower() for keyword in ["ajuda", "como"]):
            intent = "assistência"
        elif any(keyword in user_message.lower() for keyword in ["opinião", "sentir"]):
            intent = "emocional"
            
        return {
            'intent': intent,
            'confidence': 0.85,
            'relevant_keywords': self._extract_keywords(user_message)
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        # Implementação simplificada de extração de palavras-chave
        return list(set(text.lower().split()[:5]))