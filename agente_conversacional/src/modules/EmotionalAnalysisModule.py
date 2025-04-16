# src/modules/EmotionalAnalysisModule.py
from typing import Dict
from ..interfaces.IModule import IModule

class EmotionalAnalysisModule(IModule):
    """Módulo de análise emocional das mensagens."""
    
    def run(self, context: Dict) -> Dict:
        """
        Analisa a mensagem do usuário usando abordagem emocional.
        
        Args:
            context (Dict): Contexto contendo a mensagem, histórico e configurações
            
        Returns:
            Dict: Resultado da análise emocional
        """
        # Acessa os dados necessários do contexto
        message = context.get('user_message', '')
        history = context.get('history', [])
        agent_memory = context.get('agent_memory', '')
        agent_state = context.get('agent_state', {})
        
        # Obtém o prefixo emocional das configurações
        emotional_prefix = agent_state.get('config', {}).get('system_prompts', {}).get('emotional_prefix', '')
        
        # Construção do prompt para LLM
        prompt = f"{emotional_prefix}\n\nHistórico: {history}\n\nMemória: {agent_memory}\n\nMensagem: {message}\n\nAnálise emocional:"
        
        # Envio para o LLM
        llm = context.get('llm')
        if llm:
            emotional_analysis = llm.enviar_prompt(prompt)
        else:
            emotional_analysis = "Não foi possível realizar análise emocional."
        
        return {
            'emotional_analysis': emotional_analysis,
            'prompt_used': prompt
        }