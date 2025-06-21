#!/usr/bin/env python3
"""Test script to verify all performance optimizations are working correctly."""

import time
import sys
from datetime import datetime, timezone

def test_cache_system():
    """Test the enhanced cache system."""
    print("🧪 Testing Enhanced Cache System...")
    
    from ccusage_monitor.core.cache import cache
    
    # Test basic operations
    cache.clear()
    
    # Test write performance
    start = time.perf_counter()
    for i in range(1000):
        cache.set(f"test_key_{i}", f"test_value_{i}")
    write_time = time.perf_counter() - start
    
    # Test read performance
    start = time.perf_counter()
    hits = 0
    for i in range(1000):
        if cache.get(f"test_key_{i}") is not None:
            hits += 1
    read_time = time.perf_counter() - start
    
    # Test cache stats
    stats = cache.get_stats()
    
    print(f"   ✅ Write performance: {write_time*1000:.2f}ms for 1000 operations")
    print(f"   ✅ Read performance: {read_time*1000:.2f}ms for 1000 operations")
    print(f"   ✅ Cache hits: {hits}/1000")
    print(f"   ✅ Cache stats: {stats['size']} entries, {stats['hit_rate']:.1f}% hit rate")
    
    return write_time < 0.01 and read_time < 0.01  # Should be under 10ms


def test_performance_monitoring():
    """Test the performance monitoring system."""
    print("\n🧪 Testing Performance Monitoring...")
    
    from ccusage_monitor.core.performance import perf_monitor, timed_operation, get_performance_summary
    
    @timed_operation("test_operation")
    def test_function():
        time.sleep(0.001)  # 1ms delay
        return "test_result"
    
    # Run test function multiple times
    for _ in range(10):
        result = test_function()
    
    # Get performance stats
    stats = perf_monitor.get_stats("test_operation")
    summary = get_performance_summary()
    
    print(f"   ✅ Test operation stats: {stats['count']} calls, {stats['avg']*1000:.2f}ms avg")
    print(f"   ✅ Performance summary available: {len(summary.get('metrics', {}))} metrics tracked")
    
    return stats['count'] == 10 and stats['avg'] > 0


def test_display_optimizations():
    """Test display optimization features."""
    print("\n🧪 Testing Display Optimizations...")
    
    from ccusage_monitor.ui.display import create_token_progress_bar, _buffer
    
    # Test progress bar performance
    start = time.perf_counter()
    bars = []
    for i in range(100):
        bar = create_token_progress_bar(i)
        bars.append(bar)
    progress_time = time.perf_counter() - start
    
    # Test buffer operations
    _buffer.writeln("Test line 1")
    _buffer.writeln("Test line 2")
    buffer_stats = _buffer.get_stats()
    
    print(f"   ✅ Progress bar performance: {progress_time*1000:.2f}ms for 100 bars")
    print(f"   ✅ Buffer stats: {buffer_stats['writes']} writes, {buffer_stats['buffer_size']} bytes")
    
    return progress_time < 0.01  # Should be under 10ms


def test_data_operations():
    """Test data operation optimizations."""
    print("\n🧪 Testing Data Operations...")
    
    from ccusage_monitor.core import data, calculations
    
    # Test check_ccusage_installed (should be cached)
    start = time.perf_counter()
    for _ in range(10):
        result = data.check_ccusage_installed()
    check_time = time.perf_counter() - start
    
    # Test calculations with mock data
    mock_blocks = [
        {
            "startTime": datetime.now(timezone.utc).isoformat(),
            "totalTokens": 1000 + i * 100,
            "isActive": i == 0,
            "isGap": False
        }
        for i in range(5)
    ]
    
    current_time = datetime.now(timezone.utc)
    
    start = time.perf_counter()
    for _ in range(10):
        burn_rate = calculations.calculate_hourly_burn_rate(mock_blocks, current_time)
    calc_time = time.perf_counter() - start
    
    print(f"   ✅ ccusage check performance: {check_time*1000:.2f}ms for 10 calls")
    print(f"   ✅ Burn rate calculation: {calc_time*1000:.2f}ms for 10 calls")
    
    return check_time < 0.01 and calc_time < 0.01


def test_adaptive_features():
    """Test adaptive performance features."""
    print("\n🧪 Testing Adaptive Features...")
    
    from ccusage_monitor.core.performance import adaptive_refresh
    
    # Test adaptive refresh rate
    initial_rate = adaptive_refresh.get_refresh_rate()
    
    # Simulate slow performance
    adaptive_refresh.update_performance(0.2)  # 200ms operation
    slow_rate = adaptive_refresh.get_refresh_rate()
    
    # Simulate fast performance
    adaptive_refresh.update_performance(0.01)  # 10ms operation
    fast_rate = adaptive_refresh.get_refresh_rate()
    
    print(f"   ✅ Initial refresh rate: {initial_rate:.1f}s")
    print(f"   ✅ Rate after slow operation: {slow_rate:.1f}s")
    print(f"   ✅ Rate after fast operation: {fast_rate:.1f}s")
    
    return slow_rate >= initial_rate  # Should adapt to slower performance


def main():
    """Run all optimization tests."""
    print("🚀 Claude Code Usage Monitor - Optimization Test Suite")
    print("=" * 60)
    
    tests = [
        ("Cache System", test_cache_system),
        ("Performance Monitoring", test_performance_monitoring),
        ("Display Optimizations", test_display_optimizations),
        ("Data Operations", test_data_operations),
        ("Adaptive Features", test_adaptive_features),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All optimizations are working correctly!")
        return 0
    else:
        print("⚠️  Some optimizations need attention.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
