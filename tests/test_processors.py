"""
Testes do processador de texto
"""
import pytest
from src.processors.text_processor import TextProcessor


@pytest.fixture
def processor():
    """Fixture do processador"""
    return TextProcessor(chunk_size=100, chunk_overlap=20)


@pytest.fixture
def sample_decision():
    """Fixture de decisão exemplo"""
    return {
        "title": "Decisão Teste",
        "date": "2024-01-15",
        "url": "https://example.com/decisao/123",
        "content": "Esta é uma decisão judicial de teste. " * 50,
        "collected_at": "2024-01-15T10:00:00"
    }


def test_clean_text(processor):
    """Teste de limpeza de texto"""
    dirty_text = "Texto    com    espaços      extras\n\n\n\n"
    clean = processor.clean_text(dirty_text)
    assert "  " not in clean
    assert clean.strip() == "Texto com espaços extras"


def test_extract_metadata(processor, sample_decision):
    """Teste de extração de metadados"""
    metadata = processor.extract_metadata(sample_decision)
    assert metadata["title"] == "Decisão Teste"
    assert metadata["date"] == "2024-01-15"
    assert metadata["url"] == "https://example.com/decisao/123"


def test_chunk_text(processor):
    """Teste de divisão em chunks"""
    text = "A" * 500
    metadata = {"title": "Teste"}
    chunks = processor.chunk_text(text, metadata)

    assert len(chunks) > 0
    assert all('text' in chunk for chunk in chunks)
    assert all('metadata' in chunk for chunk in chunks)


def test_process_decision(processor, sample_decision):
    """Teste de processamento completo"""
    chunks = processor.process_decision(sample_decision)

    assert len(chunks) > 0
    assert all('text' in chunk for chunk in chunks)
    assert all('metadata' in chunk for chunk in chunks)
    assert all('chunk_index' in chunk['metadata'] for chunk in chunks)


def test_process_empty_decision(processor):
    """Teste com decisão vazia"""
    empty_decision = {"content": ""}
    chunks = processor.process_decision(empty_decision)
    assert len(chunks) == 0
