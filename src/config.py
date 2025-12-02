"""
Configurações do sistema de análise de jurisprudência
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Diretórios
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"

# Criar diretórios se não existirem
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, VECTORSTORE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configurações da API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Configurações do modelo
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 2000
TEMPERATURE = 0.3

# Configurações do ChromaDB
CHROMA_COLLECTION_NAME = "jurisprudencia_eleitoral"

# Configurações do scraper
DJE_BASE_URL = "https://www.tse.jus.br/jurisprudencia"
MAX_DOCUMENTS_PER_SEARCH = 100
REQUEST_DELAY = 2  # segundos entre requisições

# Configurações de processamento
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
