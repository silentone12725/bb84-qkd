"""
app.py — Flask web interface for the BB84 QKD simulation.

Run:   python app.py
Visit: http://localhost:5000
"""

import io, base64, sys, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, jsonify, request
from bb84_simulation import bb84, QBER_THRESHOLD
from bb84_plots import (
    fig_encoding_circuits,
    fig_protocol_table,
    fig_qber_comparison,
    fig_key_waterfall,
    fig_qber_statistics,
)

app = Flask(__name__)


# ─────────────────────────────────────────────
#  Helper
# ─────────────────────────────────────────────
def fig_to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=200, bbox_inches='tight',  # Increased from 130
                facecolor=fig.get_facecolor())
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return data


def result_to_steps(result: dict, n_show: int = 30) -> list:
    """Convert simulation result to a JSON-serialisable step list."""
    n = min(n_show, result['n_raw'])
    steps = []
    for i in range(n):
        s = dict(
            idx         = i,
            alice_bit   = int(result['alice_bits'][i]),
            alice_basis = int(result['alice_bases'][i]),
            bob_basis   = int(result['bob_bases'][i]),
            bob_result  = int(result['bob_results'][i]),
            match       = bool(result['match'][i]),
        )
        if result['eve_present']:
            s['eve_basis']  = int(result['eve_bases'][i])
            s['eve_result'] = int(result['eve_results'][i])
        steps.append(s)
    return steps


def result_to_table_data(result: dict, n_show: int = 50) -> dict:
    """Convert simulation result to table data for HTML rendering."""
    n = min(n_show, result['n_raw'])
    eve = result['eve_present']
    
    # Column indices
    columns = list(range(1, n + 1))
    
    # Build rows
    alice_bits = [int(result['alice_bits'][i]) for i in range(n)]
    alice_bases = ['Z' if result['alice_bases'][i] == 0 else 'X' for i in range(n)]
    bob_bases = ['Z' if result['bob_bases'][i] == 0 else 'X' for i in range(n)]
    bob_results = [int(result['bob_results'][i]) for i in range(n)]
    matches = [bool(result['match'][i]) for i in range(n)]
    
    # Calculate errors for matched pairs
    errors = []
    for i in range(n):
        if matches[i]:
            errors.append(alice_bits[i] != bob_results[i])
        else:
            errors.append(False)
    
    table_data = {
        'columns': columns,
        'alice_bits': alice_bits,
        'alice_bases': alice_bases,
        'bob_bases': bob_bases,
        'bob_results': bob_results,
        'matches': matches,
        'errors': errors,
        'eve_present': eve
    }
    
    if eve:
        table_data['eve_bases'] = ['Z' if result['eve_bases'][i] == 0 else 'X' for i in range(n)]
        table_data['eve_results'] = [int(result['eve_results'][i]) for i in range(n)]
    
    return table_data


# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html',
                           threshold=int(QBER_THRESHOLD * 100))


@app.route('/simulate', methods=['POST'])
def simulate():
    body    = request.get_json(force=True)
    n_bits  = max(20, min(400, int(body.get('n_bits', 150))))
    eve     = bool(body.get('eve', False))
    seed    = int(body.get('seed', 42))
    n_show  = min(50, n_bits)  # Increased from 30 to 50 to show more columns

    # ── Run simulations ──────────────────────────────────────────────
    rng_a = np.random.default_rng(seed)
    rng_b = np.random.default_rng(seed + 999)

    res_clean = bb84(n_bits, eve_present=False, rng=rng_a)
    res_eve   = bb84(n_bits, eve_present=True,  rng=rng_b)

    # Active scenario (for the animation)
    active = res_eve if eve else res_clean

    # ── Figures ──────────────────────────────────────────────────────
    figs = {}
    figs['encoding']   = fig_to_b64(fig_encoding_circuits())
    # Protocol tables now sent as data, not images
    figs['qber']       = fig_to_b64(fig_qber_comparison(res_clean, res_eve))
    figs['waterfall']  = fig_to_b64(fig_key_waterfall(res_clean, res_eve))
    figs['statistics'] = fig_to_b64(fig_qber_statistics(n_trials=40))

    # ── Response ─────────────────────────────────────────────────────
    return jsonify(dict(
        steps   = result_to_steps(active, n_show),
        eve     = eve,
        table_clean = result_to_table_data(res_clean, n_show),
        table_eve = result_to_table_data(res_eve, n_show),
        summary = dict(
            n_raw      = active['n_raw'],
            n_sifted   = active['n_sifted'],
            n_sample   = active['n_sample'],
            n_errors   = active['n_errors'],
            n_key      = active['n_key'],
            qber       = round(active['qber'] * 100, 2),
            threshold  = round(QBER_THRESHOLD * 100, 1),
            detected   = active['detected'],
            backend    = active['backend'],
        ),
        figures = figs,
    ))


if __name__ == '__main__':
    print('\n  BB84 QKD Visualizer')
    print('  ─────────────────────────────')
    print('  Open → http://localhost:5000')
    print('  Ctrl+C to stop\n')
    app.run(debug=True, port=5000)
