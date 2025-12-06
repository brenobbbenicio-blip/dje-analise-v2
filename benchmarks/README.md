# 📊 Performance Benchmarks

This directory contains benchmark scripts to measure and compare the performance of original vs optimized implementations.

## 📁 Files

- `benchmark_performance.py` - Basic benchmark for original implementation
- `benchmark_comparison.py` - Comprehensive comparison of original vs optimized
- `benchmark_original.json` - Baseline performance data
- `benchmark_comparison.json` - Comparison results

## 🚀 Running Benchmarks

### Basic Benchmark
```bash
python benchmarks/benchmark_performance.py
```

### Comprehensive Comparison
```bash
python benchmarks/benchmark_comparison.py
```

## 📈 Latest Results

### Performance Improvements

| Component | Original | Optimized | Speedup |
|-----------|----------|-----------|---------|
| Document Processing | 0.04ms | 0.03ms | **1.32x** |
| Scraper | 10000ms | 10ms | **965x** |
| Keyword Extraction | 0.10ms | 0.10ms | Similar |

### Key Findings

1. **Scraper optimization is the most dramatic** - 965x faster by removing artificial delays and using async operations
2. **Batch processing shows best results with larger datasets** - The test uses small datasets, so improvements are modest
3. **Caching provides instant results** - Second queries for the same text are near-instantaneous

## 🔧 Adding New Benchmarks

To add a new benchmark:

1. Create a new function in `benchmark_comparison.py`
2. Follow the existing pattern:
   ```python
   def benchmark_new_feature(self, data):
       # Test original
       stats_orig = self.time_function(original_func, data)
       
       # Test optimized
       stats_opt = self.time_function(optimized_func, data)
       
       # Calculate improvement
       speedup, improvement = self.calculate_improvement(
           stats_orig['mean'],
           stats_opt['mean']
       )
       
       # Store results
       self.results['original']['new_feature'] = stats_orig
       self.results['optimized']['new_feature'] = stats_opt
       self.results['improvements']['new_feature'] = {
           'speedup': speedup,
           'improvement': improvement
       }
   ```

3. Call it from `main()`

## 📝 Notes

- Benchmarks use small test datasets for quick execution
- Production improvements will be more significant with larger datasets
- Results may vary based on hardware and system load
- All times are in milliseconds unless otherwise noted

## 🎯 Interpreting Results

- **Speedup > 1.0**: Optimized version is faster
- **Speedup < 1.0**: Original version is faster (optimization overhead)
- **Improvement %**: Percentage reduction in execution time
  - Positive: Time reduced (faster)
  - Negative: Time increased (slower)

## 🔍 Profiling

For detailed profiling, use:

```bash
# Memory profiling
python -m memory_profiler benchmarks/benchmark_comparison.py

# Line profiling (requires line_profiler)
kernprof -l -v benchmarks/benchmark_comparison.py
```

## 📚 Further Reading

See `docs/PERFORMANCE_OPTIMIZATION.md` for detailed explanations of optimization techniques.
