# src/core/ModeloLLM.py

import requests
import json
import logging
from transformers import AutoTokenizer


class ModeloLLM:
    """
    Classe para interagir com um modelo de linguagem generativa hospedado localmente ou remotamente.
    
    Esta classe permite enviar prompts para um modelo de linguagem (LLM), receber a resposta do modelo, 
    alterar o modelo ou ajustar parâmetros como a temperatura do modelo.
    """

    def __init__(self, url_base="http://localhost:11434/api/generate", modelo="gemma3:1b", temperatura=0.7):
        """
        Inicializa a instância do modelo LLM.
        
        Args:
            url_base (str): A URL base para a API do modelo. O padrão é "http://localhost:11434/api/generate".
            modelo (str): O nome do modelo a ser utilizado. O padrão é "gemma3:1b".
            temperatura (float): A temperatura do modelo para controle de criatividade. O padrão é 0.7.
        """
        self.url_base = url_base
        self.modelo = modelo
        self.temperatura = temperatura
        logging.basicConfig(level=logging.INFO)

    def contar_tokens_gemma(self, texto):
        tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b-it")  # ou "gemma-7b-it" se for o 7b
        tokens = tokenizer.encode(texto, add_special_tokens=False)
        return len(tokens)

    def enviar_prompt(self, prompt: str) -> str:
        """
        Envia um prompt para o modelo de linguagem e retorna a resposta gerada.
        
        Args:
            prompt (str): O texto de entrada a ser enviado ao modelo.
        
        Returns:
            str: A resposta gerada pelo modelo após o processamento do prompt.
        
        Este método envia o prompt ao modelo utilizando uma requisição HTTP POST. A resposta do modelo é recebida
        de forma contínua (streaming), e as partes da resposta são concatenadas e retornadas.
        Caso haja um erro na comunicação ou decodificação da resposta, um erro apropriado é registrado e uma mensagem
        de erro é retornada.
        """
        payload = {
            "model": self.modelo,
            "prompt": prompt,
            "stream": True,
            "temperature": self.temperatura
        }
        logging.info(f"="*200)
        logging.info(f"[LLM] Enviando prompt ({self.contar_tokens_gemma(prompt)} tokens) para o modelo:\n\n '{self.modelo}': {prompt}")

        try:
            resposta_texto = ""
            response = requests.post(self.url_base, json=payload, timeout=60, stream=True)
            response.raise_for_status()

            for linha in response.iter_lines():
                if linha:
                    try:
                        linha_str = linha.decode("utf-8") if isinstance(linha, bytes) else linha
                        dado_json = json.loads(linha_str)
                        resposta_texto += dado_json.get("response", "")
                    except json.JSONDecodeError as e:
                        logging.warning(f"[LLM] Erro ao decodificar JSON: {e}")
                        continue
            logging.info(f"-"*50)
            logging.info(f"[LLM] Resposta recebida ({self.contar_tokens_gemma(resposta_texto.strip())} tokens): {resposta_texto.strip()}")
            return resposta_texto.strip()

        except requests.RequestException as e:
            logging.error(f"[LLM] Erro na requisição ao modelo: {e}")
            return "Erro ao conectar ao modelo. Verifique se o servidor está rodando."

    def alterar_modelo(self, novo_modelo: str) -> None:
        """
        Altera o modelo de linguagem a ser utilizado.
        
        Args:
            novo_modelo (str): O nome do novo modelo a ser utilizado.
        
        Este método altera o modelo de linguagem configurado, permitindo a utilização de diferentes modelos de 
        linguagem ao longo da execução.
        """
        logging.info(f"[LLM] Alterando modelo para: {novo_modelo}")
        self.modelo = novo_modelo

    def alterar_temperatura(self, nova_temp: float) -> None:
        """
        Altera a temperatura do modelo de linguagem.
        
        Args:
            nova_temp (float): O novo valor de temperatura a ser utilizado no modelo.
        
        A temperatura controla o nível de aleatoriedade na geração de respostas. Um valor mais alto resulta em
        respostas mais criativas, enquanto um valor mais baixo tende a gerar respostas mais conservadoras.
        """
        logging.info(f"[LLM] Alterando temperatura para: {nova_temp}")
        self.temperatura = nova_temp
