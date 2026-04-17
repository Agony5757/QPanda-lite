"""Tests for qpandalite.pytorch module.

This module tests:
- parameter_shift_gradient function
- compute_all_gradients function
- batch_execute function
- batch_execute_with_params function
- QuantumLayer class (when PyTorch is available)
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

# Setup mocks for dependencies
mock_cpp = MagicMock()
sys.modules['qpandalite_cpp'] = mock_cpp

mock_pyqpanda3 = MagicMock()
mock_pyqpanda3.core.draw_qprog = MagicMock()
mock_pyqpanda3.core.PIC_TYPE = MagicMock()
mock_pyqpanda3.intermediate_compiler.convert_originir_string_to_qprog = MagicMock()
sys.modules['pyqpanda3'] = mock_pyqpanda3
sys.modules['pyqpanda3.core'] = mock_pyqpanda3.core
sys.modules['pyqpanda3.intermediate_compiler'] = mock_pyqpanda3.intermediate_compiler


# =============================================================================
# Test Imports
# =============================================================================

class TestPytorchImports:
    """Test that pytorch module can be imported."""

    def test_import_gradient_module(self):
        """Test importing gradient module."""
        from qpandalite.pytorch.gradient import parameter_shift_gradient, compute_all_gradients
        assert callable(parameter_shift_gradient)
        assert callable(compute_all_gradients)

    def test_import_batch_executor_module(self):
        """Test importing batch_executor module."""
        from qpandalite.pytorch.batch_executor import batch_execute, batch_execute_with_params
        assert callable(batch_execute)
        assert callable(batch_execute_with_params)

    def test_import_quantum_layer_module(self):
        """Test importing quantum_layer module."""
        from qpandalite.pytorch.quantum_layer import QuantumLayer
        assert QuantumLayer is not None

    def test_import_main_module(self):
        """Test importing from main pytorch module."""
        from qpandalite.pytorch import (
            parameter_shift_gradient,
            compute_all_gradients,
            batch_execute,
            QuantumLayer,
        )
        assert callable(parameter_shift_gradient)
        assert callable(compute_all_gradients)
        assert callable(batch_execute)
        assert QuantumLayer is not None


# =============================================================================
# Test batch_execute
# =============================================================================

class TestBatchExecute:
    """Tests for batch_execute function."""

    def test_batch_execute_empty_list(self):
        """Test batch_execute with empty circuit list."""
        from qpandalite.pytorch.batch_executor import batch_execute

        executor = Mock()
        results = batch_execute([], executor, n_workers=1)
        assert results == []

    def test_batch_execute_single_circuit(self):
        """Test batch_execute with single circuit."""
        from qpandalite.pytorch.batch_executor import batch_execute

        mock_circuit = MagicMock()
        mock_result = np.array([0.5, 0.5])
        executor = Mock(return_value=mock_result)

        results = batch_execute([mock_circuit], executor, n_workers=1)
        assert len(results) == 1
        np.testing.assert_array_equal(results[0], mock_result)

    def test_batch_execute_multiple_circuits(self):
        """Test batch_execute with multiple circuits."""
        from qpandalite.pytorch.batch_executor import batch_execute

        circuits = [MagicMock(), MagicMock(), MagicMock()]
        executor = Mock(side_effect=[
            np.array([0.5]),
            np.array([0.3]),
            np.array([0.7]),
        ])

        results = batch_execute(circuits, executor, n_workers=2)
        assert len(results) == 3

    def test_batch_execute_with_executor_call(self):
        """Test that executor is called for each circuit."""
        from qpandalite.pytorch.batch_executor import batch_execute

        circuits = [MagicMock(name=f"circuit_{i}") for i in range(3)]
        executor = Mock(return_value=np.array([0.0]))

        batch_execute(circuits, executor, n_workers=1)
        assert executor.call_count == 3


# =============================================================================
# Test batch_execute_with_params
# =============================================================================

class TestBatchExecuteWithParams:
    """Tests for batch_execute_with_params function."""

    def test_batch_execute_with_params_empty(self):
        """Test with empty parameter list."""
        from qpandalite.pytorch.batch_executor import batch_execute_with_params

        mock_circuit = MagicMock()
        mock_circuit.copy = Mock(return_value=mock_circuit)
        executor = Mock()

        results = batch_execute_with_params(mock_circuit, [], executor)
        assert results == []

    def test_batch_execute_with_params_single(self):
        """Test with single parameter set."""
        from qpandalite.pytorch.batch_executor import batch_execute_with_params

        # Create mock circuit with _parameters
        mock_circuit = MagicMock()
        mock_circuit._parameters = {"theta": MagicMock(bind=Mock())}
        mock_circuit.copy = Mock(return_value=mock_circuit)
        executor = Mock(return_value=np.array([0.5]))

        param_values = [{"theta": 0.1}]
        results = batch_execute_with_params(mock_circuit, param_values, executor)
        assert len(results) == 1

    def test_batch_execute_with_params_multiple(self):
        """Test with multiple parameter sets."""
        from qpandalite.pytorch.batch_executor import batch_execute_with_params

        mock_circuit = MagicMock()
        mock_circuit._parameters = {
            "theta": MagicMock(bind=Mock()),
            "phi": MagicMock(bind=Mock()),
        }
        mock_circuit.copy = Mock(return_value=mock_circuit)
        executor = Mock(return_value=np.array([0.0]))

        param_values = [
            {"theta": 0.1, "phi": 0.2},
            {"theta": 0.3, "phi": 0.4},
            {"theta": 0.5, "phi": 0.6},
        ]
        results = batch_execute_with_params(mock_circuit, param_values, executor, n_workers=1)
        assert len(results) == 3


# =============================================================================
# Test parameter_shift_gradient
# =============================================================================

class TestParameterShiftGradient:
    """Tests for parameter_shift_gradient function."""

    def test_gradient_raises_on_missing_parameter(self):
        """Test that gradient raises ValueError for missing parameter."""
        from qpandalite.pytorch.gradient import parameter_shift_gradient

        mock_circuit = MagicMock()
        mock_circuit._parameters = {"theta": MagicMock()}
        # No 'phi' parameter

        expectation_fn = Mock(return_value=0.5)

        with pytest.raises(ValueError, match="not found"):
            parameter_shift_gradient(mock_circuit, "phi", expectation_fn)

    def test_gradient_computation(self):
        """Test basic gradient computation."""
        from qpandalite.pytorch.gradient import parameter_shift_gradient

        # Create mock circuit with parameter
        mock_param = MagicMock()
        mock_param._bound_value = 0.0
        mock_param.is_bound = Mock(return_value=True)

        mock_circuit = MagicMock()
        mock_circuit._parameters = {"theta": mock_param}

        # Mock copy to return same structure
        mock_plus = MagicMock()
        mock_plus._parameters = {"theta": MagicMock(bind=Mock())}
        mock_minus = MagicMock()
        mock_minus._parameters = {"theta": MagicMock(bind=Mock())}
        mock_circuit.copy = Mock(side_effect=[mock_plus, mock_minus])

        # Expectation function returns different values for +shift and -shift
        expectation_fn = Mock(side_effect=[0.6, 0.4])  # exp_plus, exp_minus

        gradient = parameter_shift_gradient(mock_circuit, "theta", expectation_fn)

        # Gradient should be 0.5 * (0.6 - 0.4) = 0.1
        assert isinstance(gradient, float)

    def test_gradient_with_custom_shift(self):
        """Test gradient with custom shift value."""
        from qpandalite.pytorch.gradient import parameter_shift_gradient

        mock_param = MagicMock()
        mock_param._bound_value = 0.0
        mock_param.is_bound = Mock(return_value=True)

        mock_circuit = MagicMock()
        mock_circuit._parameters = {"theta": mock_param}
        mock_plus = MagicMock()
        mock_plus._parameters = {"theta": MagicMock(bind=Mock())}
        mock_minus = MagicMock()
        mock_minus._parameters = {"theta": MagicMock(bind=Mock())}
        mock_circuit.copy = Mock(side_effect=[mock_plus, mock_minus])

        expectation_fn = Mock(side_effect=[0.5, 0.3])

        gradient = parameter_shift_gradient(mock_circuit, "theta", expectation_fn, shift=0.5)
        assert isinstance(gradient, float)


# =============================================================================
# Test compute_all_gradients
# =============================================================================

class TestComputeAllGradients:
    """Tests for compute_all_gradients function."""

    def test_empty_circuit_no_parameters(self):
        """Test with circuit that has no _parameters attribute."""
        from qpandalite.pytorch.gradient import compute_all_gradients

        mock_circuit = MagicMock(spec=[])  # No _parameters attribute
        expectation_fn = Mock()

        gradients = compute_all_gradients(mock_circuit, expectation_fn)
        assert gradients == {}

    def test_multiple_parameters(self):
        """Test with multiple parameters."""
        from qpandalite.pytorch.gradient import compute_all_gradients

        mock_param1 = MagicMock()
        mock_param1._bound_value = 0.0
        mock_param1.is_bound = Mock(return_value=True)

        mock_param2 = MagicMock()
        mock_param2._bound_value = 0.0
        mock_param2.is_bound = Mock(return_value=True)

        mock_circuit = MagicMock()
        mock_circuit._parameters = {"theta": mock_param1, "phi": mock_param2}

        # Mock copy to return circuits with parameters
        def make_copy():
            c = MagicMock()
            c._parameters = {
                "theta": MagicMock(bind=Mock()),
                "phi": MagicMock(bind=Mock()),
            }
            return c
        mock_circuit.copy = Mock(side_effect=[make_copy() for _ in range(4)])

        expectation_fn = Mock(return_value=0.5)

        gradients = compute_all_gradients(mock_circuit, expectation_fn)
        assert "theta" in gradients
        assert "phi" in gradients


# =============================================================================
# Test QuantumLayer (when PyTorch available)
# =============================================================================

class TestQuantumLayerWithoutPytorch:
    """Tests for QuantumLayer when PyTorch is not available."""

    def test_quantum_layer_raises_without_pytorch(self):
        """Test QuantumLayer raises ImportError without PyTorch."""
        # Simulate PyTorch not available
        with patch.dict(sys.modules, {"torch": None}):
            # Need to reimport to pick up the mock
            import importlib
            import qpandalite.pytorch.quantum_layer
            importlib.reload(qpandalite.pytorch.quantum_layer)

            from qpandalite.pytorch.quantum_layer import QuantumLayer
            with pytest.raises(ImportError, match="PyTorch"):
                QuantumLayer(MagicMock(), Mock())


class TestQuantumLayerWithPytorch:
    """Tests for QuantumLayer when PyTorch is available."""

    @pytest.mark.skip(reason="PyTorch not installed - test requires torch")
    def test_quantum_layer_initialization(self):
        """Test QuantumLayer initialization."""
        torch = pytest.importorskip("torch")

        from qpandalite.pytorch.quantum_layer import QuantumLayer

        mock_circuit = MagicMock()
        mock_circuit._parameters = {"theta": MagicMock()}
        mock_circuit.copy = Mock(return_value=mock_circuit)

        expectation_fn = Mock(return_value=0.5)

        layer = QuantumLayer(mock_circuit, expectation_fn)
        assert layer is not None
        assert hasattr(layer, "params")

    @pytest.mark.skip(reason="PyTorch not installed - test requires torch")
    def test_quantum_layer_extra_repr(self):
        """Test QuantumLayer.extra_repr."""
        torch = pytest.importorskip("torch")

        from qpandalite.pytorch.quantum_layer import QuantumLayer

        mock_circuit = MagicMock()
        mock_circuit._parameters = {"theta": MagicMock(), "phi": MagicMock()}
        mock_circuit.copy = Mock(return_value=mock_circuit)

        expectation_fn = Mock(return_value=0.5)

        layer = QuantumLayer(mock_circuit, expectation_fn)
        repr_str = layer.extra_repr()
        assert "n_params" in repr_str


# =============================================================================
# Test Module Exports
# =============================================================================

class TestModuleExports:
    """Test that __all__ exports are available."""

    def test_gradient_exports(self):
        """Test gradient module exports."""
        from qpandalite.pytorch.gradient import __all__
        assert "parameter_shift_gradient" in __all__
        assert "compute_all_gradients" in __all__

    def test_batch_executor_exports(self):
        """Test batch_executor module exports."""
        from qpandalite.pytorch.batch_executor import __all__
        assert "batch_execute" in __all__

    def test_quantum_layer_exports(self):
        """Test quantum_layer module exports."""
        from qpandalite.pytorch.quantum_layer import __all__
        assert "QuantumLayer" in __all__

    def test_main_module_exports(self):
        """Test main pytorch module exports."""
        from qpandalite.pytorch import __all__
        assert "QuantumLayer" in __all__
        assert "batch_execute" in __all__
        assert "parameter_shift_gradient" in __all__
        assert "compute_all_gradients" in __all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])