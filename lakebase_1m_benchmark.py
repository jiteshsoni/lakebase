#!/usr/bin/env python3
"""
Lakebase 1 Million Row Benchmark Entry Point
This file provides a simple interface to run the benchmark with 1M rows and 16 threads
"""

import sys
import os

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

# Import the actual benchmark
from benchmark import Lakebase1MBenchmark

def main():
    """Run benchmark with custom configuration for 1M rows and 20 threads"""
    print("🎯 Lakebase 1 Million Row Benchmark with 20 Threads")
    print("=" * 60)
    
    # Create benchmark instance
    benchmark = Lakebase1MBenchmark()
    
    # Override configuration for 1M rows and 20 threads
    benchmark.table_rows = 1000000  # 1 million rows
    benchmark.thread_counts = [20]  # Only test 20 threads
    benchmark.test_duration = 60    # 60 seconds per test
    
    print(f"📋 Custom Configuration:")
    print(f"   Target rows: {benchmark.table_rows:,}")
    print(f"   Thread count: {benchmark.thread_counts}")
    print(f"   Test duration: {benchmark.test_duration}s")
    print(f"   Batch size: {benchmark.batch_size}")
    print()
    
    # Run the benchmark
    if benchmark.run_full_benchmark():
        print(f"\n✅ 1M Row Benchmark with 20 threads completed successfully!")
    else:
        print(f"\n❌ Benchmark failed!")

if __name__ == "__main__":
    main()
