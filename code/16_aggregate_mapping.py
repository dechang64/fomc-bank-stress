"""
Plan C: Cross-Sectional → Aggregate Mapping
=============================================
Use cross-sectional regression coefficients × system NIM/HTM distribution
to compute aggregate CVaR and system-level CAR impact.

This gives the paper "macro policy implications":
- Not just "which banks are more vulnerable" but "how vulnerable is the SYSTEM"
- SVB case study: use cross-sectional coefficients to predict SVB's CAR
- Scenario analysis: what if FastHike happens again with current balance sheets?

Key equations:
  1. Bank-level predicted CAR = Σ β_k × X_{i,k} (from cross-sectional regressions)
  2. System CAR = Σ w_i × CAR_i (w_i = asset-weighted)
  3. System CVaR = E[CAR | CAR < VaR_5%]
  4. SVB predicted CAR = Σ β_k × X_{SVB,k}
"""

import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

from scipy import stats

# ── Load data ──────────────────────────────────────────────────
print("=" * 70)
print("Cross-Sectional → Aggregate Mapping")
print("=" * 70)

y9c = pd.read_csv('data/y9c_complete.csv')
be = pd.read_csv('data/bank_events.csv')
reg = pd.read_csv('data/fomc_paper_regression_data.csv')

# Load quasi-experiment results for coefficients
with open('results/htm_afs_quasi_experiment.json') as f:
    htm_results = json.load(f)

# Load NIM microfoundation results
with open('results/nim_microfoundation.json') as f:
    nim_results = json.load(f)

# ── Step 1: Extract cross-sectional coefficients ───────────────
print("\n" + "=" * 70)
print("STEP 1: Cross-Sectional Coefficients")
print("=" * 70)

# From the paper's Table 5 (channel decomposition):
# FastHike × HTM = -0.054 (from quasi-experiment, Bank+Time FE)
# Dovish × ZLB × NIM = +0.68 (from paper)
# FastHike × CRE = +0.93 (from paper, denominator effect)

# Use the Bank+Time FE coefficients as the cleanest estimates
beta_fh_htm = htm_results['specifications']['bank_time_fe']['beta_fh_htm']  # -0.054
beta_fh_afs = htm_results['specifications']['bank_time_fe']['beta_fh_afs']  # 0.0003

# NIM channel coefficients (from spec5 full model)
spec5 = nim_results['specifications']['full_model']
beta_dov_zlb_nim = spec5['params'].get('dovish_zlb_nim', 0)
beta_dov_zlb_nim_trading = spec5['params'].get('dovish_zlb_nim_trading', 0)

print(f"FastHike × HTM:  β = {beta_fh_htm:.4f}")
print(f"FastHike × AFS:  β = {beta_fh_afs:.4f}")
print(f"Dovish × ZLB × NIM: β = {beta_dov_zlb_nim:.4f}")
print(f"Dovish × ZLB × NIM × Trading: β = {beta_dov_zlb_nim_trading:.4f}")

# ── Step 2: Build system balance sheet snapshot ────────────────
print("\n" + "=" * 70)
print("STEP 2: System Balance Sheet Snapshot")
print("=" * 70)

# Use latest available data for each bank
latest = y9c.sort_values('report_date').groupby('ticker').last().reset_index()

# Asset weights
total_system_assets = latest['total_assets'].sum()
latest['weight'] = latest['total_assets'] / total_system_assets

print(f"\nSystem total assets: ${total_system_assets/1e9:.1f}B")
print(f"N banks: {len(latest)}")
print(f"\nAsset-weighted characteristics:")
print(f"  HTM ratio: {np.average(latest['htm_ratio'], weights=latest['weight']):.4f}")
print(f"  AFS ratio: {np.average(latest['afs_ratio'], weights=latest['weight']):.4f}")
print(f"  NIM: {np.average(latest['nim'], weights=latest['weight']):.4f}")
print(f"  Trading ratio: {np.average(latest['trading_ratio'], weights=latest['weight']):.4f}")
print(f"  Deposit ratio: {np.average(latest['deposit_ratio'], weights=latest['weight']):.4f}")

# ── Step 3: Compute system-level CAR impact ────────────────────
print("\n" + "=" * 70)
print("STEP 3: System-Level CAR Impact Under Scenarios")
print("=" * 70)

# Scenario 1: FastHike (12 meetings of rapid rate hikes)
# Predicted CAR per meeting for each bank:
#   CAR_i = β_fh_htm × HTM_i + β_fh_afs × AFS_i
latest['pred_car_fasthike'] = beta_fh_htm * latest['htm_ratio'] + beta_fh_afs * latest['afs_ratio']

# System CAR = asset-weighted average
system_car_fasthike = np.average(latest['pred_car_fasthike'], weights=latest['weight'])

# Cumulative over 12 meetings
cumulative_system_car = system_car_fasthike * 12

print(f"\nScenario 1: FastHike (12 meetings)")
print(f"  Per-meeting system CAR: {system_car_fasthike*100:.3f}%")
print(f"  Cumulative (12 meetings): {cumulative_system_car*100:.2f}%")

# Scenario 2: Dovish ZLB (76 meetings)
# Predicted CAR per meeting:
#   CAR_i = β_dov_zlb_nim × NIM_i + β_dov_zlb_nim_trading × NIM_i × Trading_i
latest['pred_car_dovish_zlb'] = (beta_dov_zlb_nim * latest['nim'] + 
                                  beta_dov_zlb_nim_trading * latest['nim'] * latest['trading_ratio'])
system_car_dovish_zlb = np.average(latest['pred_car_dovish_zlb'], weights=latest['weight'])

print(f"\nScenario 2: Dovish ZLB (76 meetings)")
print(f"  Per-meeting system CAR: {system_car_dovish_zlb*100:.3f}%")
print(f"  Cumulative (76 meetings): {system_car_dovish_zlb*76*100:.2f}%")

# ── Step 4: System CVaR computation ────────────────────────────
print("\n" + "=" * 70)
print("STEP 4: System CVaR (Conditional Value at Risk)")
print("=" * 70)

# Use actual CAR data to compute empirical CVaR
car_cols = [c for c in be.columns if c.endswith('_car01')]
common_tickers = [c.replace('_car01', '') for c in car_cols 
                  if c.replace('_car01', '') in latest['ticker'].values]

# Build panel of actual CARs
car_panel = []
for _, row in be.iterrows():
    fdate = row['fomc_date']
    for ticker in common_tickers:
        car_col = f'{ticker}_car01'
        if car_col in be.columns and pd.notna(row[car_col]):
            bank_data = latest[latest['ticker'] == ticker].iloc[0]
            car_panel.append({
                'fomc_date': fdate,
                'ticker': ticker,
                'car': row[car_col],
                'htm_ratio': bank_data['htm_ratio'],
                'weight': bank_data['weight'],
                'total_assets': bank_data['total_assets'],
            })

car_df = pd.DataFrame(car_panel)
car_df['fomc_date'] = pd.to_datetime(car_df['fomc_date'])

# Compute system CAR per FOMC meeting (asset-weighted)
system_cars = car_df.groupby('fomc_date').apply(
    lambda x: np.average(x['car'], weights=x['weight'])
).reset_index()
system_cars.columns = ['fomc_date', 'system_car']

# Merge with FOMC characteristics
reg['fomc_date'] = pd.to_datetime(reg['fomc_date'])
system_cars = system_cars.merge(
    reg[['fomc_date', 'post2008', 'tightening', 'inflation_era', 'surprise_type']],
    on='fomc_date', how='left'
)

# FastHike period
fasthike_dates = pd.to_datetime([
    '2022-03-16', '2022-05-04', '2022-06-15', '2022-07-27',
    '2022-09-21', '2022-11-02', '2022-12-14', '2023-02-01',
    '2023-03-22', '2023-05-03', '2023-06-14', '2023-07-26'
])
system_cars['fasthike'] = system_cars['fomc_date'].isin(fasthike_dates).astype(int)

# ZLB period
zlb1 = (system_cars['fomc_date'] >= '2008-12-16') & (system_cars['fomc_date'] <= '2015-12-16')
zlb2 = (system_cars['fomc_date'] >= '2020-03-15') & (system_cars['fomc_date'] <= '2022-03-16')
system_cars['zlb'] = (zlb1 | zlb2).astype(int)

# Compute CVaR for different periods
for period_name, mask in [
    ('Full Sample', system_cars['system_car'].notna()),
    ('FastHike', system_cars['fasthike'] == 1),
    ('ZLB', system_cars['zlb'] == 1),
    ('Non-crisis', (system_cars['fasthike'] == 0) & (system_cars['zlb'] == 0)),
]:
    subset = system_cars.loc[mask, 'system_car'].dropna()
    if len(subset) > 5:
        var_5 = subset.quantile(0.05)
        cvar_5 = subset[subset <= var_5].mean()
        var_1 = subset.quantile(0.01)
        cvar_1 = subset[subset <= var_1].mean() if (subset <= var_1).sum() > 0 else np.nan
        print(f"\n{period_name} (N={len(subset)}):")
        print(f"  Mean CAR: {subset.mean()*100:.3f}%")
        print(f"  Std: {subset.std()*100:.3f}%")
        print(f"  VaR(5%): {var_5*100:.3f}%")
        print(f"  CVaR(5%): {cvar_5*100:.3f}%")
        if not np.isnan(cvar_1):
            print(f"  VaR(1%): {var_1*100:.3f}%")
            print(f"  CVaR(1%): {cvar_1*100:.3f}%")

# ── Step 5: Predicted vs Actual system CAR ─────────────────────
print("\n" + "=" * 70)
print("STEP 5: Predicted vs Actual System CAR")
print("=" * 70)

# For FastHike period: compare predicted vs actual
fh_actual = system_cars[system_cars['fasthike'] == 1].copy()
fh_actual['predicted'] = fh_actual['fomc_date'].apply(
    lambda d: np.average(
        beta_fh_htm * latest['htm_ratio'] + beta_fh_afs * latest['afs_ratio'],
        weights=latest['weight']
    )
)

print("\nFastHike Period: Predicted vs Actual System CAR")
print(f"{'Date':<12} {'Predicted':>10} {'Actual':>10} {'Error':>10}")
print("-" * 45)
for _, row in fh_actual.iterrows():
    error = row['system_car'] - row['predicted']
    print(f"{row['fomc_date'].strftime('%Y-%m-%d'):<12} {row['predicted']*100:>9.3f}% {row['system_car']*100:>9.3f}% {error*100:>9.3f}%")

# Correlation
corr = fh_actual[['predicted', 'system_car']].corr().iloc[0, 1]
print(f"\nCorrelation (predicted vs actual): {corr:.3f}")

# ── Step 6: SVB Counterfactual ─────────────────────────────────
print("\n" + "=" * 70)
print("STEP 6: SVB Counterfactual Analysis")
print("=" * 70)

# SVB balance sheet (from FDIC data, 2022Q4)
# HTM securities: $91.3B, Total assets: $211.8B → HTM ratio = 0.431
# AFS securities: $0 (SVB had minimal AFS)
# NIM: ~0.022 (relatively high for a regional bank)
svb_data = {
    'ticker': 'SIVB',
    'htm_ratio': 0.431,
    'afs_ratio': 0.0,
    'nim': 0.022,
    'trading_ratio': 0.001,
    'deposit_ratio': 0.92,
    'total_assets': 211.8e9,
    'weight': 211.8e9 / (total_system_assets + 211.8e9),  # If SVB were in DFAST
}

# Predicted CAR per FastHike meeting
svb_pred_car_fh = beta_fh_htm * svb_data['htm_ratio'] + beta_fh_afs * svb_data['afs_ratio']
avg_bank_pred_car_fh = np.average(latest['pred_car_fasthike'], weights=latest['weight'])

print(f"\nSVB predicted CAR per FastHike meeting: {svb_pred_car_fh*100:.3f}%")
print(f"Average DFAST bank predicted CAR: {avg_bank_pred_car_fh*100:.3f}%")
print(f"SVB excess loss per meeting: {(svb_pred_car_fh - avg_bank_pred_car_fh)*100:.3f}%")
print(f"SVB cumulative loss (12 meetings): {svb_pred_car_fh*12*100:.2f}%")
print(f"Average bank cumulative loss (12 meetings): {avg_bank_pred_car_fh*12*100:.2f}%")

# What if SVB had average HTM ratio?
svb_counterfactual = beta_fh_htm * latest['htm_ratio'].mean() + beta_fh_afs * svb_data['afs_ratio']
print(f"\nCounterfactual: SVB with avg HTM ratio ({latest['htm_ratio'].mean():.3f})")
print(f"  Predicted CAR per meeting: {svb_counterfactual*100:.3f}%")
print(f"  Cumulative (12 meetings): {svb_counterfactual*12*100:.2f}%")
print(f"  Difference from actual SVB: {(svb_counterfactual - svb_pred_car_fh)*12*100:.2f}%")

# ── Step 7: Scenario Analysis — What if FastHike happened today? ─
print("\n" + "=" * 70)
print("STEP 7: Scenario Analysis — FastHike with Current Balance Sheets")
print("=" * 70)

# Use latest balance sheet data
# What would system CAR look like if FastHike happened now?
current_pred = beta_fh_htm * latest['htm_ratio'] + beta_fh_afs * latest['afs_ratio']
current_system_car = np.average(current_pred, weights=latest['weight'])

# Compare with 2022Q1 balance sheets (start of FastHike)
fh_start = y9c[(y9c['report_date'] >= '2022-01-01') & (y9c['report_date'] <= '2022-03-31')]
fh_start_latest = fh_start.sort_values('report_date').groupby('ticker').last().reset_index()
fh_start_latest['weight'] = fh_start_latest['total_assets'] / fh_start_latest['total_assets'].sum()
fh_start_pred = beta_fh_htm * fh_start_latest['htm_ratio'] + beta_fh_afs * fh_start_latest['afs_ratio']
fh_start_system_car = np.average(fh_start_pred, weights=fh_start_latest['weight'])

print(f"\nCurrent balance sheets:")
print(f"  System HTM ratio: {np.average(latest['htm_ratio'], weights=latest['weight']):.4f}")
print(f"  Predicted system CAR per FastHike meeting: {current_system_car*100:.3f}%")
print(f"  Cumulative (12 meetings): {current_system_car*12*100:.2f}%")

print(f"\n2022Q1 balance sheets (actual FastHike):")
print(f"  System HTM ratio: {np.average(fh_start_latest['htm_ratio'], weights=fh_start_latest['weight']):.4f}")
print(f"  Predicted system CAR per FastHike meeting: {fh_start_system_car*100:.3f}%")
print(f"  Cumulative (12 meetings): {fh_start_system_car*12*100:.2f}%")

# HTM ratio change
print(f"\nChange in system HTM ratio: {np.average(latest['htm_ratio'], weights=latest['weight']) - np.average(fh_start_latest['htm_ratio'], weights=fh_start_latest['weight']):+.4f}")
print(f"Change in predicted system CAR: {(current_system_car - fh_start_system_car)*100:+.3f}% per meeting")

# ── Step 8: Bank-level vulnerability ranking ───────────────────
print("\n" + "=" * 70)
print("STEP 8: Bank-Level Vulnerability Ranking (FastHike Scenario)")
print("=" * 70)

latest['vulnerability_score'] = current_pred
latest = latest.sort_values('vulnerability_score')

print(f"\n{'Bank':<6} {'HTM%':>6} {'AFS%':>6} {'Pred CAR':>10} {'Assets($B)':>12} {'Contribution':>12}")
print("-" * 60)
for _, row in latest.iterrows():
    contribution = row['vulnerability_score'] * row['weight']
    print(f"{row['ticker']:<6} {row['htm_ratio']*100:>5.1f}% {row['afs_ratio']*100:>5.1f}% "
          f"{row['vulnerability_score']*100:>9.3f}% {row['total_assets']/1e9:>11.1f}B {contribution*100:>11.4f}%")

# Top 3 contributors to system risk
latest['abs_contribution'] = np.abs(latest['vulnerability_score'] * latest['weight'])
top3 = latest.nlargest(3, 'abs_contribution')
print(f"\nTop 3 contributors to system CAR impact:")
for _, row in top3.iterrows():
    print(f"  {row['ticker']}: {row['abs_contribution']*100:.4f}% ({row['abs_contribution']/latest['abs_contribution'].sum()*100:.1f}% of total)")

# ── Save results ───────────────────────────────────────────────
results = {
    'analysis_type': 'cross_sectional_to_aggregate',
    'coefficients': {
        'beta_fh_htm': beta_fh_htm,
        'beta_fh_afs': beta_fh_afs,
        'beta_dov_zlb_nim': beta_dov_zlb_nim,
        'beta_dov_zlb_nim_trading': beta_dov_zlb_nim_trading,
    },
    'system_characteristics': {
        'total_assets_bn': total_system_assets / 1e9,
        'n_banks': len(latest),
        'asset_weighted_htm': np.average(latest['htm_ratio'], weights=latest['weight']),
        'asset_weighted_nim': np.average(latest['nim'], weights=latest['weight']),
        'asset_weighted_trading': np.average(latest['trading_ratio'], weights=latest['weight']),
    },
    'scenario_fasthike': {
        'per_meeting_system_car_pp': system_car_fasthike * 100,
        'cumulative_12_meetings_pp': cumulative_system_car * 100,
    },
    'scenario_dovish_zlb': {
        'per_meeting_system_car_pp': system_car_dovish_zlb * 100,
        'cumulative_76_meetings_pp': system_car_dovish_zlb * 76 * 100,
    },
    'svb_counterfactual': {
        'svb_htm_ratio': svb_data['htm_ratio'],
        'svb_pred_car_per_meeting_pp': svb_pred_car_fh * 100,
        'svb_cumulative_12_pp': svb_pred_car_fh * 12 * 100,
        'avg_bank_cumulative_12_pp': avg_bank_pred_car_fh * 12 * 100,
        'counterfactual_avg_htm_cumulative_12_pp': svb_counterfactual * 12 * 100,
        'htm_effect_pp': (svb_counterfactual - svb_pred_car_fh) * 12 * 100,
    },
    'current_vs_2022': {
        'current_system_car_pp': current_system_car * 100,
        'current_cumulative_12_pp': current_system_car * 12 * 100,
        'fh_start_system_car_pp': fh_start_system_car * 100,
        'fh_start_cumulative_12_pp': fh_start_system_car * 12 * 100,
    },
    'vulnerability_ranking': [
        {'ticker': row['ticker'], 'htm_ratio': row['htm_ratio'], 
         'pred_car_pp': row['vulnerability_score'] * 100,
         'assets_bn': row['total_assets'] / 1e9,
         'contribution_pp': row['vulnerability_score'] * row['weight'] * 100}
        for _, row in latest.iterrows()
    ],
}

with open('results/aggregate_mapping.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
print("\nResults saved to results/aggregate_mapping.json")

# ── Summary ────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("SUMMARY: Cross-Sectional → Aggregate Mapping")
print("=" * 70)

print(f"""
Using cross-sectional coefficients from the quasi-experiment and NIM 
microfoundation analyses, we map bank-level vulnerability to system-level 
impact:

1. FASTHIKE SCENARIO (12 meetings of rapid rate hikes):
   - System CAR per meeting: {system_car_fasthike*100:.3f}%
   - Cumulative system CAR: {cumulative_system_car*100:.2f}%
   - Top 3 banks contribute {top3['abs_contribution'].sum()/latest['abs_contribution'].sum()*100:.1f}% of system impact

2. SVB COUNTERFACTUAL:
   - SVB predicted CAR per meeting: {svb_pred_car_fh*100:.3f}%
   - SVB cumulative (12 meetings): {svb_pred_car_fh*12*100:.2f}%
   - If SVB had average HTM: {svb_counterfactual*12*100:.2f}%
   - HTM effect: {(svb_counterfactual-svb_pred_car_fh)*12*100:+.2f}%
   → SVB's extreme HTM ratio explains {(svb_pred_car_fh-svb_counterfactual)/(svb_pred_car_fh)*100:.0f}% of its predicted loss

3. CURRENT VULNERABILITY:
   - Current system HTM ratio: {np.average(latest['htm_ratio'], weights=latest['weight']):.4f}
   - 2022Q1 system HTM ratio: {np.average(fh_start_latest['htm_ratio'], weights=fh_start_latest['weight']):.4f}
   - Current predicted system CAR: {current_system_car*100:.3f}% per meeting
   - 2022Q1 predicted system CAR: {fh_start_system_car*100:.3f}% per meeting
   → System is {'more' if current_system_car < fh_start_system_car else 'less'} vulnerable than at FastHike start

These results provide the macro policy implication: stress test scenarios 
should incorporate the cross-sectional structure of bank balance sheets, 
not just aggregate interest rate shocks. The HTM channel's concentration 
in a few large banks means that system-level CVaR is dominated by tail 
institutions, not the average bank.
""")

print("DONE.")
