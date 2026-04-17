"""Result query subcommand."""

from __future__ import annotations

from typing import Optional

import typer

from .output import format_prob, print_error, print_json, print_table

app = typer.Typer(help="Query task results from quantum cloud platforms")


@app.callback(invoke_without_command=True)
def result(
    task_id: str = typer.Argument(..., help="Task ID to query"),
    platform: Optional[str] = typer.Option(None, "--platform", "-p", help="Platform: originq/quafu/ibm"),
    wait: bool = typer.Option(False, "--wait", "-w", help="Wait for task completion"),
    timeout: float = typer.Option(300.0, "--timeout", help="Timeout in seconds"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table/json"),
):
    """Query result of a submitted task."""
    show_result(task_id, platform=platform, wait=wait, timeout=timeout, format=format)


def show_result(
    task_id: str,
    platform: str | None = None,
    wait: bool = False,
    timeout: float = 300.0,
    format: str = "table",
) -> None:
    """Show task result."""
    try:
        if wait:
            result_data = _wait_for_result(task_id, platform, timeout)
        else:
            result_data = _query_result(task_id, platform)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)

    if result_data is None:
        print_error(f"No result available for task {task_id}")
        raise typer.Exit(1)

    if format == "json":
        print_json(result_data)
    else:
        _print_result_table(task_id, result_data)


def _query_result(task_id: str, platform: str | None) -> dict | None:
    """Query task result."""
    if platform == "originq":
        from qpandalite.task.origin_qcloud import task as oq_task

        return oq_task.query_by_taskid(task_id)
    elif platform == "quafu":
        from qpandalite.task.quafu import task as quafu_task

        return quafu_task.query_by_taskid(task_id)
    elif platform == "ibm":
        from qpandalite.task.ibm import task as ibm_task

        return ibm_task.query_by_taskid(task_id)
    else:
        from qpandalite.task_manager import query_task

        task_info = query_task(task_id, backend=platform)
        if task_info and task_info.result:
            return task_info.result
        return None


def _wait_for_result(task_id: str, platform: str | None, timeout: float) -> dict | None:
    """Wait for task result."""
    from qpandalite.task_manager import wait_for_result

    return wait_for_result(task_id, backend=platform, timeout=timeout)


def _print_result_table(task_id: str, result_data: dict) -> None:
    """Print result as a table."""
    print_table(
        f"Result for {task_id}",
        ["State", "Count", "Probability"],
        [
            [state, str(count), format_prob(count / sum(result_data.values()))]
            for state, count in sorted(result_data.items(), key=lambda x: x[1], reverse=True)
        ],
    )
