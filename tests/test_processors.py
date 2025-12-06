"""Testes do processador de texto para jurisprudências.

Valida as funcionalidades de limpeza, extração de metadados
e chunking de textos jurídicos.
"""
import pytest

from src.processors.text_processor import TextProcessor


@pytest.fixture
def processor() -> TextProcessor:
    """Fixture que cria um processador com configurações de teste."""
    return TextProcessor(chunk_size=100, chunk_overlap=20)


@pytest.fixture
def sample_decision() -> dict[str, str]:
    """Fixture com uma decisão de exemplo para testes."""
    return {
        "title": "Decisão Teste",
        "date": "2024-01-15",
        "url": "https://example.com/decisao/123",
        "content": "Esta é uma decisão judicial de teste. " * 50,
        "collected_at": "2024-01-15T10:00:00",
    }


def test_clean_text(processor: TextProcessor) -> None:
    """Teste de limpeza e normalização de texto."""
    dirty_text = "Texto    com    espaços      extras\n\n\n\n"
    clean = processor.clean_text(dirty_text)
    assert "  " not in clean
    assert clean.strip() == "Texto com espaços extras"


def test_extract_metadata(
    processor: TextProcessor,
    sample_decision: dict[str, str],
) -> None:
    """Teste de extração de metadados de decisão."""
    metadata = processor.extract_metadata(sample_decision)
    assert metadata["title"] == "Decisão Teste"
    assert metadata["date"] == "2024-01-15"
    assert metadata["url"] == "https://example.com/decisao/123"


def test_chunk_text(processor: TextProcessor) -> None:
    """Teste de divisão de texto em chunks."""
    text = "A" * 500
    metadata: dict[str, str] = {"title": "Teste"}
    chunks = processor.chunk_text(text, metadata)

    assert len(chunks) > 0
    assert all("text" in chunk for chunk in chunks)
    assert all("metadata" in chunk for chunk in chunks)


def test_process_decision(
    processor: TextProcessor,
    sample_decision: dict[str, str],
) -> None:
    """Teste de processamento completo de decisão."""
    chunks = processor.process_decision(sample_decision)

    assert len(chunks) > 0
    assert all("text" in chunk for chunk in chunks)
    assert all("metadata" in chunk for chunk in chunks)
    assert all("chunk_index" in chunk["metadata"] for chunk in chunks)


def test_process_empty_decision(processor: TextProcessor) -> None:
    """Teste com decisão sem conteúdo."""
    empty_decision: dict[str, str] = {"content": ""}
    chunks = processor.process_decision(empty_decision)
    assert len(chunks) == 0


def test_process_batch(processor: TextProcessor) -> None:
    """Teste de processamento em lote."""
    decisions: list[dict[str, str]] = [
        {"content": "Decisão um com conteúdo suficiente para chunking. " * 10},
        {"content": "Decisão dois com mais conteúdo para processamento. " * 10},
    ]
    chunks = processor.process_batch(decisions)
    assert len(chunks) > 0


def test_extract_process_number(processor: TextProcessor) -> None:
    """Teste de extração de número de processo CNJ."""
    decision: dict[str, str] = {
        "content": "Processo 0001234-56.2024.6.00.0001 julgado procedente.",
    }
    metadata = processor.extract_metadata(decision)
    assert "process_number" in metadata
    assert metadata["process_number"] == "0001234-56.2024.6.00.0001"


def test_extract_judicial_body(processor: TextProcessor) -> None:
    """Teste de extração de órgão julgador."""
    decision: dict[str, str] = {
        "content": "Tribunal: Superior Tribunal Eleitoral - Decisão unânime.",
    }
    metadata = processor.extract_metadata(decision)
    assert "judicial_body" in metadata
    assert "Superior Tribunal Eleitoral" in metadata["judicial_body"]
