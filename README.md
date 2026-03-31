# BB84 Quantum Key Distribution Simulator
### AIM3231 — Emerging Tools & Technologies Lab | VI Semester | Jan–May 2026
### Manipal University Jaipur — B.Tech CSE (AI & ML)

---

## What This Project Does

This project simulates the **BB84 Quantum Key Distribution (QKD) protocol** — the first and most widely studied quantum cryptography scheme, proposed by Bennett & Brassard in 1984.

It demonstrates two things:

1. How two parties (Alice and Bob) can establish a shared secret key over a public quantum channel with **information-theoretic security** — security guaranteed by the laws of physics, not computational hardness.
2. How the presence of an eavesdropper (Eve) is **automatically detected** through a statistical anomaly in the error rate of the exchanged key, without Alice or Bob ever knowing what Eve measured.

The project ships with both a **command-line runner** and a **Flask web interface** that animates the protocol step by step and renders all analysis figures inline.

---

## The Problem Being Solved

Classical encryption (RSA, ECC) derives its security from the difficulty of factoring large numbers. Shor's quantum algorithm breaks this in polynomial time. As quantum hardware matures, all currently encrypted data becomes vulnerable — including data recorded today and decrypted later ("harvest now, decrypt later" attacks).

BB84 solves this at the physics level. Its security rests on the **No-Cloning Theorem**: an unknown quantum state cannot be perfectly copied. Any interception attempt disturbs the qubits, leaving a measurable trace.

---

## Protocol Walkthrough

```
  Alice                  Quantum Channel                   Bob
    │                                                        │
    │  Encodes each bit as a qubit in a random basis         │
    │  Z-basis : 0 → |0⟩    1 → |1⟩  (Rectilinear)         │
    │  X-basis : 0 → |+⟩    1 → |−⟩  (Diagonal)            │
    │ ─────────────────────────────────────────────────────► │
    │                                                        │
    │              ┌─────────────────┐                       │
    │   (optional) │  Eve intercepts │                       │
    │              │  measures &     │                       │
    │              │  re-transmits   │                       │
    │              └─────────────────┘                       │
    │                                                        │
    │ ◄──── Classical channel: compare bases (public) ──────►│
    │                                                        │
    │       Sifting: discard bits where bases differ         │
    │       ~50% of qubits survive this step                 │
    │                                                        │
    │       QBER check: sacrifice a sample of sifted key     │
    │       Compare actual bit values — errors reveal Eve    │
    │                                                        │
    │  QBER < 11% → Channel secure, key accepted             │
    │  QBER > 11% → Eavesdropper detected, key discarded     │
```

### The 4 BB84 States

| Bit | Basis | Qubit State | Gate Sequence |
|-----|-------|-------------|---------------|
|  0  |  Z    |   \|0⟩      | (none)        |
|  1  |  Z    |   \|1⟩      | X             |
|  0  |  X    |   \|+⟩      | H             |
|  1  |  X    |   \|−⟩      | X → H        |

### Why Eve Gets Caught — The Math

Eve must guess Alice's basis with no information. She is right 50% of the time.

When Eve guesses wrong, she measures in the wrong basis, collapsing the superposition. The bit she re-sends to Bob is then random — giving Bob a 50% chance of getting the wrong answer even when his basis matches Alice's.

```
P(error | Eve present) = P(Eve wrong basis) × P(Bob gets wrong bit)
                       = 0.5 × 0.5
                       = 0.25  →  25% QBER
```

A clean channel produces 0% QBER. The 11% threshold is chosen to allow for realistic hardware noise while still reliably detecting Eve.

---

## Simulation Results

```
── Scenario A — No Eavesdropper ──────────────────────
  Raw qubits transmitted   : 200
  Sifted key length        :  93   (46.5% of raw)
  Bits used for QBER check :  46
  Errors in QBER sample    :   0
  QBER                     :  0.00%
  Security threshold       : 11.0%
  Decision                 : ✅ CHANNEL SECURE — KEY ACCEPTED
  Final key length         : 47 bits

── Scenario B — Eve Present ──────────────────────────
  Raw qubits transmitted   : 200
  Sifted key length        : 103   (51.5% of raw)
  Bits used for QBER check :  51
  Errors in QBER sample    :  13
  QBER                     : 25.49%
  Security threshold       : 11.0%
  Decision                 : 🚨 EAVESDROPPER DETECTED — KEY DISCARDED

Theory vs Simulation
  Expected QBER (no Eve)   :  ~0.00%
  Expected QBER (Eve)      : ~25.00%
  Observed  (no Eve)       :   0.00%  ✓
  Observed  (with Eve)     :  25.49%  ✓
```

---

## Folder Structure

```
bb84_qkd/
│
├── app.py                    ← Flask server — serves UI, runs simulation on demand
├── bb84_simulation.py        ← Core BB84 protocol (Qiskit + NumPy dual backend)
├── bb84_plots.py             ← All 6 matplotlib analysis figures
├── main.py                   ← Standalone CLI runner, saves figures to /figures/
├── README.md                 ← This file
│
├── templates/
│   └── index.html            ← Full web UI: channel animation + protocol table + figures
│
└── figures/                  ← Pre-generated PNGs (from main.py)
    ├── fig1_encoding_circuits.png
    ├── fig2_protocol_no_eve.png
    ├── fig3_protocol_with_eve.png
    ├── fig4_qber_comparison.png
    ├── fig5_key_waterfall.png
    └── fig6_qber_statistics.png
```

---

## Installation & Running

```bash
# 1. Install dependencies
pip install flask qiskit qiskit-aer matplotlib numpy

# 2a. Web interface (recommended — includes live animation + all figures)
python app.py
# Open http://localhost:5000

# 2b. CLI only (generates figures to /figures/, prints report to terminal)
python main.py
```

The code automatically detects whether Qiskit is installed. If not, it falls back to a **NumPy quantum backend** that implements identical physics — same probability rules, same QBER values.

---

## Web Interface — Section by Section

| Section | What it shows |
|---------|---------------|
| **01 Controls** | Qubit count slider (20–300), animation speed, Eve toggle |
| **02 Quantum Channel** | Animated Alice → (Eve) → Bob with flying qubit particles. Cyan circles = Z-basis, purple squares = X-basis. Eve's box pulses red when active. |
| **03 Protocol Trace** | Table builds row-by-row during animation. Green rows = sifted key, dim rows = discarded, red cells = errors. Live QBER counter updates in real time. |
| **04 Analysis Figures** | All 6 matplotlib figures rendered inline after simulation completes. Figures are generated fresh for each run in memory — they always match the active scenario. |

---

## Analysis Figures

| # | Figure | What it demonstrates |
|---|--------|----------------------|
| 1 | Encoding circuits | The 4 qubit states Alice prepares (gate diagrams) |
| 2 | Protocol table — no Eve | Qubit-by-qubit trace: bases, bits, match/discard |
| 3 | Protocol table — Eve present | Same trace with Eve's basis and result columns; errors visible |
| 4 | QBER comparison | Side-by-side bar chart: 0% vs ~25%, with security threshold line |
| 5 | Key length waterfall | Raw → sifted → QBER sample → final key for both scenarios |
| 6 | QBER over 40 trials | Scatter plot showing statistical separation between clean and Eve runs |

---

## Course Outcomes Addressed

| CO Code     | Bloom's Level | How Addressed |
|-------------|---------------|---------------|
| AIM3231.2   | 3 — Apply     | Pauli-X and Hadamard gates used in encoding circuits |
| AIM3231.3   | 4 — Analyze   | Basis mismatch produces probabilistic measurement outcomes; QBER analysis |
| AIM3231.4   | 3 — Apply     | No-Cloning Theorem and measurement disturbance underpin security proof |
| AIM3231.5   | 6 — Create    | Full BB84 pipeline designed, implemented, and validated against theory |

---

## References

1. Bennett, C. H., & Brassard, G. (1984). *Quantum cryptography: Public key distribution and coin tossing.* Proceedings of IEEE International Conference on Computers, Systems, and Signal Processing, 175–179.
2. Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and Quantum Information* (10th Anniversary Ed.). Cambridge University Press.
3. Singh, P. N., & Navaneetha, M. (2026). *Exploring Quantum Circuits, Quantum Cryptography and Post-Quantum Computing Using Qiskit in Python.* IC3IA 2025, Algorithms for Intelligent Systems. Springer, Singapore. https://doi.org/10.1007/978-981-96-7473-2_23
4. IBM Quantum Documentation — https://docs.quantum.ibm.com
5. Loredo, R. (2020). *Learn Quantum Computing with Python and IBM Quantum Experience.* Packt Publishing.
