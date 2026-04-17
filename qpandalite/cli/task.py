"""Task management subcommand."""

from __future__ import annotations

from typing import Optional

import typer

from .output import console, format_prob, print_error, print_json, print_success, print_table

app = typer.Typer(help="Manage submitted tasks")


@app.command("list")
def list_tasks(
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status: pending/running/success/failed"),
    platform: Optional[str] = typer.Option(None, "--platform", "-p", help="Filter by platform"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of tasks to show"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table/json"),
):
    """List submitted tasks."""
    from qpandalite.task_manager import list_tasks as _list_tasks

    tasks = _list_tasks(status=status, backend=platform)

    if not tasks:
        print_info("No tasks found")
        return

    tasks = tasks[:limit]

    if format == "json":
        print_json([task_to_dict(t) for t in tasks])
    else:
        rows = []
        for task in tasks:
            rows.append(
                [
                    task.task_id,
                    task.backend,
                    task.status,
                    str(task.shots),
                    task.submit_time[:19] if task.submit_time else "N/A",
                ]
            )
        print_table("Tasks", ["Task ID", "Platform", "Status", "Shots", "Submit Time"], rows)


@app.command()
def show(
    task_id: str = typer.Argument(..., help="Task ID to show"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table/json"),
):
    """Show details of a specific task."""
    from qpandalite.task_manager import get_task, query_task

    task_info = get_task(task_id)

    if not task_info:
        task_info = query_task(task_id)

    if not task_info:
        print_error(f"Task {task_id} not found")
        raise typer.Exit(1)

    if format == "json":
        print_json(task_to_dict(task_info))
    else:
        print_table(
            f"Task {task_id}",
            ["Property", "Value"],
            [
                ["Task ID", task_info.task_id],
                ["Backend", task_info.backend],
                ["Status", task_info.status],
                ["Shots", str(task_info.shots)],
                ["Submit Time", task_info.submit_time or "N/A"],
                ["Update Time", task_info.update_time or "N/A"],
            ],
        )

        if task_info.result:
            console.print("\n[bold]Results:[/bold]")
            total = sum(task_info.result.values())
            rows = [
                [state, str(count), format_prob(count / total)]
                for state, count in sorted(task_info.result.items(), key=lambda x: x[1], reverse=True)
            ]
            print_table("Measurement Results", ["State", "Count", "Probability"], rows)


@app.command()
def clear(
    status: Optional[str] = typer.Option(None, "--status", help="Clear tasks with this status"),
    force: bool = typer.Option(False, "--force", help="Force clear without confirmation"),
):
    """Clear completed or failed tasks from cache."""
    from qpandalite.task_manager import clear_completed_tasks, clear_cache

    if status:
        count = clear_completed_tasks()
    else:
        if not force:
            confirm = typer.confirm("Clear all cached tasks?")
            if not confirm:
                print_info("Cancelled")
                return
        count = clear_cache()

    print_success(f"Cleared {count} tasks from cache")


def task_to_dict(task_info) -> dict:
    """Convert TaskInfo to dictionary."""
    return {
        "task_id": task_info.task_id,
        "backend": task_info.backend,
        "status": task_info.status,
        "shots": task_info.shots,
        "submit_time": task_info.submit_time,
        "update_time": task_info.update_time,
        "result": task_info.result,
        "metadata": task_info.metadata,
    }