"""
Plan D: Kuttner Surprise Robustness Check
==========================================
The paper's main identification uses LM% (Loughran-McDonald negative word 
percentage) as the FOMC sentiment measure. The key concern: LM% captures 
semantic content, not monetary policy SURPRISE.

Kuttner (2001) constructs the target rate surprise from Fed Funds Futures:
  surprise = actual rate change - expected rate change (from futures)

We use a simplified version from FRED daily FFR data:
  Kuttner surprise ≈ (D/(D-d)) × ΔFFR on FOMC day

This robustness check tests:
1. Does Kuttner surprise predict bank CAR? (replicating main result)
2. Does LM% have incremental power beyond Kuttner surprise?
3. If yes → LM% captures semantic content with independent information
4. If no → LM% is just a noisy proxy for rate surprise

This is the most important robustness check for the paper's identification.
"""

import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

from scipy import stats
from linearmodels.panel import PanelOLS
import statsmodels.api as sm

# ── Load data ──────────────────────────────────────────────────
print("=" * 70)
print("Kuttner Surprise Robustness Check")
print("=" * 70)

# Load Kuttner surprise
kuttner = pd.read_csv('data/kuttner_surprise.csv')
kuttner['fomc_date'] = pd.to_datetime(kuttner['fomc_date'])
print(f"Kuttner surprises: {len(kuttner)}")

# Load bank events
be = pd.read_csv('data/bank_events.csv')
be['fomc_date'] = pd.to_datetime(be['fomc_date'])

# Load regression data (has LM% and other FOMC characteristics)
reg = pd.read_csv('data/fomc_paper_regression_data.csv')
reg['fomc_date'] = pd.to_datetime(reg['fomc_date'])

# Load Y-9C data
y9c = pd.read_csv('data/y9c_complete.csv')
y9c['report_date'] = pd.to_datetime(y9c['report_date'])

# ── Build panel ────────────────────────────────────────────────
car_cols = [c for c in be.columns if c.endswith('_car01')]
bank_tickers = [c.replace('_car01', '') for c in car_cols]
common_banks = sorted(set(y9c['ticker'].unique()) & set(bank_tickers))
print(f"Common banks: {len(common_banks)}")

# Merge Kuttner surprise with regression data
fomc_data = pd.merge(
    reg[['fomc_date', 'lm_pct', 'sentiment', 'post2008', 'tightening', 
         'inflation_era', 'surprise_type']],
    kuttner[['fomc_date', 'kuttner_surprise', 'ffr_change']],
    on='fomc_date', how='inner'
)

# Build bank-level panel
records = []
for _, row in fomc_data.iterrows():
    fdate = row['fomc_date']
    be_row = be[be['fomc_date'] == fdate]
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
                'kuttner_surprise': row['kuttner_surprise'],
                'ffr_change': row['ffr_change'],
                'post2008': row['post2008'],
                'tightening': row['tightening'],
                'inflation_era': row['inflation_era'],
            })

panel = pd.DataFrame(records)
panel['fomc_date'] = pd.to_datetime(panel['fomc_date'])
print(f"Panel shape (before Y-9C): {panel.shape}")

# Merge Y-9C data
y9c_panel = y9c[['ticker', 'report_date', 'nim', 'htm_ratio', 'afs_ratio']].copy()
y9c_panel = y9c_panel.rename(columns={'ticker': 'bank'})

panel = panel.sort_values('fomc_date').reset_index(drop=True)
y9c_panel = y9c_panel.sort_values('report_date').reset_index(drop=True)

panel = pd.merge_asof(
    panel, y9c_panel,
    left_on='fomc_date', right_on='report_date',
    by='bank', direction='backward'
)
panel = panel.dropna(subset=['nim', 'htm_ratio'])
print(f"Panel shape (after Y-9C): {panel.shape}")

# ── Define periods ─────────────────────────────────────────────
panel['zlb'] = (
    ((panel['fomc_date'] >= '2008-12-16') & (panel['fomc_date'] <= '2015-12-16')) |
    ((panel['fomc_date'] >= '2020-03-15') & (panel['fomc_date'] <= '2022-03-16'))
).astype(int)

panel['fasthike'] = (
    (panel['fomc_date'] >= '2022-03-16') & (panel['fomc_date'] <= '2023-07-26')
).astype(int)

# Standardize
panel['lm_pct_z'] = (panel['lm_pct'] - panel['lm_pct'].mean()) / panel['lm_pct'].std()
panel['kuttner_z'] = (panel['kuttner_surprise'] - panel['kuttner_surprise'].mean()) / panel['kuttner_surprise'].std()
panel['nim_z'] = (panel['nim'] - panel['nim'].mean()) / panel['nim'].std()
panel['htm_z'] = (panel['htm_ratio'] - panel['htm_ratio'].mean()) / panel['htm_ratio'].std()

# ── Specification 1: Kuttner surprise only ─────────────────────
print("\n" + "=" * 70)
print("SPECIFICATION 1: Kuttner Surprise Only")
print("=" * 70)

panel_idx = panel.set_index(['bank', 'fomc_date'])

spec1 = PanelOLS(
    panel_idx['car'],
    sm.add_constant(panel_idx[['kuttner_z']]),
    entity_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)
print(spec1.summary.tables[1])

# ── Specification 2: LM% only ─────────────────────────────────
print("\n" + "=" * 70)
print("SPECIFICATION 2: LM% Only")
print("=" * 70)

spec2 = PanelOLS(
    panel_idx['car'],
    sm.add_constant(panel_idx[['lm_pct_z']]),
    entity_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)
print(spec2.summary.tables[1])

# ── Specification 3: Both Kuttner and LM% ─────────────────────
print("\n" + "=" * 70)
print("SPECIFICATION 3: Kuttner Surprise + LM% (Horse Race)")
print("=" * 70)

spec3 = PanelOLS(
    panel_idx['car'],
    sm.add_constant(panel_idx[['kuttner_z', 'lm_pct_z']]),
    entity_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)
print(spec3.summary.tables[1])

# ── Specification 4: Cross-sectional with Kuttner ──────────────
print("\n" + "=" * 70)
print("SPECIFICATION 4: Kuttner × HTM (Cross-Sectional Channel)")
print("=" * 70)

panel['kuttner_htm'] = panel['kuttner_z'] * panel['htm_z']
panel['lm_htm'] = panel['lm_pct_z'] * panel['htm_z']
panel['kuttner_fasthike'] = panel['kuttner_z'] * panel['fasthike']
panel['lm_fasthike'] = panel['lm_pct_z'] * panel['fasthike']
panel['kuttner_fasthike_htm'] = panel['kuttner_z'] * panel['fasthike'] * panel['htm_z']
panel['lm_fasthike_htm'] = panel['lm_pct_z'] * panel['fasthike'] * panel['htm_z']

panel_idx = panel.set_index(['bank', 'fomc_date'])

spec4 = PanelOLS(
    panel_idx['car'],
    sm.add_constant(panel_idx[['kuttner_z', 'lm_pct_z', 'htm_z',
                                'kuttner_fasthike_htm', 'lm_fasthike_htm']]),
    entity_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)
print(spec4.summary.tables[1])

# ── Specification 5: NIM channel with Kuttner ──────────────────
print("\n" + "=" * 70)
print("SPECIFICATION 5: Kuttner × NIM (NIM Channel with Surprise)")
print("=" * 70)

panel['kuttner_zlb_nim'] = panel['kuttner_z'] * panel['zlb'] * panel['nim_z']
panel['lm_zlb_nim'] = panel['lm_pct_z'] * panel['zlb'] * panel['nim_z']
panel['kuttner_zlb'] = panel['kuttner_z'] * panel['zlb']
panel['lm_zlb'] = panel['lm_pct_z'] * panel['zlb']
panel['kuttner_nim'] = panel['kuttner_z'] * panel['nim_z']
panel['lm_nim'] = panel['lm_pct_z'] * panel['nim_z']
panel['zlb_nim'] = panel['zlb'] * panel['nim_z']

panel_idx = panel.set_index(['bank', 'fomc_date'])

spec5 = PanelOLS(
    panel_idx['car'],
    sm.add_constant(panel_idx[['kuttner_z', 'lm_pct_z', 'zlb', 'nim_z',
                                'kuttner_zlb', 'lm_zlb',
                                'kuttner_nim', 'lm_nim',
                                'zlb_nim',
                                'kuttner_zlb_nim', 'lm_zlb_nim']]),
    entity_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)
print(spec5.summary.tables[1])

# ── Save results ───────────────────────────────────────────────
results = {
    'analysis_type': 'kuttner_surprise_robustness',
    'n_obs': len(panel),
    'n_banks': len(common_banks),
    'specifications': {
        'kuttner_only': {
            'beta_kuttner': spec1.params.get('kuttner_z', 0),
            't_kuttner': spec1.tstats.get('kuttner_z', 0),
            'r2_within': spec1.rsquared_within,
        },
        'lm_only': {
            'beta_lm': spec2.params.get('lm_pct_z', 0),
            't_lm': spec2.tstats.get('lm_pct_z', 0),
            'r2_within': spec2.rsquared_within,
        },
        'horse_race': {
            'beta_kuttner': spec3.params.get('kuttner_z', 0),
            't_kuttner': spec3.tstats.get('kuttner_z', 0),
            'beta_lm': spec3.params.get('lm_pct_z', 0),
            't_lm': spec3.tstats.get('lm_pct_z', 0),
            'r2_within': spec3.rsquared_within,
        },
        'htm_channel': {
            'kuttner_fasthike_htm': spec4.params.get('kuttner_fasthike_htm', 0),
            't_kuttner_fasthike_htm': spec4.tstats.get('kuttner_fasthike_htm', 0),
            'lm_fasthike_htm': spec4.params.get('lm_fasthike_htm', 0),
            't_lm_fasthike_htm': spec4.tstats.get('lm_fasthike_htm', 0),
        },
        'nim_channel': {
            'kuttner_zlb_nim': spec5.params.get('kuttner_zlb_nim', 0),
            't_kuttner_zlb_nim': spec5.tstats.get('kuttner_zlb_nim', 0),
            'lm_zlb_nim': spec5.params.get('lm_zlb_nim', 0),
            't_lm_zlb_nim': spec5.tstats.get('lm_zlb_nim', 0),
        },
    }
}

with open('results/kuttner_surprise.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
print("\nSaved results/kuttner_surprise.json")

# ── Summary ────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("SUMMARY: Kuttner Surprise Robustness")
print("=" * 70)

s3 = results['specifications']['horse_race']
s4 = results['specifications']['htm_channel']
s5 = results['specifications']['nim_channel']

print(f"""
1. HORSE RACE (Kuttner vs LM%):
   Kuttner surprise: β = {s3['beta_kuttner']:.4f} (t = {s3['t_kuttner']:.2f})
   LM%:             β = {s3['beta_lm']:.4f} (t = {s3['t_lm']:.2f})
   
   {'→ LM% has incremental power beyond Kuttner surprise' if abs(s3['t_lm']) > 1.96 else '→ LM% does NOT have incremental power'}
   {'→ Kuttner surprise has incremental power' if abs(s3['t_kuttner']) > 1.96 else '→ Kuttner surprise does NOT have incremental power'}

2. HTM CHANNEL (FastHike × HTM):
   Kuttner × FastHike × HTM: β = {s4['kuttner_fasthike_htm']:.4f} (t = {s4['t_kuttner_fasthike_htm']:.2f})
   LM% × FastHike × HTM:    β = {s4['lm_fasthike_htm']:.4f} (t = {s4['t_lm_fasthike_htm']:.2f})
   
   {'→ HTM channel robust to Kuttner control' if abs(s4['t_lm_fasthike_htm']) > 1.96 else '→ HTM channel weakened by Kuttner control'}

3. NIM CHANNEL (ZLB × NIM):
   Kuttner × ZLB × NIM: β = {s5['kuttner_zlb_nim']:.4f} (t = {s5['t_kuttner_zlb_nim']:.2f})
   LM% × ZLB × NIM:    β = {s5['lm_zlb_nim']:.4f} (t = {s5['t_lm_zlb_nim']:.2f})
   
   {'→ NIM channel robust to Kuttner control' if abs(s5['t_lm_zlb_nim']) > 1.96 else '→ NIM channel weakened by Kuttner control'}

INTERPRETATION:
If LM% remains significant after controlling for Kuttner surprise, it means
that FOMC language conveys information BEYOND the rate decision itself—
forward guidance, risk assessment, and policy commitment. This is the key
identification argument: LM% is not just a noisy proxy for rate surprises.
""")

print("DONE.")
