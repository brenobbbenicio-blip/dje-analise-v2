#!/usr/bin/env python3
"""
Script para coletar dados do DJE
"""
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors.dje_collector import DJECollector
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


def main():
    """Função principal"""
    logger.info("Iniciando coleta de dados do DJE")

    # Inicializar coletor
    collector = DJECollector()

    # Coletar decisões
    decisions = collector.collect_decisions(max_pages=10)

    # Salvar decisões
    collector.save_decisions(decisions)

    logger.info(f"Coleta concluída: {len(decisions)} decisões coletadas")


if __name__ == "__main__":
    main()
