"""
Testes básicos para o sistema DJE Análise v2
"""
import pytest
from pathlib import Path
import sys

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings import DocumentProcessor
from src.scraper import DJEScraper


class TestDocumentProcessor:
    """Testes para o processador de documentos"""

    def test_processor_initialization(self):
        """Testa inicialização do processador"""
        processor = DocumentProcessor()
        assert processor is not None
        assert processor.text_splitter is not None

    def test_process_single_document(self):
        """Testa processamento de um documento"""
        processor = DocumentProcessor()

        doc = {
            'title': 'Teste',
            'text': 'Este é um texto de teste para processamento.',
            'metadata': {'id': '001'}
        }

        result = processor.process_documents([doc])

        assert len(result) > 0
        assert 'text' in result[0]
        assert 'metadata' in result[0]

    def test_clean_text(self):
        """Testa limpeza de texto"""
        processor = DocumentProcessor()

        dirty_text = "  Texto   com    espaços   extras  "
        clean = processor.clean_text(dirty_text)

        assert clean == "Texto com espaços extras"

    def test_extract_keywords(self):
        """Testa extração de palavras-chave"""
        processor = DocumentProcessor()

        text = """
        A jurisprudência eleitoral estabelece regras claras para o
        registro de candidatura. Os candidatos devem cumprir requisitos
        específicos de elegibilidade.
        """

        keywords = processor.extract_keywords(text, top_k=3)

        assert len(keywords) <= 3
        assert all(isinstance(k, str) for k in keywords)


class TestDJEScraper:
    """Testes para o scraper"""

    def test_scraper_initialization(self):
        """Testa inicialização do scraper"""
        scraper = DJEScraper()
        assert scraper is not None
        assert scraper.base_url is not None

    def test_scrape_search_results(self):
        """Testa coleta de documentos"""
        scraper = DJEScraper()

        docs = scraper.scrape_search_results("teste", max_results=2)

        assert len(docs) > 0
        assert isinstance(docs, list)
        assert 'text' in docs[0]
        assert 'metadata' in docs[0]

    def test_generate_example_documents(self):
        """Testa geração de documentos de exemplo"""
        scraper = DJEScraper()

        docs = scraper._generate_example_documents("teste", 3)

        assert len(docs) == 3
        for doc in docs:
            assert 'title' in doc
            assert 'text' in doc
            assert 'metadata' in doc


class TestConfiguration:
    """Testes para configuração"""

    def test_import_config(self):
        """Testa importação de configurações"""
        from src import config

        assert hasattr(config, 'BASE_DIR')
        assert hasattr(config, 'EMBEDDING_MODEL')
        assert hasattr(config, 'CHUNK_SIZE')

    def test_directories_exist(self):
        """Testa se diretórios foram criados"""
        from src.config import DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR

        assert DATA_DIR.exists()
        assert RAW_DATA_DIR.exists()
        assert PROCESSED_DATA_DIR.exists()


# Testes que requerem API key (marcados para pular se não configurada)
@pytest.mark.skipif(
    not Path('.env').exists(),
    reason="Requer arquivo .env configurado"
)
class TestRAGSystem:
    """Testes para o sistema RAG (requerem API key)"""

    def test_rag_initialization(self):
        """Testa inicialização do RAG"""
        try:
            from src.models import RAGSystem
            rag = RAGSystem()
            assert rag is not None
        except Exception as e:
            pytest.skip(f"API key não configurada: {e}")


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"])
