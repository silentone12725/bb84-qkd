#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║   BB84 Quantum Key Distribution Protocol                            ║
║   with Eavesdropper (Eve) Detection                                 ║
║                                                                      ║
║   Course  : AIM3231 — Emerging Tools & Technologies Lab             ║
║   Semester: VI  |  Session: Jan–May 2026                            ║
║   Tools   : Qiskit (primary) / NumPy quantum backend (fallback)     ║
╚══════════════════════════════════════════════════════════════════════╝

Protocol Flow:
  1. Alice  — generates random bits & bases; encodes qubits
  2. Channel — (optional) Eve intercepts, measures, re-encodes
  3. Bob    — measures in random bases
  4. Sifting — Alice & Bob publicly compare bases; discard mismatches
  5. QBER   — sample sifted key to estimate error rate
  6. Decision — QBER > threshold → eavesdropper detected, abort

References:
  • Bennett & Brassard (1984) — original BB84 paper
  • Nielsen & Chuang (2010)  — Quantum Computation & Quantum Information
  • IBM Qiskit Documentation — https://docs.quantum.ibm.com
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ── Qiskit (primary backend) ──────────────────────────────────────────
_QISKIT_AVAILABLE = False
try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    _QISKIT_AVAILABLE = True
    _simulator = AerSimulator()
    print("✅  Qiskit backend loaded — circuits will use AerSimulator.")
except ImportError:
    print("⚠️  Qiskit not found — using NumPy quantum backend (equivalent physics).")
    print("    Install with: pip install qiskit qiskit-aer")
    print()

# ─────────────────────────────────────────────────────────────────────
#  Configuration
# ─────────────────────────────────────────────────────────────────────
NUM_BITS       = 200    # raw qubits transmitted per run
QBER_THRESHOLD = 0.11   # security threshold: >11% QBER → abort
SAMPLE_RATIO   = 0.50   # fraction of sifted key used for QBER check
SEED           = 42


# ═════════════════════════════════════════════════════════════════════
#  BACKEND A — Qiskit Circuits
# ═════════════════════════════════════════════════════════════════════
def _qiskit_encode(bit: int, basis: int) -> "QuantumCircuit":
    """
    Alice encodes a classical bit as a qubit state.

      Basis 0 (Z / Rectilinear) :  0 → |0⟩   1 → |1⟩
      Basis 1 (X / Diagonal)    :  0 → |+⟩   1 → |−⟩

    Gate sequence:
      • bit=1  → X gate  (flip |0⟩ to |1⟩)
      • basis=1 → H gate  (Hadamard: rotates to diagonal basis)
    """
    qc = QuantumCircuit(1, 1)
    if bit == 1:
        qc.x(0)
    if basis == 1:
        qc.h(0)
    return qc


def _qiskit_measure(qc: "QuantumCircuit", basis: int) -> int:
    """
    Measure a qubit in the given basis and return the classical bit.

      Basis 0 (Z) : measure directly
      Basis 1 (X) : apply H first, then measure
                    (rotates |+⟩/|−⟩ back to |0⟩/|1⟩)
    """
    qc = qc.copy()
    if basis == 1:
        qc.h(0)
    qc.measure(0, 0)
    job    = _simulator.run(qc, shots=1)
    counts = job.result().get_counts()
    return int(list(counts.keys())[0])


# ═════════════════════════════════════════════════════════════════════
#  BACKEND B — NumPy (quantum-mechanically equivalent for BB84)
# ═════════════════════════════════════════════════════════════════════
def _numpy_measure(bit: int, encode_basis: int, measure_basis: int) -> int:
    """
    Single-qubit BB84 measurement without Qiskit.

    Physics:
      • Same basis  → deterministic result  (equals encoded bit)
      • Diff basis  → uniformly random      (superposition collapse)

    This is exactly what the Qiskit circuit above computes.
    """
    if encode_basis == measure_basis:
        return bit
    return int(np.random.randint(0, 2))


# ═════════════════════════════════════════════════════════════════════
#  BB84 Protocol — works with either backend
# ═════════════════════════════════════════════════════════════════════
def bb84(n_bits: int, eve_present: bool = False, rng: np.random.Generator = None) -> dict:
    """
    Simulate a full BB84 key exchange.

    Parameters
    ----------
    n_bits      : number of raw qubits Alice transmits
    eve_present : whether Eve intercepts every qubit
    rng         : optional NumPy RNG for reproducibility

    Returns
    -------
    dict with all protocol data (bits, bases, sifted key, QBER, …)
    """
    if rng is None:
        rng = np.random.default_rng(SEED)

    alice_bits  = rng.integers(0, 2, n_bits)
    alice_bases = rng.integers(0, 2, n_bits)
    bob_bases   = rng.integers(0, 2, n_bits)
    eve_bases   = rng.integers(0, 2, n_bits) if eve_present else None

    bob_results = np.empty(n_bits, dtype=int)
    eve_results = np.empty(n_bits, dtype=int) if eve_present else None

    # ── Transmit each qubit ──────────────────────────────────────────
    for i in range(n_bits):

        if _QISKIT_AVAILABLE:
            # ── Qiskit path ──────────────────────────────────────────
            qc = _qiskit_encode(int(alice_bits[i]), int(alice_bases[i]))

            if eve_present:
                eve_bit        = _qiskit_measure(qc, int(eve_bases[i]))
                eve_results[i] = eve_bit
                qc             = _qiskit_encode(eve_bit, int(eve_bases[i]))

            bob_results[i] = _qiskit_measure(qc, int(bob_bases[i]))

        else:
            # ── NumPy path ───────────────────────────────────────────
            if eve_present:
                eve_bit        = _numpy_measure(int(alice_bits[i]),
                                                int(alice_bases[i]),
                                                int(eve_bases[i]))
                eve_results[i] = eve_bit
                # Eve re-transmits her measured bit in her own basis
                bob_results[i] = _numpy_measure(eve_bit,
                                                int(eve_bases[i]),
                                                int(bob_bases[i]))
            else:
                bob_results[i] = _numpy_measure(int(alice_bits[i]),
                                                int(alice_bases[i]),
                                                int(bob_bases[i]))

    # ── Sifting ───────────────────────────────────────────────────────
    match        = alice_bases == bob_bases          # publicly compared
    sifted_alice = alice_bits[match]
    sifted_bob   = bob_results[match]

    # ── QBER on random sample ─────────────────────────────────────────
    n_sifted = len(sifted_alice)
    n_sample = max(1, int(n_sifted * SAMPLE_RATIO))
    idx      = rng.choice(n_sifted, n_sample, replace=False)
    errors   = int(np.sum(sifted_alice[idx] != sifted_bob[idx]))
    qber     = errors / n_sample

    # ── Final key (bits not used for QBER check) ──────────────────────
    key_mask  = np.ones(n_sifted, dtype=bool)
    key_mask[idx] = False
    final_key = sifted_alice[key_mask]

    return dict(
        # raw data
        alice_bits  = alice_bits,
        alice_bases = alice_bases,
        bob_bases   = bob_bases,
        bob_results = bob_results,
        eve_bases   = eve_bases,
        eve_results = eve_results,
        # sifted key
        match        = match,
        sifted_alice = sifted_alice,
        sifted_bob   = sifted_bob,
        # QBER
        qber        = qber,
        n_sample    = n_sample,
        n_errors    = errors,
        # final key
        final_key   = final_key,
        # counts
        n_raw       = n_bits,
        n_sifted    = n_sifted,
        n_key       = len(final_key),
        # meta
        eve_present = eve_present,
        detected    = qber > QBER_THRESHOLD,
        backend     = "Qiskit" if _QISKIT_AVAILABLE else "NumPy",
    )


# ═════════════════════════════════════════════════════════════════════
#  Report
# ═════════════════════════════════════════════════════════════════════
def print_report(res_clean: dict, res_eve: dict):
    W = 62
    print('\n' + '═' * W)
    print('  BB84 Quantum Key Distribution — Simulation Report')
    print(f'  Backend : {res_clean["backend"]}')
    print('═' * W)

    for label, res in [('Scenario A — No Eavesdropper', res_clean),
                        ('Scenario B — Eve Present',     res_eve)]:
        print(f'\n  ── {label} ──')
        print(f'    Raw qubits transmitted  : {res["n_raw"]}')
        print(f'    Sifted key length       : {res["n_sifted"]:>4}  '
              f'({res["n_sifted"]/res["n_raw"]*100:.1f}% of raw)')
        print(f'    Bits used for QBER check: {res["n_sample"]:>4}')
        print(f'    Errors in QBER sample   : {res["n_errors"]:>4}')
        print(f'    QBER                    : {res["qber"]*100:>6.2f}%')
        print(f'    Security threshold      : {QBER_THRESHOLD*100:>6.1f}%')
        status = '🚨 EAVESDROPPER DETECTED — KEY DISCARDED' \
                 if res['detected'] else '✅ CHANNEL SECURE — KEY ACCEPTED'
        print(f'    Decision                : {status}')
        print(f'    Final key length        : {res["n_key"]} bits')

    print('\n' + '─' * W)
    print('  Theory vs Simulation')
    print(f'    Expected QBER (no Eve) : ~0.00%')
    print(f'    Expected QBER (Eve)    : ~25.00%')
    print(f'    Observed  (no Eve)     : {res_clean["qber"]*100:.2f}%')
    print(f'    Observed  (with Eve)   : {res_eve["qber"]*100:.2f}%')
    print('═' * W + '\n')
