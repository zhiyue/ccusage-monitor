"""Consolidated data module with optimized ccusage interaction and caching."""

import asyncio
import json
import os
import shutil
import subprocess
import time
from typing import List, Optional, cast

from ccusage_monitor.core.cache import cache
from ccusage_monitor.core.performance import timed_operation
from ccusage_monitor.protocols import CcusageBlock, CcusageData


def check_ccusage_installed() -> bool:
    """Check if ccusage is installed (with caching)."""
    # Cache the result for the entire session
    cached = cache.get("ccusage_installed")
    if isinstance(cached, bool):
        return cached

    result = shutil.which("ccusage") is not None
    cache.set("ccusage_installed", result)

    if not result:
        print("❌ 'ccusage' command not found!")
        print("\nThis tool requires 'ccusage' to be installed globally via npm.")
        print("\nTo install ccusage:")
        print("1. Install Node.js from https://nodejs.org/ (if not already installed)")
        print("2. Run: npm install -g ccusage")
        print("\nFor more information, visit: https://github.com/ryoppippi/ccusage")

    return result


@timed_operation("ccusage_execution")
def run_ccusage() -> Optional[CcusageData]:
    """Execute ccusage blocks --json command with enhanced caching and error handling."""
    # Check cache first with adaptive TTL based on system load
    cache_ttl = _get_adaptive_cache_ttl()
    cached_data = cache.get("ccusage_data", ttl=cache_ttl)
    if cached_data is not None:
        return cast(Optional[CcusageData], cached_data)

    # Check if we're in a retry cooldown period
    last_error_time = cache.get("ccusage_last_error_time")
    if last_error_time and isinstance(last_error_time, float):
        if time.time() - last_error_time < 30:  # 30 second cooldown
            return cache.get("ccusage_data_fallback")

    try:
        # Optimized subprocess execution
        result = subprocess.run(
            ["ccusage", "blocks", "--offline", "--json"],
            capture_output=True,
            text=True,
            check=True,
            timeout=8,  # Reduced timeout for faster failure detection
            # Optimize subprocess environment
            env={**os.environ, "NODE_OPTIONS": "--max-old-space-size=512"}
        )

        data = cast(CcusageData, json.loads(result.stdout))

        # Cache both current and fallback data
        cache.set("ccusage_data", data)
        cache.set("ccusage_data_fallback", data)  # Fallback for errors

        # Clear error state
        cache.set("ccusage_last_error_time", None)

        return data

    except subprocess.TimeoutExpired:
        _handle_ccusage_error("ccusage command timed out", "timeout")
        return _get_fallback_data()
    except FileNotFoundError:
        _handle_ccusage_error("ccusage command not found. Please install it with: npm install -g ccusage", "not_found")
        return None
    except subprocess.CalledProcessError as e:
        error_msg = f"Error running ccusage: {e}"
        if e.stderr:
            error_msg += f"\nError details: {e.stderr}"
        _handle_ccusage_error(error_msg, "process_error")
        return _get_fallback_data()
    except json.JSONDecodeError as e:
        _handle_ccusage_error(f"Error parsing JSON from ccusage: {e}", "json_error")
        return _get_fallback_data()


def _get_adaptive_cache_ttl() -> float:
    """Get adaptive cache TTL based on system performance."""
    # Start with base TTL
    base_ttl = 5.0

    # Check cache hit rate
    stats = cache.get_stats()
    hit_rate = stats.get("hit_rate", 0)

    # Increase TTL if hit rate is low (system under stress)
    if hit_rate < 50:
        return base_ttl * 2
    elif hit_rate > 80:
        return base_ttl * 0.8

    return base_ttl


def _handle_ccusage_error(error_msg: str, error_type: str) -> None:
    """Handle ccusage errors with rate limiting."""
    current_time = time.time()
    last_error_time = cache.get(f"ccusage_last_{error_type}_error")

    # Only print error if it hasn't been shown recently (avoid spam)
    if not last_error_time or current_time - last_error_time > 60:
        print(f"❌ {error_msg}")
        if error_type == "process_error":
            print("\nPossible solutions:")
            print("1. Make sure you're logged into Claude in your browser")
            print("2. Try running 'ccusage login' if authentication is required")
        cache.set(f"ccusage_last_{error_type}_error", current_time)

    cache.set("ccusage_last_error_time", current_time)


def _get_fallback_data() -> Optional[CcusageData]:
    """Get fallback data when ccusage fails."""
    return cache.get("ccusage_data_fallback")


async def run_ccusage_async() -> Optional[CcusageData]:
    """Async version of run_ccusage for non-blocking execution."""
    # Check cache first
    cached_data = cache.get("ccusage_data", ttl=5)
    if cached_data is not None:
        return cast(Optional[CcusageData], cached_data)

    try:
        proc = await asyncio.create_subprocess_exec(
            "ccusage",
            "blocks",
            "--offline",
            "--json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)

        if proc.returncode != 0:
            if stderr:
                print(f"❌ Error running ccusage: {stderr.decode()}")
            return None

        data = cast(CcusageData, json.loads(stdout.decode()))
        cache.set("ccusage_data", data)
        return data

    except asyncio.TimeoutError:
        print("❌ ccusage command timed out")
        return None
    except Exception as e:
        print(f"❌ Error running ccusage: {e}")
        return None


def get_token_limit(plan: str, blocks: Optional[List[CcusageBlock]] = None) -> int:
    """Get token limit based on plan type (with caching)."""
    # For fixed plans, use cached values
    if plan != "custom_max":
        cache_key = f"token_limit_{plan}"
        cached = cache.get(cache_key)
        if isinstance(cached, (int, float)):
            return int(cached)

        limits = {"pro": 7000, "max5": 35000, "max20": 140000}
        limit = limits.get(plan, 7000)
        cache.set(cache_key, limit)
        return limit

    # For custom_max, calculate from blocks
    if not blocks:
        return 7000

    # Use list comprehension for better performance
    valid_tokens = [
        block.get("totalTokens", 0)
        for block in blocks
        if not block.get("isGap", False) and not block.get("isActive", False)
    ]

    return max(valid_tokens) if valid_tokens else 7000
