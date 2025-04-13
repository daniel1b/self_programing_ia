#!/bin/bash
# run_tests.sh
set -e  # encerra se ocorrer qualquer erro

echo "Instalando dependências..."
pip install -r requirements.txt

echo "Rodando testes unitários..."
pytest -m unit

echo "Rodando testes de integração..."
pytest -m integration

echo "Todos os testes passaram com sucesso!"