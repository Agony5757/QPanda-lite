"""Dummy adapter for local simulation without real quantum hardware.

This adapter provides a drop-in replacement for cloud backends using
local simulation. It's useful for:
- Development and testing without cloud access
- Offline development
- Quick prototyping and debugging
- Running circuits when API tokens are not available

The dummy adapter uses the built-in OriginIR simulator to execute circuits
and returns results in the same format as cloud backends.

Usage:
    from qpandalite.task.adapters.dummy_adapter import DummyAdapter

    # Create adapter with default settings
    adapter = DummyAdapter()

    # Or with noise simulation
    adapter = DummyAdapter(noise_model={'depol': 0.01})

    # Submit and query (results are immediately available)
    task_id = adapter.submit(originir_circuit, shots=1000)
    result = adapter.query(task_id)

Environment Variable:
    QPANDALITE_DUMMY: Set to 'true', '1', or 'yes' to enable dummy mode
    globally. When set, all task submissions use local simulation instead
    of real quantum backends.
"""

from __future__ import annotations

__all__ = ["DummyAdapter", "QPANDALITE_DUMMY"]

import hashlib
import os
from typing import Any, Dict, List, Optional

from .base import QuantumAdapter, TASK_STATUS_SUCCESS, TASK_STATUS_FAILED
from ..result_types import UnifiedResult
from ..normalizers import normalize_dummy

# Check environment variable for global dummy mode
QPANDALITE_DUMMY = os.environ.get("QPANDALITE_DUMMY", "").lower() in ("true", "1", "yes")


class DummyAdapter(QuantumAdapter):
    """Local simulator adapter that mimics cloud backends.

    This adapter executes circuits locally using the built-in OriginIR
    simulator instead of submitting to real quantum hardware. It provides
    the same interface as cloud adapters, making it a drop-in replacement.

    Features:
    - Immediate result availability (no waiting for queue)
    - Optional noise simulation
    - Deterministic task IDs (based on circuit hash)
    - Same result format as cloud backends

    Attributes:
        name: Adapter identifier ('dummy').
        noise_model: Optional noise configuration for simulation.
        available_qubits: List of qubit indices available for simulation.
        available_topology: List of [u, v] edges defining qubit connectivity.

    Example:
        >>> adapter = DummyAdapter()
        >>> task_id = adapter.submit("QINIT 2\\nH q[0]\\nCNOT q[0] q[1]\\nMEASURE")
        >>> result = adapter.query(task_id)
        >>> print(result['status'])
        'success'
    """

    name = "dummy"

    def __init__(
        self,
        noise_model: Optional[Dict[str, Any]] = None,
        available_qubits: Optional[List[int]] = None,
        available_topology: Optional[List[List[int]]] = None,
    ) -> None:
        """Initialize the DummyAdapter.

        Args:
            noise_model: Optional noise model configuration.
                Supported keys:
                - 'depol': Depolarizing error rate (0.0 to 1.0)
                - 'bitflip': Bit-flip error rate
                - 'readout': Readout error rate
            available_qubits: List of available qubit indices.
            available_topology: List of [u, v] edges for qubit connectivity.

        Raises:
            MissingDependencyError: If simulation dependencies are not installed.
        """
        from ..optional_deps import MissingDependencyError, check_simulation

        if not check_simulation():
            raise MissingDependencyError("qutip", "simulation")

        self.noise_model = noise_model
        self.available_qubits = available_qubits or []
        self.available_topology = available_topology or []
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._simulator_cls = None  # Lazy loaded

    def _get_simulator_cls(self):
        """Lazily load the simulator class."""
        if self._simulator_cls is None:
            from qpandalite.simulator import OriginIR_Simulator
            self._simulator_cls = OriginIR_Simulator
        return self._simulator_cls

    def _generate_task_id(self, circuit: str) -> str:
        """Generate a deterministic task ID from circuit content.

        Uses SHA256 hash of the circuit string to create a unique
        but reproducible task identifier.

        Args:
            circuit: The circuit string.

        Returns:
            16-character hex task ID.
        """
        return hashlib.sha256(circuit.encode()).hexdigest()[:16]

    # -------------------------------------------------------------------------
    # Circuit translation
    # -------------------------------------------------------------------------

    def translate_circuit(self, originir: str) -> str:
        """Return the OriginIR string unchanged.

        The dummy adapter accepts OriginIR directly, so no translation needed.

        Args:
            originir: Circuit in OriginIR format.

        Returns:
            The same OriginIR string.
        """
        return originir

    # -------------------------------------------------------------------------
    # Task submission
    # -------------------------------------------------------------------------

    def submit(
        self,
        circuit: str,
        *,
        shots: int = 1000,
        **kwargs: Any,
    ) -> str:
        """Simulate a circuit locally and cache the result.

        The circuit is executed immediately using the local simulator,
        and results are cached for later retrieval via query().

        Args:
            circuit: Circuit in OriginIR format (or pre-translated).
            shots: Number of measurement shots.
            **kwargs: Additional parameters (ignored for dummy adapter).

        Returns:
            Task ID for result retrieval.
        """
        task_id = self._generate_task_id(circuit)
        try:
            unified_result = self._simulate(circuit, shots)
            self._cache[task_id] = {
                "status": TASK_STATUS_SUCCESS,
                "result": unified_result.to_dict() if hasattr(unified_result, 'to_dict') else {
                    "counts": unified_result.counts,
                    "probabilities": unified_result.probabilities,
                },
                "unified_result": unified_result,
            }
        except Exception as e:
            self._cache[task_id] = {
                "status": TASK_STATUS_FAILED,
                "error": str(e),
            }
        return task_id

    def submit_batch(
        self,
        circuits: List[str],
        *,
        shots: int = 1000,
        **kwargs: Any,
    ) -> List[str]:
        """Simulate multiple circuits locally.

        Args:
            circuits: List of circuits in OriginIR format.
            shots: Number of measurement shots per circuit.
            **kwargs: Additional parameters (ignored).

        Returns:
            List of task IDs, one per circuit.
        """
        return [self.submit(c, shots=shots) for c in circuits]

    # -------------------------------------------------------------------------
    # Task query
    # -------------------------------------------------------------------------

    def query(self, taskid: str) -> Dict[str, Any]:
        """Retrieve the cached result for a task.

        Since dummy tasks are executed immediately on submission,
        results are always available instantly.

        Args:
            taskid: Task identifier.

        Returns:
            Result dict with 'status' and 'result' (or 'error') keys.
        """
        cached = self._cache.get(taskid)
        if cached is None:
            return {
                "status": TASK_STATUS_FAILED,
                "error": f"Task '{taskid}' not found in dummy cache",
            }
        result = {"status": cached["status"]}
        if "result" in cached:
            result["result"] = cached["result"]
        if "error" in cached:
            result["error"] = cached["error"]
        return result

    def query_batch(self, taskids: List[str]) -> Dict[str, Any]:
        """Query multiple tasks and merge results.

        Args:
            taskids: List of task identifiers.

        Returns:
            Combined result dict with overall status and merged results.
        """
        results = []
        overall_status = TASK_STATUS_SUCCESS

        for taskid in taskids:
            task_result = self.query(taskid)
            results.append(task_result.get("result", {}))
            if task_result["status"] == TASK_STATUS_FAILED:
                overall_status = TASK_STATUS_FAILED

        return {
            "status": overall_status,
            "result": results,
        }

    # -------------------------------------------------------------------------
    # Utils
    # -------------------------------------------------------------------------

    def is_available(self) -> bool:
        """Check if the dummy adapter is available.

        Returns:
            True if simulation dependencies are installed.
        """
        from ..optional_deps import check_simulation
        return check_simulation()

    def clear_cache(self) -> None:
        """Clear the internal result cache."""
        self._cache.clear()

    def _simulate(self, originir: str, shots: int) -> UnifiedResult:
        """Run simulation using the OriginIR simulator.

        Args:
            originir: Circuit in OriginIR format.
            shots: Number of shots.

        Returns:
            UnifiedResult with measurement probabilities.

        Raises:
            RuntimeError: If simulation fails.
        """
        Simulator = self._get_simulator_cls()

        # Create simulator with optional constraints
        sim = Simulator(
            available_qubits=self.available_qubits,
            available_topology=self.available_topology,
        )

        # Run simulation to get probability distribution
        probs = sim.simulate_pmeasure(originir)
        n_qubits = sim.qubit_num

        # Convert probability list to dict
        prob_dict = {}
        for i, p in enumerate(probs):
            if p > 0:
                bin_key = bin(i)[2:].zfill(n_qubits)
                prob_dict[bin_key] = float(p)

        # Create unified result
        return UnifiedResult.from_probabilities(
            probabilities=prob_dict,
            shots=shots,
            platform="dummy",
            task_id=self._generate_task_id(originir),
        )

    def _simulate_with_noise(
        self,
        originir: str,
        shots: int,
    ) -> UnifiedResult:
        """Run noisy simulation if noise model is configured.

        Args:
            originir: Circuit in OriginIR format.
            shots: Number of shots.

        Returns:
            UnifiedResult with noisy measurement probabilities.
        """
        # Check if we have a noise model
        if not self.noise_model:
            return self._simulate(originir, shots)

        # Import noisy simulator
        try:
            from qpandalite.simulator import OriginIR_NoisySimulator
            from qpandalite.simulator.error_model import ErrorLoader_GateSpecificError
        except ImportError:
            # Fall back to noiseless simulation
            return self._simulate(originir, shots)

        # Build error loader from noise model
        error_loader = ErrorLoader_GateSpecificError(**self.noise_model)

        # Create noisy simulator
        sim = OriginIR_NoisySimulator(
            error_loader=error_loader,
            available_qubits=self.available_qubits,
            available_topology=self.available_topology,
        )

        # Run simulation
        probs = sim.simulate_pmeasure(originir)
        n_qubits = sim.qubit_num

        prob_dict = {}
        for i, p in enumerate(probs):
            if p > 0:
                bin_key = bin(i)[2:].zfill(n_qubits)
                prob_dict[bin_key] = float(p)

        return UnifiedResult.from_probabilities(
            probabilities=prob_dict,
            shots=shots,
            platform="dummy",
            task_id=self._generate_task_id(originir),
        )