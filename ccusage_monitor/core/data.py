"""Consolidated data module with optimized ccusage interaction and caching."""

import asyncio
import json
import shutil
import subprocess
from typing import List, Optional, cast

from ccusage_monitor.core.cache import cache
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


def run_ccusage() -> Optional[CcusageData]:
    """Execute ccusage blocks --json command with result caching."""
    # Check cache first (5 second TTL for ccusage data)
    cached_data = cache.get("ccusage_data", ttl=5)
    if cached_data is not None:
        return cast(Optional[CcusageData], cached_data)

    try:
        # Use PIPE constants for better performance
        result = subprocess.run(
            ["ccusage", "blocks", "--offline", "--json"],
            capture_output=True,
            text=True,
            check=True,
            # Limit execution time
            timeout=10,
        )

        data = cast(CcusageData, json.loads(result.stdout))
        cache.set("ccusage_data", data)
        return data

    except subprocess.TimeoutExpired:
        print("❌ ccusage command timed out")
        return None
    except FileNotFoundError:
        print("❌ ccusage command not found. Please install it with: npm install -g ccusage")
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running ccusage: {e}")
        stderr_str = cast(Optional[str], e.stderr)
        if stderr_str:
            print(f"Error details: {stderr_str}")
        print("\nPossible solutions:")
        print("1. Make sure you're logged into Claude in your browser")
        print("2. Try running 'ccusage login' if authentication is required")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON from ccusage: {e}")
        return None


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
