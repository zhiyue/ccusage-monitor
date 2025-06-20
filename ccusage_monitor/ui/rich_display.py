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
        self._setup_layout()

    def _setup_layout(self):
        """Setup the layout structure."""
        self.layout.split_column(
            Layout(name="header", size=5),
            Layout(name="progress", size=8),
            Layout(name="stats", size=8),
            Layout(name="warnings", size=4),
            Layout(name="status", size=2),
        )

    def create_header(self) -> Panel:
        """Create the header panel."""
        header_text = Text()
        header_text.append("✨ ⭐ ✨ ", style="bold bright_cyan")
        header_text.append("CLAUDE TOKEN MONITOR", style="bold bright_white on dark_blue")
        header_text.append(" ✨ ⭐ ✨", style="bold bright_cyan")

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

        centered_table = Align.center(table)

        return Panel(
            centered_table,
            box=box.ROUNDED,
            border_style="bright_blue",
            title="[bold bright_yellow]📈 Progress Tracking[/]",
            title_align="center",
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

        centered_stats = Align.center(table)

        return Panel(
            centered_stats,
            box=box.ROUNDED,
            border_style="bright_green",
            title="[bold bright_yellow]📊 Statistics[/]",
            title_align="center",
        )

    def create_warnings_panel(self, warnings: List[Tuple[str, str]]) -> Panel:
        """Create warnings panel if needed."""
        if not warnings:
            success_text = Text("✅ All systems running smoothly", style="bold bright_green")
            centered_success = Align.center(success_text)
            return Panel(
                centered_success,
                box=box.ROUNDED,
                border_style="bright_green",
                title="[bold bright_green]🟢 System Status[/]",
                title_align="center",
            )

        warning_text = Text()
        for i, warning in enumerate(warnings):
            if i > 0:
                warning_text.append("\n")
            warning_text.append("⚠️  ", style="bold red")
            warning_text.append(warning[0], style=warning[1])

        centered_warnings = Align.center(warning_text)

        return Panel(
            centered_warnings,
            box=box.ROUNDED,
            border_style="bold red",
            title="[bold red]🚨 Warnings[/]",
            title_align="center",
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

    def display(self, data: DisplayData):
        """Display the complete interface."""
        self.update_display(data)
        self.console.clear()
        self.console.print(self.layout)

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
