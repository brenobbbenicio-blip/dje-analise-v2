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

# Configurações dos Tribunais Regionais Eleitorais
TRE_CONFIGS = {
    "TSE": {
        "name": "Tribunal Superior Eleitoral",
        "url": "https://www.tse.jus.br/jurisprudencia",
        "abbreviation": "TSE",
        "state": "Nacional",
        "search_patterns": [
            "/busca?q={term}",
            "/jurisprudencia/busca?termo={term}",
            "/pesquisa?texto={term}",
            "?s={term}"
        ]
    },
    "TRE-MG": {
        "name": "Tribunal Regional Eleitoral de Minas Gerais",
        "url": "https://www.tre-mg.jus.br/jurisprudencia",
        "abbreviation": "TRE-MG",
        "state": "MG",
        "search_patterns": [
            "/busca?q={term}",
            "/pesquisa?termo={term}",
            "/consulta?texto={term}",
            "?s={term}"
        ]
    },
    "TRE-RJ": {
        "name": "Tribunal Regional Eleitoral do Rio de Janeiro",
        "url": "https://www.tre-rj.jus.br/jurisprudencia",
        "abbreviation": "TRE-RJ",
        "state": "RJ",
        "search_patterns": [
            "/busca?q={term}",
            "/pesquisa?termo={term}",
            "/consulta?texto={term}",
            "?s={term}"
        ]
    },
    "TRE-PR": {
        "name": "Tribunal Regional Eleitoral do Paraná",
        "url": "https://www.tre-pr.jus.br/jurisprudencia",
        "abbreviation": "TRE-PR",
        "state": "PR",
        "search_patterns": [
            "/busca?q={term}",
            "/pesquisa?termo={term}",
            "/consulta?texto={term}",
            "?s={term}"
        ]
    },
    "TRE-SC": {
        "name": "Tribunal Regional Eleitoral de Santa Catarina",
        "url": "https://www.tre-sc.jus.br/jurisprudencia",
        "abbreviation": "TRE-SC",
        "state": "SC",
        "search_patterns": [
            "/busca?q={term}",
            "/pesquisa?termo={term}",
            "/consulta?texto={term}",
            "?s={term}"
        ]
    },
    "TRE-PA": {
        "name": "Tribunal Regional Eleitoral do Pará",
        "url": "https://www.tre-pa.jus.br/jurisprudencia",
        "abbreviation": "TRE-PA",
        "state": "PA",
        "search_patterns": [
            "/busca?q={term}",
            "/pesquisa?termo={term}",
            "/consulta?texto={term}",
            "?s={term}"
        ]
    },
    "TRE-RO": {
        "name": "Tribunal Regional Eleitoral de Rondônia",
        "url": "https://www.tre-ro.jus.br/jurisprudencia",
        "abbreviation": "TRE-RO",
        "state": "RO",
        "search_patterns": [
            "/busca?q={term}",
            "/pesquisa?termo={term}",
            "/consulta?texto={term}",
            "?s={term}"
        ]
    },
    "TRE-AM": {
        "name": "Tribunal Regional Eleitoral do Amazonas",
        "url": "https://www.tre-am.jus.br/jurisprudencia",
        "abbreviation": "TRE-AM",
        "state": "AM",
        "search_patterns": [
            "/busca?q={term}",
            "/pesquisa?termo={term}",
            "/consulta?texto={term}",
            "?s={term}"
        ]
    },
    "TRE-AP": {
        "name": "Tribunal Regional Eleitoral do Amapá",
        "url": "https://www.tre-ap.jus.br/jurisprudencia",
        "abbreviation": "TRE-AP",
        "state": "AP",
        "search_patterns": [
            "/busca?q={term}",
            "/pesquisa?termo={term}",
            "/consulta?texto={term}",
            "?s={term}"
        ]
    }
}

# Lista de tribunais disponíveis
AVAILABLE_TRIBUNALS = list(TRE_CONFIGS.keys())

# Configurações de processamento
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
