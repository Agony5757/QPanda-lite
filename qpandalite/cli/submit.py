"""Cloud task submission subcommand."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .output import console, print_error, print_json, print_success, print_table

app = typer.Typer(help="Submit circuits to quantum cloud platforms")


@app.callback(invoke_without_command=True)
def submit(
    input_files: list[Path] = typer.Argument(..., help="Circuit file(s) to submit", exists=True),
    platform: str = typer.Option(..., "--platform", "-p", help="Platform: originq/quafu/ibm/dummy"),
    chip_id: Optional[str] = typer.Option(None, "--chip-id", help="Chip ID for the target platform"),
    shots: int = typer.Option(1000, "--shots", "-s", help="Number of measurement shots"),
    name: Optional[str] = typer.Option(None, "--name", help="Task name"),
    wait: bool = typer.Option(False, "--wait", "-w", help="Wait for result after submission"),
    timeout: float = typer.Option(300.0, "--timeout", help="Timeout in seconds when waiting"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table/json"),
):
    """Submit circuit(s) to a quantum cloud platform."""
    if platform not in ("originq", "quafu", "ibm", "dummy"):
        print_error(f"Unknown platform: {platform}. Use originq/quafu/ibm/dummy.")
        raise typer.Exit(1)

    circuits = []
    for path in input_files:
        circuits.append(path.read_text(encoding="utf-8"))

    try:
        if len(circuits) == 1:
            task_id = _submit_single(circuits[0], platform, chip_id, shots, name)
            if format == "json":
                print_json({"task_id": task_id, "platform": platform, "shots": shots})
            else:
                print_success(f"Task submitted: {task_id}")
        else:
            task_ids = _submit_batch(circuits, platform, chip_id, shots, name)
            if format == "json":
                print_json({"task_ids": task_ids, "platform": platform, "shots": shots})
            else:
                print_table(
                    "Submitted Tasks",
                    ["#", "Task ID"],
                    [[str(i + 1), tid] for i, tid in enumerate(task_ids)],
                )
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)

    if wait and len(circuits) == 1:
        _wait_and_show(task_id, platform, timeout, format)


def _submit_single(circuit: str, platform: str, chip_id: str | None, shots: int, name: str | None) -> str:
    """Submit a single circuit."""
    if platform == "dummy":
        from qpandalite.task.originq_dummy import task as dummy_task

        return dummy_task.submit_task(circuit, shots=shots)
    elif platform == "originq":
        from qpandalite.task.origin_qcloud import task as oq_task

        kwargs = {"shots": shots}
        if chip_id:
            kwargs["chip_id"] = int(chip_id)
        if name:
            kwargs["task_name"] = name
        return oq_task.submit_task(circuit, **kwargs)
    elif platform == "quafu":
        from qpandalite.task.quafu import task as quafu_task

        kwargs = {"shots": shots}
        if chip_id:
            kwargs["chip_id"] = chip_id
        return quafu_task.submit_task(circuit, **kwargs)
    elif platform == "ibm":
        from qpandalite.task.ibm import task as ibm_task

        kwargs = {"shots": shots}
        if chip_id:
            kwargs["chip_id"] = chip_id
        return ibm_task.submit_task(circuit, **kwargs)
    raise ValueError(f"Unsupported platform: {platform}")


def _submit_batch(circuits: list[str], platform: str, chip_id: str | None, shots: int, name: str | None) -> list[str]:
    """Submit multiple circuits."""
    if platform == "dummy":
        from qpandalite.task.originq_dummy import task as dummy_task

        return [dummy_task.submit_task(c, shots=shots) for c in circuits]
    elif platform == "originq":
        from qpandalite.task.origin_qcloud import task as oq_task

        result = oq_task.submit_task(circuits, shots=shots, **({"chip_id": int(chip_id)} if chip_id else {}))
        return result if isinstance(result, list) else [result]
    elif platform == "quafu":
        from qpandalite.task.quafu import task as quafu_task

        result = quafu_task.submit_task(circuits, shots=shots, **({"chip_id": chip_id} if chip_id else {}))
        return result if isinstance(result, list) else [result]
    raise ValueError(f"Batch submission not supported for platform: {platform}")


def _wait_and_show(task_id: str, platform: str, timeout: float, format: str) -> None:
    """Wait for task result and display it."""
    from .result import show_result

    show_result(task_id, platform=platform, wait=True, timeout=timeout, format=format)
