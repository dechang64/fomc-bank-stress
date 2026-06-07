#!/usr/bin/env python3
"""
02_event_study.py
Match FOMC dates to bank trading days, compute market-model CAR[0,+1]
for 22+ CCAR banks, and test H1/H2/H3 of the new paper.

H1 (International Transmission): Dovish FOMC statements are associated
    with positive abnormal returns for CCAR banks.

H2 (Cross-Sectional Heterogeneity): The dovish-hawkish bank-return spread
    is larger for (a) banks with higher trading-book exposure, (b) banks
    with lower Tier 1 capital ratios, (c) banks with more CRE exposure.

H3 (Stress-Test Era Amplification): The dovish-hawkish spread is larger
    around DFAST/CCAR announcement weeks (June each year).
"""
import os, json
import numpy as np
import pandas as pd
from scipy import stats

PRICES = r"C:\Users\decha\Desktop\fomc_banks\data_raw\all_banks.csv"
FOMC   = r"C:\Users\decha\Desktop\fomc_supplementary_extracted\SupplementaryAppendix\data\fomc_statements.csv"
OUT    = r"C:\Users\decha\Desktop\fomc_banks\data_proc"
os.makedirs(OUT, exist_ok=True)

print("=" * 70)
print("STEP 2: FOMC × Bank Event Study")
print("=" * 70)

# ---- Load ----
px = pd.read_csv(PRICES, index_col=0, parse_dates=True)
px.sort_index(inplace=True)
fomc = pd.read_csv(FOMC, parse_dates=["date"])

# Bank tickers
BANKS = ["JPM","BAC","C","WFC","GS","MS","USB","PNC","TFC","COF",
         "BK","STT","SCHW","MTB","KEY","CFG","FITB","RF",
         "TD","BMO","RY","BCS","ALLY","NTRS"]
print(f"Banks: {len(BANKS)}")
print(f"Price history: {len(px)} rows  {px.index.min().date()} -> {px.index.max().date()}")
print(f"FOMC meetings: {len(fomc)}")

# ---- Returns ----
rets = px.pct_change(fill_method=None)
log_rets = np.log(px / px.shift(1))

# ---- Find trading day on/after FOMC date ----
def find_tday(d, max_lag=5):
    if d in px.index:
        idx = px.index.get_loc(d)
        if isinstance(idx, slice): idx = idx.start
    else:
        idx = px.index.searchsorted(d)
    return idx

# Market model: CAR using SPX as market
SPX = rets["SPX"]
N_BANKS = len(BANKS)
print(f"\nMatching {len(fomc)} FOMC events × {N_BANKS} banks ...")

# ---- Pre-compute estimation-window regression for each (event, bank) ----
rows = []
for _, r in fomc.iterrows():
    d_fomc = r["date"]
    lm = r["lm_pct"]
    sent = r.get("sentiment_category", "")
    # Find d_0 (FOMC date or next bank trading day)
    idx0 = find_tday(d_fomc)
    if idx0 is None or idx0 >= len(px): continue
    if pd.isna(px.iloc[idx0][BANKS[0]]) and pd.isna(px.iloc[idx0]["SPX"]):
        # FOMC date not a trading day, find next
        for k in range(1, 6):
            if idx0 + k < len(px) and not pd.isna(px.iloc[idx0+k]["SPX"]):
                idx0 = idx0 + k
                break
        else:
            continue
    # Find d_+1
    idx1 = None
    for k in range(1, 6):
        if idx0 + k < len(px) and not pd.isna(px.iloc[idx0+k][BANKS[0]]):
            idx1 = idx0 + k
            break
    if idx1 is None: continue
    # Estimation window
    est_lo, est_hi = idx0 - 150, idx0 - 11
    if est_lo < 0: continue
    if est_hi - est_lo < 30: continue
    # For each bank, compute market model
    rec = {"fomc_date": d_fomc, "d0": px.index[idx0], "d1": px.index[idx1], "lm_pct": lm, "sentiment": sent}
    for b in BANKS:
        y = rets[b].iloc[est_lo:est_hi]
        x = SPX.iloc[est_lo:est_hi]
        ok = y.notna() & x.notna()
        if ok.sum() < 30: continue
        beta, alpha = np.polyfit(x[ok], y[ok], 1)  # np.polyfit returns [slope, intercept]
        # AR on d0 and d1
        r_b0 = rets[b].iloc[idx0] if not pd.isna(rets[b].iloc[idx0]) else np.nan
        r_b1 = rets[b].iloc[idx1] if not pd.isna(rets[b].iloc[idx1]) else np.nan
        r_m0 = rets["SPX"].iloc[idx0] if not pd.isna(rets["SPX"].iloc[idx0]) else np.nan
        r_m1 = rets["SPX"].iloc[idx1] if not pd.isna(rets["SPX"].iloc[idx1]) else np.nan
        if pd.isna(r_b0) or pd.isna(r_b1) or pd.isna(r_m0) or pd.isna(r_m1): continue
        ar0 = r_b0 - (alpha + beta * r_m0)
        ar1 = r_b1 - (alpha + beta * r_m1)
        rec[f"{b}_ar0"] = ar0
        rec[f"{b}_ar1"] = ar1
        rec[f"{b}_car01"] = ar0 + ar1
        rec[f"{b}_alpha"] = alpha
        rec[f"{b}_beta"] = beta
    rows.append(rec)

ev = pd.DataFrame(rows)
print(f"\nMatched events: {len(ev)}")
print(f"  FOMC date range: {ev['fomc_date'].min().date()} -> {ev['fomc_date'].max().date()}")
print(f"  d_0 range:       {ev['d0'].min().date()} -> {ev['d0'].max().date()}")

# Save raw event-level
ev.to_csv(os.path.join(OUT, "bank_events.csv"), index=False)
print(f"Saved: {OUT}\\bank_events.csv ({os.path.getsize(os.path.join(OUT, 'bank_events.csv'))} bytes)")

# ---- Summary statistics ----
print()
print("Per-bank coverage (% of events with valid CAR):")
cov = {}
for b in BANKS:
    col = f"{b}_car01"
    if col in ev.columns:
        n_valid = ev[col].notna().sum()
        cov[b] = n_valid
        if n_valid < 100: continue
        m = ev[col].mean()
        s = ev[col].std()
        print(f"  {b:5s}  N={n_valid:4d}  mean CAR={m*100:+.3f}%  std={s*100:.3f}%")

# ---- Median split (paper convention) ----
med_lm = ev["lm_pct"].median()
print(f"\nMedian LM% = {med_lm:.4f}")
ev["class"] = np.where(ev["lm_pct"] > med_lm, "Hawkish", "Dovish")
print(f"  Hawkish (LM% > median): N={sum(ev['class']=='Hawkish')}")
print(f"  Dovish  (LM% <= median): N={sum(ev['class']=='Dovish')}")

# ---- H1: average bank CAR by class ----
print("\n" + "=" * 70)
print("H1: Bank CAR by FOMC Sentiment Class")
print("=" * 70)
# Equal-weighted bank average
bank_car_cols = [f"{b}_car01" for b in BANKS if f"{b}_car01" in ev.columns]
ev["avg_bank_car"] = ev[bank_car_cols].mean(axis=1)
ev["median_bank_car"] = ev[bank_car_cols].median(axis=1)

for label, col in [("Equal-weighted bank avg", "avg_bank_car"),
                    ("Median bank", "median_bank_car")]:
    dov = ev[ev["class"]=="Dovish"][col].dropna()
    hawk = ev[ev["class"]=="Hawkish"][col].dropna()
    spread = dov.mean() - hawk.mean()
    t = stats.ttest_ind(dov, hawk, equal_var=False)
    print(f"  {label}:")
    print(f"    Dovish  N={len(dov):3d}  mean={dov.mean()*100:+.3f}%  SD={dov.std()*100:.3f}%")
    print(f"    Hawkish N={len(hawk):3d}  mean={hawk.mean()*100:+.3f}%  SD={hawk.std()*100:.3f}%")
    print(f"    Spread  = {spread*100:+.3f}pp  t={t.statistic:.3f}  p={t.pvalue:.4f}")

# ---- Per-bank H1 test ----
print()
print("Per-bank H1 (Dovish - Hawkish CAR[0,+1]):")
print(f"  {'Bank':6s} {'N_dov':>5s} {'N_hawk':>6s} {'Dov%':>7s} {'Hawk%':>7s} {'Spread':>8s} {'t':>7s} {'p':>7s}")
h1_results = []
for b in BANKS:
    col = f"{b}_car01"
    if col not in ev.columns: continue
    dov = ev[ev["class"]=="Dovish"][col].dropna()
    hawk = ev[ev["class"]=="Hawkish"][col].dropna()
    if len(dov) < 10 or len(hawk) < 10: continue
    sp = dov.mean() - hawk.mean()
    t = stats.ttest_ind(dov, hawk, equal_var=False)
    h1_results.append({"bank": b, "N_dov": len(dov), "N_hawk": len(hawk),
                        "dov_mean": dov.mean(), "hawk_mean": hawk.mean(),
                        "spread": sp, "t": t.statistic, "p": t.pvalue})
    print(f"  {b:6s} {len(dov):5d} {len(hawk):6d} {dov.mean()*100:+7.3f} {hawk.mean()*100:+7.3f} {sp*100:+8.3f} {t.statistic:+7.3f} {t.pvalue:7.4f}")

# Save H1
with open(os.path.join(OUT, "h1_per_bank.json"), "w") as f:
    json.dump(h1_results, f, indent=2)

print(f"\nSaved: {OUT}\\h1_per_bank.json")
