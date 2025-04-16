# Documentação Técnica do Agente Conversacional Aurora

## 1. Visão Geral do Projeto

O projeto **Aurora** é um agente conversacional projetado para ser leve e eficiente, utilizando modelos de linguagem com poucos parâmetros em um pipeline modular que enriquece a análise para produzir respostas de alta qualidade. O sistema divide o processamento em pequenos prompts que vão agregando valor à resposta final, permitindo extrair o máximo de um modelo menor.

### 1.1 Objetivo Principal

O principal objetivo do agente Aurora é fornecer uma plataforma conversacional leve que utilize modelos de linguagem de menor escala enquanto mantém alta qualidade nas respostas. Isso é alcançado através de um pipeline estratégico de processamento que analisa e enriquece a entrada do usuário em fases, combinando análises racionais e emocionais para criar uma resposta mais completa e natural.

### 1.2 Características Principais

- **Modularidade**: Arquitetura baseada em módulos independentes com interfaces bem definidas
- **Pipeline de Processamento**: Fluxo de processamento em etapas para enriquecer a resposta final
- **Sistema de Memória Dual**: Combinação de memória imutável (configuração) e memória de longo prazo
- **Adaptabilidade**: Capacidade de alternar entre modos de processamento racional e emocional
- **Eficiência**: Projetado para funcionar com modelos de linguagem mais leves

## 2. Diagrama da Arquitetura

```
                    ┌───────────────────────────────────────────┐
                    │               Agent                       │
                    │  ┌─────────────────┐ ┌─────────────────┐  │
                    │  │  ImmutableMemory│ │ LongTermMemory  │  │
                    │  └─────────────────┘ └─────────────────┘  │
                    │  ┌─────────────────┐ ┌─────────────────┐  │
                    │  │     History     │ │    Pipeline     │  │
                    │  └─────────────────┘ └─────────────────┘  │
                    └───────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌───────────────────────────────────────────┐
                    │                Pipeline                   │
                    │                                           │
                    │  ┌─────────┐ ┌────────┐ ┌─────────────┐   │
                    │  │IntentA. │→│Rational│→│Emotional    │   │
                    │  └─────────┘ └────────┘ └─────────────┘   │
                    │       │          │            │           │
                    │       ▼          ▼            ▼           │
                    │  ┌─────────┐ ┌────────────────────────┐   │
                    │  │Sentiment│→│  ResponseConsolidator  │   │
                    │  └─────────┘ └────────────────────────┘   │
                    └───────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌───────────────────────────────────────────┐
                    │              ModeloLLM                    │
                    │                                           │
                    │  Integração com o modelo de linguagem     │
                    │  (Ollama)                                │
                    └───────────────────────────────────────────┘
```

## 3. Descrição dos Módulos

### 3.1 Core Package (`src.core`)

#### 3.1.1 Agent (`src.core.Agent`)

O módulo central que coordena todos os componentes do agente conversacional. Gerencia o fluxo de conversação, integrando o histórico, a memória e o pipeline de processamento.

**Responsabilidades:**
- Inicializar e manter todos os componentes do sistema
- Receber mensagens do usuário e processá-las
- Integrar diferentes fontes de contexto (imutável e de longo prazo)
- Orquestrar o pipeline de processamento
- Retornar a resposta final ao usuário

#### 3.1.2 History (`src.core.History`)

Gerencia o histórico de interações entre o usuário e o agente, permitindo o acesso ao contexto recente da conversa.

**Responsabilidades:**
- Armazenar interações passadas (usuário e agente)
- Fornecer métodos para adicionar novas interações
- Recuperar interações recentes para contexto
- Limpar o histórico quando necessário

#### 3.1.3 Pipeline (`src.core.Pipeline`)

Coordena o fluxo de processamento de cada mensagem através dos diferentes módulos de análise e geração de resposta.

**Responsabilidades:**
- Coletar as últimas interações do histórico
- Executar cada módulo na sequência definida
- Passar contexto e resultados entre módulos
- Consolidar as saídas dos diferentes módulos
- Fornecer a resposta final do pipeline

### 3.2 Memory Package (`src.memory`)

#### 3.2.1 ImmutableMemory (`src.memory.ImmutableMemory`)

Carrega e mantém a configuração estática do agente, incluindo personalidade e comportamentos.

**Responsabilidades:**
- Carregar configurações de personalidade e comportamento do arquivo YAML
- Fornecer acesso a essas configurações para os outros componentes
- Gerar um resumo da personalidade do agente para uso em prompts

#### 3.2.2 LongTermMemory (`src.memory.LongTermMemory`)

Gerencia informações persistentes aprendidas durante as interações, mantendo e atualizando o conhecimento do agente.

**Responsabilidades:**
- Carregar e salvar memória de longo prazo de/para um arquivo
- Atualizar a memória com novas informações
- Compactar a memória quando excede o limite de tokens
- Fornecer acesso à memória atual para outros componentes

### 3.3 LLM Package (`src.llm`)

#### 3.3.1 ModeloLLM (`src.llm.ModeloLLM`)

Interface para interagir com o modelo de linguagem generativa (Ollama).

**Responsabilidades:**
- Configurar e conectar ao modelo de linguagem
- Enviar prompts ao modelo e receber respostas
- Gerenciar parâmetros do modelo (temperatura, etc.)
- Tratamento de erros na comunicação com o modelo

### 3.4 Interfaces Package (`src.interfaces`)

#### 3.4.1 IModule (`src.interfaces.IModule`)

Define a interface padrão que todos os módulos do pipeline devem implementar.

**Responsabilidades:**
- Definir o contrato que os módulos devem seguir
- Garantir consistência entre os diferentes módulos do pipeline

### 3.5 Modules Package (`src.modules`)

#### 3.5.1 IntentAnalysis (`src.modules.IntentAnalysis`)

Analisa a intenção do usuário a partir da mensagem recebida.

**Responsabilidades:**
- Identificar o propósito da mensagem do usuário
- Detectar comandos ou solicitações específicas
- Classificar o tipo de interação

#### 3.5.2 RationalResponse (`src.modules.RationalResponse`)

Gera uma resposta baseada em lógica e fatos.

**Responsabilidades:**
- Processar a mensagem do usuário de forma objetiva
- Aplicar o prefixo racional definido na configuração
- Gerar uma resposta factual e lógica

#### 3.5.3 EmotionalResponse (`src.modules.EmotionalResponse`)

Gera uma resposta com componentes emocionais, considerando o contexto e a personalidade do agente.

**Responsabilidades:**
- Processar a mensagem com enfoque emocional
- Aplicar o prefixo emocional definido na configuração
- Gerar uma resposta que reflita a personalidade do agente

#### 3.5.4 SentimentEvaluation (`src.modules.SentimentEvaluation`)

Avalia o sentimento da interação atual para ajustar o tom da resposta.

**Responsabilidades:**
- Analisar o sentimento da mensagem do usuário
- Posicionar o sentimento na escala definida na configuração
- Atualizar o estado emocional do agente

#### 3.5.5 ResponseConsolidator (`src.modules.ResponseConsolidator`)

Unifica os resultados dos outros módulos para criar uma resposta final coerente.

**Responsabilidades:**
- Combinar as respostas racional e emocional
- Ajustar o tom baseado na avaliação de sentimento
- Formatar a resposta final de acordo com a personalidade do agente

### 3.6 Utils Package (`src.utils`)

#### 3.6.1 YAML Loader (`src.utils.yaml_loader`)

Utilitário para carregar e processar arquivos de configuração no formato YAML.

**Responsabilidades:**
- Abrir e ler arquivos YAML
- Converter o conteúdo do YAML em estruturas de dados Python
- Lidar com erros de leitura ou processamento

## 4. Fluxo Principal de Execução

1. **Inicialização do Agente**:
   - Carregamento do arquivo de configuração basic.yml
   - Inicialização da memória imutável com os dados de configuração
   - Criação/carregamento da memória de longo prazo
   - Inicialização do histórico de conversação
   - Configuração do ModeloLLM com o modelo de linguagem escolhido
   - Inicialização do pipeline e seus módulos

2. **Processamento de Mensagem**:
   - Usuário envia mensagem via `agente.send_message()`
   - A mensagem é armazenada no histórico
   - O agente coleta o contexto das memórias e do histórico recente

3. **Execução do Pipeline**:
   - **IntentAnalysis**: Determina a intenção do usuário
   - **RationalResponse**: Gera uma resposta baseada em lógica
   - **EmotionalResponse**: Gera uma resposta emocional
   - **SentimentEvaluation**: Avalia o sentimento da interação
   - **ResponseConsolidator**: Combina as respostas anteriores

4. **Geração de Resposta Final**:
   - O consolidador formata um prompt final com todos os resultados do pipeline
   - O prompt é enviado ao ModeloLLM para gerar a resposta final
   - A resposta é retornada ao usuário e armazenada no histórico

5. **Atualização da Memória**:
   - Informações relevantes são identificadas e adicionadas à memória de longo prazo
   - Se necessário, a memória é compactada para manter-se dentro do limite de tokens

## 5. Interfaces Importantes

### 5.1 Interface do Agente

```python
class Agent:
    def __init__(self, config_path: str, model_class: type):
        # Inicializa o agente com um caminho para configuração e uma classe de modelo
        pass
        
    def send_message(self, message: str) -> str:
        # Processa uma mensagem do usuário e retorna a resposta
        pass
    
    def get_context_summary(self) -> str:
        # Retorna um resumo do contexto atual para debugging
        pass
```

### 5.2 Interface do Módulo

```python
class IModule:
    def run(self, history: list[str], memory: dict) -> str:
        # Executa o processamento específico do módulo
        # e retorna o resultado
        raise NotImplementedError
```

### 5.3 Interface do Modelo LLM

```python
class ModeloLLM:
    def __init__(self, modelo: str = "default", temperatura: float = 0.7):
        # Inicializa o modelo com configurações específicas
        pass
        
    def enviar_prompt(self, prompt: str) -> str:
        # Envia um prompt para o modelo e retorna a resposta
        pass
    
    def alterar_modelo(self, novo_modelo: str) -> None:
        # Altera o modelo de linguagem a ser utilizado
        pass
    
    def alterar_temperatura(self, nova_temp: float) -> None:
        # Altera a temperatura do modelo
        pass
```

## 6. Dependências

### 6.1 Dependências Internas

- **Agent** → History, ImmutableMemory, LongTermMemory, Pipeline
- **Pipeline** → Módulos (IntentAnalysis, RationalResponse, etc.)
- **ImmutableMemory** → yaml_loader
- **LongTermMemory** → ModeloLLM (para compactação)
- **Todos os Módulos** → IModule (implementam esta interface)

### 6.2 Dependências Externas

- **PyYAML**: Para leitura e processamento de arquivos de configuração
- **Ollama**: Modelo de linguagem utilizado pelo ModeloLLM via API HTTP
- **Requests**: Para comunicação HTTP com o modelo Ollama
- **Typing** (stdlib): Para anotações de tipo
- **OS** (stdlib): Para manipulação de caminhos de arquivo
- **JSON** (stdlib): Para processamento de respostas da API

## 7. Exemplo de Uso

```python
from src.core.Agent import Agent
from src.llm.ModeloLLM import ModeloLLM

# Inicializa o agente
agente = Agent(config_path="config/basic.yml", model_class=ModeloLLM)

# Interage com o agente
resposta = agente.send_message("Olá, como você está hoje?")
print(resposta)

# Continua a conversa
resposta = agente.send_message("Pode me contar mais sobre suas capacidades?")
print(resposta)
```

## 8. Configuração do Agente

O arquivo `basic.yml` define a personalidade e comportamentos do agente:

```yaml
agent_name: Aurora
personality:
  traits:
    - curiosa
    - empática
    - lógica
  tone: gentil
  language: pt-BR

default_behavior:
  max_context_window: 5
  allow_memory_update: true
  fallback_response: "Desculpe, não consegui entender totalmente. Pode reformular?"
  processing_mode: analítico_emocional

system_prompts:
  rational_prefix: "Com base nos fatos disponíveis,"
  emotional_prefix: "Sinto que talvez..."
  sentiment_scale: ["muito triste", "triste", "neutro", "feliz", "muito feliz"]
```

Esses parâmetros influenciam diretamente como o agente processa e responde às mensagens do usuário.
