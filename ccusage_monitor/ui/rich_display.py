"""Rich-based display module for beautiful terminal UI."""

from datetime import datetime
from typing import List, Tuple, TypedDict

from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text


class StatsData(TypedDict):
    """Type definition for statistics data."""

    tokens_used: int
    token_limit: int
    tokens_left: int
    burn_rate: float
    predicted_end: str
    reset_time: str
    cost_usd: float


class DisplayData(TypedDict):
    """Type definition for display data."""

    token_pct: float
    time_pct: float
    tokens_used: int
    token_limit: int
    time_remaining: str
    stats: StatsData
    warnings: List[Tuple[str, str]]
    status_message: str


class RichDisplay:
    """Rich-based display manager for ccusage monitor."""

    def __init__(self):
        self.console: Console = Console()
        self.layout: Layout = Layout()
        self._trend_data: List[float] = []
        self._setup_layout()

    def _setup_layout(self):
        """Setup the layout structure."""
        self.layout.split_column(
            Layout(name="header", size=5),
            Layout(name="progress", size=8),
            Layout(name="stats", size=10),
            Layout(name="warnings", size=6),  # Increased size to prevent layout shifts
            Layout(name="status", size=2),
        )

    def create_header(self) -> Panel:
        """Create the header panel with subtle animation."""
        import time

        # Create subtle pulsing effect based on current time (slower)
        pulse_phase = int(time.time() / 2) % 2  # Changes every 2 seconds

        header_text = Text()

        if pulse_phase == 0:
            header_text.append("✨ ", style="bold bright_cyan")
            header_text.append("CLAUDE TOKEN MONITOR", style="bold bright_white on blue")
            header_text.append(" ✨", style="bold bright_cyan")
        else:
            header_text.append("⭐ ", style="bold cyan")
            header_text.append("CLAUDE TOKEN MONITOR", style="bold white on bright_blue")
            header_text.append(" ⭐", style="bold cyan")

        centered_header = Align.center(header_text)

        return Panel(
            centered_header,
            box=box.DOUBLE,
            style="bright_blue",
            expand=True,
            title="[bold bright_yellow]🤖 AI Monitor[/]",
            title_align="left",
            subtitle="[dim]Real-time Usage Tracking[/]",
            subtitle_align="right",
        )

    def create_progress_panel(self, token_pct: float, time_pct: float, time_remaining: str) -> Panel:
        """Create the progress bars panel."""
        # Determine token bar color based on usage
        if token_pct < 50:
            token_style = "green"
            token_emoji = "🟢"
        elif token_pct < 80:
            token_style = "yellow"
            token_emoji = "🟡"
        else:
            token_style = "red"
            token_emoji = "🔴"

        # Token progress bar
        token_progress = Progress(
            TextColumn(f"[bold bright_white]{token_emoji} Token Usage:[/]"),
            BarColumn(
                bar_width=50,
                complete_style=f"bold {token_style}",
                finished_style=f"bold {token_style}",
            ),
            TextColumn("[progress.percentage][bold bright_white]{task.percentage:>3.1f}%[/]"),
            expand=False,
        )
        token_progress.add_task("tokens", total=100, completed=int(token_pct))

        # Time progress bar
        time_progress = Progress(
            TextColumn("[bold bright_white]⏰ Time to Reset:[/]"),
            BarColumn(
                bar_width=50,
                complete_style="bold bright_blue",
                finished_style="bold bright_blue",
                pulse_style="bold cyan",
            ),
            TextColumn(f"[bold bright_cyan]{time_remaining}[/]"),
            expand=False,
        )
        time_progress.add_task("time", total=100, completed=int(time_pct))

        # Combine in a table with better spacing
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row(token_progress)
        table.add_row("")  # Empty row for spacing
        table.add_row(time_progress)

        # Don't center table to maintain consistent layout
        return Panel(
            table,
            box=box.ROUNDED,
            border_style="bright_blue",
            title="[bold bright_yellow]📈 Progress Tracking[/]",
            title_align="center",
            padding=(0, 2),  # Add horizontal padding
        )

    def create_stats_panel(self, stats: StatsData) -> Panel:
        """Create the statistics panel."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="bold bright_white", no_wrap=True, width=20)
        table.add_column(style="default")

        # Tokens row with enhanced styling
        tokens_text = Text()
        tokens_text.append(f"{stats['tokens_used']:,}", style="bold bright_green")
        tokens_text.append(" / ", style="dim white")
        tokens_text.append(f"~{stats['token_limit']:,}", style="bold bright_blue")
        tokens_text.append(" (", style="dim white")
        tokens_text.append(f"{stats['tokens_left']:,} left", style="bold bright_cyan")
        tokens_text.append(")", style="dim white")
        table.add_row("🎯 Tokens:", tokens_text)

        # Burn rate row with color coding
        burn_text = Text()
        if stats["burn_rate"] > 100:
            burn_style = "bold red"
            burn_emoji = "🚨"
        elif stats["burn_rate"] > 50:
            burn_style = "bold yellow"
            burn_emoji = "⚡"
        else:
            burn_style = "bold green"
            burn_emoji = "🔥"

        burn_text.append(f"{stats['burn_rate']:.1f}", style=burn_style)
        burn_text.append(" tokens/min", style="dim white")
        table.add_row(f"{burn_emoji} Burn Rate:", burn_text)

        table.add_row("", "")  # Empty row for spacing

        # Predictions with enhanced styling
        pred_text = Text(stats["predicted_end"], style="bold bright_magenta")
        table.add_row("🏁 Predicted End:", pred_text)

        reset_text = Text(stats["reset_time"], style="bold bright_yellow")
        table.add_row("🔄 Token Reset:", reset_text)

        table.add_row("", "")  # Empty row for spacing

        # Session cost
        cost_text = Text()
        if stats["cost_usd"] > 10:
            cost_style = "bold red"
            cost_emoji = "💳"
        elif stats["cost_usd"] > 1:
            cost_style = "bold yellow"
            cost_emoji = "💸"
        else:
            cost_style = "bold green"
            cost_emoji = "💰"

        cost_text.append(f"${stats['cost_usd']:.2f}", style=cost_style)
        cost_text.append(" this 5hr window", style="dim white")
        table.add_row(f"{cost_emoji} Cost:", cost_text)

        # Don't center stats to maintain consistent layout
        return Panel(
            table,
            box=box.ROUNDED,
            border_style="bright_green",
            title="[bold bright_yellow]📊 Token Statistics[/]",
            title_align="center",
            padding=(0, 2),  # Add horizontal padding
        )

    def create_warnings_panel(self, warnings: List[Tuple[str, str]]) -> Panel:
        """Create warnings panel with fixed height."""
        warning_lines: List[Text] = []

        if not warnings:
            warning_lines.append(Text("✅ All systems running smoothly", style="bold bright_green"))
            border_style = "bright_green"
            title = "[bold bright_green]🟢 System Status[/]"
        else:
            for warning in warnings[:3]:  # Limit to 3 warnings to prevent overflow
                line = Text()
                line.append("⚠️  ", style="bold red")
                line.append(warning[0], style=warning[1])
                warning_lines.append(line)
            border_style = "bold red"
            title = "[bold red]🚨 Warnings[/]"

        # Pad with empty lines to maintain consistent height
        while len(warning_lines) < 3:
            warning_lines.append(Text(""))

        # Join all lines with newlines
        content = Text()
        for i, line in enumerate(warning_lines):
            if i > 0:
                content.append("\n")
            content.append(line)

        return Panel(
            content,
            box=box.ROUNDED,
            border_style=border_style,
            title=title,
            title_align="center",
            padding=(0, 2),  # Add horizontal padding
            height=6,  # Fixed height to match layout
        )

    def create_status_bar(self, time_str: str, message: str = "Smooth sailing...") -> Align:
        """Create the status bar."""
        status = Text()
        status.append("⏰ ", style="bold bright_blue")
        status.append(time_str, style="bold bright_white")
        status.append(" │ ", style="dim white")
        status.append("📝 ", style="bold bright_green")
        status.append(message, style="bold bright_cyan")
        status.append(" │ ", style="dim white")
        status.append("Press ", style="dim white")
        status.append("Ctrl+C", style="bold red")
        status.append(" to exit", style="dim white")
        status.append(" ✨", style="bright_yellow")

        return Align.center(status)

    def create_mini_chart(self, data_points: List[float], width: int = 20) -> Text:
        """Create a simple mini chart using unicode characters."""
        if not data_points or len(data_points) < 2:
            return Text("📊 No data", style="dim")

        # Normalize data to 0-8 range for unicode blocks
        max_val = max(data_points)
        min_val = min(data_points)

        if max_val == min_val:
            # All values are the same
            chart_text = Text()
            chart_text.append("▄" * width, style="cyan")
            return chart_text

        # Unicode block characters for different heights
        blocks = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

        chart_text = Text()

        # Sample data points to fit the width
        if len(data_points) > width:
            # Take evenly spaced samples
            step = len(data_points) / width
            sampled_points = [data_points[int(i * step)] for i in range(width)]
        else:
            # Pad with the last value or repeat
            sampled_points = data_points + [data_points[-1]] * (width - len(data_points))

        for point in sampled_points:
            # Normalize to 0-8 range
            normalized = (point - min_val) / (max_val - min_val) * 8
            block_index = min(8, int(normalized))

            # Color based on value
            if normalized > 6:
                style = "red"
            elif normalized > 4:
                style = "yellow"
            else:
                style = "green"

            chart_text.append(blocks[block_index], style=style)

        return chart_text

    def update_trend_data(self, hourly_usage: List[float]):
        """Update trend data for mini charts."""
        self._trend_data = hourly_usage[-24:]  # Keep last 24 hours

    def display(self, data: DisplayData):
        """Display the complete interface."""
        self.update_display(data)
        # Note: console.clear() removed - Live handles screen updates

    def update_display(self, data: DisplayData):
        """Update the entire display with new data."""
        # Update header
        self.layout["header"].update(self.create_header())

        # Update progress
        self.layout["progress"].update(
            self.create_progress_panel(data["token_pct"], data["time_pct"], data["time_remaining"])
        )

        # Update stats
        self.layout["stats"].update(self.create_stats_panel(data["stats"]))

        # Update warnings
        self.layout["warnings"].update(self.create_warnings_panel(data["warnings"]))

        # Update status
        self.layout["status"].update(
            self.create_status_bar(datetime.now().strftime("%H:%M:%S"), data["status_message"])
        )


def create_rich_display() -> RichDisplay:
    """Create a new Rich display instance."""
    return RichDisplay()
