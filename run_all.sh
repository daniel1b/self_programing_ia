#!/bin/bash
# run_all.sh
set -e

echo "Executando testes..."
./run_tests.sh

echo "Testes concluídos com sucesso. Iniciando deploy..."
./deploy.sh

echo "Pipeline local concluída com sucesso!"
