# src/core/History.py

from typing import List

class History:
    """
    Classe que gerencia o histórico de interações entre o usuário e o agente.
    
    O histórico armazena entradas de interações, onde cada interação consiste 
    no input do usuário e na resposta do agente. A classe oferece métodos para 
    adicionar novas interações, recuperar interações anteriores e limpar o histórico.
    """

    def __init__(self) -> None:
        """
        Inicializa o objeto History com um histórico vazio.

        Este método é chamado automaticamente quando uma instância da classe 
        é criada. O histórico começa vazio e pode ser atualizado com interações
        através do método add_interaction.
        """
        self._interactions: List[str] = []

    def add_interaction(self, user_input: str, agent_response: str) -> None:
        """
        Adiciona uma nova interação ao histórico.
        
        Args:
            user_input (str): A mensagem enviada pelo usuário.
            agent_response (str): A resposta gerada pelo agente.

        O método cria uma entrada formatada com o input do usuário e a resposta
        do agente, que é então adicionada à lista de interações armazenada.
        """
        entry = f"Usuário: {user_input.strip()}\nAgente: {agent_response.strip()}"
        self._interactions.append(entry)

    def get_last_interactions(self, n: int = 5) -> List[str]:
        """
        Retorna as últimas n interações do histórico.
        
        Args:
            n (int): O número de interações a serem retornadas. O padrão é 5.

        Returns:
            List[str]: Uma lista contendo as últimas n interações no formato 
            de strings.

        Se o número de interações for menor que n, todas as interações existentes
        serão retornadas.
        """
        return self._interactions[-n:]

    def get_all(self) -> List[str]:
        """
        Retorna todo o histórico de interações.
        
        Returns:
            List[str]: Uma lista contendo todas as interações armazenadas no histórico.
        """
        return self._interactions.copy()

    def clear(self) -> None:
        """
        Limpa todo o histórico de interações.
        
        Este método é útil para reiniciar o histórico, especialmente em cenários 
        de teste ou quando se deseja limpar o estado do agente.

        Não retorna nenhum valor.
        """
        self._interactions.clear()
