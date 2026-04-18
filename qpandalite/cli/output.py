"""Output formatting utilities for CLI."""

from __future__ import annotations

import json
import sys
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()
err_console = Console(stderr=True)


def print_table(
    title: str,
    columns: list[str],
    rows: list[list[Any]],
) -> None:
    """Print a rich table to console."""
    table = Table(title=title)
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*[str(v) for v in row])
    console.print(table)


def print_json(data: dict[str, Any] | list[Any]) -> None:
    """Print data as JSON to stdout."""
    console.print(json.dumps(data, indent=2, ensure_ascii=False))


def print_error(message: str) -> None:
    """Print error message to stderr."""
    err_console.print(f"[red]Error:[/red] {message}")


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def format_prob(value: float) -> str:
    """Format probability as percentage string."""
    return f"{value * 100:.1f}%"


def write_output(content: str, output: str | None = None) -> None:
    """Write content to file or stdout."""
    if output:
        with open(output, "w") as f:
            f.write(content)
        print_success(f"Output written to {output}")
    else:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
