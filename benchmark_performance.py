#!/usr/bin/env python3
"""Benchmark script to compare original vs optimized performance."""

import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict

import psutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ccusage_monitor import calculations, calculations_optimized, data, data_optimized
from ccusage_monitor.cache import cache


def generate_test_data(num_blocks=100):
    """Generate test data similar to ccusage output."""
    current_time = datetime.now(timezone.utc)
    blocks = []

    for i in range(num_blocks):
        # Create blocks going back in time
        start_time = current_time.timestamp() - (i * 300)  # 5 minutes apart
        end_time = start_time + 240  # 4 minute sessions

        block = {
            "startTime": datetime.fromtimestamp(start_time, timezone.utc).isoformat(),
            "actualEndTime": datetime.fromtimestamp(end_time, timezone.utc).isoformat(),
            "totalTokens": 1000 + (i * 10),
            "isActive": i == 0,
            "isGap": False,
        }
        blocks.append(block)

    # Add some gaps
    for i in range(5, num_blocks, 10):
        blocks[i]["isGap"] = True

    return {"blocks": blocks}


def benchmark_burn_rate(blocks, current_time, iterations=1000) -> Dict[str, Any]:
    """Benchmark burn rate calculations."""
    result_orig = None
    result_opt = None
    # Original
    start = time.perf_counter()
    for _ in range(iterations):
        result_orig = calculations.calculate_hourly_burn_rate(blocks, current_time)
    time_orig = time.perf_counter() - start

    # Clear cache for fair comparison
    cache.clear()

    # Optimized
    start = time.perf_counter()
    for _ in range(iterations):
        result_opt = calculations_optimized.calculate_hourly_burn_rate(blocks, current_time)
    time_opt = time.perf_counter() - start

    return {
        "original": {"time": time_orig, "result": result_orig},
        "optimized": {"time": time_opt, "result": result_opt},
        "speedup": time_orig / time_opt if time_opt > 0 else 0,
    }


def benchmark_reset_time(current_time, iterations=1000) -> Dict[str, Any]:
    """Benchmark reset time calculations."""
    result_orig = None
    result_opt = None
    # Original
    start = time.perf_counter()
    for _ in range(iterations):
        result_orig = calculations.get_next_reset_time(current_time)
    time_orig = time.perf_counter() - start

    # Clear cache
    cache.clear()

    # Optimized
    start = time.perf_counter()
    for _ in range(iterations):
        result_opt = calculations_optimized.get_next_reset_time(current_time)
    time_opt = time.perf_counter() - start

    return {
        "original": {"time": time_orig, "result": result_orig},
        "optimized": {"time": time_opt, "result": result_opt},
        "speedup": time_orig / time_opt if time_opt > 0 else 0,
    }


def benchmark_token_limit(blocks, iterations=1000) -> Dict[str, Any]:
    """Benchmark token limit calculations."""
    result_orig = None
    result_opt = None
    # Original
    start = time.perf_counter()
    for _ in range(iterations):
        result_orig = data.get_token_limit("custom_max", blocks)
    time_orig = time.perf_counter() - start

    # Clear cache
    cache.clear()

    # Optimized
    start = time.perf_counter()
    for _ in range(iterations):
        result_opt = data_optimized.get_token_limit("custom_max", blocks)
    time_opt = time.perf_counter() - start

    return {
        "original": {"time": time_orig, "result": result_orig},
        "optimized": {"time": time_opt, "result": result_opt},
        "speedup": time_orig / time_opt if time_opt > 0 else 0,
    }


def measure_memory_usage():
    """Measure current memory usage."""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024  # MB


def main():
    """Run performance benchmarks."""
    print("🔬 Claude Code Usage Monitor - Performance Benchmark")
    print("=" * 60)

    # Generate test data
    print("\n📊 Generating test data...")
    test_data = generate_test_data(100)
    blocks = test_data["blocks"]
    current_time = datetime.now(timezone.utc)

    print(f"Generated {len(blocks)} blocks for testing")

    # Benchmark calculations
    print("\n🏃 Running benchmarks...")

    # 1. Burn rate calculation
    print("\n1. Burn Rate Calculation (1000 iterations):")
    burn_rate_results = benchmark_burn_rate(blocks, current_time)
    print(f"   Original:  {burn_rate_results['original']['time']:.3f}s")
    print(f"   Optimized: {burn_rate_results['optimized']['time']:.3f}s")
    print(f"   Speedup:   {burn_rate_results['speedup']:.2f}x")

    # 2. Reset time calculation
    print("\n2. Reset Time Calculation (1000 iterations):")
    reset_time_results = benchmark_reset_time(current_time)
    print(f"   Original:  {reset_time_results['original']['time']:.3f}s")
    print(f"   Optimized: {reset_time_results['optimized']['time']:.3f}s")
    print(f"   Speedup:   {reset_time_results['speedup']:.2f}x")

    # 3. Token limit calculation
    print("\n3. Token Limit Calculation (1000 iterations):")
    token_limit_results = benchmark_token_limit(blocks)
    print(f"   Original:  {token_limit_results['original']['time']:.3f}s")
    print(f"   Optimized: {token_limit_results['optimized']['time']:.3f}s")
    print(f"   Speedup:   {token_limit_results['speedup']:.2f}x")

    # 4. Cache effectiveness
    print("\n4. Cache Effectiveness Test:")
    cache.clear()

    # First call (no cache)
    start = time.perf_counter()
    calculations_optimized.calculate_hourly_burn_rate(blocks, current_time)
    first_call_time = time.perf_counter() - start

    # Second call (with cache)
    start = time.perf_counter()
    calculations_optimized.calculate_hourly_burn_rate(blocks, current_time)
    cached_call_time = time.perf_counter() - start

    print(f"   First call:  {first_call_time * 1000:.3f}ms")
    print(f"   Cached call: {cached_call_time * 1000:.3f}ms")
    print(f"   Cache speedup: {first_call_time / cached_call_time:.0f}x")

    # Overall summary
    print("\n📈 Overall Performance Summary:")
    avg_speedup = (burn_rate_results["speedup"] + reset_time_results["speedup"] + token_limit_results["speedup"]) / 3
    print(f"   Average speedup: {avg_speedup:.2f}x")
    print(f"   Memory usage: {measure_memory_usage():.1f} MB")

    print("\n✅ Benchmark complete!")


if __name__ == "__main__":
    main()
