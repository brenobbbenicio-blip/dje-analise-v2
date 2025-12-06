"""
Tests for optimized implementations
"""
import pytest
from pathlib import Path
import sys
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings.document_processor_optimized import DocumentProcessorOptimized
from src.scraper.dje_scraper_optimized import DJEScraperOptimized


class TestDocumentProcessorOptimized:
    """Tests for optimized document processor"""
    
    def test_processor_initialization(self):
        """Test processor initialization"""
        processor = DocumentProcessorOptimized()
        assert processor is not None
        assert processor.text_splitter is not None
        assert processor.use_multiprocessing is True
        assert processor.whitespace_pattern is not None
    
    def test_process_single_document(self):
        """Test processing single document"""
        processor = DocumentProcessorOptimized(use_multiprocessing=False)
        
        doc = {
            'title': 'Test Document',
            'text': 'This is a test document for processing.',
            'metadata': {'id': '001'}
        }
        
        result = processor.process_documents([doc])
        
        assert len(result) > 0
        assert 'text' in result[0]
        assert 'metadata' in result[0]
        assert result[0]['metadata']['title'] == 'Test Document'
    
    def test_process_multiple_documents(self):
        """Test processing multiple documents"""
        processor = DocumentProcessorOptimized(use_multiprocessing=False)
        
        docs = [
            {
                'title': f'Document {i}',
                'text': f'This is test document {i}. ' * 50,
                'metadata': {'id': str(i)}
            }
            for i in range(5)
        ]
        
        result = processor.process_documents(docs)
        
        assert len(result) > 0
        assert all('text' in doc for doc in result)
    
    def test_clean_text(self):
        """Test text cleaning"""
        processor = DocumentProcessorOptimized()
        
        dirty_text = "  Text   with    extra   spaces  "
        clean = processor.clean_text(dirty_text)
        
        assert clean == "Text with extra spaces"
    
    def test_clean_text_batch(self):
        """Test batch text cleaning"""
        processor = DocumentProcessorOptimized()
        
        texts = [
            "  Text   1  ",
            "  Text   2  ",
            "  Text   3  "
        ]
        
        cleaned = processor.clean_text_batch(texts)
        
        assert len(cleaned) == len(texts)
        assert all(isinstance(text, str) for text in cleaned)
        assert cleaned[0] == "Text 1"
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        processor = DocumentProcessorOptimized()
        
        text = """
        A jurisprudência eleitoral estabelece regras importantes para
        eleições justas. Os candidatos devem cumprir requisitos de
        elegibilidade conforme a legislação eleitoral.
        """
        
        keywords = processor.extract_keywords(text, top_k=3)
        
        assert len(keywords) <= 3
        assert all(isinstance(k, str) for k in keywords)
        assert 'eleitoral' in keywords
    
    def test_extract_keywords_batch(self):
        """Test batch keyword extraction"""
        processor = DocumentProcessorOptimized(use_multiprocessing=False)
        
        texts = [
            "A jurisprudência eleitoral estabelece regras importantes",
            "Os candidatos devem cumprir requisitos legais",
            "O tribunal decide sobre questões eleitorais"
        ]
        
        keywords_list = processor.extract_keywords_batch(texts, top_k=2)
        
        assert len(keywords_list) == len(texts)
        assert all(isinstance(kw_list, list) for kw_list in keywords_list)
    
    def test_stopwords_frozen(self):
        """Test that stopwords is a frozenset"""
        processor = DocumentProcessorOptimized()
        assert isinstance(processor.stopwords, frozenset)
    
    def test_cache_initialization(self):
        """Test word to ID cache initialization"""
        processor = DocumentProcessorOptimized()
        assert isinstance(processor.word_to_id_cache, dict)
        assert isinstance(processor.id_to_word_cache, list)


class TestDJEScraperOptimized:
    """Tests for optimized scraper"""
    
    def test_scraper_initialization(self):
        """Test scraper initialization"""
        scraper = DJEScraperOptimized()
        assert scraper is not None
        assert scraper.base_url is not None
        assert scraper.max_concurrent > 0
    
    def test_scrape_search_results_sync(self):
        """Test sync scraping"""
        scraper = DJEScraperOptimized()
        
        docs = scraper.scrape_search_results("test", max_results=3)
        
        assert len(docs) > 0
        assert isinstance(docs, list)
        assert 'text' in docs[0]
        assert 'metadata' in docs[0]
    
    def test_scrape_search_results_async(self):
        """Test async scraping via sync wrapper"""
        scraper = DJEScraperOptimized()
        
        # Use asyncio.run to test async function
        docs = asyncio.run(scraper.scrape_search_results_async("test", max_results=3))
        
        assert len(docs) > 0
        assert isinstance(docs, list)
        assert 'text' in docs[0]
    
    def test_generate_example_documents(self):
        """Test example document generation"""
        scraper = DJEScraperOptimized()
        
        docs = scraper._generate_example_documents("test", 3)
        
        assert len(docs) == 3
        for doc in docs:
            assert 'title' in doc
            assert 'text' in doc
            assert 'metadata' in doc
    
    def test_save_and_load_documents(self):
        """Test document save/load"""
        scraper = DJEScraperOptimized()
        
        docs = scraper._generate_example_documents("test", 2)
        filename = "test_optimized_docs.json"
        
        # Save
        scraper.save_documents(docs, filename)
        
        # Load
        loaded = scraper.load_documents(filename)
        
        assert len(loaded) == len(docs)
        assert loaded[0]['title'] == docs[0]['title']


class TestOptimizedPerformance:
    """Performance comparison tests"""
    
    def test_document_processing_performance(self):
        """Test that optimized version is not slower"""
        from src.embeddings.document_processor import DocumentProcessor
        import time
        
        docs = [
            {
                'title': f'Doc {i}',
                'text': 'Sample text. ' * 20,
                'metadata': {'id': i}
            }
            for i in range(5)
        ]
        
        # Original
        processor_orig = DocumentProcessor()
        start = time.perf_counter()
        result_orig = processor_orig.process_documents(docs)
        time_orig = time.perf_counter() - start
        
        # Optimized
        processor_opt = DocumentProcessorOptimized(use_multiprocessing=False)
        start = time.perf_counter()
        result_opt = processor_opt.process_documents(docs)
        time_opt = time.perf_counter() - start
        
        # Should produce same number of chunks
        assert len(result_orig) == len(result_opt)
        
        # Optimized should not be significantly slower (allowing 2x tolerance)
        assert time_opt < time_orig * 2.0
    
    def test_keyword_extraction_correctness(self):
        """Test that optimized keyword extraction produces valid results"""
        processor = DocumentProcessorOptimized()
        
        text = "eleitoral eleitoral candidatos candidatos candidatos tribunal"
        keywords = processor.extract_keywords(text, top_k=2)
        
        # Should extract most frequent words
        assert 'candidatos' in keywords
        assert 'eleitoral' in keywords


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
