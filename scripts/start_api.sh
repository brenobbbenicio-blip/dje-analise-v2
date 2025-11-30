#!/bin/bash
# Script para iniciar a API

set -e

echo "Iniciando API DJE Análise v2..."

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Iniciar API
python -m uvicorn src.api.main:app \
    --host ${API_HOST:-0.0.0.0} \
    --port ${API_PORT:-8000} \
    --reload
