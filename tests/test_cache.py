#!/usr/bin/env python3
"""Comprehensive unit tests for cache module with static typing."""

import os
import sys
import time
import unittest
from typing import Dict, List, Optional

from typing_extensions import override

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytz

from ccusage_monitor.cache import Cache, CacheValue, cache
from ccusage_monitor.protocols import CcusageData


class TestCacheBasicOperations(unittest.TestCase):
    """Test basic cache operations."""
    
    cache: Cache[CacheValue]  # Declare instance variable

    @override
    def setUp(self) -> None:
        """Create a new cache instance for each test."""
        self.cache = Cache()
        # Also clear the global cache
        cache.clear()

    def test_get_set_string(self) -> None:
        """Test get/set with string values."""
        key: str = "test_key"
        value: str = "test_value"

        # Initially, key should not exist
        result: Optional[CacheValue] = self.cache.get(key)
        self.assertIsNone(result)

        # Set value
        self.cache.set(key, value)

        # Get value back
        result = self.cache.get(key)
        self.assertEqual(result, value)
        self.assertIsInstance(result, str)

    def test_get_set_bool(self) -> None:
        """Test get/set with boolean values."""
        self.cache.set("bool_true", True)
        self.cache.set("bool_false", False)

        result_true: Optional[CacheValue] = self.cache.get("bool_true")
        result_false: Optional[CacheValue] = self.cache.get("bool_false")

        self.assertTrue(result_true)
        self.assertFalse(result_false)
        self.assertIsInstance(result_true, bool)
        self.assertIsInstance(result_false, bool)

    def test_get_set_float(self) -> None:
        """Test get/set with float values."""
        key: str = "float_key"
        value: float = 3.14159

        self.cache.set(key, value)
        result: Optional[CacheValue] = self.cache.get(key)

        self.assertEqual(result, value)
        self.assertIsInstance(result, float)

    def test_get_set_dict(self) -> None:
        """Test get/set with dictionary values."""
        key: str = "dict_key"
        value = {"name": "test", "count": 42, "active": True}

        self.cache.set(key, value)
        result: Optional[CacheValue] = self.cache.get(key)

        self.assertEqual(result, value)
        self.assertIsInstance(result, dict)

    def test_get_set_ccusage_data(self) -> None:
        """Test get/set with CcusageData TypedDict."""
        key: str = "ccusage_key"
        value: CcusageData = {"blocks": [{"totalTokens": 1000, "isActive": True, "startTime": "2024-01-01T10:00:00Z"}]}

        self.cache.set(key, value)
        result: Optional[CacheValue] = self.cache.get(key)

        self.assertEqual(result, value)
        self.assertIsInstance(result, dict)
        if isinstance(result, dict):
            self.assertIn("blocks", result)

    def test_get_set_pytz_timezone(self) -> None:
        """Test get/set with pytz timezone objects."""
        key: str = "tz_key"
        value: pytz.BaseTzInfo = pytz.timezone("US/Eastern")

        self.cache.set(key, value)
        result: Optional[CacheValue] = self.cache.get(key)

        self.assertEqual(result, value)
        self.assertIsInstance(result, pytz.tzinfo.BaseTzInfo)

    def test_overwrite_value(self) -> None:
        """Test overwriting an existing value."""
        key: str = "overwrite_key"

        self.cache.set(key, "initial_value")
        self.assertEqual(self.cache.get(key), "initial_value")

        self.cache.set(key, "new_value")
        self.assertEqual(self.cache.get(key), "new_value")

    def test_multiple_keys(self) -> None:
        """Test multiple keys stored simultaneously."""
        keys_values: Dict[str, CacheValue] = {"key1": "value1", "key2": 42.0, "key3": True, "key4": {"data": "test"}}

        # Set all values
        for key, value in keys_values.items():
            self.cache.set(key, value)

        # Verify all values
        for key, expected_value in keys_values.items():
            actual_value: Optional[CacheValue] = self.cache.get(key)
            self.assertEqual(actual_value, expected_value)

    def test_clear_cache(self) -> None:
        """Test clearing the cache."""
        # Add multiple items
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")

        # Verify they exist
        self.assertIsNotNone(self.cache.get("key1"))
        self.assertIsNotNone(self.cache.get("key2"))
        self.assertIsNotNone(self.cache.get("key3"))

        # Clear cache
        self.cache.clear()

        # Verify all are gone
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
        self.assertIsNone(self.cache.get("key3"))


class TestCacheTTL(unittest.TestCase):
    """Test cache TTL (time-to-live) functionality."""
    
    cache: Cache[CacheValue]  # Declare instance variable

    @override
    def setUp(self) -> None:
        """Create a new cache instance for each test."""
        self.cache = Cache()
        cache.clear()

    def test_no_ttl(self) -> None:
        """Test that items without TTL don't expire."""
        key: str = "no_ttl_key"
        value: str = "no_ttl_value"

        self.cache.set(key, value)

        # Sleep a bit
        time.sleep(0.1)

        # Should still be there
        result: Optional[CacheValue] = self.cache.get(key)
        self.assertEqual(result, value)

        # Even with TTL=0 on get, should still be there
        result = self.cache.get(key, ttl=0)
        self.assertEqual(result, value)

    def test_expired_ttl(self) -> None:
        """Test that items expire after TTL."""
        key: str = "ttl_key"
        value: str = "ttl_value"

        self.cache.set(key, value)

        # Sleep longer than TTL
        time.sleep(0.11)

        # Should be expired with TTL=0.1
        result: Optional[CacheValue] = self.cache.get(key, ttl=0.1)
        self.assertIsNone(result)

        # Key should be removed from cache
        result = self.cache.get(key)
        self.assertIsNone(result)

    def test_not_expired_ttl(self) -> None:
        """Test that items don't expire before TTL."""
        key: str = "ttl_key"
        value: str = "ttl_value"

        self.cache.set(key, value)

        # Sleep less than TTL
        time.sleep(0.05)

        # Should still be valid with TTL=0.1
        result: Optional[CacheValue] = self.cache.get(key, ttl=0.1)
        self.assertEqual(result, value)

    def test_ttl_removes_expired_entry(self) -> None:
        """Test that expired entries are removed from cache."""
        key: str = "expire_key"
        value: str = "expire_value"

        self.cache.set(key, value)

        # Sleep to expire
        time.sleep(0.11)

        # Get with TTL should return None and remove entry
        result: Optional[CacheValue] = self.cache.get(key, ttl=0.1)
        self.assertIsNone(result)

        # Verify it's actually removed (not just returning None)
        # This tests the internal state
        self.assertNotIn(key, self.cache._cache)  # pyright: ignore[reportPrivateUsage]

    def test_different_ttl_per_get(self) -> None:
        """Test different TTL values on get calls."""
        key: str = "ttl_key"
        value: str = "ttl_value"

        self.cache.set(key, value)

        # Sleep 0.15 seconds
        time.sleep(0.15)

        # Should be expired with TTL=0.1
        result: Optional[CacheValue] = self.cache.get(key, ttl=0.1)
        self.assertIsNone(result)

        # Set again
        self.cache.set(key, value)
        time.sleep(0.05)

        # Should be valid with TTL=0.2
        result = self.cache.get(key, ttl=0.2)
        self.assertEqual(result, value)


class TestGlobalCacheInstance(unittest.TestCase):
    """Test the global cache instance."""

    @override
    def setUp(self) -> None:
        """Clear global cache before each test."""
        cache.clear()

    def test_global_cache_operations(self) -> None:
        """Test operations on the global cache instance."""
        # Test basic operations
        cache.set("global_key", "global_value")
        result: Optional[CacheValue] = cache.get("global_key")
        self.assertEqual(result, "global_value")

        # Test clear
        cache.clear()
        result = cache.get("global_key")
        self.assertIsNone(result)

    def test_global_cache_ttl(self) -> None:
        """Test TTL on global cache instance."""
        cache.set("ttl_key", "ttl_value")

        # Should be valid immediately
        result: Optional[CacheValue] = cache.get("ttl_key", ttl=0.1)
        self.assertEqual(result, "ttl_value")

        # Sleep and check expiration
        time.sleep(0.11)
        result = cache.get("ttl_key", ttl=0.1)
        self.assertIsNone(result)

    def test_global_cache_type_safety(self) -> None:
        """Test type safety with global cache."""
        # Store different types
        cache.set("bool_key", True)
        cache.set("float_key", 3.14)
        cache.set("str_key", "hello")
        cache.set("dict_key", {"a": 1, "b": 2})

        # Retrieve and verify types
        bool_val: Optional[CacheValue] = cache.get("bool_key")
        float_val: Optional[CacheValue] = cache.get("float_key")
        str_val: Optional[CacheValue] = cache.get("str_key")
        dict_val: Optional[CacheValue] = cache.get("dict_key")

        self.assertIsInstance(bool_val, bool)
        self.assertIsInstance(float_val, float)
        self.assertIsInstance(str_val, str)
        self.assertIsInstance(dict_val, dict)


class TestCacheEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    cache: Cache[CacheValue]  # Declare instance variable

    @override
    def setUp(self) -> None:
        """Create a new cache instance for each test."""
        self.cache = Cache()

    def test_none_key(self) -> None:
        """Test handling of None as key."""
        # This will likely cause a TypeError since dict keys must be hashable
        with self.assertRaises(TypeError):
            self.cache.set(None, "value")  # pyright: ignore[reportArgumentType]  # type: ignore[arg-type]

    def test_empty_string_key(self) -> None:
        """Test empty string as key."""
        key: str = ""
        value: str = "empty_key_value"

        self.cache.set(key, value)
        result: Optional[CacheValue] = self.cache.get(key)
        self.assertEqual(result, value)

    def test_special_character_keys(self) -> None:
        """Test keys with special characters."""
        keys: List[str] = [
            "key with spaces",
            "key\twith\ttabs",
            "key\nwith\nnewlines",
            "key_with_unicode_😀",
            "key/with/slashes",
            "key:with:colons",
            "key[with]brackets",
        ]

        for key in keys:
            self.cache.set(key, f"value_for_{key}")

        for key in keys:
            result: Optional[CacheValue] = self.cache.get(key)
            self.assertEqual(result, f"value_for_{key}")

    def test_negative_ttl(self) -> None:
        """Test negative TTL values."""
        key: str = "neg_ttl_key"
        value: str = "neg_ttl_value"

        self.cache.set(key, value)

        # Negative TTL should immediately expire
        result: Optional[CacheValue] = self.cache.get(key, ttl=-1)
        self.assertIsNone(result)

    def test_very_large_ttl(self) -> None:
        """Test very large TTL values."""
        key: str = "large_ttl_key"
        value: str = "large_ttl_value"

        self.cache.set(key, value)

        # Very large TTL should work fine
        result: Optional[CacheValue] = self.cache.get(key, ttl=999999)
        self.assertEqual(result, value)

    def test_concurrent_access(self) -> None:
        """Test cache behavior with rapid concurrent-like access."""
        # This is a simple test since we're not using threading
        # but it tests rapid successive operations
        num_operations: int = 1000

        for i in range(num_operations):
            key: str = f"key_{i % 10}"  # Reuse 10 keys
            value: int = i
            self.cache.set(key, value)

        # Verify final values
        for i in range(10):
            key = f"key_{i}"
            result: Optional[CacheValue] = self.cache.get(key)
            # Should have the last value written to this key
            expected: int = 990 + i  # Last iteration that wrote to this key
            self.assertEqual(result, expected)


class TestCachePerformance(unittest.TestCase):
    """Test cache performance characteristics."""
    
    cache: Cache[CacheValue]  # Declare instance variable

    @override
    def setUp(self) -> None:
        """Create a new cache instance for each test."""
        self.cache = Cache()

    def test_large_cache_size(self) -> None:
        """Test cache with many entries."""
        num_entries: int = 10000

        # Add many entries
        start_time: float = time.time()
        for i in range(num_entries):
            self.cache.set(f"key_{i}", f"value_{i}")
        set_time: float = time.time() - start_time

        # Verify all entries exist
        start_time = time.time()
        for i in range(num_entries):
            result: Optional[CacheValue] = self.cache.get(f"key_{i}")
            self.assertEqual(result, f"value_{i}")
        get_time: float = time.time() - start_time

        # Performance should be reasonable (< 1 second for 10k operations)
        self.assertLess(set_time, 1.0)
        self.assertLess(get_time, 1.0)

    def test_clear_performance(self) -> None:
        """Test clear performance with many entries."""
        num_entries: int = 10000

        # Add many entries
        for i in range(num_entries):
            self.cache.set(f"key_{i}", f"value_{i}")

        # Clear should be fast
        start_time: float = time.time()
        self.cache.clear()
        clear_time: float = time.time() - start_time

        self.assertLess(clear_time, 0.1)  # Should be very fast

        # Verify cache is empty
        for i in range(min(100, num_entries)):  # Check first 100
            result: Optional[CacheValue] = self.cache.get(f"key_{i}")
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
