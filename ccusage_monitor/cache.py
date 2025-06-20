"""Cache module for performance optimization."""

import time
from typing import Any, Dict, Generic, Optional, Tuple, TypeVar, Union

import pytz

from ccusage_monitor.protocols import CcusageData, DisplayValues

T = TypeVar("T")

# The cache can store a variety of types. This Union defines them.
CacheValue = Union[bool, CcusageData, float, str, pytz.BaseTzInfo, Dict[str, Any], DisplayValues]


class Cache(Generic[T]):
    """Simple in-memory cache with TTL support."""

    def __init__(self) -> None:
        self._cache: Dict[str, Tuple[T, float]] = {}

    def get(self, key: str, ttl: float = 0) -> Optional[T]:
        """Get value from cache if not expired.

        Args:
            key: Cache key
            ttl: Time to live in seconds (0 = no expiration)

        Returns:
            Cached value or None if expired/not found
        """
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]

        if ttl > 0 and time.time() - timestamp > ttl:
            # Expired
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: T) -> None:
        """Store value in cache with current timestamp."""
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()


# Global cache instance
cache: "Cache[CacheValue]" = Cache()
