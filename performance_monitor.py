#!/usr/bin/env python3
"""Performance monitoring and optimization tool for Claude Code Usage Monitor."""

import argparse
import json
import time
from datetime import datetime
from typing import Dict, Any

from ccusage_monitor.core.cache import cache
from ccusage_monitor.core.performance import get_performance_summary, perf_monitor


def run_performance_test(duration: int = 60) -> Dict[str, Any]:
    """Run performance test for specified duration."""
    print(f"🔬 Running performance test for {duration} seconds...")
    
    # Import here to avoid circular imports
    from ccusage_monitor.core import data, calculations
    from datetime import datetime, timezone
    
    start_time = time.time()
    test_results = {
        "duration": duration,
        "operations": {
            "ccusage_calls": 0,
            "burn_rate_calculations": 0,
            "cache_hits": 0,
            "cache_misses": 0
        },
        "timings": {},
        "errors": []
    }
    
    # Generate some test data
    current_time = datetime.now(timezone.utc)
    mock_blocks = [
        {
            "startTime": current_time.isoformat(),
            "totalTokens": 1000 + i * 100,
            "isActive": i == 0,
            "isGap": False
        }
        for i in range(10)
    ]
    
    iteration = 0
    while time.time() - start_time < duration:
        iteration += 1
        
        try:
            # Test data operations
            if iteration % 5 == 0:  # Every 5th iteration
                result = data.run_ccusage()
                test_results["operations"]["ccusage_calls"] += 1
            
            # Test calculations
            burn_rate = calculations.calculate_hourly_burn_rate(mock_blocks, current_time)
            test_results["operations"]["burn_rate_calculations"] += 1
            
            # Small delay to simulate real usage
            time.sleep(0.1)
            
        except Exception as e:
            test_results["errors"].append(str(e))
    
    # Get final performance stats
    test_results["timings"] = get_performance_summary()
    
    # Get cache stats
    cache_stats = cache.get_stats()
    test_results["operations"]["cache_hits"] = cache_stats["hits"]
    test_results["operations"]["cache_misses"] = cache_stats["misses"]
    
    return test_results


def analyze_performance(results: Dict[str, Any]) -> None:
    """Analyze and display performance results."""
    print("\n📊 Performance Analysis Results")
    print("=" * 50)
    
    # Operations summary
    ops = results["operations"]
    print(f"\n🔄 Operations Summary:")
    print(f"   ccusage calls: {ops['ccusage_calls']}")
    print(f"   Burn rate calculations: {ops['burn_rate_calculations']}")
    print(f"   Cache hits: {ops['cache_hits']}")
    print(f"   Cache misses: {ops['cache_misses']}")
    
    if ops['cache_hits'] + ops['cache_misses'] > 0:
        hit_rate = ops['cache_hits'] / (ops['cache_hits'] + ops['cache_misses']) * 100
        print(f"   Cache hit rate: {hit_rate:.1f}%")
    
    # Timing analysis
    timings = results["timings"]
    if "metrics" in timings:
        print(f"\n⏱️  Performance Metrics:")
        for name, stats in timings["metrics"].items():
            if stats["count"] > 0:
                print(f"   {name}:")
                print(f"     Average: {stats['avg']*1000:.2f}ms")
                print(f"     Min: {stats['min']*1000:.2f}ms")
                print(f"     Max: {stats['max']*1000:.2f}ms")
                print(f"     Count: {stats['count']}")
    
    # Adaptive refresh rate
    if "refresh_rate" in timings:
        print(f"\n🔄 Adaptive refresh rate: {timings['refresh_rate']:.1f}s")
    
    # Errors
    if results["errors"]:
        print(f"\n❌ Errors encountered: {len(results['errors'])}")
        for error in results["errors"][:5]:  # Show first 5 errors
            print(f"   - {error}")
    
    # Recommendations
    print(f"\n💡 Performance Recommendations:")
    
    if ops.get('cache_hits', 0) + ops.get('cache_misses', 0) > 0:
        hit_rate = ops['cache_hits'] / (ops['cache_hits'] + ops['cache_misses']) * 100
        if hit_rate < 70:
            print("   - Consider increasing cache TTL values")
        elif hit_rate > 95:
            print("   - Cache is highly effective")
    
    if "metrics" in timings:
        ccusage_stats = timings["metrics"].get("ccusage_execution", {})
        if ccusage_stats.get("avg", 0) > 0.5:
            print("   - ccusage execution is slow, consider increasing cache TTL")
        
        burn_rate_stats = timings["metrics"].get("burn_rate_calculation", {})
        if burn_rate_stats.get("avg", 0) > 0.1:
            print("   - Burn rate calculation could be optimized further")


def benchmark_specific_operation(operation: str, iterations: int = 1000) -> None:
    """Benchmark a specific operation."""
    print(f"\n🏃 Benchmarking {operation} ({iterations} iterations)...")
    
    from ccusage_monitor.core import data, calculations
    from datetime import datetime, timezone
    
    current_time = datetime.now(timezone.utc)
    mock_blocks = [
        {
            "startTime": current_time.isoformat(),
            "totalTokens": 1000 + i * 100,
            "isActive": i == 0,
            "isGap": False
        }
        for i in range(10)
    ]
    
    # Clear cache for fair benchmark
    cache.clear()
    
    start_time = time.perf_counter()
    
    if operation == "burn_rate":
        for _ in range(iterations):
            calculations.calculate_hourly_burn_rate(mock_blocks, current_time)
    elif operation == "ccusage":
        for _ in range(min(iterations, 10)):  # Limit ccusage calls
            data.run_ccusage()
    else:
        print(f"Unknown operation: {operation}")
        return
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    avg_time = total_time / iterations
    
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Average time: {avg_time*1000:.3f}ms")
    print(f"   Operations per second: {iterations/total_time:.1f}")


def main():
    """Main performance monitoring function."""
    parser = argparse.ArgumentParser(description="Performance monitoring for Claude Code Usage Monitor")
    parser.add_argument("--test", "-t", type=int, default=30, help="Run performance test for N seconds")
    parser.add_argument("--benchmark", "-b", choices=["burn_rate", "ccusage"], help="Benchmark specific operation")
    parser.add_argument("--iterations", "-i", type=int, default=1000, help="Number of iterations for benchmark")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    print("🚀 Claude Code Usage Monitor - Performance Tool")
    print("=" * 50)
    
    if args.benchmark:
        benchmark_specific_operation(args.benchmark, args.iterations)
    else:
        results = run_performance_test(args.test)
        analyze_performance(results)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to {args.output}")


if __name__ == "__main__":
    main()
