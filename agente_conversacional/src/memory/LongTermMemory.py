import os
from src.llm.ModeloLLM import ModeloLLM

class LongTermMemory:
    """
    Classe para gerenciar a memória de longo prazo de um agente, armazenando e atualizando informações 
    ao longo do tempo, mantendo o histórico de interações e dados relevantes.

    Essa classe carrega e mantém a memória de longo prazo de um agente, armazenando as informações em um 
    arquivo, compactando a memória quando necessário e utilizando um modelo de linguagem para resumir e 
    incorporar novas informações.
    """

    def __init__(self, file_path: str, llm: ModeloLLM, max_tokens: int = 2000):
        """
        Inicializa a memória de longo prazo com um caminho de arquivo e uma instância do modelo de linguagem.

        Args:
            file_path (str): O caminho do arquivo onde a memória será armazenada.
            llm (ModeloLLM): A instância do modelo de linguagem a ser usado para compactar a memória.
            max_tokens (int): Número máximo de tokens que a memória pode conter antes de ser compactada.
                              O padrão é 2000 tokens.
        """
        self.file_path = file_path
        self.llm = llm
        self.max_tokens = max_tokens
        self.memory = self.load_memory()

    def load_memory(self) -> str:
        """
        Carrega a memória de longo prazo a partir de um arquivo.

        Verifica se o arquivo de memória existe; se existir, o conteúdo é carregado.
        Caso contrário, a memória é inicializada como uma string vazia.

        Returns:
            str: O conteúdo da memória carregado a partir do arquivo.
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def get_memory(self) -> str:
        """
        Retorna o conteúdo atual da memória, sem espaços em branco extras.

        Returns:
            str: A memória atual do agente.
        """
        return self.memory.strip()

    def update_memory(self, new_info: str):
        """
        Atualiza a memória com novas informações e, se necessário, compacta a memória.

        O método adiciona a nova informação ao final da memória e, se a quantidade de tokens ultrapassar
        o limite configurado, chama a função de compactação para reduzir o tamanho da memória.
        Em seguida, salva a memória atualizada no arquivo.

        Args:
            new_info (str): Nova informação a ser adicionada à memória.
        """
        self.memory += f"\n{new_info}"
        if len(self.memory.split()) > self.max_tokens:
            self._compact_memory()
        self.save_memory()

    def _compact_memory(self, debug: bool = False):
        """
        Compacta a memória para manter o conteúdo dentro do limite de tokens.

        Gera um resumo da memória existente utilizando o modelo LLM. Em caso de erro,
        preserva a memória atual e registra uma mensagem de aviso.

        Args:
            debug (bool): Se True, imprime o prompt enviado ao LLM para depuração.
        """
        prompt = (
            "Resumo e incorporação de informações:\n\n"
            "Texto existente da memória:\n"
            f"{self.memory}\n\n"
            "Resumo isso em um texto mais curto, mantendo os pontos principais de forma compreensível e adicione ao final a nova informação já integrada."
        )
        if debug:
            print("[DEBUG] Prompt enviado para o LLM:\n", prompt)
        try:
            resumo = self.llm.enviar_prompt(prompt)
            if resumo and resumo.strip():
                self.memory = resumo.strip()
            else:
                print("[WARN] Resumo vazio recebido do LLM. Memória não foi modificada.")
        except Exception as e:
            print(f"[ERRO] Falha ao compactar memória: {e}. Memória antiga preservada.")

    def save_memory(self):
        """
        Salva a memória no arquivo.

        Grava o conteúdo atualizado da memória no arquivo configurado, garantindo que as
        alterações sejam persistidas.
        """
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(self.memory.strip())
