#!/usr/bin/env python3
"""Script para processar e indexar dados no sistema RAG.

Carrega decisões coletadas, processa em chunks e indexa
no vector store para busca semântica.
"""
import json
import sys
from pathlib import Path
from typing import Any

# Adiciona src ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings  # noqa: E402
from src.processors.text_processor import TextProcessor  # noqa: E402
from src.rag.rag_system import RAGSystem  # noqa: E402
from src.utils.logger import setup_logger  # noqa: E402

logger = setup_logger(__name__)


def load_decisions(file_path: Path) -> list[dict[str, Any]]:
    """Carrega decisões de um arquivo JSON.

    Args:
        file_path: Caminho para o arquivo JSON.

    Returns:
        Lista de decisões como dicionários.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    """Executa o processamento e indexação de dados."""
    logger.info("Iniciando processamento e indexação")

    # Encontra o arquivo mais recente de decisões
    raw_files = list(settings.RAW_DATA_DIR.glob("decisions_*.json"))
    if not raw_files:
        logger.error("Nenhum arquivo de decisões encontrado")
        return

    latest_file = max(raw_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Processando arquivo: {latest_file}")

    decisions = load_decisions(latest_file)
    logger.info(f"Carregadas {len(decisions)} decisões")

    processor = TextProcessor()
    chunks = processor.process_batch(decisions)
    logger.info(f"Gerados {len(chunks)} chunks")

    rag_system = RAGSystem()
    rag_system.index_documents(chunks)

    logger.info("Indexação concluída com sucesso")


if __name__ == "__main__":
    main()
