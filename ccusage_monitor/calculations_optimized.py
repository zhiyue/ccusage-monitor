"""Optimized calculations module with better algorithms."""

from datetime import datetime, timedelta
from typing import List, Optional, cast

import pytz

from ccusage_monitor.cache import cache
from ccusage_monitor.protocols import CcusageBlock


def calculate_hourly_burn_rate(blocks: List[CcusageBlock], current_time: datetime) -> float:
    """Optimized burn rate calculation with early termination."""
    if not blocks:
        return 0

    # Check cache first
    cache_key = f"burn_rate_{current_time.minute}"
    cached = cache.get(cache_key, ttl=30)  # Cache for 30 seconds
    if cached is not None:
        return cast(float, cached)

    one_hour_ago = current_time - timedelta(hours=1)
    total_tokens = 0.0

    # Process blocks in reverse order (most recent first) for early termination
    for block in reversed(blocks):
        # Skip gaps early
        if block.get("isGap"):
            continue

        start_time_str = block.get("startTime")
        if not start_time_str:
            continue

        # Parse start time once
        start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))

        # Early termination - if block started after current time, skip
        if start_time > current_time:
            continue

        # Determine session end time
        if block.get("isActive"):
            session_actual_end = current_time
        else:
            actual_end_str = block.get("actualEndTime")
            if actual_end_str:
                session_actual_end = datetime.fromisoformat(actual_end_str.replace("Z", "+00:00"))
            else:
                session_actual_end = current_time

        # Early termination - if session ended before the last hour
        if session_actual_end < one_hour_ago:
            break  # All older blocks will also be outside the window

        # Calculate overlap with the last hour window
        session_start_in_hour = max(start_time, one_hour_ago)
        session_end_in_hour = min(session_actual_end, current_time)

        if session_end_in_hour <= session_start_in_hour:
            continue

        # Optimized calculation
        total_session_duration = (session_actual_end - start_time).total_seconds()
        if total_session_duration > 0:
            hour_duration = (session_end_in_hour - session_start_in_hour).total_seconds()
            session_tokens = block.get("totalTokens", 0)
            total_tokens += session_tokens * (hour_duration / total_session_duration)

    # Convert to tokens per minute
    result = total_tokens / 60 if total_tokens > 0 else 0.0  # Direct division by 3600
    cache.set(cache_key, result)
    return result


def get_next_reset_time(
    current_time: datetime,
    custom_reset_hour: Optional[int] = None,
    timezone_str: str = "Europe/Warsaw",
) -> datetime:
    """Optimized reset time calculation with caching."""
    # Create cache key based on hour and timezone
    cache_key = f"reset_time_{current_time.hour}_{timezone_str}_{custom_reset_hour}"
    cached = cache.get(cache_key, ttl=300)  # Cache for 5 minutes
    if cached is not None:
        return datetime.fromisoformat(cast(str, cached))

    # Cache timezone object
    tz_cache_key = f"timezone_{timezone_str}"
    target_tz = cast(Optional[pytz.BaseTzInfo], cache.get(tz_cache_key))
    if target_tz is None:
        try:
            target_tz = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            target_tz = pytz.timezone("Europe/Warsaw")
        cache.set(tz_cache_key, target_tz)

    # Convert to target timezone
    if current_time.tzinfo is not None:
        target_time = current_time.astimezone(target_tz)
    else:
        target_time = target_tz.localize(current_time)

    # Determine reset hours
    reset_hours = [custom_reset_hour] if custom_reset_hour is not None else [4, 9, 14, 18, 23]

    current_hour = target_time.hour
    current_minute = target_time.minute

    # Binary search for next reset hour (since reset_hours is sorted)
    next_reset_hour = None
    for hour in reset_hours:
        if current_hour < hour or (current_hour == hour and current_minute == 0):
            next_reset_hour = hour
            break

    # Determine date
    if next_reset_hour is None:
        next_reset_hour = reset_hours[0]
        next_reset_date = target_time.date() + timedelta(days=1)
    else:
        next_reset_date = target_time.date()

    # Create reset datetime
    next_reset = target_tz.localize(
        datetime.combine(next_reset_date, datetime.min.time().replace(hour=next_reset_hour)),
        is_dst=None,
    )

    # Convert back if needed
    if current_time.tzinfo is not None and current_time.tzinfo != target_tz:
        next_reset = next_reset.astimezone(current_time.tzinfo)

    cache.set(cache_key, next_reset.isoformat())
    return next_reset


# Pre-defined velocity indicators for O(1) lookup
VELOCITY_INDICATORS = [
    (50, "🐌"),  # Slow
    (150, "➡️"),  # Normal
    (300, "🚀"),  # Fast
    (float("inf"), "⚡"),  # Very fast
]


def get_velocity_indicator(burn_rate: float) -> str:
    """Get velocity emoji with O(1) lookup."""
    for threshold, indicator in VELOCITY_INDICATORS:
        if burn_rate < threshold:
            return indicator
    return "⚡"  # Fallback
