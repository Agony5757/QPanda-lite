'''This is the demo for QPanda-lite

# 3. Result Post-Processing

## Concepts:

    UnifiedResult: QPanda-lite normalizes results from all platforms into
    a unified format with counts and probabilities.

    Expectation values: The analyzer module provides functions to compute
    expectation values of Pauli operators from measurement results.

'''

import math
from qpandalite import (
    Circuit,
    submit_task,
    wait_for_result,
    calculate_expectation,
    shots2prob,
)


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


def demo_3():
    """Demonstrate result post-processing."""
    circuit = build_circuit()

    # Submit task with dummy mode
    task_id = submit_task(circuit, backend='originq', shots=1000, dummy=True)

    # Wait for result
    result = wait_for_result(task_id, backend='originq', timeout=60)

    if result:
        print(f"Counts: {result.get('counts', {})}")
        print(f"Probabilities: {result.get('probabilities', {})}")

        # Calculate expectation values using probabilities
        probs = result.get('probabilities', {})
        if probs:
            # Calculate <ZII> and <IIZ> expectation values
            exp_zii = calculate_expectation(probs, 'ZII')
            exp_iiz = calculate_expectation(probs, 'IIZ')
            print(f"<ZII> = {exp_zii}")
            print(f"<IIZ> = {exp_iiz}")

        # Convert counts to probabilities manually
        counts = result.get('counts', {})
        if counts:
            prob_dist = shots2prob(counts)
            print(f"Manual probability conversion: {prob_dist}")


if __name__ == '__main__':
    demo_3()
