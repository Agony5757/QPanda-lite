"""
Named quantum register and qubit types.

This module provides:
- Qubit: Named reference to a single qubit within a register
- QReg: Named quantum register with indexing and slicing support
- QRegSlice: Slice view of a QReg for multi-qubit operations

Example usage:
    qr = QReg(name="a", size=4, base_index=0)
    q0 = qr[0]           # Qubit(name="a[0]", index=0, base_index=0)
    q_slice = qr[1:3]    # QRegSlice with qubits at indices 1, 2
    int(q0)              # 0 (physical qubit index)
    int(qr[2])           # 2
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

__all__ = ["Qubit", "QReg", "QRegSlice"]


@dataclass
class Qubit:
    """Named reference to a single qubit within a quantum register.

    Attributes:
        name: Full name of the qubit, e.g., "a[0]"
        index: Index within the parent register
        base_index: Starting physical qubit index for the parent register

    Example:
        >>> q = Qubit(name="a[2]", index=2, base_index=10)
        >>> int(q)
        12
    """

    name: str
    index: int
    base_index: int

    def __int__(self) -> int:
        """Return the physical qubit index (base_index + index)."""
        return self.base_index + self.index

    def __eq__(self, other: object) -> bool:
        """Two Qubits are equal if they have the same name."""
        if not isinstance(other, Qubit):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        """Hash based on name for use in sets and dicts."""
        return hash(self.name)

    def __repr__(self) -> str:
        return f"Qubit({self.name!r}, index={self.index}, base_index={self.base_index})"


class QRegSlice:
    """Slice view of a QReg for multi-qubit operations.

    This class provides iteration and indexing over a subset of qubits
    from a parent register.

    Attributes:
        register: Parent QReg
        indices: List of indices within the parent register
    """

    def __init__(self, register: QReg, indices: list[int]) -> None:
        self._register = register
        self._indices = indices

    @property
    def register(self) -> QReg:
        return self._register

    @property
    def indices(self) -> list[int]:
        return self._indices.copy()

    def __len__(self) -> int:
        return len(self._indices)

    def __iter__(self) -> Iterator[Qubit]:
        for idx in self._indices:
            yield self._register[idx]

    def __getitem__(self, key: int) -> Qubit:
        """Get a specific Qubit from the slice."""
        return self._register[self._indices[key]]

    def __repr__(self) -> str:
        indices_str = ", ".join(map(str, self._indices))
        return f"QRegSlice({self._register.name}[{indices_str}])"


class QReg:
    """Named quantum register with indexing and slicing support.

    QReg provides named access to qubits within a circuit, supporting
    integer indexing, negative indexing, and slicing.

    Attributes:
        name: Name of the register
        size: Number of qubits in the register
        base_index: Starting physical qubit index (set when mapped to circuit)

    Example:
        >>> qr = QReg(name="a", size=4, base_index=0)
        >>> qr[0]
        Qubit('a[0]', index=0, base_index=0)
        >>> qr[1:3]
        QRegSlice(a[1, 2])
        >>> len(qr)
        4
    """

    def __init__(
        self,
        name: str,
        size: int,
        base_index: int = 0,
    ) -> None:
        if size <= 0:
            raise ValueError(f"QReg size must be positive, got {size}")
        self._name = name
        self._size = size
        self._base_index = base_index

    @property
    def name(self) -> str:
        return self._name

    @property
    def size(self) -> int:
        return self._size

    @property
    def base_index(self) -> int:
        return self._base_index

    @base_index.setter
    def base_index(self, value: int) -> None:
        self._base_index = value

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, key: int | slice) -> Qubit | QRegSlice:
        """Index or slice the register.

        Args:
            key: Integer index or slice

        Returns:
            Qubit for single index, QRegSlice for slice

        Raises:
            IndexError: If index is out of range
        """
        if isinstance(key, slice):
            # Convert slice to list of indices
            start, stop, step = key.indices(self._size)
            indices = list(range(start, stop, step))
            return QRegSlice(self, indices)
        else:
            # Handle negative indexing
            if key < 0:
                key = self._size + key
            if key < 0 or key >= self._size:
                raise IndexError(f"QReg index {key} out of range for size {self._size}")
            return Qubit(
                name=f"{self._name}[{key}]",
                index=key,
                base_index=self._base_index,
            )

    @property
    def qubits(self) -> list[Qubit]:
        """Return list of all Qubit objects in this register."""
        return [self[i] for i in range(self._size)]

    def __repr__(self) -> str:
        return f"QReg({self._name!r}, size={self._size}, base_index={self._base_index})"
