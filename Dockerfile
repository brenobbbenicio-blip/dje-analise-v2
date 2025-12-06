# Multi-stage build para otimizar tamanho da imagem
FROM python:3.11-slim as builder

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --user -r requirements.txt

# Imagem final
FROM python:3.11-slim

# Criar usuário não-root
RUN useradd -m -u 1000 appuser

# Definir diretório de trabalho
WORKDIR /app

# Copiar dependências instaladas
COPY --from=builder /root/.local /home/appuser/.local

# Copiar código da aplicação
COPY --chown=appuser:appuser . .

# Criar diretórios necessários
RUN mkdir -p data/raw data/processed data/embeddings && \
    chown -R appuser:appuser data/

# Mudar para usuário não-root
USER appuser

# Adicionar .local/bin ao PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Expor porta da API
EXPOSE 8000

# Comando padrão
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
