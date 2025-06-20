"""Cache module for performance optimization."""

import time
from typing import Any, Dict, Optional, Tuple


class Cache:
    """Simple in-memory cache with TTL support."""

    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float]] = {}

    def get(self, key: str, ttl: float = 0) -> Optional[Any]:
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

    def set(self, key: str, value: Any) -> None:
        """Store value in cache with current timestamp."""
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()


# Global cache instance
_cache = Cache()
