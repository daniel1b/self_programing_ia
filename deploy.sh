#!/bin/bash
# deploy.sh
set -e

echo "Atualizando código com 'git pull'..."
git pull

echo "Instalando dependências..."
pip install -r requirements.txt

# Comando para reiniciar ou executar sua aplicação.
# Se estiver usando um serviço (como systemd), por exemplo:
# sudo systemctl restart meu_servico

# Ou se for executar a aplicação diretamente:
echo "Iniciando a aplicação..."
nohup python src/main.py > app.log 2>&1 &

echo "Deploy concluído!"
