# src/core/Pipeline.py
from typing import List, Dict
from ..interfaces.IModule import IModule

class Pipeline:
    def __init__(self, modules: List[IModule]):
        self.modules = modules
        self.execution_context = {}

    def process(self, agent_context: Dict) -> str:
        """
        Executa o fluxo de processamento usando o contexto do Agent
        
        Args:
            agent_context (Dict): Dados do Agent (histórico, memórias, estado)
            
        Returns:
            str: Resposta final processada
        """
        context = agent_context.copy()
        context['partial_results'] = {}  # Inicializa dicionário para resultados parciais
        
        for module in self.modules:
            module_name = module.__class__.__name__
            result = module.run(context)
            context['partial_results'][module_name] = result
            
        # Extrair resposta final do último módulo (assumindo que é o de consolidação)
        final_module_result = context['partial_results'].get('ResponseConsolidationModule', {})
        final_response = final_module_result.get('final_response', '')
        
        # Fallback se não houver resposta
        if not final_response:
            final_response = agent_context.get('fallback_response', 'Não foi possível processar a resposta.')
            
        return final_response