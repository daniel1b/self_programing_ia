# main_bot.py
import telebot
import logging
import os
from dotenv import load_dotenv

# Importa os componentes do agente
from src.core.Agent import Agent
from src.memory.ImmutableMemory import ImmutableMemory
from src.memory.LongTermMemory import LongTermMemory
from src.core.History import History
from src.llm.ModeloLLM import ModeloLLM  # Atualizado para utilizar o modelo da classe

# Configurações iniciais
load_dotenv()
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OLLAMA_URL = os.getenv("OLLAMA_URL")  # URL para o modelo de linguagem

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Inicializa as dependências do agente:
immutable_memory = ImmutableMemory("./config/basic.yml")
llm = ModeloLLM(url_base=OLLAMA_URL, modelo="gemma3:1b", temperatura=0.7)
history = History()
long_term_memory = LongTermMemory(file_path="long_term_memory.txt", llm=llm, max_tokens=2000)

# Obtém a configuração completa a partir da memória imutável
config = immutable_memory.get_config()

# Cria a instância do agente com as dependências
agente = Agent(
    config=config,
    llm=llm,
    history=history,
    immutable_memory=immutable_memory,
    long_term_memory=long_term_memory
)

# Handler para reset do agente via comando Telegram
@bot.message_handler(commands=["reset"])
def resetar_estado(message):
    agente.reset()  # Reinicia o agente (limpa histórico, memória de longo prazo e estado interno)
    bot.reply_to(message, "✅ Estado do agente reiniciado com sucesso.")

# Handler para processar todas as mensagens de texto
@bot.message_handler(func=lambda m: True)
def responder_ao_usuario(message):
    logging.info(f"Mensagem recebida de {message.chat.id}: {message.text}")

    # Informa ao usuário que o agente está processando a mensagem
    aguardar_msg = bot.reply_to(message, "🤔 Aguarde enquanto analiso sua mensagem...")

    # Processa a mensagem com o agente, que utiliza o método receive para integrar o fluxo completo de análise
    resposta = agente.receive(message.text)

    # Envia a resposta final para o usuário
    bot.edit_message_text(resposta, message.chat.id, aguardar_msg.message_id)
    logging.info(f"Resposta enviada para {message.chat.id}: {resposta}")

# Inicializa o bot
if __name__ == "__main__":
    logging.info("🤖 Agente conversacional iniciado no Telegram.")
    bot.polling()
