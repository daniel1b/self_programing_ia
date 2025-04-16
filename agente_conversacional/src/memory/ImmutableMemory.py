# src/memory/ImmutableMemory.py

from src.utils.yaml_loader import load_yaml

class ImmutableMemory:
    """
    Classe que carrega e mantém a memória imutável de configuração do agente.

    Esta classe carrega os dados de configuração do agente a partir de um arquivo YAML,
    fornecendo métodos para acessar informações sobre a personalidade, comportamentos e 
    outros parâmetros do agente.
    """

    def __init__(self, config_path: str):
        """
        Inicializa a memória imutável carregando as configurações a partir de um arquivo YAML.

        Args:
            config_path (str): O caminho para o arquivo de configuração YAML que contém
                                as informações do agente, incluindo nome, personalidade e comportamento.
        """
        self._raw_data = load_yaml(config_path)
        self.agent_name = self._raw_data.get("agent_name", "Agente")
        self.personality = self._raw_data.get("personality", {})
        self.default_behavior = self._raw_data.get("default_behavior", {})
        self.system_prompts = self._raw_data.get("system_prompts", {})

    def get_summary(self) -> str:
        """
        Retorna um resumo textual da personalidade e comportamentos do agente.

        Este método gera uma descrição baseada nas informações carregadas da configuração do agente,
        incluindo os traços de personalidade, tom de comunicação, idioma e modo de processamento.

        Returns:
            str: Um resumo textual com a personalidade e comportamentos do agente.
        """
        traits = ', '.join(self.personality.get("traits", []))
        tone = self.personality.get("tone", "neutro")
        lang = self.personality.get("language", "pt-BR")
        return (
            #f"{self.agent_name} é um agente com traços de personalidade {traits}, "
            #f"com tom {tone}, operando em {lang}. "
            #f"Modo padrão: {self.default_behavior.get('processing_mode', 'desconhecido')}."
        )

    def get_config(self) -> dict:
        """
        Retorna todo o dicionário de dados da memória imutável.

        Este método fornece acesso ao conteúdo completo da configuração carregada, 
        permitindo o acesso direto a todos os dados, incluindo nome do agente, personalidade, 
        comportamentos padrão e prompts do sistema.

        Returns:
            dict: O dicionário contendo os dados carregados do arquivo de configuração YAML.
        """
        return self._raw_data
