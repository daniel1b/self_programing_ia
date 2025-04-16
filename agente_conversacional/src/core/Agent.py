# src/core/Agent.py
import time
import json
from typing import Optional

class Agent:
    """
    Classe Agent para gerenciar a interação do agente conversacional.

    Responsável por orquestrar o fluxo de mensagens, integração com memória,
    análise de sentimento e geração da resposta final.
    """

    def __init__(self, config: dict, llm, history, immutable_memory, long_term_memory):
        """
        Inicializa uma instância do Agent.

        Args:
            config (dict): Configuração do agente, incluindo parâmetros e comportamentos.
            llm (ModeloLLM): Instância do modelo de linguagem para gerar respostas.
            history (History): Instância para gerenciamento do histórico de interações.
            immutable_memory (ImmutableMemory): Instância contendo a configuração imutável do agente.
            long_term_memory (LongTermMemory): Instância para gerenciamento da memória de longo prazo.
        """
        self.config = config
        self.llm = llm
        self.history = history
        self.immutable_memory = immutable_memory
        self.long_term_memory = long_term_memory
        self.sentiment: Optional[str] = None
        self.state = {}
        self.start_time = time.time()

    def analyze_and_update_sentiment(self):
        """
        Analisa o sentimento com base nas interações recentes e atualiza o estado do agente.

        Este método coleta as últimas interações do histórico, aplica a análise de sentimento 
        (atualmente exemplificada como um valor fixo) e atualiza o atributo interno 'sentiment'.
        """
        recent_interactions = self.history.get_last_interactions()
        # Aqui você integraria uma lógica avançada para análise de sentimento com base nas interações.
        self.sentiment = "neutro"  # Exemplo de valor fixo
        print("Sentimento atualizado para:", self.sentiment)

    def analyze_sentiment(self, text: str) -> str:
        """
        Analisa o sentimento de um texto específico.

        Args:
            text (str): Texto a ser analisado.

        Returns:
            str: Sentimento identificado (por exemplo, "feliz", "triste", "neutro").
        """
        # Implementação placeholder; na prática, uma função ou modelo pode ser invocado.
        return "neutro"

    def create_prompt(self, message: str) -> str:
        """
        Cria um prompt para o modelo LLM com base no contexto atual e na mensagem do usuário.

        Args:
            message (str): Mensagem enviada pelo usuário.

        Returns:
            str: Prompt formatado para envio ao modelo de linguagem.
        """
        context_summary = self.get_context_summary()
        prompt = (
            f"Contexto:\n{context_summary}\n\n"
            f"Mensagem do usuário: {message}\n"
            "Resposta:"
        )
        return prompt

    def get_context_summary(self) -> str:
        """
        Gera um resumo do contexto atual para o modelo LLM.

        Esse método reúne informações da configuração imutável, do histórico recente e da memória de longo prazo
        para formar um resumo que auxilia a geração de resposta.

        Returns:
            str: Resumo do contexto.
        """
        history_summary = "\n".join(self.history.get_last_interactions())
        immutable_summary = self.immutable_memory.get_summary()
        long_term = self.long_term_memory.get_memory()
        context = (
            f"{immutable_summary}\n"
            f"Histórico de Interações:\n{history_summary}\n\n"
            f"Memória de Longo Prazo:\n{long_term}"
        )
        return context

    def get_session_duration(self) -> float:
        """
        Retorna a duração da sessão atual em segundos.

        Returns:
            float: Número de segundos desde o início da sessão.
        """
        return time.time() - self.start_time
    def receive(self, message: str) -> str:
        """
        Processa uma mensagem recebida e retorna a resposta gerada pelo agente.

        Esse método integra os seguintes passos:
        1. Atualiza a análise de sentimento com base no histórico.
        2. Cria um prompt-base usando o contexto atual e a mensagem do usuário.
        3. Para cada system prompt configurado, gera um prompt específico (com instruções) e coleta a resposta do LLM.
        4. Monta um prompt final que reúne a solicitação do usuário, as respostas dos system prompts e uma instrução final 
        para elaborar uma resposta final integrada.
        5. Envia o prompt final ao LLM, atualiza o histórico e a memória de longo prazo.
        6. Solicita um resumo sucinto da resposta final para tornar a interação mais direta.

        Args:
            message (str): Mensagem enviada pelo usuário.

        Returns:
            str: Resposta final e resumida do agente.
        """
        # 1. Atualiza a análise de sentimento.
        self.analyze_and_update_sentiment()

        # 2. Cria o prompt-base com o contexto (histórico, configuração imutável, memória de longo prazo, etc.)
        base_prompt = self.create_prompt(message)

        # 3. Gera respostas intermediárias com base nos system prompts
        system_prompts = self.immutable_memory.system_prompts
        respostas_system = {}
        for key, instructions in system_prompts.items():
            prompt_especifico = f"{base_prompt}\n{instructions}\nUsuário: {message}"
            resposta = self.llm.enviar_prompt(prompt_especifico)
            respostas_system[key] = resposta

        # 4. Monta o prompt final para elaborar a resposta integrada
        prompt_final = f"Solicitação do usuário: {message}\n\nRespostas anteriores:\n"
        for key, resp in respostas_system.items():
            prompt_final += f"{key}: {resp}\n"
        prompt_final += (
            "\nCom base nas respostas anteriores e na solicitação do usuário, "
            "elabore uma resposta final clara e coesa."
        )

        resposta_final = self.llm.enviar_prompt(prompt_final)

        # 5. Atualiza histórico e memória
        self.history.add_interaction(message, resposta_final)
        self.update_long_term_memory(message, resposta_final)

        # 6. Solicita um resumo sucinto da resposta final
        prompt_resumo = (
            f"Resumo final da resposta:\n{resposta_final}\n\n"
            "Agora, reescreva isso de forma mais sucinta e direta, mantendo o significado completo. "
            "Evite repetições e mantenha o tom adequado à personalidade do agente."
        )
        resposta_sucinta = self.llm.enviar_prompt(prompt_resumo)

        return resposta_sucinta


    def reset(self):
        """
        Reinicia o estado do agente.

        Este método limpa o histórico, reseta a memória de longo prazo, e reinicializa
        os atributos internos (como o sentimento e a duração da sessão).
        """
        self.history.clear()
        self.long_term_memory.memory = ""
        self.long_term_memory.save_memory()
        self.sentiment = None
        self.state = {}
        self.start_time = time.time()
        print("Estado do agente reiniciado.")

    def save_state(self) -> bool:
        """
        Salva o estado atual do agente em um arquivo.

        Utilizando um formato JSON simples, este método persistirá informações como
        o sentimento atual, o estado interno e a duração da sessão.

        Returns:
            bool: True se o salvamento for bem-sucedido, False caso contrário.
        """
        try:
            state_data = {
                "sentiment": self.sentiment,
                "state": self.state,
                "session_duration": self.get_session_duration()
            }
            with open("agent_state.json", "w", encoding="utf-8") as f:
                json.dump(state_data, f)
            return True
        except Exception as e:
            print(f"Erro ao salvar estado: {e}")
            return False

    def set_sentiment(self, sentiment: str):
        """
        Define o sentimento atual do agente.

        Args:
            sentiment (str): Novo sentimento a ser atribuído.
        """
        self.sentiment = sentiment
        print("Sentimento definido como:", self.sentiment)

    def update_long_term_memory(self, message: str, response: str):
        """
        Atualiza a memória de longo prazo com a nova interação, se considerada significativa.

        A interação é formatada e adicionada à memória; caso o número de tokens ultrapasse o limite definido,
        a memória é compactada.

        Args:
            message (str): Mensagem do usuário.
            response (str): Resposta gerada pelo agente.
        """
        interaction_summary = f"Usuário: {message}\nAgente: {response}"
        self.long_term_memory.update_memory(interaction_summary)
        print("Memória de longo prazo atualizada.")
