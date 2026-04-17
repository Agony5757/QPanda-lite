"""Circuit format conversion subcommand."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .output import console, print_error, print_info, print_table, write_output

app = typer.Typer(help="Circuit format conversion (OriginIR <-> QASM)")


def _detect_format(content: str) -> str:
    """Detect circuit format from content."""
    stripped = content.strip()
    if stripped.startswith("QINIT") or "ORIGINIR" in stripped.upper():
        return "originir"
    if stripped.startswith("OPENQASM") or "qelib1.inc" in stripped:
        return "qasm"
    return "unknown"


@app.callback(invoke_without_command=True)
def convert(
    input_file: Path = typer.Argument(..., help="Input circuit file (OriginIR or QASM)", exists=True),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: originir/qasm"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file (default: stdout)"),
    info: bool = typer.Option(False, "--info", help="Show circuit statistics"),
):
    """Convert circuit between OriginIR and QASM formats."""
    content = input_file.read_text(encoding="utf-8")
    source_format = _detect_format(content)

    if source_format == "unknown":
        print_error(f"Cannot detect format of {input_file}. Use --format to specify.")
        raise typer.Exit(1)

    if format is None:
        format = "qasm" if source_format == "originir" else "originir"

    if format == source_format:
        print_error(f"Input is already in {format} format. Specify a different --format.")
        raise typer.Exit(1)

    if source_format == "originir" and format == "qasm":
        result_content = _originir_to_qasm(content)
    elif source_format == "qasm" and format == "originir":
        result_content = _qasm_to_originir(content)
    else:
        print_error(f"Unsupported conversion: {source_format} -> {format}")
        raise typer.Exit(1)

    if info:
        _print_info(content, source_format)

    write_output(result_content, str(output) if output else None)


def _originir_to_qasm(originir: str) -> str:
    """Convert OriginIR to QASM."""
    from qpandalite.originir import OriginIR_BaseParser

    parser = OriginIR_BaseParser()
    parser.parse(originir)
    return parser.to_qasm()


def _qasm_to_originir(qasm: str) -> str:
    """Convert QASM to OriginIR."""
    from qpandalite.qasm import QASM_Parser

    parser = QASM_Parser()
    parser.parse(qasm)
    return parser.originir


def _print_info(content: str, fmt: str) -> None:
    """Print circuit statistics."""
    if fmt == "originir":
        from qpandalite.originir import OriginIR_BaseParser

        parser = OriginIR_BaseParser()
        parser.parse(content)
        circuit = parser.to_circuit()
    else:
        from qpandalite.qasm import QASM_Parser

        parser = QASM_Parser()
        parser.parse(content)
        circuit = parser.to_circuit()

    print_table(
        "Circuit Info",
        ["Property", "Value"],
        [
            ["Qubits", str(circuit.qubit_num)],
            ["Cbits", str(circuit.cbit_num)],
            ["Depth", str(circuit.depth)],
            ["Gates", str(len(circuit.opcodes))],
        ],
    )
