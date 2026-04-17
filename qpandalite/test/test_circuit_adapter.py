"""Tests for circuit_adapter module."""

import unittest
from unittest.mock import MagicMock, patch

from qpandalite.circuit_builder import Circuit
from qpandalite.circuit_adapter import (
    CircuitAdapter,
    OriginQCircuitAdapter,
    QuafuCircuitAdapter,
    IBMCircuitAdapter,
)


class TestCircuitAdapterInterface(unittest.TestCase):
    """Test the CircuitAdapter abstract base class interface."""

    def test_abstract_methods(self):
        """Test that CircuitAdapter cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            CircuitAdapter()


class TestOriginQCircuitAdapter(unittest.TestCase):
    """Test OriginQCircuitAdapter."""

    def test_get_supported_gates(self):
        """Test that supported gates are returned."""
        adapter = OriginQCircuitAdapter()
        gates = adapter.get_supported_gates()
        self.assertIsInstance(gates, list)
        self.assertIn("H", gates)
        self.assertIn("CNOT", gates)
        self.assertIn("MEASURE", gates)

    def test_adapt_without_pyqpanda3(self):
        """Test that adapt raises RuntimeError when pyqpanda3 is not installed."""
        adapter = OriginQCircuitAdapter()

        # Mock _pyqpanda3 as None to simulate missing import
        adapter._pyqpanda3 = None
        adapter._convert_originir = None

        circuit = Circuit()
        circuit.h(0)

        with patch.dict("sys.modules", {"pyqpanda3": None}):
            with self.assertRaises(RuntimeError) as context:
                adapter.adapt(circuit)
            self.assertIn("pyqpanda3", str(context.exception))


class TestQuafuCircuitAdapter(unittest.TestCase):
    """Test QuafuCircuitAdapter."""

    def test_get_supported_gates(self):
        """Test that supported gates are returned."""
        adapter = QuafuCircuitAdapter()
        gates = adapter.get_supported_gates()
        self.assertIsInstance(gates, list)
        self.assertIn("H", gates)
        self.assertIn("CNOT", gates)
        self.assertIn("MEASURE", gates)

    def test_adapt_without_quafu(self):
        """Test that adapt raises RuntimeError when quafu is not installed."""
        adapter = QuafuCircuitAdapter()

        # Reset the imports to simulate missing package
        adapter._quafu = None
        adapter._QuantumCircuit = None

        circuit = Circuit()
        circuit.h(0)

        with patch.dict("sys.modules", {"quafu": None}):
            with self.assertRaises(RuntimeError) as context:
                adapter.adapt(circuit)
            self.assertIn("quafu", str(context.exception))


class TestIBMCircuitAdapter(unittest.TestCase):
    """Test IBMCircuitAdapter."""

    def test_get_supported_gates(self):
        """Test that supported gates are returned."""
        adapter = IBMCircuitAdapter()
        gates = adapter.get_supported_gates()
        self.assertIsInstance(gates, list)
        self.assertIn("H", gates)
        self.assertIn("CNOT", gates)
        self.assertIn("CX", gates)  # IBM uses CX for CNOT
        self.assertIn("MEASURE", gates)

    def test_adapt_single_circuit(self):
        """Test adapting a single circuit."""
        try:
            import qiskit
        except ImportError:
            self.skipTest("qiskit not installed")

        adapter = IBMCircuitAdapter()
        circuit = Circuit()
        circuit.h(0)
        circuit.cnot(0, 1)
        circuit.measure(0, 1)

        qiskit_circuit = adapter.adapt(circuit)

        self.assertEqual(qiskit_circuit.num_qubits, 2)
        self.assertEqual(qiskit_circuit.num_clbits, 2)

    def test_adapt_batch(self):
        """Test batch adaptation of circuits."""
        try:
            import qiskit
        except ImportError:
            self.skipTest("qiskit not installed")

        adapter = IBMCircuitAdapter()

        circuit1 = Circuit()
        circuit1.h(0)
        circuit1.measure(0)

        circuit2 = Circuit()
        circuit2.x(0)
        circuit2.measure(0)

        qiskit_circuits = adapter.adapt_batch([circuit1, circuit2])

        self.assertEqual(len(qiskit_circuits), 2)
        for qc in qiskit_circuits:
            self.assertEqual(qc.num_qubits, 1)
            self.assertEqual(qc.num_clbits, 1)


class TestGateCoverage(unittest.TestCase):
    """Test that adapters cover the expected gate sets."""

    def test_originq_covers_basic_gates(self):
        """Test that OriginQ adapter covers basic quantum gates."""
        adapter = OriginQCircuitAdapter()
        gates = set(adapter.get_supported_gates())

        basic_gates = {"H", "X", "Y", "Z", "CNOT", "CZ", "RX", "RY", "RZ"}
        self.assertTrue(basic_gates.issubset(gates))

    def test_ibm_covers_qasm_gates(self):
        """Test that IBM adapter covers standard QASM gates."""
        adapter = IBMCircuitAdapter()
        gates = set(adapter.get_supported_gates())

        qasm_gates = {"H", "X", "Y", "Z", "CNOT", "CX", "CZ"}
        self.assertTrue(qasm_gates.issubset(gates))


if __name__ == "__main__":
    unittest.main()
