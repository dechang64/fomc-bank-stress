#!/usr/bin/env python3
"""
03_stress_era_analysis.py
Test regime-dependent and DFAST-window effects of FOMC language on bank returns.

H2 (Stress-Test Era Amplification): The dovish-hawkish bank-return spread
    is larger in the post-2009 DFAST era than in the pre-2009 era.

H3 (DFAST Announcement Window): The dovish-hawkish bank-return spread
    is amplified in the 5 trading days surrounding annual DFAST/CCAR
    announcement dates (typically in June).

H4 (Quintile Response): The bank-return response to LM% is non-monotonic
    across quintiles, with the most-dovish (Q1) and most-hawkish (Q5)
    generating weaker responses than the middle quintiles.
"""
import os, json
import numpy as np
import pandas as pd
from scipy import stats

EV = "data/bank_events.csv"
OUT = "data"

ev = pd.read_csv(EV, parse_dates=["fomc_date","d0","d1"])

# Bank CAR columns
BANK_CAR_COLS = [c for c in ev.columns if c.endswith("_car01")]
BANKS = [c.replace("_car01","") for c in BANK_CAR_COLS]
print(f"Banks: {len(BANKS)}")
print(f"Events: {len(ev)}")

# Average bank CAR
ev["avg_bank_car"] = ev[BANK_CAR_COLS].mean(axis=1)
ev["median_bank_car"] = ev[BANK_CAR_COLS].median(axis=1)

# Median split
med_lm = ev["lm_pct"].median()
ev["class"] = np.where(ev["lm_pct"] > med_lm, "Hawkish", "Dovish")

# ---- H2: Pre vs Post-2009 (DFAST era) ----
print("\n" + "=" * 70)
print("H2: Stress-Test Era Amplification (Pre-2009 vs Post-2009)")
print("=" * 70)
ev["era"] = np.where(ev["fomc_date"] < pd.Timestamp("2009-01-01"),
                     "Pre-DFAST", "DFAST-era")
for era in ["Pre-DFAST", "DFAST-era"]:
    sub = ev[ev["era"]==era]
    dov = sub[sub["class"]=="Dovish"]["avg_bank_car"].dropna()
    hawk = sub[sub["class"]=="Hawkish"]["avg_bank_car"].dropna()
    if len(dov) < 5 or len(hawk) < 5: continue
    spread = dov.mean() - hawk.mean()
    se = np.sqrt(dov.var(ddof=1)/len(dov) + hawk.var(ddof=1)/len(hawk))
    t = spread/se if se > 0 else np.nan
    print(f"  {era:10s}  N_total={len(sub):3d}  N_dov={len(dov):3d}  N_hawk={len(hawk):3d}  "
          f"Dov mean={dov.mean()*100:+.3f}%  Hawk mean={hawk.mean()*100:+.3f}%  "
          f"Spread={spread*100:+.3f}pp  t={t:.2f}")

# ---- DFAST announcement dates ----
# Key stress-test/CCAR result announcement dates (from FRB press releases)
# Format: (year, [list of announcement dates])
DFAST_DATES = {
    # SCAP (2009)
    2009: [pd.Timestamp("2009-05-07")],  # SCAP results
    # CCAR (2010-)
    2010: [pd.Timestamp("2010-11-09")],  # first CCAR
    2011: [pd.Timestamp("2011-03-01"), pd.Timestamp("2011-11-22")],
    2012: [pd.Timestamp("2012-03-13"), pd.Timestamp("2012-11-13")],
    2013: [pd.Timestamp("2013-03-07"), pd.Timestamp("2013-10-17")],
    2014: [pd.Timestamp("2014-03-20"), pd.Timestamp("2014-10-23")],
    2015: [pd.Timestamp("2015-03-05"), pd.Timestamp("2015-10-15")],
    2016: [pd.Timestamp("2016-06-23")],  # CCAR results published
    2017: [pd.Timestamp("2017-06-28")],
    2018: [pd.Timestamp("2018-06-28")],
    2019: [pd.Timestamp("2019-06-27")],
    2020: [pd.Timestamp("2020-06-25")],
    2021: [pd.Timestamp("2021-06-24")],
    2022: [pd.Timestamp("2022-06-23")],
    2023: [pd.Timestamp("2023-06-28")],
    2024: [pd.Timestamp("2024-06-26")],
    2025: [pd.Timestamp("2025-06-27")],
}
all_dfast = []
for ys, ds in DFAST_DATES.items():
    all_dfast.extend(ds)
all_dfast = pd.DatetimeIndex(all_dfast)
print(f"\nDFAST announcement dates: {len(all_dfast)}  "
      f"{all_dfast.min().date()} to {all_dfast.max().date()}")

# Mark events within ±5 trading days of any DFAST date
WINDOW = 5
near_dfast = []
for d in all_dfast:
    near_dfast.append((d - pd.tseries.offsets.BDay(WINDOW)).date())
    near_dfast.append((d + pd.tseries.offsets.BDay(WINDOW)).date())
near_dfast_set = set()
# Convert to date set
for d in all_dfast:
    for k in range(-WINDOW, WINDOW+1):
        bd = d + pd.tseries.offsets.BDay(k)
        near_dfast_set.add(bd.date())

ev["in_dfast_window"] = ev["d0"].dt.date.isin(near_dfast_set)
print(f"  FOMC events within ±{WINDOW} BD of DFAST: {ev['in_dfast_window'].sum()} of {len(ev)}")

print("\n" + "=" * 70)
print("H3: DFAST Announcement Window Amplification")
print("=" * 70)
for window_label, mask in [("Outside DFAST window", ~ev["in_dfast_window"]),
                            ("Inside DFAST window", ev["in_dfast_window"])]:
    sub = ev[mask]
    dov = sub[sub["class"]=="Dovish"]["avg_bank_car"].dropna()
    hawk = sub[sub["class"]=="Hawkish"]["avg_bank_car"].dropna()
    if len(dov) < 5 or len(hawk) < 5: continue
    spread = dov.mean() - hawk.mean()
    se = np.sqrt(dov.var(ddof=1)/len(dov) + hawk.var(ddof=1)/len(hawk))
    t = spread/se if se > 0 else np.nan
    print(f"  {window_label:25s}  N={len(sub):3d}  "
          f"Dov mean={dov.mean()*100:+.3f}%  Hawk mean={hawk.mean()*100:+.3f}%  "
          f"Spread={spread*100:+.3f}pp  t={t:.2f}")

# ---- H4: Quintile response ----
print("\n" + "=" * 70)
print("H4: Quintile Response (Equal-weighted bank avg CAR)")
print("=" * 70)
ev_q = ev.sort_values("lm_pct").reset_index(drop=True)
ev_q["quintile"] = pd.qcut(ev_q["lm_pct"], 5, labels=False) + 1
quintile_results = []
for q in range(1, 6):
    sub = ev_q[ev_q["quintile"]==q]
    car = sub["avg_bank_car"]
    m = car.mean(); s = car.std(ddof=1); n = len(car)
    se = s/np.sqrt(n)
    t = m/se if se > 0 else np.nan
    print(f"  Q{q}: N={n:3d}  LM%=[{sub['lm_pct'].min():.2f}, {sub['lm_pct'].max():.2f}]  "
          f"mean CAR={m*100:+.3f}%  SE={se*100:.3f}%  t={t:+.2f}")
    quintile_results.append({"Q": int(q), "N": int(n),
                             "lm_min": float(sub['lm_pct'].min()),
                             "lm_max": float(sub['lm_pct'].max()),
                             "car_mean": float(m), "car_se": float(se), "t": float(t) if not np.isnan(t) else None})
# Peak test
q1_car = ev_q[ev_q["quintile"]==1]["avg_bank_car"]
q2_car = ev_q[ev_q["quintile"]==2]["avg_bank_car"]
q3_car = ev_q[ev_q["quintile"]==3]["avg_bank_car"]
q4_car = ev_q[ev_q["quintile"]==4]["avg_bank_car"]
q5_car = ev_q[ev_q["quintile"]==5]["avg_bank_car"]
peak_q = [q1_car.mean(), q2_car.mean(), q3_car.mean(), q4_car.mean(), q5_car.mean()].index(max([q1_car.mean(), q2_car.mean(), q3_car.mean(), q4_car.mean(), q5_car.mean()])) + 1
print(f"  Peak quintile: Q{peak_q}")

# ---- Bootstrap CI for H1 spread (Dovish - Hawkish) on equal-weighted bank avg ----
print("\n" + "=" * 70)
print("Bootstrap 95% CI for H1 Spread (Dovish - Hawkish) on equal-weighted bank avg")
print("=" * 70)
rng = np.random.default_rng(42)
dov_idx = np.where(ev["class"].values=="Dovish")[0]
hawk_idx = np.where(ev["class"].values=="Hawkish")[0]
n_boots = 10000
boots = np.empty(n_boots)
all_car = ev["avg_bank_car"].values
for b in range(n_boots):
    ds = rng.choice(dov_idx, size=len(dov_idx), replace=True)
    hs = rng.choice(hawk_idx, size=len(hawk_idx), replace=True)
    boots[b] = all_car[ds].mean() - all_car[hs].mean()
ci_lo, ci_hi = np.percentile(boots, [2.5, 97.5])
print(f"  Mean spread: {boots.mean()*100:+.3f}pp")
print(f"  95% CI:       [{ci_lo*100:+.3f}pp, {ci_hi*100:+.3f}pp]")

# ---- Per-bank H2 (era-split) for top-5 most-affected banks ----
print("\n" + "=" * 70)
print("H2 Per-Bank (Pre-DFAST vs DFAST-era, sorted by full-sample |spread|)")
print("=" * 70)
h1 = json.load(open("data/h1_per_bank.json"))
top_banks = sorted(h1, key=lambda x: abs(x["spread"]), reverse=True)[:10]
print(f"  {'Bank':6s} {'Pre-D spread':>12s} {'Pre-D t':>8s} {'DFAST spread':>13s} {'DFAST t':>8s} {'Δ':>8s}")
h2_per_bank = []
for b in top_banks:
    name = b["bank"]
    col = f"{name}_car01"
    pre = ev[ev["era"]=="Pre-DFAST"].dropna(subset=[col])
    post = ev[ev["era"]=="DFAST-era"].dropna(subset=[col])
    pre_dov = pre[pre["class"]=="Dovish"][col]
    pre_hawk = pre[pre["class"]=="Hawkish"][col]
    post_dov = post[post["class"]=="Dovish"][col]
    post_hawk = post[post["class"]=="Hawkish"][col]
    if len(pre_dov) < 5 or len(pre_hawk) < 5: continue
    pre_spread = pre_dov.mean() - pre_hawk.mean()
    pre_t = (pre_spread) / np.sqrt(pre_dov.var(ddof=1)/len(pre_dov) + pre_hawk.var(ddof=1)/len(pre_hawk))
    post_spread = post_dov.mean() - post_hawk.mean()
    post_t = (post_spread) / np.sqrt(post_dov.var(ddof=1)/len(post_dov) + post_hawk.var(ddof=1)/len(post_hawk))
    delta = post_spread - pre_spread
    print(f"  {name:6s} {pre_spread*100:+12.3f} {pre_t:+8.2f} {post_spread*100:+13.3f} {post_t:+8.2f} {delta*100:+8.3f}")
    h2_per_bank.append({"bank": name, "pre_spread": pre_spread, "pre_t": pre_t,
                         "post_spread": post_spread, "post_t": post_t, "delta": delta})

# ---- Save ----
out = {
    "H1_avg": {
        "Dov_N": int(sum(ev["class"]=="Dovish")),
        "Hawk_N": int(sum(ev["class"]=="Hawkish")),
        "Dov_mean": float(ev[ev["class"]=="Dovish"]["avg_bank_car"].mean()),
        "Hawk_mean": float(ev[ev["class"]=="Hawkish"]["avg_bank_car"].mean()),
        "spread": float(ev[ev["class"]=="Dovish"]["avg_bank_car"].mean() - ev[ev["class"]=="Hawkish"]["avg_bank_car"].mean()),
        "t_welch": float(stats.ttest_ind(ev[ev["class"]=="Dovish"]["avg_bank_car"].dropna(),
                                          ev[ev["class"]=="Hawkish"]["avg_bank_car"].dropna(),
                                          equal_var=False).statistic),
        "p_welch": float(stats.ttest_ind(ev[ev["class"]=="Dovish"]["avg_bank_car"].dropna(),
                                          ev[ev["class"]=="Hawkish"]["avg_bank_car"].dropna(),
                                          equal_var=False).pvalue),
    },
    "H1_bootstrap": {
        "mean_spread": float(boots.mean()),
        "ci_lo": float(ci_lo), "ci_hi": float(ci_hi),
    },
    "H2": h2_per_bank,
    "H3": {
        "in_dfast_N": int(ev["in_dfast_window"].sum()),
        "in_dfast_spread": float(ev[ev["in_dfast_window"]][ev["class"]=="Dovish"]["avg_bank_car"].mean() -
                                   ev[ev["in_dfast_window"]][ev["class"]=="Hawkish"]["avg_bank_car"].mean()) if ev["in_dfast_window"].sum() > 0 else None,
        "out_dfast_spread": float(ev[~ev["in_dfast_window"]][ev["class"]=="Dovish"]["avg_bank_car"].mean() -
                                    ev[~ev["in_dfast_window"]][ev["class"]=="Hawkish"]["avg_bank_car"].mean()),
    },
    "H4_quintile": quintile_results,
}
with open(os.path.join(OUT, "stress_era_results.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"\nSaved: {OUT}\\stress_era_results.json")
