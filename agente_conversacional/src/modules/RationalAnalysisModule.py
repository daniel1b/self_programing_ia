# src/modules/RationalAnalysisModule.py
from typing import Dict
from ..interfaces.IModule import IModule

class RationalAnalysisModule(IModule):
    """Módulo de análise racional das mensagens."""
    
    def run(self, context: Dict) -> Dict:
        """
        Analisa a mensagem do usuário usando abordagem racional.
        
        Args:
            context (Dict): Contexto contendo a mensagem, histórico e configurações
            
        Returns:
            Dict: Resultado da análise racional
        """
        # Acessa os dados necessários do contexto
        message = context.get('user_message', '')
        history = context.get('history', [])
        agent_memory = context.get('agent_memory', '')
        agent_state = context.get('agent_state', {})
        
        # Obtém o prefixo racional das configurações
        rational_prefix = agent_state.get('config', {}).get('system_prompts', {}).get('rational_prefix', '')
        
        # Construção do prompt para LLM
        prompt = f"{rational_prefix}\n\nHistórico: {history}\n\nMemória: {agent_memory}\n\nMensagem: {message}\n\nAnálise racional:"
        
        # Envio para o LLM (assumindo que context tem uma referência ao LLM)
        llm = context.get('llm')
        if llm:
            rational_analysis = llm.enviar_prompt(prompt)
        else:
            rational_analysis = "Não foi possível realizar análise racional."
        
        return {
            'rational_analysis': rational_analysis,
            'prompt_used': prompt
        }