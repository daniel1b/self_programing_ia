# src/modules/ResponseConsolidationModule.py
from typing import Dict
from ..interfaces.IModule import IModule

class ResponseConsolidationModule(IModule):
    """Módulo para consolidar diferentes análises em uma resposta final."""
    
    def run(self, context: Dict) -> Dict:
        """
        Consolida as diferentes análises em uma resposta coerente.
        
        Args:
            context (Dict): Contexto contendo as análises e configurações
            
        Returns:
            Dict: Resultado final consolidado
        """
        # Obtém as análises anteriores
        partial_results = context.get('partial_results', {})
        
        rational_result = partial_results.get('RationalAnalysisModule', {})
        emotional_result = partial_results.get('EmotionalAnalysisModule', {})
        
        # Extraindo as análises
        rational_analysis = rational_result.get('rational_analysis', '')
        emotional_analysis = emotional_result.get('emotional_analysis', '')
        
        # Dados do agente
        agent_state = context.get('agent_state', {})
        personality = agent_state.get('personality', {})
        tone = personality.get('tone', 'neutro')
        
        # Construindo o prompt de consolidação
        prompt = f"""
        Baseado nas seguintes análises:
        
        ANÁLISE RACIONAL:
        {rational_analysis}
        
        ANÁLISE EMOCIONAL:
        {emotional_analysis}
        
        Considerando que o agente tem um tom {tone}, consolide estas análises em uma resposta única e coerente:
        """
        
        # Envio para o LLM
        llm = context.get('llm')
        if llm:
            final_response = llm.enviar_prompt(prompt)
        else:
            # Fallback
            final_response = f"Com base na análise racional e emocional: {rational_analysis[:100]}... {emotional_analysis[:100]}..."
        
        return {
            'final_response': final_response,
            'prompt_used': prompt
        }