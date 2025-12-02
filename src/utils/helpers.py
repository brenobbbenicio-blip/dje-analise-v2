"""
Funções auxiliares do sistema
"""
from typing import Dict, Any
import json
from pathlib import Path
from datetime import datetime


def format_result(result: Dict[str, Any]) -> str:
    """
    Formata resultado da consulta para exibição

    Args:
        result: Resultado da consulta RAG

    Returns:
        String formatada
    """
    output = []
    output.append("\n" + "=" * 80)
    output.append("RESULTADO DA ANÁLISE")
    output.append("=" * 80)
    output.append(f"\nPergunta: {result['query']}\n")
    output.append("-" * 80)
    output.append("\nResposta:")
    output.append(result['answer'])
    output.append("\n" + "-" * 80)
    output.append("\nFontes consultadas:")

    for i, source in enumerate(result['sources'], 1):
        metadata = source.get('metadata', {})
        output.append(f"\n{i}. {metadata.get('title', 'Documento sem título')}")
        output.append(f"   Relevância: {1 - source.get('distance', 0):.2f}")
        if 'number' in metadata:
            output.append(f"   Número: {metadata['number']}")
        if 'year' in metadata:
            output.append(f"   Ano: {metadata['year']}")

    output.append("\n" + "=" * 80 + "\n")

    return "\n".join(output)


def save_result(result: Dict[str, Any], output_dir: Path):
    """
    Salva resultado em arquivo JSON

    Args:
        result: Resultado para salvar
        output_dir: Diretório de saída
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"consulta_{timestamp}.json"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return filepath


def print_banner():
    """Imprime banner do sistema"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║        Sistema de Análise de Jurisprudência Eleitoral com RAG v2.0          ║
║                                                                              ║
║              Análise inteligente de decisões eleitorais                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def validate_api_key(api_key: str) -> bool:
    """
    Valida se a API key está configurada

    Args:
        api_key: Chave da API

    Returns:
        True se válida, False caso contrário
    """
    return bool(api_key and api_key.strip() and api_key != "")
