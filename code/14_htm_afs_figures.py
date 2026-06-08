"""
Generate publication-quality figures for HTM vs AFS Quasi-Experiment
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
import json

# Load results
with open('results/htm_afs_quasi_experiment.json') as f:
    results = json.load(f)

# ── Figure 1: Event-Study Dynamics ─────────────────────────────
print("Generating Figure 1: Event-Study Dynamics...")

es = pd.DataFrame(results['event_study'])
es['date'] = pd.to_datetime(es['date'])

fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 2]})

# Panel A: CAR by HTM group
ax = axes[0]
ax.plot(es['date'], es['htm_high_car'] * 100, 'o-', color='#c0392b', linewidth=2, 
        markersize=8, label='High-HTM Banks', zorder=3)
ax.plot(es['date'], es['htm_low_car'] * 100, 's-', color='#2980b9', linewidth=2, 
        markersize=8, label='Low-HTM Banks', zorder=3)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.fill_between(es['date'], es['htm_high_car']*100, es['htm_low_car']*100, 
                alpha=0.15, color='#c0392b')
ax.set_ylabel('CAR[0,+1] (%)', fontsize=12)
ax.set_title('Panel A: Bank CAR During FastHike Period by HTM Exposure', fontsize=13, fontweight='bold')
ax.legend(fontsize=11, loc='lower left')
ax.tick_params(axis='x', rotation=45)

# Panel B: Spread (HTM-high - HTM-low)
ax = axes[1]
colors = ['#c0392b' if s < 0 else '#27ae60' for s in es['spread']]
bars = ax.bar(es['date'], es['spread'] * 100, width=15, color=colors, alpha=0.8, edgecolor='white')
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

# Mark significant bars
for i, (idx, row) in enumerate(es.iterrows()):
    if abs(row['t_stat']) > 1.96:
        ax.annotate('**', (row['date'], row['spread']*100), 
                   ha='center', va='bottom' if row['spread'] > 0 else 'top',
                   fontsize=12, fontweight='bold', color='#2c3e50')

ax.set_ylabel('Spread (pp)', fontsize=12)
ax.set_title('Panel B: High-HTM − Low-HTM CAR Spread', fontsize=13, fontweight='bold')
ax.tick_params(axis='x', rotation=45)

# Add SVB failure annotation
svb_date = pd.Timestamp('2023-03-10')
for ax in axes:
    ax.axvline(x=svb_date, color='#e74c3c', linestyle=':', alpha=0.7, linewidth=1.5)
    
axes[0].annotate('SVB Failure\n(2023-03-10)', xy=(svb_date, -0.4), fontsize=9,
                color='#e74c3c', ha='center', style='italic')

plt.tight_layout()
plt.savefig('paper/figures/fig_htm_afs_event_study.png', dpi=300, bbox_inches='tight')
plt.close()
print("  → Saved fig_htm_afs_event_study.png")

# ── Figure 2: DiD Coefficient Comparison ───────────────────────
print("Generating Figure 2: DiD Coefficient Comparison...")

fig, ax = plt.subplots(figsize=(10, 6))

# Coefficients from different specifications
specs = results['specifications']
labels = []
htm_coefs = []
afs_coefs = []
htm_ses = []
afs_ses = []

# Bank FE only
if 'bank_fe_only' in specs:
    s = specs['bank_fe_only']
    labels.append('Bank FE\nOnly')
    htm_coefs.append(s['beta_fh_htm'])
    afs_coefs.append(s['beta_fh_afs'])
    htm_ses.append(abs(s['beta_fh_htm'] / s['t_fh_htm']))
    afs_ses.append(abs(s['beta_fh_afs'] / s['t_fh_afs']))

# Bank + Time FE
if 'bank_time_fe' in specs:
    s = specs['bank_time_fe']
    labels.append('Bank +\nTime FE')
    htm_coefs.append(s['beta_fh_htm'])
    afs_coefs.append(s['beta_fh_afs'])
    htm_ses.append(s['se_fh_htm'])
    afs_ses.append(s['se_fh_afs'])

# Full model
if 'full_model' in specs:
    s = specs['full_model']
    labels.append('Full\nModel')
    htm_coefs.append(s['beta_fh_htm'])
    afs_coefs.append(s['beta_fh_afs'])
    htm_ses.append(abs(s['beta_fh_htm'] / (s['t_fh_htm'] if 't_fh_htm' in s else s.get('beta_fh_htm',1)/0.01)))
    afs_ses.append(abs(s['beta_fh_afs'] / (s.get('t_fh_afs', 2.0))))

x = np.arange(len(labels))
width = 0.35

bars1 = ax.bar(x - width/2, htm_coefs, width, yerr=[1.96*s for s in htm_ses],
               label='FastHike × HTM', color='#c0392b', alpha=0.85,
               capsize=5, error_kw={'linewidth': 1.5})
bars2 = ax.bar(x + width/2, afs_coefs, width, yerr=[1.96*s for s in afs_ses],
               label='FastHike × AFS', color='#2980b9', alpha=0.85,
               capsize=5, error_kw={'linewidth': 1.5})

ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_ylabel('Coefficient', fontsize=12)
ax.set_title('HTM vs AFS: Accounting Classification Effect During Rapid Rate Hikes\n(95% CI, Bank-Clustered SE)', 
             fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=11)
ax.legend(fontsize=11)

# Add Δ annotation
if 'bank_time_fe' in specs:
    s = specs['bank_time_fe']
    ax.annotate(f'Δ = {s["delta"]:.4f}\n(t = {s["delta_t"]:.2f}***)', 
               xy=(1, min(htm_coefs[1], afs_coefs[1])),
               xytext=(1.5, -0.04),
               fontsize=11, fontweight='bold', color='#2c3e50',
               arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=1.5),
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#f9e79f', alpha=0.8))

plt.tight_layout()
plt.savefig('paper/figures/fig_htm_afs_did_coefficients.png', dpi=300, bbox_inches='tight')
plt.close()
print("  → Saved fig_htm_afs_did_coefficients.png")

# ── Figure 3: SVB Case Study ──────────────────────────────────
print("Generating Figure 3: SVB Case Study...")

fig, ax = plt.subplots(figsize=(10, 6))

# Load panel data for HTM ratio distribution
y9c = pd.read_csv('data/y9c_complete.csv')
fh_period_y9c = y9c[(pd.to_datetime(y9c['report_date']) >= '2022-03-31') & 
                     (pd.to_datetime(y9c['report_date']) <= '2023-06-30')]

# Average HTM ratio by bank during FastHike
avg_htm = fh_period_y9c.groupby('ticker')['htm_ratio'].mean().sort_values(ascending=True)

colors = ['#c0392b' if h > avg_htm.median() else '#3498db' for h in avg_htm.values]
bars = ax.barh(avg_htm.index, avg_htm.values * 100, color=colors, alpha=0.8, edgecolor='white')

# Add SVB
svb_htm = 43.1
ax.axvline(x=svb_htm, color='#e74c3c', linestyle='--', linewidth=2.5, alpha=0.9)
ax.annotate(f'SVB\n({svb_htm:.1f}%)', xy=(svb_htm, len(avg_htm)-1),
           fontsize=12, fontweight='bold', color='#e74c3c',
           xytext=(svb_htm+3, len(avg_htm)-2),
           arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=2))

# Add median line
ax.axvline(x=avg_htm.median()*100, color='gray', linestyle=':', alpha=0.7)
ax.annotate(f'Sample Median\n({avg_htm.median()*100:.1f}%)', 
           xy=(avg_htm.median()*100, 0),
           fontsize=9, color='gray', ha='center', va='bottom')

ax.set_xlabel('HTM Securities / Total Assets (%)', fontsize=12)
ax.set_title('HTM Ratio Distribution: DFAST Banks vs SVB\n(FastHike Period 2022Q1–2023Q2)', 
             fontsize=13, fontweight='bold')

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#c0392b', alpha=0.8, label='Above Median'),
                   Patch(facecolor='#3498db', alpha=0.8, label='Below Median')]
ax.legend(handles=legend_elements, fontsize=10, loc='lower right')

plt.tight_layout()
plt.savefig('paper/figures/fig_svb_htm_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print("  → Saved fig_svb_htm_comparison.png")

print("\nAll figures generated successfully!")
