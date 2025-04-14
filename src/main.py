import telebot
import requests
import logging
import json
import os
from dotenv import load_dotenv

# Configurações
load_dotenv()
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OLLAMA_URL = os.getenv("OLLAMA_URL")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Armazena o estado de cada usuário
user_states = {}

# === Estrutura inicial do estado de cada usuário ===
def criar_estado_usuario():
    return {
        "memoria_recente": [],            # [(usuario, bot), ...]
        "memoria_longo_prazo": "",        # resumo da conversa
        "pensamento_racional": "",        # analítico
        "pensamento_emocional": "",       # subjetivo
        "sentimento": "",                 # emocional atual
    }


def enviar_prompt_para_modelo(prompt):
    #logging.info(f"Enviando o seguinte prompt para o modelo: {prompt}")
    
    payload = {
        "model": "gemma3:1b",  # ou o modelo que você estiver usando
        "prompt": prompt
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60, stream=True)
        response.raise_for_status()

        resposta_texto = ""
        for linha in response.iter_lines():
            if linha:
                try:
                    linha_str = linha.decode("utf-8") if isinstance(linha, bytes) else linha
                    dado_json = json.loads(linha_str)
                    resposta_texto += dado_json.get("response", "")
                except json.JSONDecodeError as e:
                    logging.warning(f"Erro ao decodificar linha JSON: {e}")
                    continue
        logging.info(f"Resposta do modelo: {resposta_texto}")
        return resposta_texto
    except requests.RequestException as e:
        logging.error(f"Erro na requisição ao Ollama: {e}")
        return "Erro ao conectar ao Ollama. Verifique se o servidor está rodando."

def handle_user_message(chat_id, mensagem_usuario):
    if chat_id not in user_states:
        user_states[chat_id] = criar_estado_usuario()

    estado = user_states[chat_id]

    print("inicando analise...")

    # 1. Atualiza memória recente com a nova mensagem do usuário
    atualizar_memoria_recente(estado, mensagem_usuario)
    #logging.info(f"Memória recente atualizada: {estado['memoria_recente']}")

    # 2. Gera o pensamento racional com base na memória recente
    prompt_racional = gerar_prompt_pensamento_racional(estado)
    #logging.info(f"Prompt do Pensamento Racional: {prompt_racional}")
    estado["pensamento_racional"] = enviar_prompt_para_modelo(prompt_racional)

    # 3. Gera o pensamento emocional com base na memória recente e racional
    prompt_emocional = gerar_prompt_pensamento_emocional(estado)
    #logging.info(f"Prompt do Pensamento Emocional: {prompt_emocional}")
    estado["pensamento_emocional"] = enviar_prompt_para_modelo(prompt_emocional)

    # 4. Gera o sentimento atual da conversa
    prompt_sentimento = gerar_prompt_sentimento(estado)
    #logging.info(f"Prompt do Sentimento: {prompt_sentimento}")
    estado["sentimento"] = enviar_prompt_para_modelo(prompt_sentimento)

    # 5. Gera a resposta final para o usuário
    prompt_resposta = gerar_prompt_resposta_usuario(estado)
    #logging.info(f"Prompt da Resposta Final: {prompt_resposta}")
    resposta_bot = enviar_prompt_para_modelo(prompt_resposta)

    # 6. Atualiza memória recente com a resposta do bot
    atualizar_resposta_bot(estado, resposta_bot)
    logging.info(f"Memória recente após resposta do bot: {estado['memoria_recente']}")

    # 7. Atualiza memória de longo prazo, resumindo se necessário
    nova_memoria_longa = estado["memoria_longo_prazo"] + f" | {mensagem_usuario} -> {resposta_bot}"
    estado["memoria_longo_prazo"] = resumir_memoria_longa(nova_memoria_longa)
    logging.info(f"Memória de longo prazo atualizada: {estado['memoria_longo_prazo']}")

    return resposta_bot



# === Manipulação da memória recente ===
def atualizar_memoria_recente(estado, mensagem_usuario):
    estado["memoria_recente"].append([mensagem_usuario, None])
    if len(estado["memoria_recente"]) > 2:
        estado["memoria_recente"].pop(0)

def atualizar_resposta_bot(estado, resposta_bot):
    if estado["memoria_recente"]:
        ultima = estado["memoria_recente"][-1]
        estado["memoria_recente"][-1] = (ultima[0], resposta_bot)

# === Funções de pensamento e sentimento ===
def gerar_prompt_pensamento_racional(estado):
    memoria_recente = estado["memoria_recente"]
    print(f"mem_rec:{memoria_recente}")
    interacoes_formatadas = "\n".join(
        [f"Usuário: {u}\nAssistente: {b}" if b else f"Usuário: {u}" for u, b in memoria_recente]
    )

    return f"""
Você é um agente analítico. Seu trabalho é observar interações recentes entre um usuário e um assistente e identificar de forma clara e objetiva qual é a intenção principal do usuário.

Interações recentes:
{interacoes_formatadas}

Tarefa:
- Analise objetivamente o que o usuário disse.
- Seja direto e preciso, sem devaneios ou suposições excessivas.

Responda com um texto curto e claro descrevendo a intenção do usuário.
"""

def gerar_prompt_pensamento_emocional(estado):
    memoria_recente = estado['memoria_recente']
    pensamento_racional = estado['pensamento_racional']

    interacoes_formatadas = "\n".join(
        [f"Usuário: {u}\nAssistente: {b}" if b else f"Usuário: {u}" for u, b in memoria_recente]
    )


    return f"""
Você é um sistema sensível a emoções. Seu trabalho é analisar a conversa entre o usuário e o assistente, considerando também o que o usuário deseja (pensamento racional), e inferir o estado emocional predominante da interação.

Interações recentes:
{interacoes_formatadas}

Intenção racional do usuário:
{pensamento_racional}

Tarefa:
- Avalie o tom emocional da conversa (ex: frustração, alegria, ansiedade, dúvida, etc.).
- Descreva brevemente o estado emocional do usuário.

Seja sucinto, emocional e intuitivo.
"""


def gerar_prompt_sentimento(estado):
    pensamento_emocional = estado['pensamento_emocional']
    pensamento_racional = estado['pensamento_racional']
    return f"""
Você é um agente reflexivo. Com base na análise racional e emocional de uma conversa com o usuário, você deve expressar qual é o sentimento predominante no momento.

Pensamento racional:
{pensamento_racional}

Pensamento emocional:
{pensamento_emocional}

Tarefa:
- Descreva o sentimento do momento com uma ou duas frases.
- Seja introspectivo, mas objetivo.

Exemplo: "Sinto que o usuário está inseguro, mas disposto a colaborar."
"""


def gerar_prompt_resposta_usuario(estado):
    memoria_recente= estado['memoria_recente']
    pensamento_racional= estado['pensamento_racional']
    pensamento_emocional= estado['pensamento_emocional']
    sentimento= estado['sentimento']
    ultima_mensagem = memoria_recente[-1][0] if memoria_recente else ""

    return f"""
Você é um agente conversacional simpático, inteligente e emocionalmente atento.

Última mensagem do usuário:
"{ultima_mensagem}"

Contexto recente:
- Pensamento racional: {pensamento_racional}
- Pensamento emocional: {pensamento_emocional}
- Sentimento atual: {sentimento}

Tarefa:
- Responda à última mensagem do usuário de forma útil, e clara.
- Responda com o tom levando em conta o sentimento atual.
- O usuario não precisa saber sobre o sentimento, a resposta deve ser objetiva, somente o que ele perguntou.

Responda diretamente ao usuário.
"""


def gerar_prompt_resumo_longo_prazo(memoria_antiga):
    return f"""
Você é responsável por resumir a memória de longo prazo de um agente conversacional.

Texto original:
"{memoria_antiga}"

Tarefa:
- Resuma o conteúdo de forma clara e objetiva.
- Mantenha no máximo 300 caracteres.
- Elimine detalhes repetitivos ou irrelevantes.

Retorne apenas o resumo.
"""

def resumir_memoria_longa(texto_longo):
    if len(texto_longo) <= 300:
        return texto_longo

    prompt = f"""
Você é um assistente responsável por compactar memórias longas de um agente conversacional.

Texto original:
\"\"\"{texto_longo}\"\"\"

Tarefa:
- Resuma o conteúdo mantendo os principais acontecimentos ou sentimentos.
- Use no máximo 300 caracteres.
- Elimine repetições e mantenha a essência da conversa.

Retorne apenas o resumo, sem explicações ou comentários extras.
"""



    try:
        resultado = enviar_prompt_para_modelo(prompt)

        if len(resultado) > 300:
            resultado = resultado[:297] + "..."
        return resultado
    except Exception as e:
        logging.error(f"Erro ao resumir memória de longo prazo: {e}")
        return "[Erro ao resumir memória longa]"


# === Telegram Bot ===
@bot.message_handler(commands=["reset"])
def resetar_estado(message):
    user_states.pop(message.chat.id, None)
    bot.reply_to(message, "✅ Estado do agente resetado com sucesso.")

@bot.message_handler(func=lambda msg: True)
def responder_ao_usuario(message):
    logging.info(f"Mensagem recebida de {message.chat.id}: {message.text}")
    aguardando = bot.reply_to(message, "🤔 Pensando na resposta...")
    resposta = handle_user_message(message.chat.id, message.text)
    bot.edit_message_text(resposta, message.chat.id, aguardando.message_id)

# === Inicialização ===
if __name__ == "__main__":
    logging.info("🤖 Agente conversacional iniciado.")
    bot.polling()
