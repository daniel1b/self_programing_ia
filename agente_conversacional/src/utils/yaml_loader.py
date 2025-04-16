# src/utils/yaml_loader.py

import yaml

def load_yaml(filepath: str) -> dict:
    """
    Carrega o conteúdo de um arquivo YAML e retorna como um dicionário.

    Este método abre um arquivo YAML especificado pelo caminho do arquivo e converte 
    seu conteúdo em um dicionário Python usando a função `yaml.safe_load`.

    Args:
        filepath (str): O caminho para o arquivo YAML a ser carregado.

    Returns:
        dict: O conteúdo do arquivo YAML convertido para um dicionário.
    
    Raises:
        FileNotFoundError: Se o arquivo especificado não for encontrado.
        yaml.YAMLError: Se ocorrer um erro ao tentar carregar o conteúdo do arquivo YAML.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)
