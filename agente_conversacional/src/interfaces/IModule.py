# src/interfaces/IModule.py
from abc import ABC, abstractmethod
from typing import Dict

class IModule(ABC):
    """
    Interface abstrata para módulos de processamento.
    """
    
    @abstractmethod
    def run(self, context: Dict) -> Dict:
        """
        Método principal de execução do módulo.
        
        Args:
            context (Dict): Contexto completo contendo dados do agente
            
        Returns:
            Dict: Resultado do processamento do módulo
        """
        pass