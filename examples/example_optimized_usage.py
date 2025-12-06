"""
Example demonstrating optimized implementations
Shows how to use the performance-optimized versions for production
"""
import sys
from pathlib import Path
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings.document_processor_optimized import DocumentProcessorOptimized
from src.scraper.dje_scraper_optimized import DJEScraperOptimized
# Note: RAGSystemOptimized requires OpenAI API key to run
# from src.models.rag_system_optimized import RAGSystemOptimized


def example_1_optimized_document_processing():
    """
    Example 1: Optimized Document Processing
    
    Shows how to use the optimized document processor with:
    - Parallel processing
    - Batch text cleaning
    - Fast keyword extraction
    """
    print("\n" + "="*80)
    print("Example 1: Optimized Document Processing")
    print("="*80)
    
    # Create processor with multiprocessing enabled
    processor = DocumentProcessorOptimized(
        chunk_size=1000,
        chunk_overlap=200,
        use_multiprocessing=True,  # Enable parallel processing
        max_workers=4  # Use 4 worker threads
    )
    
    # Sample documents
    documents = [
        {
            'title': 'Acórdão TSE 001',
            'text': 'Este é um exemplo de documento jurídico sobre eleições. ' * 50,
            'metadata': {'year': 2023, 'number': '001'}
        },
        {
            'title': 'Acórdão TSE 002',
            'text': 'Outro documento sobre jurisprudência eleitoral. ' * 50,
            'metadata': {'year': 2023, 'number': '002'}
        },
        {
            'title': 'Acórdão TSE 003',
            'text': 'Mais um documento sobre decisões eleitorais importantes. ' * 50,
            'metadata': {'year': 2023, 'number': '003'}
        }
    ]
    
    # Process documents (parallel processing automatically used)
    print("\n📄 Processing documents with parallel processing...")
    processed = processor.process_documents(documents)
    print(f"✓ Processed {len(documents)} documents into {len(processed)} chunks")
    
    # Batch text cleaning
    print("\n🧹 Batch text cleaning...")
    dirty_texts = [
        "  Text   with    extra   spaces  ",
        "Another  text   with   spaces   ",
        "Yet   another    one    "
    ]
    cleaned = processor.clean_text_batch(dirty_texts)
    print(f"✓ Cleaned {len(dirty_texts)} texts")
    print(f"  Example: '{dirty_texts[0]}' → '{cleaned[0]}'")
    
    # Fast keyword extraction
    print("\n🔑 Fast keyword extraction...")
    text = """
    A jurisprudência eleitoral brasileira estabelece regras importantes para 
    garantir eleições justas e transparentes. Os candidatos devem cumprir 
    requisitos específicos de elegibilidade conforme estabelecido pela 
    legislação eleitoral vigente. O Tribunal Superior Eleitoral decide sobre 
    questões eleitorais importantes que impactam o processo democrático.
    """
    keywords = processor.extract_keywords(text, top_k=5)
    print(f"✓ Extracted {len(keywords)} keywords: {', '.join(keywords)}")


def example_2_optimized_scraping():
    """
    Example 2: Optimized Async Scraping
    
    Shows how to use the optimized scraper with:
    - Async operations
    - Concurrent requests
    - Minimal delays
    """
    print("\n" + "="*80)
    print("Example 2: Optimized Async Scraping")
    print("="*80)
    
    # Create optimized scraper
    scraper = DJEScraperOptimized(max_concurrent=10)
    
    print("\n📥 Scraping documents with async operations...")
    documents = scraper.scrape_search_results(
        search_term="eleições",
        max_results=5
    )
    
    print(f"✓ Scraped {len(documents)} documents")
    for i, doc in enumerate(documents, 1):
        print(f"  {i}. {doc['title']}")
    
    # Save documents
    print("\n💾 Saving documents...")
    scraper.save_documents(documents, "optimized_example.json")
    print("✓ Documents saved")


def example_3_batch_operations():
    """
    Example 3: Batch Operations
    
    Shows the power of batch processing for better performance
    """
    print("\n" + "="*80)
    print("Example 3: Batch Operations")
    print("="*80)
    
    processor = DocumentProcessorOptimized(use_multiprocessing=True, max_workers=4)
    
    # Create a larger batch of texts
    texts = [
        "A jurisprudência eleitoral estabelece regras importantes " * 10,
        "Candidatos devem cumprir requisitos de elegibilidade " * 10,
        "O tribunal superior eleitoral decide sobre questões eleitorais " * 10,
        "As decisões judiciais devem ser fundamentadas em precedentes " * 10,
        "O processo democrático exige transparência e lisura " * 10,
    ] * 5  # 25 texts total
    
    print(f"\n📦 Processing batch of {len(texts)} texts...")
    
    # Batch keyword extraction (uses parallel processing)
    keywords_list = processor.extract_keywords_batch(texts, top_k=3)
    
    print(f"✓ Extracted keywords for {len(keywords_list)} texts")
    print(f"  Example keywords: {keywords_list[0]}")
    
    # Batch text cleaning
    cleaned_texts = processor.clean_text_batch(texts)
    print(f"✓ Cleaned {len(cleaned_texts)} texts")


async def example_4_async_patterns():
    """
    Example 4: Async Patterns
    
    Shows advanced async usage patterns
    """
    print("\n" + "="*80)
    print("Example 4: Advanced Async Patterns")
    print("="*80)
    
    scraper = DJEScraperOptimized(max_concurrent=20)
    
    print("\n🔄 Concurrent scraping of multiple search terms...")
    
    # Scrape multiple search terms concurrently
    search_terms = ["eleições", "candidatura", "propaganda", "prestação"]
    
    tasks = [
        scraper.scrape_search_results_async(term, max_results=3)
        for term in search_terms
    ]
    
    results = await asyncio.gather(*tasks)
    
    total_docs = sum(len(docs) for docs in results)
    print(f"✓ Scraped {total_docs} documents from {len(search_terms)} searches")
    
    for term, docs in zip(search_terms, results):
        print(f"  '{term}': {len(docs)} documents")


def example_5_performance_comparison():
    """
    Example 5: Performance Comparison
    
    Shows side-by-side comparison of original vs optimized
    """
    print("\n" + "="*80)
    print("Example 5: Performance Comparison")
    print("="*80)
    
    import time
    from src.embeddings.document_processor import DocumentProcessor
    
    # Create test data
    documents = [
        {
            'title': f'Document {i}',
            'text': 'Sample text content for testing performance. ' * 20,
            'metadata': {'id': i}
        }
        for i in range(10)
    ]
    
    # Test original
    print("\n📊 Testing ORIGINAL implementation...")
    processor_orig = DocumentProcessor()
    start = time.perf_counter()
    result_orig = processor_orig.process_documents(documents)
    time_orig = time.perf_counter() - start
    print(f"  Time: {time_orig*1000:.2f}ms")
    
    # Test optimized
    print("\n🚀 Testing OPTIMIZED implementation...")
    processor_opt = DocumentProcessorOptimized(use_multiprocessing=False)
    start = time.perf_counter()
    result_opt = processor_opt.process_documents(documents)
    time_opt = time.perf_counter() - start
    print(f"  Time: {time_opt*1000:.2f}ms")
    
    # Show improvement
    speedup = time_orig / time_opt if time_opt > 0 else 0
    improvement = ((time_orig - time_opt) / time_orig * 100) if time_orig > 0 else 0
    
    print(f"\n💡 Results:")
    print(f"  Speedup: {speedup:.2f}x")
    print(f"  Improvement: {improvement:.1f}%")


def main():
    """Run all examples"""
    print("\n🚀 DJE Análise v2 - Optimized Implementation Examples")
    print("="*80)
    
    try:
        # Run synchronous examples
        example_1_optimized_document_processing()
        example_2_optimized_scraping()
        example_3_batch_operations()
        example_5_performance_comparison()
        
        # Run async example
        print("\n⏳ Running async example...")
        asyncio.run(example_4_async_patterns())
        
        print("\n" + "="*80)
        print("✅ All examples completed successfully!")
        print("="*80)
        
        print("\n📚 Next Steps:")
        print("  1. Review the optimized code in src/*_optimized.py files")
        print("  2. Check docs/PERFORMANCE_OPTIMIZATION.md for details")
        print("  3. Run benchmarks with: python benchmarks/benchmark_comparison.py")
        print("  4. Install performance deps: pip install -r requirements-performance.txt")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
