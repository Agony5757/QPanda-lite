'''This is the demo for QPanda-lite

# 2. Run in Dummy Mode

## Concepts:

    Dummy mode: a mode that produces locally simulated results instead of
    sending them to real quantum cloud platforms. This is used to test
    your program before real task submission.

## Unified API

    QPanda-lite provides a unified interface for submitting tasks to
    different quantum backends (OriginQ, Quafu, IBM). Simply change the
    'backend' parameter to switch platforms.

## Enabling Dummy Mode

    There are three ways to enable dummy mode:

    1. Environment variable: export QPANDALITE_DUMMY=true
    2. Code: os.environ['QPANDALITE_DUMMY'] = 'true'
    3. Per-task: submit_task(..., dummy=True)

'''

import math
import os
from qpandalite import Circuit, submit_task, wait_for_result, query_task


def build_circuit():
    """Build a simple quantum circuit."""
    c = Circuit()
    c.x(0)
    c.rx(1, math.pi)
    c.ry(2, math.pi / 2)
    c.cnot(2, 3)
    c.cz(1, 2)
    c.measure(0, 1, 2)
    return c


def demo_2():
    """Demonstrate dummy mode task submission."""
    # Build circuit
    circuit = build_circuit()

    # Submit task with dummy=True for local simulation
    # This works without any real cloud platform configuration
    task_id = submit_task(
        circuit,
        backend='originq',
        shots=1000,
        dummy=True
    )

    print(f"Task ID: {task_id}")

    # Wait for result (immediate for dummy mode)
    result = wait_for_result(task_id, backend='originq', timeout=60)

    if result:
        print(f"Status: success")
        print(f"Counts: {result.get('counts', {})}")
        print(f"Probabilities: {result.get('probabilities', {})}")
    else:
        print("Task did not complete")

    # Query task status
    task_info = query_task(task_id, backend='originq')
    print(f"Task status: {task_info.status}")


def demo_2_env():
    """Demonstrate dummy mode via environment variable."""
    # Enable dummy mode globally
    os.environ['QPANDALITE_DUMMY'] = 'true'

    circuit = build_circuit()

    # All submissions will use local simulation
    task_id = submit_task(circuit, backend='originq', shots=1000)
    result = wait_for_result(task_id, backend='originq')

    print(f"Result: {result}")


if __name__ == '__main__':
    demo_2()
