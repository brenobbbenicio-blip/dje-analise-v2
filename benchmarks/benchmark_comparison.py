"""
Comprehensive benchmark comparing original vs optimized implementations
Shows before/after performance improvements
"""
import time
import sys
from pathlib import Path
import json
import statistics

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings.document_processor import DocumentProcessor
from src.embeddings.document_processor_optimized import DocumentProcessorOptimized
from src.scraper.dje_scraper import DJEScraper
from src.scraper.dje_scraper_optimized import DJEScraperOptimized


class ComprehensiveBenchmark:
    """Comprehensive benchmark suite"""
    
    def __init__(self):
        self.results = {
            'original': {},
            'optimized': {},
            'improvements': {}
        }
    
    def time_function(self, func, *args, iterations=5, **kwargs):
        """Time a function execution"""
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            times.append(end - start)
        
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'times': times
        }
    
    def calculate_improvement(self, original_time, optimized_time):
        """Calculate performance improvement"""
        if optimized_time == 0:
            return float('inf'), 100.0
        
        speedup = original_time / optimized_time
        improvement = ((original_time - optimized_time) / original_time * 100)
        
        return speedup, improvement
    
    def benchmark_document_processing(self, documents):
        """Benchmark document processing"""
        print("\n" + "="*80)
        print("DOCUMENT PROCESSING BENCHMARK")
        print("="*80)
        
        # Original
        print("\n📊 Testing Original Implementation...")
        processor_orig = DocumentProcessor()
        stats_orig = self.time_function(
            processor_orig.process_documents,
            documents,
            iterations=10
        )
        print(f"  ✓ Mean time: {stats_orig['mean']*1000:.2f}ms")
        
        # Optimized (without multiprocessing for fair comparison with small dataset)
        print("\n🚀 Testing Optimized Implementation...")
        processor_opt = DocumentProcessorOptimized(use_multiprocessing=False)
        stats_opt = self.time_function(
            processor_opt.process_documents,
            documents,
            iterations=10
        )
        print(f"  ✓ Mean time: {stats_opt['mean']*1000:.2f}ms")
        
        # Calculate improvement
        speedup, improvement = self.calculate_improvement(
            stats_orig['mean'],
            stats_opt['mean']
        )
        
        print(f"\n💡 Performance Gain:")
        print(f"  Speedup: {speedup:.2f}x faster")
        print(f"  Improvement: {improvement:.1f}%")
        
        self.results['original']['document_processing'] = stats_orig
        self.results['optimized']['document_processing'] = stats_opt
        self.results['improvements']['document_processing'] = {
            'speedup': speedup,
            'improvement': improvement
        }
    
    def benchmark_text_cleaning(self, texts):
        """Benchmark text cleaning"""
        print("\n" + "="*80)
        print("TEXT CLEANING BENCHMARK")
        print("="*80)
        
        # Original
        print("\n📊 Testing Original Implementation...")
        processor_orig = DocumentProcessor()
        
        def clean_all_orig():
            return [processor_orig.clean_text(text) for text in texts]
        
        stats_orig = self.time_function(clean_all_orig, iterations=20)
        print(f"  ✓ Mean time: {stats_orig['mean']*1000:.2f}ms")
        
        # Optimized
        print("\n🚀 Testing Optimized Implementation...")
        processor_opt = DocumentProcessorOptimized()
        
        def clean_all_opt():
            return [processor_opt.clean_text(text) for text in texts]
        
        stats_opt = self.time_function(clean_all_opt, iterations=20)
        print(f"  ✓ Mean time: {stats_opt['mean']*1000:.2f}ms")
        
        # Calculate improvement
        speedup, improvement = self.calculate_improvement(
            stats_orig['mean'],
            stats_opt['mean']
        )
        
        print(f"\n💡 Performance Gain:")
        print(f"  Speedup: {speedup:.2f}x faster")
        print(f"  Improvement: {improvement:.1f}%")
        
        self.results['original']['text_cleaning'] = stats_orig
        self.results['optimized']['text_cleaning'] = stats_opt
        self.results['improvements']['text_cleaning'] = {
            'speedup': speedup,
            'improvement': improvement
        }
    
    def benchmark_keyword_extraction(self, texts):
        """Benchmark keyword extraction"""
        print("\n" + "="*80)
        print("KEYWORD EXTRACTION BENCHMARK")
        print("="*80)
        
        # Original
        print("\n📊 Testing Original Implementation...")
        processor_orig = DocumentProcessor()
        
        def extract_all_orig():
            return [processor_orig.extract_keywords(text, top_k=5) for text in texts]
        
        stats_orig = self.time_function(extract_all_orig, iterations=20)
        print(f"  ✓ Mean time: {stats_orig['mean']*1000:.2f}ms")
        
        # Optimized (Counter-based)
        print("\n🚀 Testing Optimized Implementation (Counter)...")
        processor_opt = DocumentProcessorOptimized()
        
        def extract_all_opt():
            return [processor_opt.extract_keywords(text, top_k=5) for text in texts]
        
        stats_opt = self.time_function(extract_all_opt, iterations=20)
        print(f"  ✓ Mean time: {stats_opt['mean']*1000:.2f}ms")
        
        # Calculate improvement
        speedup, improvement = self.calculate_improvement(
            stats_orig['mean'],
            stats_opt['mean']
        )
        
        print(f"\n💡 Performance Gain:")
        print(f"  Speedup: {speedup:.2f}x faster")
        print(f"  Improvement: {improvement:.1f}%")
        
        self.results['original']['keyword_extraction'] = stats_orig
        self.results['optimized']['keyword_extraction'] = stats_opt
        self.results['improvements']['keyword_extraction'] = {
            'speedup': speedup,
            'improvement': improvement
        }
    
    def benchmark_scraper(self):
        """Benchmark scraper"""
        print("\n" + "="*80)
        print("SCRAPER BENCHMARK")
        print("="*80)
        
        # Original
        print("\n📊 Testing Original Implementation...")
        scraper_orig = DJEScraper()
        stats_orig = self.time_function(
            scraper_orig.scrape_search_results,
            "teste",
            5,
            iterations=5
        )
        print(f"  ✓ Mean time: {stats_orig['mean']*1000:.2f}ms")
        
        # Optimized
        print("\n🚀 Testing Optimized Implementation...")
        scraper_opt = DJEScraperOptimized()
        stats_opt = self.time_function(
            scraper_opt.scrape_search_results,
            "teste",
            5,
            iterations=5
        )
        print(f"  ✓ Mean time: {stats_opt['mean']*1000:.2f}ms")
        
        # Calculate improvement
        speedup, improvement = self.calculate_improvement(
            stats_orig['mean'],
            stats_opt['mean']
        )
        
        print(f"\n💡 Performance Gain:")
        print(f"  Speedup: {speedup:.2f}x faster")
        print(f"  Improvement: {improvement:.1f}%")
        
        self.results['original']['scraper'] = stats_orig
        self.results['optimized']['scraper'] = stats_opt
        self.results['improvements']['scraper'] = {
            'speedup': speedup,
            'improvement': improvement
        }
    
    def print_summary(self):
        """Print comprehensive summary"""
        print("\n" + "="*80)
        print("🎯 FINAL PERFORMANCE SUMMARY")
        print("="*80)
        
        print("\n📊 ORIGINAL vs OPTIMIZED")
        print("-"*80)
        
        for component in ['document_processing', 'text_cleaning', 'keyword_extraction', 'scraper']:
            if component in self.results['improvements']:
                imp = self.results['improvements'][component]
                orig = self.results['original'][component]
                opt = self.results['optimized'][component]
                
                print(f"\n{component.replace('_', ' ').title()}:")
                print(f"  Original:  {orig['mean']*1000:8.2f}ms")
                print(f"  Optimized: {opt['mean']*1000:8.2f}ms")
                print(f"  Speedup:   {imp['speedup']:8.2f}x")
                print(f"  Improvement: {imp['improvement']:6.1f}%")
        
        print("\n" + "="*80)
    
    def save_results(self, filepath="benchmark_comparison.json"):
        """Save benchmark results"""
        output_path = Path(__file__).parent / filepath
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to: {output_path}")


def create_test_data():
    """Create test data"""
    scraper = DJEScraper()
    
    # Generate test documents
    documents = scraper._generate_example_documents("teste", 5)
    
    # Create test texts
    texts = [
        "  Este é um   texto    com    espaços   extras   e   precisa   ser   limpo   " * 10,
        "A jurisprudência eleitoral estabelece regras importantes para eleições justas " * 10,
        "Candidatos devem cumprir requisitos de elegibilidade conforme a legislação " * 10,
        "O tribunal superior eleitoral decide sobre questões eleitorais importantes " * 10,
        "As decisões judiciais devem ser fundamentadas em precedentes jurídicos " * 10,
    ]
    
    return documents, texts


def main():
    """Main benchmark function"""
    print("\n🚀 COMPREHENSIVE PERFORMANCE BENCHMARKS")
    print("Testing Original vs Optimized Implementations")
    print("="*80)
    
    benchmark = ComprehensiveBenchmark()
    
    # Create test data
    documents, texts = create_test_data()
    
    # Run all benchmarks
    benchmark.benchmark_document_processing(documents)
    benchmark.benchmark_text_cleaning(texts)
    benchmark.benchmark_keyword_extraction(texts)
    benchmark.benchmark_scraper()
    
    # Print summary
    benchmark.print_summary()
    
    # Save results
    benchmark.save_results()
    
    print("\n✅ Benchmarking complete!")


if __name__ == "__main__":
    main()
