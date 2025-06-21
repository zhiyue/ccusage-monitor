"""Performance optimization utilities."""

import time
from typing import Any, Dict, List, Optional
from collections import deque
import threading


class StringPool:
    """String pool for reducing memory allocations in hot paths."""
    
    def __init__(self, max_size: int = 100):
        self._pool: Dict[str, str] = {}
        self._access_order: deque = deque(maxlen=max_size)
        self._lock = threading.Lock()
    
    def get_string(self, template: str, *args: Any) -> str:
        """Get formatted string from pool or create new one."""
        if not args:
            return template
            
        key = f"{template}:{':'.join(str(arg) for arg in args)}"
        
        with self._lock:
            if key in self._pool:
                # Move to end (most recently used)
                self._access_order.remove(key)
                self._access_order.append(key)
                return self._pool[key]
            
            # Create new string
            result = template.format(*args) if '{}' in template else template % args
            
            # Add to pool
            if len(self._pool) >= self._access_order.maxlen:
                # Remove least recently used
                oldest_key = self._access_order.popleft()
                del self._pool[oldest_key]
            
            self._pool[key] = result
            self._access_order.append(key)
            return result


class PerformanceMonitor:
    """Monitor performance metrics for optimization."""
    
    def __init__(self):
        self._metrics: Dict[str, List[float]] = {}
        self._start_times: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def start_timer(self, name: str) -> None:
        """Start timing an operation."""
        self._start_times[name] = time.perf_counter()
    
    def end_timer(self, name: str) -> float:
        """End timing and record the duration."""
        if name not in self._start_times:
            return 0.0
            
        duration = time.perf_counter() - self._start_times[name]
        
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = deque(maxlen=100)  # Keep last 100 measurements
            self._metrics[name].append(duration)
        
        del self._start_times[name]
        return duration
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        with self._lock:
            if name not in self._metrics or not self._metrics[name]:
                return {"count": 0, "avg": 0.0, "min": 0.0, "max": 0.0}
            
            values = list(self._metrics[name])
            return {
                "count": len(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "recent": values[-1] if values else 0.0
            }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get all performance statistics."""
        return {name: self.get_stats(name) for name in self._metrics.keys()}


class AdaptiveRefreshRate:
    """Adaptive refresh rate based on system performance."""
    
    def __init__(self, base_rate: float = 3.0, min_rate: float = 1.0, max_rate: float = 10.0):
        self.base_rate = base_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self._performance_history: deque = deque(maxlen=10)
        self._current_rate = base_rate
    
    def update_performance(self, operation_time: float) -> None:
        """Update performance metrics and adjust refresh rate."""
        self._performance_history.append(operation_time)
        
        if len(self._performance_history) >= 5:
            avg_time = sum(self._performance_history) / len(self._performance_history)
            
            # If operations are taking too long, reduce refresh rate
            if avg_time > 0.1:  # 100ms threshold
                self._current_rate = min(self._current_rate * 1.2, self.max_rate)
            elif avg_time < 0.05:  # 50ms threshold
                self._current_rate = max(self._current_rate * 0.9, self.min_rate)
    
    def get_refresh_rate(self) -> float:
        """Get current adaptive refresh rate."""
        return self._current_rate


# Global instances
string_pool = StringPool()
perf_monitor = PerformanceMonitor()
adaptive_refresh = AdaptiveRefreshRate()


def format_cached(template: str, *args: Any) -> str:
    """Format string using cached pool."""
    return string_pool.get_string(template, *args)


def timed_operation(name: str):
    """Decorator for timing operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            perf_monitor.start_timer(name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = perf_monitor.end_timer(name)
                adaptive_refresh.update_performance(duration)
        return wrapper
    return decorator


def get_performance_summary() -> Dict[str, Any]:
    """Get comprehensive performance summary."""
    return {
        "metrics": perf_monitor.get_all_stats(),
        "refresh_rate": adaptive_refresh.get_refresh_rate(),
        "string_pool_size": len(string_pool._pool)
    }
