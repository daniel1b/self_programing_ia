import telebot
import requests
import logging
import json
import re
import os

# Configuração do logging para depuração
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carrega as variáveis do arquivo .env
load_dotenv()


TOKEN = os.getenv('GITHUB_TOKEN')
OLLAMA_URL = os.getenv('OLLAMA_URL')

bot = telebot.TeleBot(TOKEN)

# Agora, conversation_context armazena um dicionário com:
# - 'context': resumo geral da conversa
# - 'user_messages': lista das mensagens do usuário
# - 'model_responses': lista das respostas do modelo
conversation_context = {}

def build_prompt(message, history):
    # Obtém os componentes do histórico
    context = history.get('context', "This was the user's first message.")
    user_msgs = history.get('user_messages', [])
    model_responses = history.get('model_responses', [])
    
    # Filtra as duas últimas mensagens e respostas (em ordem cronológica)
    recent_user_msgs = user_msgs[-5:] if len(user_msgs) >= 5 else user_msgs
    recent_model_responses = model_responses[-5:] if len(model_responses) >= 5 else model_responses

    # Constrói uma representação intercalada da conversa,
    # assumindo que as mensagens estão emparelhadas (User, Assistant)
    conversation_lines = []

    for u_msg, a_msg in zip(recent_user_msgs, recent_model_responses):            
        conversation_lines.append(f"Assistant: {a_msg}")
        conversation_lines.append(f"User: {u_msg}")

    history_str = "\n".join(conversation_lines)

    prompt = f"""
You are a friendly AI chat.

Task:
- Read the previous conversation summary.
- Review the recent conversation history.
- Understand the new user message.
- Reply clearly and naturally.
- Provide a short, third-person summary of what just happened to update the context.

Instructions:
- Respond strictly in JSON with two keys:
    "response": your helpfull answer,
    "last_message_context": a short, third-person summary of what the user is talking.

--- 
Previous context:
{context}

Recent conversation history:
{history_str}

New User message:
"{message}"

Reply with JSON only:
{{
  "response": "...",
  "last_message_context": "..."
}}
"""
    return prompt

def extract_json_block(texto):
    # Tenta encontrar blocos de código entre ```json ... ``` ou ``` ... ```
    padrao_blocos = re.compile(r'```(?:json)?\s*(\{.*?\})\s*```', re.DOTALL)
    matches = padrao_blocos.findall(texto)
    for m in matches:
        try:
            json.loads(m)
            return m
        except:
            continue

    # Caso não tenha blocos markdown, tenta achar JSON diretamente no texto
    padrao_json_simples = re.compile(r'(\{.*?\})', re.DOTALL)
    matches_simples = padrao_json_simples.findall(texto)
    for m in matches_simples:
        try:
            json.loads(m)
            return m
        except:
            continue

    return None

def parse_model_response(texto):
    # Tenta extrair o JSON
    json_str = extract_json_block(texto)
    if json_str:
        try:
            return json.loads(json_str)
        except Exception as e:
            logging.error(f"Erro ao decodificar JSON extraído: {e}")
    else:
        logging.error("Bloco JSON não encontrado na resposta.")
    return None

# ... (todas as imports e configs anteriores)
def chat_ollama(entrada_para_modelo, chat_id):
    global conversation_context

    logging.info(f"Mensagem traduzida para modelo: {entrada_para_modelo}")

    if chat_id not in conversation_context:
        conversation_context[chat_id] = {
            'context': "This was the user's first message.",
            'user_messages': [],
            'model_responses': []
        }
    
    history = conversation_context[chat_id]
    history['user_messages'].append(entrada_para_modelo)

    prompt = build_prompt(entrada_para_modelo, history)

    payload = {
        "model": "deepseek-r1:1.5b",
        "prompt": prompt
    }

    logging.info(f"Enviando para Ollama: {prompt}")

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

        data = parse_model_response(resposta_texto)
        if data is not None:
            saida_para_usuario = data.get("response", None)
            if saida_para_usuario is None:
                logging.error("Campo 'response' não encontrado.")
                return "Erro: resposta malformada. Por favor, tente novamente."

            logging.info(f"Resposta para usuário: {saida_para_usuario}")

            novo_contexto_raw = data.get("last_message_context", "")
            history['context'] = novo_contexto_raw
            history['model_responses'].append(saida_para_usuario)

            history['user_messages'] = history['user_messages'][-2:]
            history['model_responses'] = history['model_responses'][-2:]

            return saida_para_usuario
        else:
            return "Não consegui entender a resposta do modelo. Pode tentar reformular?"
    except requests.RequestException as e:
        logging.error(f"Erro na requisição ao Ollama: {e}")
        return "Erro ao conectar ao Ollama. Verifique se o servidor está rodando."



@bot.message_handler(commands=['reset'])
def resetar_contexto(message):
    conversation_context.pop(message.chat.id, None)
    bot.reply_to(message, "✅ Contexto da conversa foi reiniciado com sucesso.")

@bot.message_handler(func=lambda message: True)
def responder(message):
    logging.info(f"Mensagem recebida do Telegram: {message.text}")
    aguardando_msg = bot.reply_to(message, "Aguarde, estou processando sua resposta...")
    resposta = chat_ollama(message.text, message.chat.id)
    bot.edit_message_text(resposta, chat_id=message.chat.id, message_id=aguardando_msg.message_id)
    logging.info(f"Resposta enviada para o Telegram: {resposta}")

logging.info("🤖 Bot está rodando...")
bot.polling()