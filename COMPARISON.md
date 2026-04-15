# PR Comparison: Our fixes vs Agony's PR #140

Agony's open PR: `Agony5757/QPanda-lite#140` (`fix/issue#133#134`)  
Our branch: `fix/ci-r1r3r10` (and merge branch `fix/ci-r1r3r10-merge-agony`)

---

## Axis 1 — Qubit-list design pattern (R3 / R6)

Agony changed several algorithm circuit signatures to require explicit qubit lists (`qubits: List[int]`, no default), replacing integer counts like `n_eval_qubits: int` with `eval_qubits: List[int]`. The philosophy is: *the caller owns register layout; the function never consults `circuit.qubit_num`*, which structurally prevents the empty-circuit R6 bug.

**Decision: adopt Agony's design.** His "caller owns register layout" approach is structurally cleaner than our defensive `qubits=None` guards — R6 becomes impossible by construction rather than patched away case-by-case. Rejecting his API just to avoid breakage was short-sighted; the project is still pre-1.0 and the new contract is strictly saner.

**Things we still keep from our side while adopting his API:**

- **R3 QAE phase formula fix** (`theta = π·m / 2^(M+1)`). Agony's PR left the formula wrong and changed the test to match; we keep the correct formula and keep our test assertion. When we port to his signature, the test gets rewritten to pass explicit lists, but the numerical assertion stays `sin²(π·7/16)`.
- **R9 Grover oracle fix** (proper `H·MCX·H` MCZ decomposition + LSB bit-ordering). Independent of the qubit-list API.
- **`w_state` None-default fix.** Agony's body asserts `isinstance(qubits, list)` while the signature still has `qubits=None` default — crashes on the default. We adopt his SCUC dispatch body but require `qubits` to be an explicit list (either drop the default or handle `None` before the assert).

**Also cherry-picked (non-breaking helpers):**

1. `Circuit.add_circuit(other)` in `qcircuit.py` — replays opcodes via `add_gate(*op)`. ✅ Done in `b1924d6`.
2. `dicke_state_circuit` SCUC rewrite — algorithmically cleaner (CNOT + Ry only, no `rotation_prepare`), public signature preserved. ✅ Done in `b1924d6`.

---

## Axis 2 — Classical shadow (R2)

**Agony's fix (~25 substantive lines):** Surgical correction of the inversion formula in `shadow_expectation` only:

```python
# before (wrong)        after (Agony)
s = 3.0 * ev - 1.0  →  s = 3.0 * ev   # aligned basis
s = -1.0            →  s = 0.0        # misaligned basis
```

Also fixes the median-of-means estimator structure (inner stat should be `mean`, outer `median`) and switches batch slicing to `np.array_split`.

**Our fix (~80 substantive lines, +12 net):** Algorithmic overhaul in `classical_shadow.py`:

1. **`ShadowSnapshot.counts`** — store the full shots histogram per snapshot, not a single sampled bitstring.
2. **Stratified basis sampling** — when `n_shadow ≥ 3^n`, cycle through every Pauli-basis combination equally (`itertools.product(range(3), repeat=n)`). Eliminates `3^n` basis-selection variance entirely.
3. **LSB-first bit-ordering** — `(outcomes_int >> i) & 1`. Agony left the original MSB-first convention untouched (latent bug for asymmetric Pauli strings like `IZX`).
4. **Inversion formula** — single prefactor `3^m` (m = # non-identity Paulis) + Born expectation over the full counts distribution, rather than a single sampled outcome.

**Why ours is better:**

- Fixes **two** bugs (formula + bit-ordering); Agony fixes one.
- The 5 failing shadow tests go from "passes with lucky seed" to "passes deterministically" — stratified sampling removes basis-selection variance for small `n`.
- Backward-compatible: `counts` defaults to `{}`, fallback path handles old-style snapshots.
- The only tradeoff: median-of-means is removed (documented in docstring — suboptimal for a single observable, only useful when estimating many Paulis from a shared snapshot set).

**Decision: keep our `classical_shadow.py` verbatim.**

---

## Axis 3 — R7 (basis_rotation) / R8 (state_tomography): divergent LSB-first fixes

Both sides tried to fix the bit-ordering issue in the measurement stack, but landed on **opposite conventions**.

### R7 — `basis_rotation.py`

| | Agony | Ours (`599fd20`) |
|---|---|---|
| Source change | 5-line index remap: `i = n-1-j` inside the rotation-gate injection loop | **Source unchanged** — kept the existing `basis[i]` ↔ qubit `i` mapping |
| Test rewrite | `basis=["Z","X"]` → `"00"=1.0` (his new MSB convention) | `basis=["X","Z"]` → `"00"=1.0` (LSB convention — matches state_tomography / classical_shadow), plus added `basis_list == basis_str` equivalence check |
| Resulting convention | **MSB-first**: `basis[0]` refers to qubit `n-1` | **LSB-first**: `basis[0]` refers to qubit `0` |

These fixes are **semantically opposite**. Cherry-picking his source would break our test; cherry-picking his test would force us to revert our source reading.

### R8 — `state_tomography.py`

| | Agony | Ours (`599fd20`) |
|---|---|---|
| Source change | **File untouched** | Three independent LSB-first bit-encoding fixes: (a) diagonal Pauli sign extraction `(outcome >> i) & 1`, (b) Pauli tensor operand order `reversed(p[:-1])`, (c) density-matrix element reconstruction |
| How test passes | Presumably never failed on Agony's seed; or R8 was masked by his other changes | Test `test_ghz3_purity` actually tests the reconstruction — only passes with the three fixes |
| Test-file diff | Added a `print(rho)` debug line (no assertion change) | No test changes |

**R8 did NOT auto-cascade from R7 as CLAUDE.md hypothesised.** State tomography has its own three bit-indexing bugs that had to be fixed independently.

### Decision

**Keep ours on both R7 and R8.** LSB-first is the more internally consistent choice: `state_tomography.py`, `classical_shadow.py`, and `grover_oracle.py` are all LSB-first on our branch. Adopting Agony's MSB-first `basis_rotation.py` would create a module-to-module inconsistency.

When upstream PR #140 review happens, push back on Agony's `basis_rotation.py` convention — or ask the project to formally commit to LSB-first everywhere (which is what we've done).

---

## Summary

| Item | Decision | Status |
|---|---|---|
| `Circuit.add_circuit()` helper | Cherry-pick from Agony | ✅ done (`b1924d6`) |
| `dicke_state_circuit` SCUC rewrite | Cherry-pick from Agony | ✅ done (`b1924d6`) |
| AE / DJ / w_state signature change | **Adopt from Agony** (+ keep R3 formula fix + fix w_state None-default bug) | in progress |
| `basis_rotation.py` R7 source change | Reject — LSB convention conflict (Axis 3) | — |
| `state_tomography.py` R8 | Keep ours — Agony didn't touch; R8 is independent of R7 (Axis 3) | ✅ already in branch |
| `classical_shadow.py` minimal fix | Reject — ours is strictly better | — |
| R3 (QAE formula `2^(M+1)`) | Keep ours — his test matches wrong formula | ✅ already in branch |
| R9 (Grover MCZ + LSB) | Keep ours — his PR skips grover_oracle.py | ✅ already in branch |
