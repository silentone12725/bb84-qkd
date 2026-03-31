"""
bb84_plots.py — Dark-mode matplotlib figures for BB84 QKD project.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MaxNLocator

QBER_THRESHOLD = 0.11
BASIS_SYM = {0: 'Z', 1: 'X'}

D = dict(
    bg        = '#080c14',
    bg2       = '#0d1320',
    bg3       = '#111927',
    border    = '#1e2d45',
    text      = '#c8d8e8',
    text_dim  = '#5a7a9a',
    cyan      = '#00e5ff',
    cyan_dim  = '#007a8a',
    purple    = '#b060ff',
    green     = '#00e676',
    amber     = '#ffab40',
    red       = '#ff5252',
    blue      = '#42a5f5',
    grid      = '#1a2a3f',
)


def _dark_axes(ax, facecolor=None):
    ax.set_facecolor(facecolor or D['bg2'])
    ax.tick_params(colors=D['text_dim'], labelsize=9)
    ax.xaxis.label.set_color(D['text'])
    ax.yaxis.label.set_color(D['text'])
    ax.title.set_color(D['text'])
    for spine in ax.spines.values():
        spine.set_edgecolor(D['border'])
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(color=D['grid'], linewidth=0.8, zorder=0)


def _dark_fig(fig):
    fig.patch.set_facecolor(D['bg'])


def _legend(ax, **kw):
    return ax.legend(facecolor=D['bg3'], edgecolor=D['border'],
                     labelcolor=D['text'], fontsize=9, **kw)


# ── Fig 1 — Encoding States ───────────────────────────────────────────
def fig_encoding_circuits(save_path=None):
    try:
        from qiskit import QuantumCircuit
        fig, axes = plt.subplots(1, 4, figsize=(14, 3.0))
        _dark_fig(fig)
        configs = [
            (0, 0, '|0⟩  bit=0, Z-basis'),
            (1, 0, '|1⟩  bit=1, Z-basis'),
            (0, 1, '|+⟩  bit=0, X-basis'),
            (1, 1, '|−⟩  bit=1, X-basis'),
        ]
        for ax, (bit, basis, title) in zip(axes, configs):
            qc = QuantumCircuit(1, 1)
            if bit == 1: qc.x(0)
            if basis == 1: qc.h(0)
            qc.draw('mpl', ax=ax, style='bw')
            ax.set_facecolor(D['bg2'])
            ax.set_title(title, fontsize=9, fontweight='bold', pad=8,
                         color=D['cyan'] if basis == 0 else D['purple'])
        fig.suptitle("Alice's 4 BB84 Encoding Circuits",
                     fontsize=13, fontweight='bold', color=D['text'], y=1.02)
    except ImportError:
        fig, ax = plt.subplots(figsize=(12, 3.8))
        _dark_fig(fig)
        ax.set_facecolor(D['bg'])
        ax.axis('off')
        rows = [
            ['State',   '|0⟩',       '|1⟩',       '|+⟩',       '|−⟩'     ],
            ['Bit',     '0',          '1',          '0',          '1'       ],
            ['Basis',   'Z  (↕)',     'Z  (↕)',     'X  (↗)',     'X  (↗)'  ],
            ['Gates',   '(none)',     'X gate',     'H gate',     'X → H'   ],
            ['State',   '|0⟩→|0⟩',  '|0⟩→|1⟩',  '|0⟩→|+⟩',  '|0⟩→|−⟩'],
        ]
        cc = [
            [D['bg3']] * 5,
            [D['bg3'], D['cyan_dim'], D['cyan_dim'], '#3a1060', '#3a1060'],
            [D['bg3'], D['cyan_dim'], D['cyan_dim'], '#3a1060', '#3a1060'],
            [D['bg3'], D['cyan_dim'], D['cyan_dim'], '#3a1060', '#3a1060'],
            [D['bg3'], D['cyan_dim'], D['cyan_dim'], '#3a1060', '#3a1060'],
        ]
        tbl = ax.table(cellText=rows, cellColours=cc, cellLoc='center', loc='center')
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(11)
        tbl.scale(1.2, 2.5)
        for (ri, ci), cell in tbl.get_celld().items():
            cell.set_edgecolor(D['border'])
            if ri == 0 or ci == 0:
                cell.set_text_props(color=D['text_dim'], fontweight='bold')
            elif ci in (1, 2):
                cell.set_text_props(color=D['cyan'])
            else:
                cell.set_text_props(color=D['purple'])
        ax.set_title("Alice's 4 BB84 Encoding States — Gate Reference",
                     fontsize=13, fontweight='bold', color=D['text'], pad=14)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches='tight', facecolor=D['bg'])  # Increased DPI
        print(f'  Saved → {save_path}')
    return fig


# ── Fig 2/3 — Protocol Table ──────────────────────────────────────────
def fig_protocol_table(result, n_show=18, save_path=None):
    n   = min(n_show, result['n_raw'])
    eve = result['eve_present']
    ab  = result['alice_bits'][:n]
    aba = result['alice_bases'][:n]
    bb  = result['bob_bases'][:n]
    br  = result['bob_results'][:n]
    m   = result['match'][:n]

    row_labels = ['Alice bit', 'Alice basis', 'Bob basis', 'Bob result', 'Basis match']
    row_data   = [
        [str(b) for b in ab],
        [BASIS_SYM[b] for b in aba],
        [BASIS_SYM[b] for b in bb],
        [str(b) for b in br],
        ['✓' if x else '✗' for x in m],
    ]

    if eve:
        eb = result['eve_bases'][:n]
        er = result['eve_results'][:n]
        row_labels = ['Alice bit','Alice basis','⚠ Eve basis','⚠ Eve result',
                      'Bob basis','Bob result','Basis match']
        row_data   = [
            [str(b) for b in ab],
            [BASIS_SYM[b] for b in aba],
            [BASIS_SYM[b] for b in eb],
            [str(b) for b in er],
            [BASIS_SYM[b] for b in bb],
            [str(b) for b in br],
            ['✓' if x else '✗' for x in m],
        ]

    # Increased width: 1.2 per column (was 0.75)
    height  = 0.58 * len(row_labels) + 1.0
    fig, ax = plt.subplots(figsize=(max(20, n * 1.2), height))
    _dark_fig(fig)
    ax.set_facecolor(D['bg'])
    ax.axis('off')

    cell_colors = []
    for ri, row in enumerate(row_data):
        row_clr = []
        label = row_labels[ri]
        for ci, val in enumerate(row):
            matched = m[ci]
            error   = (ab[ci] != br[ci])
            if 'match' in label.lower():
                row_clr.append('#0a3320' if val == '✓' else '#2d0a0a')
            elif '⚠' in label:
                row_clr.append('#2a1a00')
            elif matched:
                row_clr.append('#3d0a0a' if (label in ('Alice bit','Bob result') and error) else '#0a2a1a')
            else:
                row_clr.append(D['bg3'])
        cell_colors.append(row_clr)

    tbl = ax.table(cellText=row_data, rowLabels=row_labels,
                   colLabels=[str(i+1) for i in range(n)],
                   cellColours=cell_colors, cellLoc='center', loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)  # Increased from 8.5
    tbl.scale(1.3, 2.2)  # Increased horizontal scale from 1 to 1.3, vertical from 1.75 to 2.2

    for (ri, ci), cell in tbl.get_celld().items():
        cell.set_edgecolor(D['border'])
        cell.set_linewidth(0.5)
        label = row_labels[ri - 1] if 0 < ri <= len(row_labels) else ''
        if ri == 0:
            cell.set_facecolor(D['bg3'])
            cell.set_text_props(color=D['text_dim'], fontsize=10)  # Increased from 8
        elif ci == -1:
            cell.set_facecolor(D['bg3'])
            clr = D['amber'] if '⚠' in label else D['text_dim']
            cell.set_text_props(color=clr, fontsize=10,  # Increased from 8
                                fontweight='bold' if '⚠' in label else 'normal')
        else:
            matched = m[ci] if ci < len(m) else False
            error   = (ab[ci] != br[ci]) if ci < len(ab) else False
            if 'match' in label.lower():
                c = D['green'] if row_data[ri-1][ci] == '✓' else D['red']
                cell.set_text_props(color=c, fontweight='bold')
            elif '⚠' in label:
                cell.set_text_props(color=D['amber'])
            elif 'basis' in label.lower():
                val = row_data[ri-1][ci]
                cell.set_text_props(color=D['cyan'] if val == 'Z' else D['purple'])
            elif matched and error and label in ('Alice bit','Bob result'):
                cell.set_text_props(color=D['red'], fontweight='bold')
            elif matched:
                cell.set_text_props(color=D['green'])
            else:
                cell.set_text_props(color=D['text_dim'])

    eve_tag   = '   ⚠  Eve intercepting' if eve else '   ✅  No eavesdropper'
    ax.set_title(f'BB84 Protocol — First {n} Qubits{eve_tag}',
                 fontsize=13, fontweight='bold',  # Increased from 11
                 color=D['red'] if eve else D['green'],
                 pad=12, loc='left')

    patches = [
        mpatches.Patch(color='#0a2a1a', label='Matching basis (kept)'),
        mpatches.Patch(color=D['bg3'],  label='Mismatched (discarded)'),
        mpatches.Patch(color='#3d0a0a', label='Error in sifted key'),
    ]
    if eve:
        patches.append(mpatches.Patch(color='#2a1a00', label="Eve's data"))
    ax.legend(handles=patches, loc='lower right', fontsize=9,  # Increased from 8
              bbox_to_anchor=(1.0, -0.1),
              facecolor=D['bg3'], edgecolor=D['border'], labelcolor=D['text'])

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches='tight', facecolor=D['bg'])  # Increased DPI from 150
        print(f'  Saved → {save_path}')
    return fig


# ── Fig 4 — QBER Comparison ───────────────────────────────────────────
def fig_qber_comparison(res_clean, res_eve, save_path=None):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    _dark_fig(fig)

    # Calculate dynamic y-axis limit based on max QBER
    qber_clean_pct = res_clean['qber'] * 100
    qber_eve_pct = res_eve['qber'] * 100
    thrs_pct = QBER_THRESHOLD * 100
    
    # Set y_max to accommodate the highest value + padding
    max_qber = max(qber_clean_pct, qber_eve_pct, thrs_pct + 5)
    y_max = max(20, max_qber * 1.25)  # At least 20%, with 25% padding above max value

    for ax, (title, res, color) in zip(axes, [
        ('Without Eavesdropper',   res_clean, D['green']),
        ('With Eavesdropper (Eve)', res_eve,  D['red']),
    ]):
        _dark_axes(ax, D['bg2'])
        pct  = res['qber'] * 100
        thrs = QBER_THRESHOLD * 100

        # Narrow bar with padding to the right for badge
        ax.bar([0], [pct], width=0.3, color=color, alpha=0.85,
               edgecolor=color, linewidth=1.5, zorder=3, label=f'QBER = {pct:.1f}%')
        ax.axhline(thrs, color=D['amber'], linestyle='--', linewidth=2,
                   label=f'Threshold = {thrs:.0f}%', zorder=4)
        ax.axhspan(thrs, y_max, alpha=0.06, color=D['red'], zorder=1)

        ax.set_xlim(-0.4, 0.8)   # Extended right side for badge placement
        ax.set_ylim(0, y_max)  # Dynamic y-axis
        ax.set_xticks([])
        ax.set_ylabel('QBER (%)', fontsize=11)
        ax.set_title(title, fontsize=13, fontweight='bold', color=color, pad=12)
        _legend(ax, loc='upper left')

        # Value label above bar (dynamic positioning to avoid hitting top)
        label_y = min(pct + (y_max * 0.03), y_max - (y_max * 0.08))
        ax.text(0, label_y, f'{pct:.1f}%',
                ha='center', va='bottom', fontsize=20,
                fontweight='bold', color=color, zorder=5)

        # Verdict badge — positioned in the RIGHT PADDING area, inside axes
        # Vertically centered to avoid overlap with any bar height
        badge_x = 0.55  # In the right padding area
        badge_y = y_max * 0.50  # Vertically centered
            
        if res['detected']:
            btxt, bfc, bec = '🚨 EAVESDROPPED\nKey Discarded', '#1a0505', D['red']
        else:
            btxt, bfc, bec = '✅ CHANNEL SECURE\nKey Accepted', '#051a0a', D['green']

        ax.text(badge_x, badge_y, btxt, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color=bec,
                bbox=dict(boxstyle='round,pad=0.6',
                          facecolor=bfc, edgecolor=bec, linewidth=1.8),
                zorder=6)

    fig.suptitle('Quantum Bit Error Rate (QBER) — Clean vs Eve',
                 fontsize=14, fontweight='bold', color=D['text'], y=1.01)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches='tight', facecolor=D['bg'])  # Increased DPI
        print(f'  Saved → {save_path}')
    return fig


# ── Fig 5 — Key Length Waterfall ──────────────────────────────────────
def fig_key_waterfall(res_clean, res_eve, save_path=None):
    stages = ['Raw\nQubits', 'After\nSifting', 'QBER\nSample', 'Final\nKey']
    fig, ax = plt.subplots(figsize=(10, 5.5))
    _dark_fig(fig)
    _dark_axes(ax, D['bg2'])

    width = 0.33
    x     = np.arange(len(stages))

    for offset, (label, res, color, glow) in enumerate([
        ('No Eve',      res_clean, D['blue'], D['cyan']),
        ('Eve Present', res_eve,   D['red'],  D['amber']),
    ]):
        vals = [res['n_raw'], res['n_sifted'], res['n_sample'], res['n_key']]
        xi   = x + (offset - 0.5) * width
        bars = ax.bar(xi, vals, width=width*0.92, color=color, alpha=0.85,
                      edgecolor=glow, linewidth=1.2, label=label, zorder=3)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + res_clean['n_raw']*0.012,
                    str(v), ha='center', va='bottom',
                    fontsize=10, fontweight='bold', color=glow)

    ax.set_xticks(x)
    ax.set_xticklabels(stages, fontsize=11, color=D['text'])
    ax.set_ylabel('Number of Bits', fontsize=11)
    ax.set_title('Key Length at Each Protocol Stage',
                 fontsize=13, fontweight='bold', color=D['text'], pad=12)
    ax.set_ylim(0, res_clean['n_raw'] * 1.22)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    _legend(ax, loc='upper right')

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches='tight', facecolor=D['bg'])  # Increased DPI
        print(f'  Saved → {save_path}')
    return fig


# ── Fig 6 — QBER Statistics ───────────────────────────────────────────
def fig_qber_statistics(n_trials=60, save_path=None):
    from bb84_simulation import bb84

    rng_seed = np.random.default_rng(7)
    clean_qbers, eve_qbers = [], []
    for _ in range(n_trials):
        rng = np.random.default_rng(int(rng_seed.integers(1e6)))
        clean_qbers.append(bb84(100, eve_present=False, rng=rng)['qber'] * 100)
        rng = np.random.default_rng(int(rng_seed.integers(1e6)))
        eve_qbers.append(bb84(100, eve_present=True,  rng=rng)['qber'] * 100)

    clean_qbers = np.array(clean_qbers)
    eve_qbers   = np.array(eve_qbers)

    fig, ax = plt.subplots(figsize=(11, 5))
    _dark_fig(fig)
    _dark_axes(ax, D['bg2'])

    ax.scatter(range(n_trials), clean_qbers, color=D['green'],
               alpha=0.8, s=60, zorder=4,
               label=f'No Eve  (mean = {clean_qbers.mean():.1f}%)')
    ax.scatter(range(n_trials), eve_qbers, color=D['red'],
               alpha=0.8, s=60, marker='D', zorder=4,
               label=f'Eve present  (mean = {eve_qbers.mean():.1f}%)')

    ax.axhline(clean_qbers.mean(), color=D['green'], linestyle=':', linewidth=1, alpha=0.4)
    ax.axhline(eve_qbers.mean(),   color=D['red'],   linestyle=':', linewidth=1, alpha=0.4)

    thrs = QBER_THRESHOLD * 100
    
    # Dynamic y-axis based on max QBER value
    max_qber = max(eve_qbers.max(), clean_qbers.max(), thrs + 5)
    y_max = max(20, max_qber * 1.15)  # At least 20%, with 15% padding
    
    ax.axhline(thrs, color=D['amber'], linestyle='--', linewidth=2,
               zorder=5, label=f'Threshold ({thrs:.0f}%)')
    ax.axhspan(thrs, y_max, alpha=0.06, color=D['red'], zorder=1)

    detected = int(np.sum(eve_qbers > thrs))
    label_y = min(thrs + (y_max * 0.05), y_max - (y_max * 0.05))  # Dynamic label position
    ax.text(n_trials*0.98, label_y,
            f'Eve detected in {detected}/{n_trials} trials',
            ha='right', fontsize=9.5, color=D['amber'], fontweight='bold')

    ax.set_xlabel('Trial Index', fontsize=11)
    ax.set_ylabel('QBER (%)', fontsize=11)
    ax.set_title(f'QBER Distribution over {n_trials} Trials  (100 qubits each)',
                 fontsize=13, fontweight='bold', color=D['text'], pad=12)
    ax.set_ylim(0, y_max)  # Dynamic y-axis
    ax.set_xlim(-1, n_trials)
    _legend(ax, loc='upper left')

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches='tight', facecolor=D['bg'])  # Increased DPI
        print(f'  Saved → {save_path}')
    return fig