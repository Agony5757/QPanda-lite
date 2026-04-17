"""Tests for circuit_adapter module."""

import unittest
from unittest.mock import MagicMock, patch, Mock

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

    def test_adapt_batch(self):
        """Test that adapt_batch calls adapt for each circuit."""
        # Create a concrete adapter for testing
        class MockAdapter(CircuitAdapter):
            def adapt(self, circuit):
                return f"adapted_{circuit}"
            def get_supported_gates(self):
                return ["H"]

        adapter = MockAdapter()
        circuits = [Circuit(), Circuit()]
        circuits[0].h(0)
        circuits[1].x(0)

        results = adapter.adapt_batch(circuits)
        self.assertEqual(len(results), 2)

    def test_get_originir(self):
        """Test _get_originir extracts OriginIR string."""
        class MockAdapter(CircuitAdapter):
            def adapt(self, circuit):
                return None
            def get_supported_gates(self):
                return []

        adapter = MockAdapter()
        circuit = Circuit()
        circuit.h(0)

        originir = adapter._get_originir(circuit)
        self.assertIn("QINIT", originir)
        self.assertIn("H", originir)


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

    def test_supported_gates_includes_rotation_gates(self):
        """Test that rotation gates are included."""
        adapter = OriginQCircuitAdapter()
        gates = adapter.get_supported_gates()
        self.assertIn("RX", gates)
        self.assertIn("RY", gates)
        self.assertIn("RZ", gates)
        self.assertIn("U1", gates)
        self.assertIn("U2", gates)
        self.assertIn("U3", gates)

    def test_supported_gates_includes_two_qubit_gates(self):
        """Test that two-qubit gates are included."""
        adapter = OriginQCircuitAdapter()
        gates = adapter.get_supported_gates()
        self.assertIn("CNOT", gates)
        self.assertIn("CZ", gates)
        self.assertIn("SWAP", gates)
        self.assertIn("ISWAP", gates)


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

    def test_adapt_with_mock_quafu(self):
        """Test adapt with mocked quafu module."""
        # Create mock QuantumCircuit
        mock_qc = Mock()
        mock_qc.h = Mock()
        mock_qc.x = Mock()
        mock_qc.cnot = Mock()
        mock_qc.measure = Mock()

        mock_quafu = Mock()
        mock_quafu.QuantumCircuit = Mock(return_value=mock_qc)

        adapter = QuafuCircuitAdapter()
        adapter._quafu = mock_quafu
        adapter._QuantumCircuit = mock_quafu.QuantumCircuit

        circuit = Circuit()
        circuit.h(0)
        circuit.x(1)
        circuit.cnot(0, 1)
        circuit.measure(0)

        with patch("qpandalite.circuit_adapter.QuafuCircuitAdapter._ensure_imports"):
            result = adapter.adapt(circuit)

        self.assertEqual(result, mock_qc)

    def test_adapt_rotation_gates_with_mock(self):
        """Test adapt with rotation gates using mock."""
        mock_qc = Mock()
        mock_qc.rx = Mock()
        mock_qc.ry = Mock()
        mock_qc.rz = Mock()
        mock_qc.measure = Mock()

        mock_quafu = Mock()
        mock_quafu.QuantumCircuit = Mock(return_value=mock_qc)

        adapter = QuafuCircuitAdapter()
        adapter._quafu = mock_quafu
        adapter._QuantumCircuit = mock_quafu.QuantumCircuit

        circuit = Circuit()
        circuit.rx(0, 0.5)
        circuit.ry(1, 0.3)
        circuit.rz(2, 0.1)
        circuit.measure(0)

        with patch("qpandalite.circuit_adapter.QuafuCircuitAdapter._ensure_imports"):
            result = adapter.adapt(circuit)

        self.assertEqual(result, mock_qc)

    def test_adapt_two_qubit_gates_with_mock(self):
        """Test adapt with two-qubit gates using mock."""
        mock_qc = Mock()
        mock_qc.cnot = Mock()
        mock_qc.cz = Mock()
        mock_qc.measure = Mock()

        mock_quafu = Mock()
        mock_quafu.QuantumCircuit = Mock(return_value=mock_qc)

        adapter = QuafuCircuitAdapter()
        adapter._quafu = mock_quafu
        adapter._QuantumCircuit = mock_quafu.QuantumCircuit

        circuit = Circuit()
        circuit.cnot(0, 1)
        circuit.cz(1, 2)
        circuit.measure(0, 1)

        with patch("qpandalite.circuit_adapter.QuafuCircuitAdapter._ensure_imports"):
            result = adapter.adapt(circuit)

        self.assertEqual(result, mock_qc)

    def test_adapt_with_dagger_block_mock(self):
        """Test adapt with DAGGER block using mock."""
        mock_qc = Mock()
        mock_qc.h = Mock()
        mock_qc.cnot = Mock()
        mock_qc.s = Mock()
        mock_qc.sdg = Mock()
        mock_qc.t = Mock()
        mock_qc.tdg = Mock()
        mock_qc.measure = Mock()

        mock_quafu = Mock()
        mock_quafu.QuantumCircuit = Mock(return_value=mock_qc)

        adapter = QuafuCircuitAdapter()
        adapter._quafu = mock_quafu
        adapter._QuantumCircuit = mock_quafu.QuantumCircuit

        circuit = Circuit()
        circuit.s(0)
        circuit.t(1)
        with circuit.dagger():
            circuit.h(0)
        circuit.measure(0)

        with patch("qpandalite.circuit_adapter.QuafuCircuitAdapter._ensure_imports"):
            result = adapter.adapt(circuit)

        self.assertEqual(result, mock_qc)

    def test_adapt_with_barrier_mock(self):
        """Test adapt with BARRIER using mock."""
        mock_qc = Mock()
        mock_qc.h = Mock()
        mock_qc.barrier = Mock()
        mock_qc.measure = Mock()

        mock_quafu = Mock()
        mock_quafu.QuantumCircuit = Mock(return_value=mock_qc)

        adapter = QuafuCircuitAdapter()
        adapter._quafu = mock_quafu
        adapter._QuantumCircuit = mock_quafu.QuantumCircuit

        circuit = Circuit()
        circuit.h(0)
        circuit.barrier(0)
        circuit.measure(0)

        with patch("qpandalite.circuit_adapter.QuafuCircuitAdapter._ensure_imports"):
            result = adapter.adapt(circuit)

        self.assertEqual(result, mock_qc)


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

    def test_adapt_without_qiskit(self):
        """Test that adapt raises RuntimeError when qiskit is not installed."""
        adapter = IBMCircuitAdapter()
        adapter._qiskit = None

        circuit = Circuit()
        circuit.h(0)

        with patch.dict("sys.modules", {"qiskit": None}):
            with self.assertRaises(RuntimeError) as context:
                adapter.adapt(circuit)
            self.assertIn("qiskit", str(context.exception))

    def test_adapt_with_mock_qiskit(self):
        """Test adapt with mocked qiskit module."""
        mock_circuit = Mock()
        mock_circuit.num_qubits = 2
        mock_circuit.num_clbits = 2

        mock_qiskit = Mock()
        mock_qiskit.QuantumCircuit = Mock()
        mock_qiskit.QuantumCircuit.from_qasm_str = Mock(return_value=mock_circuit)

        adapter = IBMCircuitAdapter()
        adapter._qiskit = mock_qiskit

        circuit = Circuit()
        circuit.h(0)
        circuit.cnot(0, 1)
        circuit.measure(0, 1)

        result = adapter.adapt(circuit)
        self.assertEqual(result, mock_circuit)

    def test_adapt_batch_with_mock(self):
        """Test batch adaptation with mocked qiskit."""
        mock_circuit1 = Mock()
        mock_circuit1.num_qubits = 1

        mock_circuit2 = Mock()
        mock_circuit2.num_qubits = 1

        mock_qiskit = Mock()
        mock_qiskit.QuantumCircuit = Mock()
        mock_qiskit.QuantumCircuit.from_qasm_str = Mock(
            side_effect=[mock_circuit1, mock_circuit2]
        )

        adapter = IBMCircuitAdapter()
        adapter._qiskit = mock_qiskit

        circuit1 = Circuit()
        circuit1.h(0)
        circuit1.measure(0)

        circuit2 = Circuit()
        circuit2.x(0)
        circuit2.measure(0)

        results = adapter.adapt_batch([circuit1, circuit2])
        self.assertEqual(len(results), 2)

    def test_adapt_with_transpilation_mock(self):
        """Test adapt_with_transpilation with mocked qiskit."""
        mock_circuit = Mock()
        mock_transpiled = Mock()

        mock_backend = Mock()

        mock_qiskit = Mock()
        mock_qiskit.QuantumCircuit = Mock()
        mock_qiskit.QuantumCircuit.from_qasm_str = Mock(return_value=mock_circuit)
        mock_qiskit.compiler = Mock()
        mock_qiskit.compiler.transpile = Mock(return_value=mock_transpiled)

        adapter = IBMCircuitAdapter()
        adapter._qiskit = mock_qiskit

        circuit = Circuit()
        circuit.h(0)
        circuit.measure(0)

        result = adapter.adapt_with_transpilation(circuit, backend=mock_backend)
        self.assertEqual(result, mock_transpiled)
        mock_qiskit.compiler.transpile.assert_called_once()

    def test_adapt_with_transpilation_no_backend_mock(self):
        """Test adapt_with_transpilation without backend."""
        mock_circuit = Mock()

        mock_qiskit = Mock()
        mock_qiskit.QuantumCircuit = Mock()
        mock_qiskit.QuantumCircuit.from_qasm_str = Mock(return_value=mock_circuit)

        adapter = IBMCircuitAdapter()
        adapter._qiskit = mock_qiskit

        circuit = Circuit()
        circuit.h(0)
        circuit.measure(0)

        result = adapter.adapt_with_transpilation(circuit, backend=None)
        self.assertEqual(result, mock_circuit)

    def test_supported_gates_includes_u_gates(self):
        """Test that U gates are included."""
        adapter = IBMCircuitAdapter()
        gates = adapter.get_supported_gates()
        self.assertIn("U1", gates)
        self.assertIn("U2", gates)
        self.assertIn("U3", gates)


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

    def test_quafu_covers_basic_gates(self):
        """Test that Quafu adapter covers basic gates."""
        adapter = QuafuCircuitAdapter()
        gates = set(adapter.get_supported_gates())

        basic_gates = {"H", "X", "Y", "Z", "RX", "RY", "RZ", "CNOT"}
        self.assertTrue(basic_gates.issubset(gates))


if __name__ == "__main__":
    unittest.main()
