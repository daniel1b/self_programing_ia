import os
import sys
from pathlib import Path
from src.modules.CognitionProcess import CognitivePipeline
from src.llm.ModeloLLM import ModeloLLM
from transformers import AutoTokenizer

def contar_tokens_gemma(texto):
    tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b-it")  # ou "gemma-7b-it" se for o 7b
    tokens = tokenizer.encode(texto, add_special_tokens=False)
    return len(tokens)


def executar_exemplo():
    # Definir o caminho para o arquivo YAML
    yaml_path = Path("./config/cogn1.yml")
    
    # Verificar se o arquivo existe
    if not os.path.exists(yaml_path):
        print(f"Erro: Arquivo YAML não encontrado em: {yaml_path}")
        return
    
    # Definir a entrada do usuário
    path = Path("D:/Projects/self_programing_ia/agente_conversacional/test/historia.txt")
    if not os.path.exists(path):
        print(f"Erro: Arquivo de entrada não encontrado em: {path}")
        return
    with open(path, 'r', encoding='utf-8') as f:
        text_input = f.read().strip()
    if not text_input:
        print("Erro: Arquivo de entrada está vazio.")
        return


    try:
        # Criar instância do ModeloLLM
        modelo_llm = ModeloLLM(
            url_base="http://localhost:11434/api/generate",
            modelo="gemma3:1b",
            temperatura=0.7
        )
        
        print(f"Carregando pipeline do arquivo: {yaml_path}")

       
        # Inicializar e executar o pipeline
        pipeline = CognitivePipeline(yaml_path, modelo_llm)

        input_dict = {'texto': text_input, 'acao': 'resumir o texto'}
        resultado = pipeline.execute(input_dict)
        
        print("\n=== TESTE DO PIPELINE COGNITIVO ===")
        print(f"Entrada do usuário: {input_dict}")  # Exibe os primeiros 50 caracteres da entrada
        print(f"\nResultado Final: {resultado}")
        

    
    except Exception as e:
        print(f"Erro na execução do pipeline: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    executar_exemplo()
