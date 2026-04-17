"""
Symbolic parameters for parametric quantum circuits.

This module provides:
- Parameter: Named symbolic parameter for parametric gates
- Parameters: Array of named parameters with indexing support

These classes enable symbolic expressions for gate parameters that can be
bound to concrete values at execution time.

Example usage:
    theta = Parameter("theta")
    phi = Parameter("phi")

    # Arithmetic operations create symbolic expressions
    expr = theta + phi / 2

    # Bind values and evaluate
    theta.bind(1.0)
    phi.bind(2.0)
    result = expr.evalf()  # 2.0
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import sympy as sp

if TYPE_CHECKING:
    pass

__all__ = ["Parameter", "Parameters"]


class Parameter:
    """Named symbolic parameter for parametric quantum circuits.

    Parameter supports arithmetic operations that create symbolic expressions
    using sympy. The parameter can be bound to a concrete value or evaluated
    with a provided values dictionary.

    Attributes:
        name: Parameter name
        symbol: Underlying sympy Symbol

    Example:
        >>> theta = Parameter("theta")
        >>> phi = Parameter("phi")
        >>> expr = theta * 2 + phi
        >>> # Evaluate with concrete values
        >>> float(expr.subs({theta.symbol: 1.0, phi.symbol: 0.5}))
        2.5
    """

    def __init__(self, name: str) -> None:
        """Initialize a named parameter.

        Args:
            name: Parameter name (must be unique within a circuit)
        """
        self._name = name
        self._symbol = sp.Symbol(name)
        self._bound_value: float | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def symbol(self) -> sp.Symbol:
        return self._symbol

    def bind(self, value: float) -> None:
        """Bind a concrete value to this parameter.

        Args:
            value: The numeric value to bind
        """
        self._bound_value = float(value)

    def evaluate(self, values: dict[str, float] | None = None) -> float:
        """Evaluate the parameter.

        If the parameter is bound, returns the bound value.
        Otherwise, looks up the value in the provided dictionary.

        Args:
            values: Optional dictionary mapping parameter names to values

        Returns:
            The evaluated numeric value

        Raises:
            ValueError: If parameter is not bound and not in values dict
        """
        if self._bound_value is not None:
            return self._bound_value
        if values is not None and self._name in values:
            return values[self._name]
        raise ValueError(f"Parameter '{self._name}' is not bound and no value provided")

    @property
    def is_bound(self) -> bool:
        """Check if the parameter has a bound value."""
        return self._bound_value is not None

    def __add__(self, other: Parameter | float | int) -> sp.Expr:
        return self._symbol + (other._symbol if isinstance(other, Parameter) else other)

    def __radd__(self, other: float | int) -> sp.Expr:
        return other + self._symbol

    def __sub__(self, other: Parameter | float | int) -> sp.Expr:
        return self._symbol - (other._symbol if isinstance(other, Parameter) else other)

    def __rsub__(self, other: float | int) -> sp.Expr:
        return other - self._symbol

    def __mul__(self, other: Parameter | float | int) -> sp.Expr:
        return self._symbol * (other._symbol if isinstance(other, Parameter) else other)

    def __rmul__(self, other: float | int) -> sp.Expr:
        return other * self._symbol

    def __truediv__(self, other: Parameter | float | int) -> sp.Expr:
        return self._symbol / (other._symbol if isinstance(other, Parameter) else other)

    def __rtruediv__(self, other: float | int) -> sp.Expr:
        return other / self._symbol

    def __neg__(self) -> sp.Expr:
        return -self._symbol

    def __repr__(self) -> str:
        bound_str = f"={self._bound_value}" if self._bound_value is not None else ""
        return f"Parameter({self._name!r}{bound_str})"

    def __hash__(self) -> int:
        return hash(self._name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Parameter):
            return NotImplemented
        return self._name == other._name


class Parameters:
    """Array of named parameters with indexing support.

    Creates multiple Parameter objects with names "{name}_{index}".

    Attributes:
        name: Base name for the parameter array

    Example:
        >>> alphas = Parameters("alpha", size=4)
        >>> alphas[0]
        Parameter('alpha_0')
        >>> alphas.names
        ['alpha_0', 'alpha_1', 'alpha_2', 'alpha_3']
        >>> alphas.bind([0.1, 0.2, 0.3, 0.4])
        >>> alphas[0].evaluate()
        0.1
    """

    def __init__(self, name: str, size: int) -> None:
        """Initialize a parameter array.

        Args:
            name: Base name for parameters
            size: Number of parameters in the array

        Raises:
            ValueError: If size is not positive
        """
        if size <= 0:
            raise ValueError(f"Parameters size must be positive, got {size}")
        self._name = name
        self._params: list[Parameter] = [Parameter(f"{name}_{i}") for i in range(size)]

    @property
    def name(self) -> str:
        return self._name

    @property
    def names(self) -> list[str]:
        """Return list of all parameter names."""
        return [p.name for p in self._params]

    @property
    def symbols(self) -> list[sp.Symbol]:
        """Return list of all sympy symbols."""
        return [p.symbol for p in self._params]

    def __len__(self) -> int:
        return len(self._params)

    def __getitem__(self, index: int) -> Parameter:
        return self._params[index]

    def __iter__(self) -> Iterator[Parameter]:
        return iter(self._params)

    def bind(self, values: list[float]) -> None:
        """Bind values to all parameters.

        Args:
            values: List of values (must match array size)

        Raises:
            ValueError: If values length doesn't match array size
        """
        if len(values) != len(self._params):
            raise ValueError(f"Values length {len(values)} doesn't match Parameters size {len(self._params)}")
        for param, value in zip(self._params, values, strict=True):
            param.bind(value)

    def evaluate(self, values: list[float] | None = None) -> list[float]:
        """Evaluate all parameters.

        Args:
            values: Optional list of values to use (must match array size)

        Returns:
            List of evaluated values
        """
        if values is not None:
            self.bind(values)
        return [p.evaluate() for p in self._params]

    def __repr__(self) -> str:
        return f"Parameters({self._name!r}, size={len(self._params)})"
