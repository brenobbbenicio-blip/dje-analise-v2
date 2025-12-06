"""Configurações centralizadas do sistema DJE Análise.

Este módulo define todas as configurações da aplicação usando Pydantic Settings,
permitindo sobrescrever valores via variáveis de ambiente ou arquivo .env.
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas via variáveis de ambiente.

    Attributes:
        BASE_DIR: Diretório raiz do projeto.
        DATA_DIR: Diretório base para dados.
        RAW_DATA_DIR: Diretório para dados brutos coletados.
        PROCESSED_DATA_DIR: Diretório para dados processados.
        EMBEDDINGS_DIR: Diretório para armazenar embeddings.
        API_HOST: Host para o servidor da API.
        API_PORT: Porta para o servidor da API.
        API_RELOAD: Se True, habilita hot-reload em desenvolvimento.
        OPENAI_API_KEY: Chave de API da OpenAI.
        OPENAI_MODEL: Modelo de chat da OpenAI.
        EMBEDDING_MODEL: Modelo de embeddings da OpenAI.
        EMBEDDING_DIMENSION: Dimensão dos vetores de embedding.
        CHUNK_SIZE: Tamanho máximo de cada chunk de texto.
        CHUNK_OVERLAP: Sobreposição entre chunks consecutivos.
        TOP_K_RESULTS: Número padrão de resultados em buscas.
        CHROMA_PERSIST_DIR: Diretório de persistência do ChromaDB.
        COLLECTION_NAME: Nome da coleção no ChromaDB.
        DJE_BASE_URL: URL base do Diário da Justiça Eletrônica.
        REQUEST_TIMEOUT: Timeout para requisições HTTP em segundos.
        MAX_RETRIES: Número máximo de tentativas para requisições.
        RATE_LIMIT_DELAY: Delay entre requisições em segundos.
        LOG_LEVEL: Nível de logging (DEBUG, INFO, WARNING, ERROR).
        LOG_FORMAT: Formato das mensagens de log.
    """

    # Diretórios
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    EMBEDDINGS_DIR: Path = DATA_DIR / "embeddings"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # OpenAI
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    # RAG
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "data/embeddings/chroma"
    COLLECTION_NAME: str = "dje_jurisprudencia"

    # Scraping
    DJE_BASE_URL: str = (
        "https://www.tse.jus.br/servicos-judiciais/diario-da-justica-eletronica"
    )
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RATE_LIMIT_DELAY: float = 1.0

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()

# Criar diretórios se não existirem
settings.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
