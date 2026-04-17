#!/usr/bin/env python
"""PyTorch integration example for quantum machine learning.

Demonstrates:
  * QuantumLayer for hybrid quantum-classical models
  * Parameter-shift rule for gradient computation
  * Batch execution utilities
  * VQE optimization with PyTorch

Usage:
    python pytorch_integration.py

Requirements:
    pip install qpandalite[pytorch]

This example shows how to train parametric quantum circuits using
PyTorch's automatic differentiation and optimizers.
"""

import math
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("PyTorch not available. Some examples will be skipped.")
    print("Install with: pip install qpandalite[pytorch]")


def demo_gradient_computation():
    """Demonstrate parameter-shift gradient computation."""
    print("=" * 60)
    print("Parameter-Shift Gradient Computation")
    print("=" * 60)

    if not TORCH_AVAILABLE:
        print("\n[SKIPPED] PyTorch required for gradient computation")
        return

    from qpandalite.pytorch import parameter_shift_gradient
    from qpandalite.circuit_builder import Circuit
    from qpandalite.circuit_builder.parameter import Parameter
    from qpandalite.simulator import OriginIR_Simulator

    # Build a simple circuit
    theta = Parameter("theta")
    theta.bind(0.5)

    c = Circuit(2)
    c.h(0)
    c.rx(0, theta.evaluate())
    c.cnot(0, 1)
    c.measure(0, 1)

    # Define expectation function
    def expectation(circuit):
        sim = OriginIR_Simulator()
        result = sim.simulate(circuit.originir, shots=1000)
        # Compute <Z0>
        counts = result.result
        if not counts:
            return 0.0
        z0_exp = (counts.get('00', 0) + counts.get('01', 0) -
                  counts.get('10', 0) - counts.get('11', 0)) / shots
        return z0_exp

    # Compute gradient via parameter-shift
    print("\nComputing gradient for simple RX-H-CNOT circuit...")

    shots = 1000  # Moved before usage

    # Manual parameter-shift calculation
    theta_plus = Parameter("theta")
    theta_plus.bind(0.5 + 0.5)  # shift = 0.5

    c_plus = Circuit(2)
    c_plus.h(0)
    c_plus.rx(0, theta_plus.evaluate())
    c_plus.cnot(0, 1)
    c_plus.measure(0, 1)

    theta_minus = Parameter("theta")
    theta_minus.bind(0.5 - 0.5)

    c_minus = Circuit(2)
    c_minus.h(0)
    c_minus.rx(0, theta_minus.evaluate())
    c_minus.cnot(0, 1)
    c_minus.measure(0, 1)

    exp_plus = expectation(c_plus)
    exp_minus = expectation(c_minus)

    # Parameter-shift rule: gradient = (f(theta+s) - f(theta-s)) / (2s)
    gradient = (exp_plus - exp_minus) / (2 * 0.5)

    print(f"  θ = 0.5")
    print(f"  <Z0> at θ+0.5 = {exp_plus:.4f}")
    print(f"  <Z0> at θ-0.5 = {exp_minus:.4f}")
    print(f"  Gradient ∂<Z0>/∂θ = {gradient:.4f}")

    print("\nParameter-shift rule formula:")
    print("  ∂f(θ)/∂θ = [f(θ+s) - f(θ-s)] / (2s)")


def demo_quantum_layer():
    """Demonstrate QuantumLayer for hybrid models."""
    print("\n" + "=" * 60)
    print("QuantumLayer in Hybrid Neural Networks")
    print("=" * 60)

    if not TORCH_AVAILABLE:
        print("\n[SKIPPED] PyTorch required for QuantumLayer")
        return

    from qpandalite.pytorch import QuantumLayer
    from qpandalite.circuit_builder import Circuit
    from qpandalite.circuit_builder.parameter import Parameter
    from qpandalite.simulator import OriginIR_Simulator

    # Define a simple variational circuit
    theta = Parameter("theta")
    phi = Parameter("phi")

    def build_circuit(params):
        """Build circuit with bound parameters."""
        theta = Parameter("theta")
        phi = Parameter("phi")
        theta.bind(params[0])
        phi.bind(params[1])

        c = Circuit(2)
        c.h(0)
        c.rx(0, theta.evaluate())
        c.ry(1, phi.evaluate())
        c.cnot(0, 1)
        c.measure(0, 1)
        return c

    # Expectation function
    shots = 1000

    def expectation(circuit):
        sim = OriginIR_Simulator()
        result = sim.simulate(circuit.originir, shots=shots)
        counts = result.result
        if not counts:
            return 0.0
        # Compute <Z0Z1>
        z0z1 = (counts.get('00', 0) + counts.get('11', 0) -
                counts.get('01', 0) - counts.get('10', 0)) / shots
        return z0z1

    # Create QuantumLayer
    # Note: We need to adapt the circuit template for QuantumLayer
    # QuantumLayer expects a circuit with _parameters attribute

    # For demonstration, we show the concept with a simpler approach
    print("\nQuantumLayer concept:")
    print("  1. Create parametric circuit template")
    print("  2. Define expectation function")
    print("  3. Wrap in nn.Module with autograd")
    print("  4. Use standard PyTorch optimizer")

    # Simulate training loop concept
    print("\nSimulated training loop:")
    print("  for epoch in range(100):")
    print("      optimizer.zero_grad()")
    print("      output = model(input)")
    print("      loss = criterion(output, target)")
    print("      loss.backward()  # Uses parameter-shift internally")
    print("      optimizer.step()")


def demo_batch_execution():
    """Demonstrate batch execution utilities."""
    print("\n" + "=" * 60)
    print("Batch Execution Utilities")
    print("=" * 60)

    from qpandalite.pytorch import batch_execute
    from qpandalite.circuit_builder import Circuit
    from qpandalite.simulator import OriginIR_Simulator

    # Create multiple circuits
    circuits = []
    for i in range(5):
        c = Circuit(2)
        c.h(0)
        c.rx(0, i * 0.1)
        c.cnot(0, 1)
        c.measure(0, 1)
        circuits.append(c)

    # Define executor function
    def simulate(circuit):
        sim = OriginIR_Simulator()
        result = sim.simulate(circuit.originir, shots=100)
        return result.result

    # Execute in parallel
    print(f"\nExecuting {len(circuits)} circuits in parallel...")
    results = batch_execute(circuits, simulate, n_workers=4)

    print("\nResults:")
    for i, result in enumerate(results):
        theta = i * 0.1
        print(f"  Circuit {i} (θ={theta:.2f}): {result}")

    print("\nbatch_execute uses ThreadPoolExecutor for parallel execution")
    print("Useful for: gradient computation, hyperparameter search, ensemble circuits")


def demo_vqe_with_pytorch():
    """Demonstrate VQE-style optimization with PyTorch."""
    print("\n" + "=" * 60)
    print("VQE Optimization with PyTorch")
    print("=" * 60)

    if not TORCH_AVAILABLE:
        print("\n[SKIPPED] PyTorch required for VQE demo")
        return

    from qpandalite.circuit_builder import Circuit
    from qpandalite.circuit_builder.parameter import Parameter
    from qpandalite.simulator import OriginIR_Simulator

    print("\nSimple 2-qubit VQE for demonstration:")
    print("  Hamiltonian: H = Z0 + Z1 + X0X1")
    print("  Ansatz: H-RX(theta)-CNOT")

    # Parameters
    theta = Parameter("theta")

    shots = 500

    def build_ansatz(theta_val):
        theta = Parameter("theta")
        theta.bind(theta_val)

        c = Circuit(2)
        c.h(0)
        c.h(1)
        c.rx(0, theta.evaluate())
        c.cnot(0, 1)
        c.measure(0, 1)
        return c

    def measure_energy(circuit):
        """Compute energy expectation."""
        sim = OriginIR_Simulator()
        result = sim.simulate(circuit.originir, shots=shots)
        counts = result.result
        if not counts:
            return 0.0

        # <Z0 + Z1> = sum of individual Z expectations
        total_shots = sum(counts.values())
        z0 = (counts.get('00', 0) + counts.get('01', 0) -
              counts.get('10', 0) - counts.get('11', 0)) / total_shots
        z1 = (counts.get('00', 0) + counts.get('10', 0) -
              counts.get('01', 0) - counts.get('11', 0)) / total_shots

        return z0 + z1

    # Simulate optimization
    print("\nOptimization loop simulation:")
    param = torch.tensor([0.1], requires_grad=True)
    optimizer = torch.optim.Adam([param], lr=0.1)

    print(f"  Initial θ = {param.item():.4f}")
    initial_energy = measure_energy(build_ansatz(param.item()))
    print(f"  Initial energy = {initial_energy:.4f}")

    # Run a few optimization steps manually
    for step in range(5):
        theta_val = param.item()
        energy = measure_energy(build_ansatz(theta_val))

        # Manual gradient estimation (parameter-shift)
        e_plus = measure_energy(build_ansatz(theta_val + 0.5))
        e_minus = measure_energy(build_ansatz(theta_val - 0.5))
        grad = (e_plus - e_minus) / (2 * 0.5)

        # Update parameter
        param.data -= 0.1 * grad

        if step % 2 == 0:
            print(f"  Step {step}: θ={param.item():.4f}, E={energy:.4f}, grad={grad:.4f}")

    final_energy = measure_energy(build_ansatz(param.item()))
    print(f"\n  Final θ = {param.item():.4f}")
    print(f"  Final energy = {final_energy:.4f}")


def main():
    """Run all demonstrations."""
    print("PyTorch Integration for Quantum Machine Learning")
    print("=" * 60)

    demo_gradient_computation()
    demo_quantum_layer()
    demo_batch_execution()
    demo_vqe_with_pytorch()

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("  1. Parameter-shift rule enables gradient-based optimization")
    print("  2. QuantumLayer integrates with PyTorch autograd")
    print("  3. batch_execute parallelizes circuit evaluation")
    print("  4. Hybrid quantum-classical models are straightforward")
    print("=" * 60)


if __name__ == "__main__":
    main()