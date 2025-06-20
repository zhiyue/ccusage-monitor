"""Rich-based display module for beautiful terminal UI."""

from datetime import datetime
from typing import Any, Dict, List, Tuple

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text


class RichDisplay:
    """Rich-based display manager for ccusage monitor."""

    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self._setup_layout()

    def _setup_layout(self):
        """Setup the layout structure."""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="progress", size=7),
            Layout(name="stats", size=6),
            Layout(name="warnings", size=3),
            Layout(name="status", size=1),
        )

    def create_header(self) -> Panel:
        """Create the header panel."""
        header_text = Text()
        header_text.append("✦ ✧ ✦ ✧ ", style="cyan")
        header_text.append("CLAUDE TOKEN MONITOR", style="bold cyan")
        header_text.append(" ✦ ✧ ✦ ✧", style="cyan")

        return Panel(
            header_text,
            box=box.DOUBLE,
            style="cyan",
            expand=False,
        )

    def create_progress_panel(
        self, token_pct: float, time_pct: float, tokens_used: int, token_limit: int, time_remaining: str
    ) -> Panel:
        """Create the progress bars panel."""
        # Token progress bar
        token_progress = Progress(
            TextColumn("[bold]📊 Token Usage:[/]"),
            BarColumn(bar_width=50),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            expand=False,
        )
        token_progress.add_task("tokens", total=100, completed=int(token_pct))

        # Time progress bar
        time_progress = Progress(
            TextColumn("[bold]⏳ Time to Reset:[/]"),
            BarColumn(bar_width=50, complete_style="blue", finished_style="blue"),
            TextColumn(f"{time_remaining}"),
            expand=False,
        )
        time_progress.add_task("time", total=100, completed=int(time_pct))

        # Combine in a table
        table = Table(show_header=False, box=None, padding=(0, 0))
        table.add_row(token_progress)
        table.add_row("")  # Empty row for spacing
        table.add_row(time_progress)

        return Panel(table, box=box.ROUNDED, border_style="dim")

    def create_stats_panel(self, stats: Dict[str, Any]) -> Panel:
        """Create the statistics panel."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="bold white", no_wrap=True)
        table.add_column(style="default")

        # Tokens row
        tokens_text = Text()
        tokens_text.append(f"{stats['tokens_used']:,}", style="bold white")
        tokens_text.append(" / ", style="dim")
        tokens_text.append(f"~{stats['token_limit']:,}", style="dim")
        tokens_text.append(" (", style="dim")
        tokens_text.append(f"{stats['tokens_left']:,} left", style="cyan")
        tokens_text.append(")", style="dim")
        table.add_row("🎯 Tokens:", tokens_text)

        # Burn rate row
        burn_text = Text()
        burn_text.append(f"{stats['burn_rate']:.1f}", style="yellow")
        burn_text.append(" tokens/min", style="dim")
        table.add_row("🔥 Burn Rate:", burn_text)

        table.add_row("", "")  # Empty row

        # Predictions
        table.add_row("🏁 Predicted End:", stats["predicted_end"])
        table.add_row("🔄 Token Reset:", stats["reset_time"])

        return Panel(table, box=box.ROUNDED, border_style="dim")

    def create_warnings_panel(self, warnings: List[Tuple[str, str]]) -> Panel:
        """Create warnings panel if needed."""
        if not warnings:
            return Panel("", box=box.ROUNDED, height=1, border_style="dim")

        warning_text = Text()
        for i, warning in enumerate(warnings):
            if i > 0:
                warning_text.append("\n")
            warning_text.append(warning[0], style=warning[1])

        return Panel(warning_text, box=box.ROUNDED, border_style="red")

    def create_status_bar(self, time_str: str, message: str = "Smooth sailing...") -> Text:
        """Create the status bar."""
        status = Text()
        status.append("⏰ ", style="dim")
        status.append(time_str, style="dim")
        status.append(" 📝 ", style="dim")
        status.append(message, style="cyan")
        status.append(" | ", style="dim")
        status.append("Ctrl+C to exit", style="dim")
        status.append(" 🟨")
        return status

    def update_display(self, data: Dict[str, Any]):
        """Update the entire display with new data."""
        # Update header
        self.layout["header"].update(self.create_header())

        # Update progress
        self.layout["progress"].update(
            self.create_progress_panel(
                data["token_pct"], data["time_pct"], data["tokens_used"], data["token_limit"], data["time_remaining"]
            )
        )

        # Update stats
        self.layout["stats"].update(self.create_stats_panel(data["stats"]))

        # Update warnings
        self.layout["warnings"].update(self.create_warnings_panel(data.get("warnings", [])))

        # Update status
        self.layout["status"].update(
            self.create_status_bar(datetime.now().strftime("%H:%M:%S"), data.get("status_message", "Smooth sailing..."))
        )


def create_rich_display() -> RichDisplay:
    """Create a new Rich display instance."""
    return RichDisplay()
