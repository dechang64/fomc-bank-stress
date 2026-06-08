"""
Generate publication-quality figures for Cross-Sectional → Aggregate Mapping
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

# Load results
with open('results/aggregate_mapping.json') as f:
    results = json.load(f)

# ── Figure 1: Bank Vulnerability Ranking ───────────────────────
print("Generating Figure 1: Bank Vulnerability Ranking...")

ranking = pd.DataFrame(results['vulnerability_ranking'])
ranking = ranking.sort_values('pred_car_pp')

fig, ax = plt.subplots(figsize=(10, 7))

colors = ['#c0392b' if x < -0.5 else '#e67e22' if x < 0 else '#27ae60' 
          for x in ranking['pred_car_pp']]

bars = ax.barh(range(len(ranking)), ranking['pred_car_pp'], color=colors, 
               edgecolor='white', linewidth=0.5, height=0.7)

ax.set_yticks(range(len(ranking)))
ax.set_yticklabels(ranking['ticker'], fontsize=11)
ax.set_xlabel('Predicted CAR per FastHike Meeting (%)', fontsize=12)
ax.set_title('Bank Vulnerability Ranking: FastHike Scenario\n(Cross-Sectional Coefficients × Current Balance Sheets)', 
             fontsize=13, fontweight='bold')

# Add SVB reference line
ax.axvline(x=-2.318, color='#8e44ad', linestyle='--', linewidth=2, alpha=0.8)
ax.annotate('SVB\n(-2.32%)', xy=(-2.318, len(ranking)-0.5), fontsize=10, 
            color='#8e44ad', fontweight='bold', ha='center', va='bottom')

# Add value labels
for i, (val, bar) in enumerate(zip(ranking['pred_car_pp'], bars)):
    offset = 0.05 if val >= 0 else -0.05
    ha = 'left' if val >= 0 else 'right'
    ax.text(val + offset, i, f'{val:.2f}%', va='center', ha=ha, fontsize=9)

ax.axvline(x=0, color='black', linewidth=0.5)
ax.set_xlim(-2.8, 0.8)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('paper/figures/fig_aggregate_vulnerability.png', dpi=300, bbox_inches='tight')
plt.close()
print("  → Saved fig_aggregate_vulnerability.png")

# ── Figure 2: SVB Counterfactual Decomposition ────────────────
print("Generating Figure 2: SVB Counterfactual...")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Cumulative CAR comparison
ax = axes[0]
categories = ['SVB\n(Actual HTM)', 'SVB\n(Avg HTM)', 'DFAST\nAverage']
cumulative_cars = [-27.81, -6.57, -0.88]
colors = ['#c0392b', '#e67e22', '#2980b9']

bars = ax.bar(categories, cumulative_cars, color=colors, edgecolor='white', width=0.6)
for bar, val in zip(bars, cumulative_cars):
    ax.text(bar.get_x() + bar.get_width()/2, val - 0.5, f'{val:.1f}%', 
            ha='center', va='top', fontsize=11, fontweight='bold', color='white')

ax.set_ylabel('Cumulative CAR (12 FastHike meetings, %)', fontsize=11)
ax.set_title('SVB Counterfactual:\nHTM Ratio Explains 76% of Predicted Loss', 
             fontsize=12, fontweight='bold')
ax.axhline(y=0, color='black', linewidth=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Panel B: HTM ratio comparison
ax = axes[1]
banks_htm = ranking.sort_values('htm_ratio', ascending=False)
top_banks = banks_htm.head(8)

ax.bar(range(len(top_banks)), top_banks['htm_ratio'] * 100, 
       color='#3498db', edgecolor='white', width=0.6)
ax.axhline(y=43.1, color='#c0392b', linestyle='--', linewidth=2)
ax.annotate('SVB (43.1%)', xy=(3, 43.1), fontsize=10, color='#c0392b', 
            fontweight='bold', ha='center', va='bottom')

ax.set_xticks(range(len(top_banks)))
ax.set_xticklabels(top_banks['ticker'], fontsize=10)
ax.set_ylabel('HTM Securities / Total Assets (%)', fontsize=11)
ax.set_title('HTM Ratio: DFAST Banks vs SVB', fontsize=12, fontweight='bold')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('paper/figures/fig_svb_counterfactual.png', dpi=300, bbox_inches='tight')
plt.close()
print("  → Saved fig_svb_counterfactual.png")

# ── Figure 3: System CVaR by Period ────────────────────────────
print("Generating Figure 3: System CVaR...")

fig, ax = plt.subplots(figsize=(8, 5))

periods = ['Full\nSample', 'FastHike', 'ZLB', 'Non-crisis']
var5 = [-3.019, -2.798, -2.771, -3.064]
cvar5 = [-4.764, -3.090, -3.906, -5.196]

x = np.arange(len(periods))
width = 0.35

bars1 = ax.bar(x - width/2, var5, width, label='VaR (5%)', color='#3498db', edgecolor='white')
bars2 = ax.bar(x + width/2, cvar5, width, label='CVaR (5%)', color='#c0392b', edgecolor='white')

ax.set_ylabel('System CAR (%)', fontsize=12)
ax.set_title('System-Level Risk: VaR and CVaR by Period\n(Asset-Weighted DFAST Bank Portfolio)', 
             fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(periods, fontsize=11)
ax.legend(fontsize=11)
ax.axhline(y=0, color='black', linewidth=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add value labels
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 0.15, 
            f'{bar.get_height():.1f}%', ha='center', va='top', fontsize=8, color='white')
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 0.15, 
            f'{bar.get_height():.1f}%', ha='center', va='top', fontsize=8, color='white')

plt.tight_layout()
plt.savefig('paper/figures/fig_system_cvar.png', dpi=300, bbox_inches='tight')
plt.close()
print("  → Saved fig_system_cvar.png")

print("\nAll aggregate mapping figures generated!")
