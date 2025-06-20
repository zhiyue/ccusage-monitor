"""Comprehensive tests for ccusage_monitor.core.cache module."""

import time
from unittest.mock import patch

import pytest

from ccusage_monitor.core.cache import Cache, cache


class TestCache:
    """Test the Cache class."""

    def test_cache_initialization(self):
        """Test cache initializes correctly."""
        test_cache = Cache()
        assert len(test_cache._cache) == 0

    def test_cache_set_and_get(self):
        """Test basic set and get operations."""
        test_cache = Cache()

        test_cache.set("key1", "value1")
        assert test_cache.get("key1") == "value1"

    def test_cache_get_nonexistent_key(self):
        """Test getting a key that doesn't exist returns None."""
        test_cache = Cache()
        assert test_cache.get("nonexistent") is None

    def test_cache_overwrite_value(self):
        """Test overwriting existing cache value."""
        test_cache = Cache()

        test_cache.set("key1", "value1")
        test_cache.set("key1", "value2")
        assert test_cache.get("key1") == "value2"

    def test_cache_ttl_expiration(self):
        """Test cache TTL expiration."""
        test_cache = Cache()

        # Mock time to simulate expiration
        with patch("ccusage_monitor.core.cache.time.time") as mock_time:
            # Set initial time when value was stored
            original_time = 1000.0
            mock_time.return_value = original_time

            # Set the value with known timestamp
            test_cache.set("key1", "value1")

            # Simulate 2 seconds passed
            mock_time.return_value = original_time + 2
            assert test_cache.get("key1", ttl=1) is None

    def test_cache_ttl_not_expired(self):
        """Test cache value within TTL."""
        test_cache = Cache()

        with patch("ccusage_monitor.core.cache.time.time") as mock_time:
            original_time = 1000.0
            mock_time.return_value = original_time

            test_cache.set("key1", "value1")

            # Simulate 0.5 seconds passed (within 1 second TTL)
            mock_time.return_value = original_time + 0.5
            assert test_cache.get("key1", ttl=1) == "value1"

    def test_cache_clear(self):
        """Test clearing cache."""
        test_cache = Cache()

        test_cache.set("key1", "value1")
        test_cache.set("key2", "value2")

        test_cache.clear()
        assert len(test_cache._cache) == 0
        assert test_cache.get("key1") is None
        assert test_cache.get("key2") is None

    def test_cache_different_data_types(self):
        """Test caching different Python data types."""
        test_cache = Cache()

        test_values = [
            ("str", "string value"),
            ("int", 123),
            ("float", 45.67),
            ("bool_true", True),
            ("bool_false", False),
            ("list", [1, 2, 3]),
            ("dict", {"key": "value"}),
            ("tuple", (1, 2, 3)),
            ("none", None),
        ]

        for key, value in test_values:
            test_cache.set(key, value)
            assert test_cache.get(key) == value

    def test_cache_no_ttl_means_no_expiration(self):
        """Test that TTL=0 means no expiration check."""
        test_cache = Cache()

        with patch("time.time") as mock_time:
            original_time = time.time()
            mock_time.return_value = original_time

            test_cache.set("key1", "value1")

            # Simulate a very long time passed
            mock_time.return_value = original_time + 10000

            # Should still return value when ttl=0 (default)
            assert test_cache.get("key1") == "value1"
            assert test_cache.get("key1", ttl=0) == "value1"


class TestGlobalCacheInstance:
    """Test the global cache instance."""

    def test_global_cache_exists(self):
        """Test that global cache instance exists."""
        assert cache is not None
        assert isinstance(cache, Cache)

    def test_global_cache_basic_operations(self):
        """Test basic operations on global cache."""
        # Clear cache first
        cache.clear()

        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

        cache.clear()  # Clean up

    def test_global_cache_persistence_across_imports(self):
        """Test that global cache persists across module imports."""
        cache.clear()
        cache.set("persistent_key", "persistent_value")

        # Re-import the module
        from ccusage_monitor.core.cache import cache as cache2

        assert cache2.get("persistent_key") == "persistent_value"
        cache.clear()  # Clean up


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
