#!/usr/bin/env python3
"""
main.py — Run the full BB84 QKD simulation and generate all figures.

Usage:
    python main.py

Output:
    Prints protocol report to stdout.
    Saves 6 PNG figures to ./figures/
"""

import os
import sys
import numpy as np

# ── ensure local modules are importable ──────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from bb84_simulation import bb84, print_report, NUM_BITS, SEED
from bb84_plots import (
    fig_encoding_circuits,
    fig_protocol_table,
    fig_qber_comparison,
    fig_key_waterfall,
    fig_qber_statistics,
)

import matplotlib
matplotlib.use('Agg')   # headless rendering

OUT = os.path.join(os.path.dirname(__file__), 'figures')
os.makedirs(OUT, exist_ok=True)

# ═════════════════════════════════════════════════════════════════════
#  Run simulations
# ═════════════════════════════════════════════════════════════════════
print('\n' + '─' * 62)
print('  AIM3231 — BB84 QKD Mini Project')
print('─' * 62)
print(f'  Simulating {NUM_BITS} qubits (seed={SEED}) ...\n')

rng_a = np.random.default_rng(SEED)
rng_b = np.random.default_rng(SEED + 1)   # different seed so Eve run differs

result_clean = bb84(NUM_BITS, eve_present=False, rng=rng_a)
result_eve   = bb84(NUM_BITS, eve_present=True,  rng=rng_b)

# ── Print report ─────────────────────────────────────────────────────
print_report(result_clean, result_eve)

# ═════════════════════════════════════════════════════════════════════
#  Generate figures
# ═════════════════════════════════════════════════════════════════════
print('  Generating figures ...')

fig_encoding_circuits(save_path=f'{OUT}/fig1_encoding_circuits.png')
fig_protocol_table(result_clean, n_show=18,
                   save_path=f'{OUT}/fig2_protocol_no_eve.png')
fig_protocol_table(result_eve,   n_show=18,
                   save_path=f'{OUT}/fig3_protocol_with_eve.png')
fig_qber_comparison(result_clean, result_eve,
                    save_path=f'{OUT}/fig4_qber_comparison.png')
fig_key_waterfall(result_clean, result_eve,
                  save_path=f'{OUT}/fig5_key_waterfall.png')
fig_qber_statistics(n_trials=60,
                    save_path=f'{OUT}/fig6_qber_statistics.png')

print('\n  ✅  All figures saved to ./figures/')
print('─' * 62 + '\n')
