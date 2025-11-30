#!/usr/bin/env python3
"""
Script para processar e indexar dados no RAG
"""
import sys
import json
from pathlib import Path
from typing import List

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.processors.text_processor import TextProcessor
from src.rag.rag_system import RAGSystem
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


def load_decisions(file_path: Path) -> List[dict]:
    """Carrega decisões de arquivo JSON"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Função principal"""
    logger.info("Iniciando processamento e indexação")

    # Encontrar arquivo mais recente de decisões
    raw_files = list(settings.RAW_DATA_DIR.glob("decisions_*.json"))
    if not raw_files:
        logger.error("Nenhum arquivo de decisões encontrado")
        return

    latest_file = max(raw_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Processando arquivo: {latest_file}")

    # Carregar decisões
    decisions = load_decisions(latest_file)
    logger.info(f"Carregadas {len(decisions)} decisões")

    # Processar decisões
    processor = TextProcessor()
    chunks = processor.process_batch(decisions)
    logger.info(f"Gerados {len(chunks)} chunks")

    # Indexar no RAG
    rag_system = RAGSystem()
    rag_system.index_documents(chunks)

    logger.info("Indexação concluída com sucesso")


if __name__ == "__main__":
    main()
