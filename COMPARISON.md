# Implementation Comparison: dicke_state SCUC Rewrite

This document compares the Dicke state preparation implementation in this branch
(`fix/ci-r1r3r10`) against the upstream fix in `Agony5757/QPanda-lite`
(`fix/issue#133#134`).

## Algorithm Level: Identical

Both implementations use the **SCUC (Sequential Conditional Unitary Cascade)**
algorithm from Bärtschi & Eidenbenz (2019), arXiv:1904.07358.
The high-level structure is the same in both:

1. **Initialization**: Apply X to the **last k qubits** to create |00…011…1⟩.
2. **first_block**: for l = n, n−1, …, k+1 — apply SCS_{l,k} to
   `qubits[l−k−1 : l]` (the rightmost k+1 qubits of the first-l window).
3. **second_block**: for l = k, k−1, …, 2 — apply SCS_{l,l−1} to
   `qubits[0 : l]`.

The rotation angles are also identical: for SCS_{m,l}, the 2-qubit gate uses
`θ = arccos(√(1/m))` and the 3-qubit gate uses `θ = arccos(√(l/m))` for
each inner index l.

## Gate Decomposition Level: Different

The two implementations differ in how they decompose the controlled-rotation
primitives required by the SCS units.

### CRY (singly-controlled RY)

| | Implementation |
|---|---|
| **Upstream (Agony)** | Manual decomposition: `Ry(θ/2) · CX(ctrl,tgt) · Ry(−θ/2) · CX(ctrl,tgt)` |
| **This branch** | Native `add_gate("RY", tgt, params=θ, control_qubits=[ctrl])`, which the QPanda-lite QASM layer maps directly to `cry` (in `available_qasm_2q1p_gates`) |

### CCRY (doubly-controlled RY)

Neither QPanda-lite implementation supports a native `ccry` gate (it is not in
`qpandalite/circuit_builder/qasm_spec.py`'s gate set), so both must decompose it.

| | Decomposition | Gate count |
|---|---|---|
| **Upstream (Agony)** | Gray-code V-chain: `CRy(ctrl2,tgt, θ/2) · CX(ctrl1,ctrl2) · CRy(ctrl2,tgt, −θ/2) · CX(ctrl1,ctrl2) · CRy(ctrl1,tgt, θ/2)` | 5 gates (3 CRY + 2 CX) |
| **This branch** | Toffoli sandwich: `CRy(ctrl2,tgt, θ/2) · CCX(ctrl1,ctrl2,tgt) · CRy(ctrl2,tgt, −θ/2) · CCX(ctrl1,ctrl2,tgt)` | 4 gates (2 CRY + 2 Toffoli) |

Both decompositions are standard textbook methods and are numerically equivalent.
Correctness is verified by the same test suite (all 10 tests pass on both paths).

### Why Toffoli here

The Toffoli gate (`ccx`) is a native 3-qubit gate in QPanda-lite's QASM spec
(`available_qasm_3q_gates`), so the Toffoli-sandwich decomposition avoids
introducing extra single-qubit `Ry` pulses outside a CRY context.
The Gray-code decomposition is also valid and has one fewer Toffoli call if
the backend has efficient CRY but expensive Toffoli; the choice is backend-dependent.

## Reference

This branch's implementation was derived independently from:

- **andre-juan/dicke_states_preparation** — `dicke_states.py`
  (<https://github.com/andre-juan/dicke_states_preparation/blob/main/dicke_states.py>)
  A Qiskit reference implementation of the Bärtschi & Eidenbenz (2019) SCUC
  algorithm, with `gate_i`, `gate_ii_l`, and `SCS_{n,k}` matching the paper
  directly. Used as the structural template for this rewrite; gate decompositions
  were then adapted to QPanda-lite's available gate set.

- **Bärtschi & Eidenbenz (2019)** — "Deterministic Preparation of Dicke States",
  arXiv:1904.07358.

The upstream fix (`Agony5757/QPanda-lite`, branch `fix/issue#133#134`) was
discovered via `git fetch upstream` *after* the rewrite was complete.
The algorithmic convergence confirms both implementations follow the paper correctly.
