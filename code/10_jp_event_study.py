#!/usr/bin/env python3
"""
02_jp_event_study.py
Match FOMC dates to Japanese bank trading days, compute market-model
CAR[0, +1] using Nikkei 225 as the market proxy, and test H1-H4 for
the Japanese bank sample.

Key timezone handling:
  - FOMC is released at 2pm US ET.
  - For US (NY): same trading day, FOMC date = d_0.
  - For Japan (Tokyo): 2pm ET = 4-5am JST NEXT day. So the FOMC news hits
    JP markets on the FIRST JP TRADING DAY ON OR AFTER (FOMC_date + 1).
  - Example: FOMC on Tue 1994-05-17 2pm ET = Wed 1994-05-18 3am JST.
    The news is priced into JP on Wed 1994-05-18.
"""
import os, json
import numpy as np
import pandas as pd
from scipy import stats

PRICES = "data/all_jp_banks.csv"
FOMC   = "data/fomc_statements.csv"
OUT    = "data"
os.makedirs(OUT, exist_ok=True)

print("=" * 70)
print("STEP 2: FOMC × Japanese Bank Event Study")
print("=" * 70)

# ---- Load ----
px = pd.read_csv(PRICES, index_col=0, parse_dates=True)
px.sort_index(inplace=True)
fomc = pd.read_csv(FOMC, parse_dates=["date"])

JP_BANKS = ["MUFG", "Mizuho", "SMFG", "SMTH", "Resona", "Chiba",
            "Gunma", "Suruga", "Yamaguchi", "Concordia", "Hokuhoku"]
print(f"JP banks: {len(JP_BANKS)}")
print(f"Price history: {len(px)} rows  {px.index.min().date()} -> {px.index.max().date()}")
print(f"FOMC meetings: {len(fomc)}")

# ---- Returns ----
rets = px.pct_change(fill_method=None)

# ---- Find JP trading day on or after FOMC_date + 1 day ----
# (FOMC at 2pm ET is after JP close at 3pm JST same day, so it's the NEXT JP day)
# Use Nikkei 225 (NK225) to determine JP trading days, since it's available for
# the full 1993-2026 period; individual banks have shorter histories (MUFG 2005+,
# Mizuho 2003+, etc.) and would falsely flag "not a JP trading day" if used.
def find_jp_tday_after_offset(d, offset_days=1, max_lag=10):
    target = d + pd.Timedelta(days=offset_days)
    if target in px.index:
        idx = px.index.get_loc(target)
        if isinstance(idx, slice): idx = idx.start
    else:
        idx = px.index.searchsorted(target)
    for k in range(max_lag + 1):
        if idx + k >= len(px): return None
        d_cand = px.index[idx + k]
        if pd.notna(px.iloc[idx + k]["NK225"]):  # use Nikkei, not first bank
            return d_cand, idx + k
    return None

def find_next_jp_tday(idx0):
    for k in range(1, 8):
        if idx0 + k >= len(px): return None, None
        d_cand = px.index[idx0 + k]
        if pd.notna(px.iloc[idx0 + k]["NK225"]):
            return d_cand, idx0 + k
    return None, None

# Market model: use Nikkei 225 as market
NK = rets["NK225"]

# ---- Pre-compute for each (event, bank) ----
rows = []
for _, r in fomc.iterrows():
    d_fomc = r["date"]
    lm = r["lm_pct"]
    sent = r.get("sentiment_category", "")
    # FOMC_date + 1 day = JP event day 0
    d0, idx0 = find_jp_tday_after_offset(d_fomc, offset_days=1, max_lag=10)
    if d0 is None: continue
    # Day +1 in JP
    d1, idx1 = find_next_jp_tday(idx0)
    if d1 is None: continue
    # Estimation window [-150, -11] trading days in JP
    est_lo, est_hi = idx0 - 150, idx0 - 11
    if est_lo < 0: continue
    if est_hi - est_lo < 30: continue
    # For each JP bank, market model CAR
    rec = {"fomc_date": d_fomc, "d0": d0, "d1": d1, "lm_pct": lm, "sentiment": sent}
    for b in JP_BANKS:
        y = rets[b].iloc[est_lo:est_hi]
        x = NK.iloc[est_lo:est_hi]
        ok = y.notna() & x.notna()
        if ok.sum() < 30: continue
        beta, alpha = np.polyfit(x[ok].values, y[ok].values, 1)
        # AR on d0 and d1
        r_b0 = rets[b].iloc[idx0] if not pd.isna(rets[b].iloc[idx0]) else np.nan
        r_b1 = rets[b].iloc[idx1] if not pd.isna(rets[b].iloc[idx1]) else np.nan
        r_m0 = NK.iloc[idx0] if not pd.isna(NK.iloc[idx0]) else np.nan
        r_m1 = NK.iloc[idx1] if not pd.isna(NK.iloc[idx1]) else np.nan
        if pd.isna(r_b0) or pd.isna(r_b1) or pd.isna(r_m0) or pd.isna(r_m1): continue
        ar0 = r_b0 - (alpha + beta * r_m0)
        ar1 = r_b1 - (alpha + beta * r_m1)
        rec[f"{b}_ar0"] = ar0
        rec[f"{b}_ar1"] = ar1
        rec[f"{b}_car01"] = ar0 + ar1
        rec[f"{b}_alpha"] = alpha
        rec[f"{b}_beta"] = beta
    rows.append(rec)

ev_jp = pd.DataFrame(rows)
print(f"\nMatched events: {len(ev_jp)}")
print(f"  FOMC date range: {ev_jp['fomc_date'].min().date()} -> {ev_jp['fomc_date'].max().date()}")

# Save
ev_jp.to_csv(os.path.join(OUT, "jp_bank_events.csv"), index=False)
print(f"Saved: {OUT}\\jp_bank_events.csv")

# ---- Coverage ----
print()
print("Per-JP-bank coverage:")
JP_CAR_COLS = [f"{b}_car01" for b in JP_BANKS if f"{b}_car01" in ev_jp.columns]
for b in JP_BANKS:
    col = f"{b}_car01"
    if col in ev_jp.columns:
        n_valid = ev_jp[col].notna().sum()
        if n_valid > 10:
            m = ev_jp[col].mean()
            print(f"  {b:10s}  N={n_valid:4d}  mean CAR={m*100:+.3f}%  std={ev_jp[col].std()*100:.3f}%")

# Average CAR
ev_jp["avg_jp_car"] = ev_jp[JP_CAR_COLS].mean(axis=1)
ev_jp["median_jp_car"] = ev_jp[JP_CAR_COLS].median(axis=1)

# Median split
med_lm = ev_jp["lm_pct"].median()
ev_jp["class"] = np.where(ev_jp["lm_pct"] > med_lm, "Hawkish", "Dovish")

# ---- H1: Full-sample ----
print()
print("=" * 70)
print("H1: Full-Sample Dovish-Hawkish Bank-Return Spread (Japan)")
print("=" * 70)
for label, col in [("Equal-weighted JP bank avg", "avg_jp_car"),
                    ("Median JP bank", "median_jp_car")]:
    dov = ev_jp[ev_jp["class"]=="Dovish"][col].dropna()
    hawk = ev_jp[ev_jp["class"]=="Hawkish"][col].dropna()
    spread = dov.mean() - hawk.mean()
    t = stats.ttest_ind(dov, hawk, equal_var=False)
    print(f"  {label}:")
    print(f"    Dovish  N={len(dov):3d}  mean={dov.mean()*100:+.3f}%  SD={dov.std()*100:.3f}%")
    print(f"    Hawkish N={len(hawk):3d}  mean={hawk.mean()*100:+.3f}%  SD={hawk.std()*100:.3f}%")
    print(f"    Spread  = {spread*100:+.3f}pp  t={t.statistic:.3f}  p={t.pvalue:.4f}")

# Per-bank
print()
print("Per-JP-bank H1 (Dovish - Hawkish CAR[0,+1]):")
h1_jp = []
for b in JP_BANKS:
    col = f"{b}_car01"
    if col not in ev_jp.columns: continue
    dov = ev_jp[ev_jp["class"]=="Dovish"][col].dropna()
    hawk = ev_jp[ev_jp["class"]=="Hawkish"][col].dropna()
    if len(dov) < 5 or len(hawk) < 5: continue
    sp = dov.mean() - hawk.mean()
    t = stats.ttest_ind(dov, hawk, equal_var=False)
    h1_jp.append({"bank": b, "N_dov": len(dov), "N_hawk": len(hawk),
                  "dov_mean": dov.mean(), "hawk_mean": hawk.mean(),
                  "spread": sp, "t": t.statistic, "p": t.pvalue})
    print(f"  {b:10s} {len(dov):5d} {len(hawk):5d} {dov.mean()*100:+7.3f} {hawk.mean()*100:+7.3f} {sp*100:+8.3f} {t.statistic:+7.3f} {t.pvalue:7.4f}")

with open(os.path.join(OUT, "jp_h1.json"), "w") as f:
    json.dump(h1_jp, f, indent=2)

# ---- H2: Pre-DFAST vs DFAST ----
print()
print("=" * 70)
print("H2: Pre-DFAST vs DFAST-Era (Japan)")
print("=" * 70)
ev_jp["era"] = np.where(ev_jp["fomc_date"] < pd.Timestamp("2009-01-01"),
                        "Pre-DFAST", "DFAST-era")
for era in ["Pre-DFAST", "DFAST-era"]:
    sub = ev_jp[ev_jp["era"]==era]
    dov = sub[sub["class"]=="Dovish"]["avg_jp_car"].dropna()
    hawk = sub[sub["class"]=="Hawkish"]["avg_jp_car"].dropna()
    if len(dov) < 5 or len(hawk) < 5: continue
    sp = dov.mean() - hawk.mean()
    se = np.sqrt(dov.var(ddof=1)/len(dov) + hawk.var(ddof=1)/len(hawk))
    t = sp/se if se > 0 else np.nan
    print(f"  {era:10s}  N={len(sub):3d}  Dov={dov.mean()*100:+.3f}%  Hawk={hawk.mean()*100:+.3f}%  Spread={sp*100:+.3f}pp  t={t:.2f}")

# ---- Bootstrap ----
print()
print("=" * 70)
print("Bootstrap 95% CI for Japan H1 Spread")
print("=" * 70)
rng = np.random.default_rng(42)
dov_idx = ev_jp[ev_jp["class"]=="Dovish"].index.values
hawk_idx = ev_jp[ev_jp["class"]=="Hawkish"].index.values
# Use iloc to get integer positions (some rows have NaN avg_jp_car)
dov_pos = [ev_jp.index.get_loc(i) for i in dov_idx if pd.notna(ev_jp.loc[i, "avg_jp_car"])]
hawk_pos = [ev_jp.index.get_loc(i) for i in hawk_idx if pd.notna(ev_jp.loc[i, "avg_jp_car"])]
print(f"  Valid dov positions: {len(dov_pos)}, hawk: {len(hawk_pos)}")
boots = np.empty(10000)
all_car = ev_jp["avg_jp_car"].values
for b in range(10000):
    ds = rng.choice(dov_pos, size=len(dov_pos), replace=True)
    hs = rng.choice(hawk_pos, size=len(hawk_pos), replace=True)
    boots[b] = all_car[ds].mean() - all_car[hs].mean()
boots = boots[~np.isnan(boots)]
ci_lo, ci_hi = np.percentile(boots, [2.5, 97.5])
print(f"  Mean: {boots.mean()*100:+.3f}pp  95% CI: [{ci_lo*100:+.3f}pp, {ci_hi*100:+.3f}pp]")

# ---- Save results ----
results = {
    "N_events": int(len(ev_jp)),
    "N_banks": int(len(JP_BANKS)),
    "H1_avg": {
        "Dov_N": int(sum(ev_jp["class"]=="Dovish")),
        "Hawk_N": int(sum(ev_jp["class"]=="Hawkish")),
        "Dov_mean": float(ev_jp[ev_jp["class"]=="Dovish"]["avg_jp_car"].mean()),
        "Hawk_mean": float(ev_jp[ev_jp["class"]=="Hawkish"]["avg_jp_car"].mean()),
        "spread": float(ev_jp[ev_jp["class"]=="Dovish"]["avg_jp_car"].mean() - ev_jp[ev_jp["class"]=="Hawkish"]["avg_jp_car"].mean()),
        "t_welch": float(stats.ttest_ind(ev_jp[ev_jp["class"]=="Dovish"]["avg_jp_car"].dropna(),
                                          ev_jp[ev_jp["class"]=="Hawkish"]["avg_jp_car"].dropna(),
                                          equal_var=False).statistic),
        "p_welch": float(stats.ttest_ind(ev_jp[ev_jp["class"]=="Dovish"]["avg_jp_car"].dropna(),
                                          ev_jp[ev_jp["class"]=="Hawkish"]["avg_jp_car"].dropna(),
                                          equal_var=False).pvalue),
    },
    "bootstrap": {
        "mean_spread": float(boots.mean()) if not np.isnan(boots.mean()) else None,
        "ci_lo": float(ci_lo) if not np.isnan(ci_lo) else None,
        "ci_hi": float(ci_hi) if not np.isnan(ci_hi) else None,
    },
}
with open(os.path.join(OUT, "jp_h1_results.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {OUT}\\jp_h1_results.json")
