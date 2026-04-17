"""Main CLI entry point for QPanda-lite."""

from __future__ import annotations

import typer

app = typer.Typer(
    name="qpandalite",
    help="QPanda-lite - A lightweight quantum computing framework",
    no_args_is_help=True,
)


@app.callback()
def main():
    """QPanda-lite CLI - Quantum computing from the command line."""
    pass


# Import and register subcommands
from . import circuit
from . import simulate
from . import submit
from . import result
from . import config_cmd as config
from . import task

app.add_typer(circuit.app, name="circuit")
app.add_typer(simulate.app, name="simulate")
app.add_typer(submit.app, name="submit")
app.add_typer(result.app, name="result")
app.add_typer(config.app, name="config")
app.add_typer(task.app, name="task")
