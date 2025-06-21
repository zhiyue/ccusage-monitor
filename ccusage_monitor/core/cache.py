"""Enhanced cache module for performance optimization."""

import time
from typing import Any, Dict, Generic, Optional, Tuple, TypeVar, Union
from collections import OrderedDict

import pytz

from ccusage_monitor.protocols import CcusageData, DisplayValues

T = TypeVar("T")

# The cache can store a variety of types. This Union defines them.
CacheValue = Union[bool, CcusageData, float, str, pytz.BaseTzInfo, Dict[str, Any], DisplayValues]


class LRUCache(Generic[T]):
    """LRU Cache with TTL support and size limits for better memory management."""

    def __init__(self, max_size: int = 1000) -> None:
        self._cache: OrderedDict[str, Tuple[T, float]] = OrderedDict()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def get(self, key: str, ttl: float = 0) -> Optional[T]:
        """Get value from cache if not expired.

        Args:
            key: Cache key
            ttl: Time to live in seconds (0 = no expiration)

        Returns:
            Cached value or None if expired/not found
        """
        if key not in self._cache:
            self._misses += 1
            return None

        value, timestamp = self._cache[key]

        # Check TTL
        if ttl > 0 and time.time() - timestamp > ttl:
            # Expired - remove and return None
            del self._cache[key]
            self._misses += 1
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        self._hits += 1
        return value

    def set(self, key: str, value: T) -> None:
        """Store value in cache with current timestamp."""
        current_time = time.time()

        if key in self._cache:
            # Update existing key
            self._cache[key] = (value, current_time)
            self._cache.move_to_end(key)
        else:
            # Add new key
            self._cache[key] = (value, current_time)

            # Enforce size limit
            if len(self._cache) > self._max_size:
                # Remove least recently used item
                self._cache.popitem(last=False)

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate
        }

    def cleanup_expired(self, ttl: float) -> int:
        """Remove expired entries and return count of removed items."""
        if ttl <= 0:
            return 0

        current_time = time.time()
        expired_keys = []

        for key, (_, timestamp) in self._cache.items():
            if current_time - timestamp > ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)


# Global cache instance with optimized settings
cache: "LRUCache[CacheValue]" = LRUCache(max_size=500)  # Reduced size for better memory usage
