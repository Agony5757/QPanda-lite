"""Demo tests using the unified task API."""

import math

import pytest

import qpandalite
from qpandalite import Circuit, submit_task, wait_for_result, calculate_expectation

from qpandalite.test._utils import qpandalite_test


def _check_simulation_available():
    """Check if simulation dependencies are available."""
    try:
        from qpandalite.task.optional_deps import SIMULATION_AVAILABLE
        return SIMULATION_AVAILABLE
    except ImportError:
        return False


SIMULATION_AVAILABLE = _check_simulation_available()


def _build_circuit():
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
    """Demo 2: Submit task using dummy mode."""
    if not SIMULATION_AVAILABLE:
        pytest.skip("Simulation dependencies (qutip) not available")
        return

    circuit = _build_circuit()

    # Submit with dummy=True for local simulation
    task_id = submit_task(circuit, backend='originq', shots=1000, dummy=True)
    print(f"Task ID: {task_id}")

    # Wait for result (immediate for dummy mode)
    result = wait_for_result(task_id, backend='originq', timeout=60)

    if result:
        print(f"Counts: {result.get('counts', {})}")
        print(f"Probabilities: {result.get('probabilities', {})}")


def demo_3():
    """Demo 3: Result post-processing with expectation values."""
    if not SIMULATION_AVAILABLE:
        pytest.skip("Simulation dependencies (qutip) not available")
        return

    circuit = _build_circuit()

    # Submit with dummy mode
    task_id = submit_task(circuit, backend='originq', shots=1000, dummy=True)
    result = wait_for_result(task_id, backend='originq', timeout=60)

    if result:
        probs = result.get('probabilities', {})
        print(f"Probabilities: {probs}")

        # Calculate expectation values using probabilities
        if probs:
            exps = [
                calculate_expectation(probs, h)
                for h in ['ZII', 'IIZ']
            ]
            print(f"<ZII> = {exps[0]}")
            print(f"<IIZ> = {exps[1]}")


@qpandalite_test('Test Demos')
def run_test_demos():
    demo_2()
    demo_3()


if __name__ == '__main__':
    run_test_demos()
