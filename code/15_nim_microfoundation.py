"""
Plan B: NIM Channel Microfoundation — Rebalancing Channel
==========================================================
Upgrade the NIM channel from "empirical regularity" to "theory-driven prediction."

Key insight from Lu & Wu (2024): Dovish ZLB → QE → rebalancers rotate from bonds 
to equities → banks as "bond-like" assets get rotated away from → BUT high-NIM 
banks receive trading income compensation.

Testable predictions:
1. Dovish × ZLB × NIM × TradingRatio: high-trading high-NIM banks benefit MORE
   (rebalancing channel + trading income compensation)
2. Dovish × ZLB × NIM × DepositRatio: high-deposit high-NIM banks benefit MORE
   (deposit franchise value channel — deposit betas are sticky)
3. Dovish × ZLB × NIM × HTM: high-HTM high-NIM banks benefit LESS
   (HTM locks in low yields, NIM compression not compensated)
4. NIM change (ΔNIM) as alternative: if rebalancing channel works, NIM change 
   should predict CAR during ZLB, not just NIM level

This upgrades NIM from "a balance-sheet characteristic that happens to predict 
returns" to "a theoretically motivated channel with testable cross-predictions."
"""

import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

from scipy import stats
import statsmodels.api as sm
from linearmodels.panel import PanelOLS

# ── Load data ──────────────────────────────────────────────────
print("=" * 70)
print("NIM Channel Microfoundation: Rebalancing Channel Analysis")
print("=" * 70)

y9c = pd.read_csv('data/y9c_complete.csv')
be = pd.read_csv('data/bank_events.csv')
reg = pd.read_csv('data/fomc_paper_regression_data.csv')

y9c['report_date'] = pd.to_datetime(y9c['report_date'])
reg['fomc_date'] = pd.to_datetime(reg['fomc_date'])

common_banks = sorted(set(y9c['ticker'].unique()) & 
                      set(c.replace('_car01','') for c in be.columns if c.endswith('_car01')))
print(f"\nCommon banks: {len(common_banks)}")

# ── Build panel ────────────────────────────────────────────────
fomc_chars = reg[['fomc_date', 'lm_pct', 'sentiment', 'post2008', 'tightening', 
                  'inflation_era', 'surprise_type']].copy()

records = []
for _, row in fomc_chars.iterrows():
    fdate = row['fomc_date']
    be_row = be[be['fomc_date'] == fdate.strftime('%Y-%m-%d')]
    if len(be_row) == 0:
        continue
    be_row = be_row.iloc[0]
    for bank in common_banks:
        car_col = f'{bank}_car01'
        if car_col in be.columns:
            records.append({
                'fomc_date': fdate,
                'bank': bank,
                'car': be_row[car_col],
                'lm_pct': row['lm_pct'],
                'post2008': row['post2008'],
                'tightening': row['tightening'],
                'inflation_era': row['inflation_era'],
            })

panel = pd.DataFrame(records)
panel['fomc_date'] = pd.to_datetime(panel['fomc_date'])

# ── Merge Y-9C data ───────────────────────────────────────────
y9c_panel = y9c[['ticker', 'report_date', 'nim', 'trading_ratio', 'deposit_ratio',
                  'htm_ratio', 'afs_ratio', 'nim_change']].copy()
y9c_panel = y9c_panel.rename(columns={'ticker': 'bank'})

# Match each FOMC date to most recent Y-9C report
# merge_asof requires globally sorted 'on' column
panel = panel.sort_values('fomc_date').reset_index(drop=True)
y9c_panel = y9c_panel.sort_values('report_date').reset_index(drop=True)

panel = pd.merge_asof(
    panel, y9c_panel,
    left_on='fomc_date', right_on='report_date',
    by='bank', direction='backward'
)
panel = panel.dropna(subset=['nim', 'trading_ratio', 'deposit_ratio', 'htm_ratio'])
print(f"Panel shape: {panel.shape}")

# ── Define periods ─────────────────────────────────────────────
panel['zlb'] = 0
zlb1 = (panel['fomc_date'] >= '2008-12-16') & (panel['fomc_date'] <= '2015-12-16')
zlb2 = (panel['fomc_date'] >= '2020-03-15') & (panel['fomc_date'] <= '2022-03-16')
panel.loc[zlb1 | zlb2, 'zlb'] = 1

panel['fasthike'] = 0
fh = (panel['fomc_date'] >= '2022-03-16') & (panel['fomc_date'] <= '2023-07-26')
panel.loc[fh, 'fasthike'] = 1

panel['dovish'] = (panel['lm_pct'] < panel['lm_pct'].quantile(0.25)).astype(int)
panel['hawkish'] = (panel['lm_pct'] > panel['lm_pct'].quantile(0.75)).astype(int)

# Standardize continuous variables for interaction interpretability
for col in ['nim', 'trading_ratio', 'deposit_ratio', 'htm_ratio', 'nim_change']:
    panel[f'{col}_z'] = (panel[col] - panel[col].mean()) / panel[col].std()

print(f"\nZLB meetings: {panel.groupby('fomc_date')['zlb'].first().sum()}")
print(f"FastHike meetings: {panel.groupby('fomc_date')['fasthike'].first().sum()}")
print(f"Dovish meetings: {panel['dovish'].sum()}")
print(f"Hawkish meetings: {panel['hawkish'].sum()}")

# ── Create all interaction terms BEFORE setting panel index ────
panel['dovish_zlb'] = panel['dovish'] * panel['zlb']
panel['dovish_nim'] = panel['dovish'] * panel['nim_z']
panel['zlb_nim'] = panel['zlb'] * panel['nim_z']
panel['dovish_zlb_nim'] = panel['dovish'] * panel['zlb'] * panel['nim_z']

panel['dovish_zlb_nim_trading'] = panel['dovish'] * panel['zlb'] * panel['nim_z'] * panel['trading_ratio_z']
panel['dovish_zlb_trading'] = panel['dovish'] * panel['zlb'] * panel['trading_ratio_z']
panel['zlb_nim_trading'] = panel['zlb'] * panel['nim_z'] * panel['trading_ratio_z']
panel['dovish_nim_trading'] = panel['dovish'] * panel['nim_z'] * panel['trading_ratio_z']
panel['nim_trading'] = panel['nim_z'] * panel['trading_ratio_z']

panel['dovish_zlb_nim_deposit'] = panel['dovish'] * panel['zlb'] * panel['nim_z'] * panel['deposit_ratio_z']
panel['dovish_zlb_deposit'] = panel['dovish'] * panel['zlb'] * panel['deposit_ratio_z']
panel['zlb_nim_deposit'] = panel['zlb'] * panel['nim_z'] * panel['deposit_ratio_z']
panel['dovish_nim_deposit'] = panel['dovish'] * panel['nim_z'] * panel['deposit_ratio_z']
panel['nim_deposit'] = panel['nim_z'] * panel['deposit_ratio_z']

panel['dovish_zlb_nim_htm'] = panel['dovish'] * panel['zlb'] * panel['nim_z'] * panel['htm_ratio_z']
panel['dovish_zlb_htm'] = panel['dovish'] * panel['zlb'] * panel['htm_ratio_z']
panel['zlb_nim_htm'] = panel['zlb'] * panel['nim_z'] * panel['htm_ratio_z']
panel['dovish_nim_htm'] = panel['dovish'] * panel['nim_z'] * panel['htm_ratio_z']
panel['nim_htm'] = panel['nim_z'] * panel['htm_ratio_z']

panel['dovish_zlb_nimchg'] = panel['dovish'] * panel['zlb'] * panel['nim_change_z']
panel['dovish_nimchg'] = panel['dovish'] * panel['nim_change_z']
panel['zlb_nimchg'] = panel['zlb'] * panel['nim_change_z']

# ── Set panel index ────────────────────────────────────────────
panel = panel.set_index(['bank', 'fomc_date'])

# ── Specification 1: Baseline NIM channel ─────────────────────
print("\n" + "=" * 70)
print("SPECIFICATION 1: Baseline NIM Channel (Bank FE)")
print("=" * 70)

spec1 = PanelOLS(
    panel['car'],
    sm.add_constant(panel[['dovish', 'zlb', 'nim_z', 
                            'dovish_zlb', 'dovish_nim', 'zlb_nim', 'dovish_zlb_nim']]),
    entity_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)
print(spec1.summary.tables[1])

# ── Specification 2: Add Trading Ratio interaction ────────────
print("\n" + "=" * 70)
print("SPECIFICATION 2: NIM × Trading Ratio (Rebalancing Channel)")
print("=" * 70)

spec2 = PanelOLS(
    panel['car'],
    sm.add_constant(panel[['dovish', 'zlb', 'nim_z', 'trading_ratio_z',
                            'dovish_zlb', 'dovish_nim', 'zlb_nim', 'dovish_zlb_nim',
                            'dovish_zlb_trading', 'zlb_nim_trading', 'dovish_nim_trading',
                            'nim_trading', 'dovish_zlb_nim_trading']]),
    entity_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)
print(spec2.summary.tables[1])

# ── Specification 3: Add Deposit Ratio interaction ─────────────
print("\n" + "=" * 70)
print("SPECIFICATION 3: NIM × Deposit Ratio (Deposit Franchise Value)")
print("=" * 70)

spec3 = PanelOLS(
    panel['car'],
    sm.add_constant(panel[['dovish', 'zlb', 'nim_z', 'deposit_ratio_z',
                            'dovish_zlb', 'dovish_nim', 'zlb_nim', 'dovish_zlb_nim',
                            'dovish_zlb_deposit', 'zlb_nim_deposit', 'dovish_nim_deposit',
                            'nim_deposit', 'dovish_zlb_nim_deposit']]),
    entity_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)
print(spec3.summary.tables[1])

# ── Specification 4: Add HTM interaction (negative prediction) ─
print("\n" + "=" * 70)
print("SPECIFICATION 4: NIM × HTM (HTM Lock-in Reduces NIM Benefit)")
print("=" * 70)

spec4 = PanelOLS(
    panel['car'],
    sm.add_constant(panel[['dovish', 'zlb', 'nim_z', 'htm_ratio_z',
                            'dovish_zlb', 'dovish_nim', 'zlb_nim', 'dovish_zlb_nim',
                            'dovish_zlb_htm', 'zlb_nim_htm', 'dovish_nim_htm',
                            'nim_htm', 'dovish_zlb_nim_htm']]),
    entity_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)
print(spec4.summary.tables[1])

# ── Specification 5: Full model with all interactions ─────────
print("\n" + "=" * 70)
print("SPECIFICATION 5: Full Model (All Three Interactions)")
print("=" * 70)

spec5 = PanelOLS(
    panel['car'],
    sm.add_constant(panel[['dovish', 'zlb', 'nim_z', 'trading_ratio_z', 
                            'deposit_ratio_z', 'htm_ratio_z',
                            'dovish_zlb', 'dovish_nim', 'zlb_nim', 'dovish_zlb_nim',
                            'dovish_zlb_trading', 'zlb_nim_trading', 'dovish_nim_trading',
                            'nim_trading', 'dovish_zlb_nim_trading',
                            'dovish_zlb_deposit', 'zlb_nim_deposit', 'dovish_nim_deposit',
                            'nim_deposit', 'dovish_zlb_nim_deposit',
                            'dovish_zlb_htm', 'zlb_nim_htm', 'dovish_nim_htm',
                            'nim_htm', 'dovish_zlb_nim_htm']]),
    entity_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)
print(spec5.summary.tables[1])

# ── Specification 6: NIM change vs NIM level ──────────────────
print("\n" + "=" * 70)
print("SPECIFICATION 6: NIM Change (ΔNIM) vs NIM Level")
print("=" * 70)

spec6 = PanelOLS(
    panel['car'],
    sm.add_constant(panel[['dovish', 'zlb', 'nim_z', 'nim_change_z',
                            'dovish_zlb', 'dovish_nim', 'zlb_nim', 'dovish_zlb_nim',
                            'dovish_nimchg', 'zlb_nimchg', 'dovish_zlb_nimchg']]),
    entity_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)
print(spec6.summary.tables[1])

# ── Save results ───────────────────────────────────────────────
results = {
    'analysis_type': 'nim_microfoundation_rebalancing',
    'n_obs': len(panel),
    'n_banks': len(common_banks),
    'specifications': {}
}

for name, spec in [('baseline_nim', spec1), ('nim_trading', spec2), 
                    ('nim_deposit', spec3), ('nim_htm', spec4),
                    ('full_model', spec5), ('nim_change', spec6)]:
    params = spec.params.to_dict()
    tstats = spec.tstats.to_dict()
    pvals = spec.pvalues.to_dict()
    results['specifications'][name] = {
        'params': {k: float(v) for k, v in params.items()},
        'tstats': {k: float(v) for k, v in tstats.items()},
        'pvalues': {k: float(v) for k, v in pvals.items()},
        'r2_within': float(spec.rsquared_within),
        'n_obs': int(spec.nobs),
    }

with open('results/nim_microfoundation.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
print("\nResults saved to results/nim_microfoundation.json")

# ── Summary ────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("SUMMARY: NIM Channel Microfoundation")
print("=" * 70)

print("""
The rebalancing channel predicts three cross-sectional patterns:

1. Dovish×ZLB×NIM×TradingRatio > 0: High-trading high-NIM banks benefit MORE
   → Trading income compensates for NIM compression during ZLB
   → Spec 2 coefficient: {:.4f} (t = {:.2f})

2. Dovish×ZLB×NIM×DepositRatio > 0: High-deposit high-NIM banks benefit MORE
   → Deposit franchise value (sticky betas) preserves NIM during ZLB
   → Spec 3 coefficient: {:.4f} (t = {:.2f})

3. Dovish×ZLB×NIM×HTM < 0: High-HTM high-NIM banks benefit LESS
   → HTM locks in low yields, NIM compression not compensated
   → Spec 4 coefficient: {:.4f} (t = {:.2f})

If all three predictions hold, the NIM channel is not just an empirical 
regularity but a theory-driven prediction with testable cross-implications.
""".format(
    results['specifications']['nim_trading']['params'].get('dovish_zlb_nim_trading', 0),
    results['specifications']['nim_trading']['tstats'].get('dovish_zlb_nim_trading', 0),
    results['specifications']['nim_deposit']['params'].get('dovish_zlb_nim_deposit', 0),
    results['specifications']['nim_deposit']['tstats'].get('dovish_zlb_nim_deposit', 0),
    results['specifications']['nim_htm']['params'].get('dovish_zlb_nim_htm', 0),
    results['specifications']['nim_htm']['tstats'].get('dovish_zlb_nim_htm', 0),
))

print("DONE.")
