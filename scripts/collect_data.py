#!/usr/bin/env python3
"""Script para coletar dados do DJE.

Executa a coleta de decisões judiciais do Diário da Justiça Eletrônica
e salva os resultados em formato JSON.
"""
import sys
from pathlib import Path

# Adiciona src ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors.dje_collector import DJECollector  # noqa: E402
from src.utils.logger import setup_logger  # noqa: E402

logger = setup_logger(__name__)


def main() -> None:
    """Executa a coleta de dados do DJE."""
    logger.info("Iniciando coleta de dados do DJE")

    collector = DJECollector()
    decisions = collector.collect_decisions(max_pages=10)
    collector.save_decisions(decisions)

    logger.info(f"Coleta concluída: {len(decisions)} decisões coletadas")


if __name__ == "__main__":
    main()
