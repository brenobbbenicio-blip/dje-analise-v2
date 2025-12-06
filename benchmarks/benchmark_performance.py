"""
Benchmark script to measure performance improvements
Compares original vs optimized implementations
"""
import time
import sys
from pathlib import Path
import json
import statistics

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings.document_processor import DocumentProcessor
from src.scraper.dje_scraper import DJEScraper


class PerformanceBenchmark:
    """Benchmark utility for measuring performance"""
    
    def __init__(self):
        self.results = {}
    
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
            'stdev': statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def benchmark_document_processing(self, processor, documents, name="Original"):
        """Benchmark document processing"""
        print(f"\n🔍 Benchmarking {name} Document Processing...")
        
        stats = self.time_function(
            processor.process_documents,
            documents,
            iterations=5
        )
        
        self.results[f'document_processing_{name.lower()}'] = stats
        
        print(f"  Mean time: {stats['mean']*1000:.2f}ms")
        print(f"  Median: {stats['median']*1000:.2f}ms")
        print(f"  Min: {stats['min']*1000:.2f}ms")
        print(f"  Max: {stats['max']*1000:.2f}ms")
        print(f"  Std Dev: {stats['stdev']*1000:.2f}ms")
        
        return stats
    
    def benchmark_text_cleaning(self, processor, texts, name="Original"):
        """Benchmark text cleaning"""
        print(f"\n🔍 Benchmarking {name} Text Cleaning...")
        
        def clean_all():
            return [processor.clean_text(text) for text in texts]
        
        stats = self.time_function(clean_all, iterations=10)
        
        self.results[f'text_cleaning_{name.lower()}'] = stats
        
        print(f"  Mean time: {stats['mean']*1000:.2f}ms")
        print(f"  Median: {stats['median']*1000:.2f}ms")
        
        return stats
    
    def benchmark_keyword_extraction(self, processor, texts, name="Original"):
        """Benchmark keyword extraction"""
        print(f"\n🔍 Benchmarking {name} Keyword Extraction...")
        
        def extract_all():
            return [processor.extract_keywords(text, top_k=5) for text in texts]
        
        stats = self.time_function(extract_all, iterations=5)
        
        self.results[f'keyword_extraction_{name.lower()}'] = stats
        
        print(f"  Mean time: {stats['mean']*1000:.2f}ms")
        print(f"  Median: {stats['median']*1000:.2f}ms")
        
        return stats
    
    def calculate_speedup(self, original_stats, optimized_stats):
        """Calculate speedup factor"""
        original_mean = original_stats['mean']
        optimized_mean = optimized_stats['mean']
        speedup = original_mean / optimized_mean if optimized_mean > 0 else 0
        improvement = ((original_mean - optimized_mean) / original_mean * 100) if original_mean > 0 else 0
        return speedup, improvement
    
    def print_summary(self):
        """Print benchmark summary"""
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY")
        print("="*80)
        
        for key, stats in self.results.items():
            print(f"\n{key}:")
            print(f"  Mean: {stats['mean']*1000:.2f}ms")
            print(f"  Median: {stats['median']*1000:.2f}ms")
    
    def save_results(self, filepath="benchmark_results.json"):
        """Save benchmark results to file"""
        output_path = Path(__file__).parent / filepath
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to: {output_path}")


def create_test_data():
    """Create test data for benchmarking"""
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


def run_original_benchmarks():
    """Run benchmarks for original implementation"""
    print("\n" + "="*80)
    print("ORIGINAL IMPLEMENTATION BENCHMARKS")
    print("="*80)
    
    benchmark = PerformanceBenchmark()
    
    # Create test data
    documents, texts = create_test_data()
    
    # Initialize original processor
    processor = DocumentProcessor()
    
    # Run benchmarks
    benchmark.benchmark_document_processing(processor, documents, "Original")
    benchmark.benchmark_text_cleaning(processor, texts, "Original")
    benchmark.benchmark_keyword_extraction(processor, texts, "Original")
    
    return benchmark


def main():
    """Main benchmark function"""
    print("\n🚀 Starting Performance Benchmarks")
    print("="*80)
    
    # Run original benchmarks
    benchmark = run_original_benchmarks()
    
    # Print summary
    benchmark.print_summary()
    
    # Save results
    benchmark.save_results("benchmark_original.json")
    
    print("\n✅ Benchmarking complete!")


if __name__ == "__main__":
    main()
