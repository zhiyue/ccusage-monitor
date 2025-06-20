"""Protocols for type-hinting dynamic modules."""

from datetime import datetime
from typing import List, Optional, Protocol, TypedDict, Union


class CcusageBlock(TypedDict, total=False):
    """Represents a single block from the ccusage tool."""

    isActive: bool
    totalTokens: int
    startTime: str
    isGap: bool
    actualEndTime: str


class CcusageData(TypedDict):
    """Represents the top-level structure of data from ccusage."""

    blocks: List[CcusageBlock]


class DisplayValues(TypedDict):
    """Strongly typed dictionary for display values."""

    usage_percentage: float
    tokens_used_fmt: str
    token_limit_fmt: str
    tokens_left_fmt: str
    burn_rate_fmt: str
    predicted_end_str: str
    reset_time_str: str
    velocity_indicator: str
    tokens_left: int


class DisplayProtocol(Protocol):
    """A protocol for display modules to ensure type safety."""

    def print_header(self) -> None: ...

    def create_token_progress_bar(self, percentage: float, width: int = 50) -> str: ...

    def create_time_progress_bar(
        self, elapsed_minutes: Union[float, int], total_minutes: Union[float, int], width: int = 50
    ) -> str: ...

    def clear_screen(self) -> None: ...

    def hide_cursor(self) -> None: ...

    def show_cursor(self) -> None: ...

    def writeln(self, text: str = "") -> None: ...

    def flush_buffer(self) -> None: ...


class DataProtocol(Protocol):
    """A protocol for data modules to ensure type safety."""

    def check_ccusage_installed(self) -> bool: ...

    def run_ccusage(self) -> Optional[CcusageData]: ...

    def get_token_limit(self, plan: str, blocks: Optional[List[CcusageBlock]] = None) -> int: ...


class CalculationsProtocol(Protocol):
    """A protocol for calculations modules to ensure type safety."""

    def calculate_hourly_burn_rate(self, blocks: List[CcusageBlock], current_time: datetime) -> float: ...

    def get_next_reset_time(
        self, current_time: datetime, custom_reset_hour: Optional[int] = None, timezone_str: str = "Europe/Warsaw"
    ) -> datetime: ...

    def get_velocity_indicator(self, burn_rate: float) -> str: ...


class CLIArgs:
    """Type definition for command-line arguments."""

    plan: str = "pro"
    reset_hour: Optional[int] = None
    timezone: str = "Europe/Warsaw"
    performance: bool = False
    rich: bool = False
    refresh: int = 3
