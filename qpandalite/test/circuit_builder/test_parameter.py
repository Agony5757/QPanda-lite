"""
Comprehensive unit tests for qpandalite.circuit_builder.parameter.

Tests cover:
- Parameter: creation, naming, symbolic expressions, binding
- Parameters: array creation, indexing, batch binding
- Parametric circuits: gates with symbolic parameters
- Parameter evaluation and binding
"""

import pytest
import sympy as sp
from qpandalite.circuit_builder.parameter import Parameter, Parameters
from qpandalite.circuit_builder import Circuit


# =============================================================================
# TestParameter
# =============================================================================


class TestParameter:
    """Tests for Parameter class."""

    def test_parameter_creation(self):
        """Parameter can be created with a name."""
        p = Parameter(name="theta")
        assert p.name == "theta"

    def test_parameter_symbol(self):
        """Parameter has a sympy Symbol."""
        p = Parameter(name="theta")
        assert isinstance(p.symbol, sp.Symbol)
        assert p.symbol.name == "theta"

    def test_parameter_arithmetic_add(self):
        """Parameter supports addition."""
        p1 = Parameter(name="theta")
        p2 = Parameter(name="phi")
        expr = p1 + p2
        assert isinstance(expr, sp.Expr)
        # Evaluate with values
        result = expr.subs({p1.symbol: 1.0, p2.symbol: 2.0})
        assert float(result) == 3.0

    def test_parameter_arithmetic_add_float(self):
        """Parameter can be added to a float."""
        p = Parameter(name="theta")
        expr = p + 1.5
        result = expr.subs({p.symbol: 2.0})
        assert float(result) == 3.5

    def test_parameter_arithmetic_mul(self):
        """Parameter supports multiplication."""
        p = Parameter(name="theta")
        expr = p * 2.0
        result = expr.subs({p.symbol: 3.0})
        assert float(result) == 6.0

    def test_parameter_arithmetic_neg(self):
        """Parameter supports negation."""
        p = Parameter(name="theta")
        expr = -p
        result = expr.subs({p.symbol: 1.0})
        assert float(result) == -1.0

    def test_parameter_bind(self):
        """Parameter can be bound to a value."""
        p = Parameter(name="theta")
        assert not p.is_bound
        p.bind(1.5)
        assert p.is_bound
        assert p.evaluate() == 1.5

    def test_parameter_evaluate_with_values_dict(self):
        """Parameter can be evaluated with a values dict."""
        p = Parameter(name="theta")
        assert p.evaluate({"theta": 2.0}) == 2.0

    def test_parameter_evaluate_bound(self):
        """Bound parameter evaluates without needing values dict."""
        p = Parameter(name="theta")
        p.bind(3.14)
        assert p.evaluate() == 3.14

    def test_parameter_repr(self):
        """Parameter repr is informative."""
        p = Parameter(name="theta")
        assert "theta" in repr(p)


# =============================================================================
# TestParameters
# =============================================================================


class TestParameters:
    """Tests for Parameters class (parameter array)."""

    def test_parameters_creation(self):
        """Parameters can be created with name and size."""
        ps = Parameters(name="alpha", size=4)
        assert ps.name == "alpha"
        assert len(ps) == 4

    def test_parameters_indexing(self):
        """Parameters[i] returns a Parameter."""
        ps = Parameters(name="alpha", size=4)
        p0 = ps[0]
        assert isinstance(p0, Parameter)
        assert p0.name == "alpha_0"

    def test_parameters_iteration(self):
        """Parameters can be iterated."""
        ps = Parameters(name="alpha", size=3)
        params = list(ps)
        assert len(params) == 3
        assert all(isinstance(p, Parameter) for p in params)

    def test_parameters_bind_all(self):
        """Parameters can bind all values at once."""
        ps = Parameters(name="theta", size=4)
        values = [0.1, 0.2, 0.3, 0.4]
        ps.bind(values)
        for i, v in enumerate(values):
            assert ps[i].evaluate() == v

    def test_parameters_names(self):
        """Parameters have correct individual names."""
        ps = Parameters(name="alpha", size=3)
        assert ps.names == ["alpha_0", "alpha_1", "alpha_2"]


# =============================================================================
# TestParametricCircuit
# =============================================================================


class TestParametricCircuit:
    """Tests for Circuit with symbolic parameters."""

    def test_circuit_parameter_tracking(self):
        """Circuit tracks parameters used in gates."""
        c = Circuit()
        theta = Parameter(name="theta")
        # Add gate with parameter (Phase 2 feature - to be implemented)
        # c.rx(0, theta)
        # assert c.num_parameters == 1
        # assert "theta" in c.parameter_names

    def test_circuit_with_multiple_parameters(self):
        """Circuit can use multiple parameters."""
        c = Circuit()
        theta = Parameter(name="theta")
        phi = Parameter(name="phi")
        # c.rx(0, theta)
        # c.ry(1, phi)
        # assert c.num_parameters == 2


# =============================================================================
# TestParameterEvaluation
# =============================================================================


class TestParameterEvaluation:
    """Tests for evaluating symbolic expressions."""

    def test_simple_expression(self):
        """Simple parameter expression can be evaluated."""
        theta = Parameter(name="theta")
        expr = theta * 2 + 1
        result = expr.subs({theta.symbol: 0.5})
        assert float(result) == 2.0

    def test_compound_expression(self):
        """Compound expressions with multiple parameters."""
        theta = Parameter(name="theta")
        phi = Parameter(name="phi")
        expr = theta + phi / 2
        result = expr.subs({theta.symbol: 1.0, phi.symbol: 4.0})
        assert float(result) == 3.0

    def test_expression_with_parameters_array(self):
        """Expression using Parameters array elements."""
        alphas = Parameters(name="alpha", size=4)
        expr = alphas[0] + alphas[1] * 2
        result = expr.subs({
            alphas[0].symbol: 1.0,
            alphas[1].symbol: 2.0
        })
        assert float(result) == 5.0