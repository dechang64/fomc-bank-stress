#!/usr/bin/env python3
"""
v6.2 analysis: H3 cross-section + new H5 using Y-9C bank balance sheets.

H3 (Cross-Sectional Heterogeneity, v6.2): The dovish-hawkish bank-return spread
    is larger for banks with higher trading-book exposure (trading_ratio) and
    higher CRE loan share (cre_ratio), measured using Y-9C bank balance sheet
    data.

H5 (Capital Channel, v6.2): The dovish-hawkish bank-return spread is larger
    for banks with low Tier 1 capital ratios and negative tier1_yoy_pct
    (capital depletion), consistent with capital-constrained banks being more
    sensitive to FOMC information.
"""
import os, json
import numpy as np
import pandas as pd
from scipy import stats

EV = r"C:\Users\decha\Desktop\fomc_banks\data_proc\bank_events.csv"
Y9C = r"C:\Users\decha\Desktop\fomc_banks\wrds\raw\y9c_quarterly.csv"
OUT = r"C:\Users\decha\Desktop\fomc_banks\results"
os.makedirs(OUT, exist_ok=True)

# RSSD9001 -> ticker
BANK_RSSD_TO_TICKER = {
    1039502: "JPM", 1073757: "BAC", 1951350: "C", 1120754: "WFC",
    2380443: "GS", 2162962: "MS", 1119794: "USB", 1069778: "PNC",
    1131787: "TFC", 1101404: "COF", 1394156: "BK", 1111435: "STT",
    1167398: "SCHW", 1037003: "MTB", 1068195: "KEY", 1132449: "CFG",
    1070345: "FITB", 1086533: "RF", 1011528: "TD", 1028330: "BMO",
    1028332: "RY", 1064334: "BCS", 1075874: "ALLY", 1199611: "NTRS",
}

print("=" * 70)
print("v6.2 ANALYSIS: H3 + H5 with Y-9C bank balance sheets")
print("=" * 70)

# ---- Load event data ----
ev = pd.read_csv(EV, parse_dates=["fomc_date","d0","d1"])
BANK_CAR_COLS = [c for c in ev.columns if c.endswith("_car01")]
BANKS = [c.replace("_car01","") for c in BANK_CAR_COLS]
ev["avg_bank_car"] = ev[BANK_CAR_COLS].mean(axis=1)
med_lm = ev["lm_pct"].median()
ev["class"] = np.where(ev["lm_pct"] > med_lm, "Hawkish", "Dovish")
print(f"Events: {len(ev)}, Banks (with valid CAR): {len(BANKS)}")

# ---- Load Y-9C data ----
y9c = pd.read_csv(Y9C, parse_dates=["report_date"])
y9c["ticker"] = y9c["rssd9001"].map(BANK_RSSD_TO_TICKER)
y9c = y9c.dropna(subset=["ticker"])
print(f"\nY-9C: {len(y9c):,} rows, {y9c['ticker'].nunique()} banks, "
      f"date range {y9c['report_date'].min().date()} to {y9c['report_date'].max().date()}")
print(f"  Tickers: {sorted(y9c['ticker'].unique())}")

# Y-9C summary by bank
print("\n=== Y-9C by bank (most recent quarter) ===")
latest = y9c.sort_values("report_date").groupby("ticker").tail(1).sort_values("trading_ratio", ascending=False)
cols_to_show = ["ticker", "report_date", "total_assets", "tier1_capital", "trading_assets", "cre_loans", "tier1_ratio", "trading_ratio", "cre_ratio"]
print(latest[cols_to_show].to_string(index=False))

# Bank-level average ratios (across all available quarters)
print("\n=== Y-9C by bank (time-averaged ratios) ===")
avg = y9c.groupby("ticker").agg(
    N=("tier1_ratio", "count"),
    tier1_ratio_mean=("tier1_ratio", "mean"),
    trading_ratio_mean=("trading_ratio", "mean"),
    cre_ratio_mean=("cre_ratio", "mean"),
    cash_ratio_mean=("cash_ratio", "mean"),
    tier1_yoy_pct_mean=("tier1_yoy_pct", "mean"),
).reset_index().sort_values("trading_ratio_mean", ascending=False)
print(avg.to_string(index=False))

# ---- Merge Y-9C ratios into event data ----
# For each FOMC event, use the most recent Y-9C balance sheet (<= event date)
y9c = y9c.sort_values(["ticker", "report_date"])
ev["ticker"] = ev["fomc_date"]  # placeholder, fix below

# Need to merge each event with the most recent Y-9C for the bank's ticker
# For this, we need a (event_fomc_date, bank_ticker) -> y9c record
# Build a per-event per-bank merged frame

# Y-9C lookup: for each (ticker, date), find most recent Y-9C <= date
def get_y9c_at(ticker, date, y9c_df):
    sub = y9c_df[(y9c_df["ticker"]==ticker) & (y9c_df["report_date"] <= date)]
    if len(sub) == 0:
        return None
    return sub.sort_values("report_date").iloc[-1]

# For each FOMC event, for each bank, attach most-recent Y-9C ratios
records = []
for _, er in ev.iterrows():
    d = er["fomc_date"]
    for b in BANKS:
        y = get_y9c_at(b, d, y9c)
        car_col = f"{b}_car01"
        if y is not None and pd.notna(er.get(car_col)):
            records.append({
                "fomc_date": d, "d0": er["d0"], "d1": er["d1"],
                "lm_pct": er["lm_pct"], "class": er["class"],
                "ticker": b, "car": er[car_col],
                # Y-9C: divide by tier1_capital as size proxy (bhckb986 = total_assets
                # returned all NULL in this WRDS instance; tier1_capital ~ total_assets
                # for these 14 BHCs and is non-missing)
                "tier1_capital": float(y["tier1_capital"]) if pd.notna(y["tier1_capital"]) else np.nan,
                "trading_assets": float(y["trading_assets"]) if pd.notna(y["trading_assets"]) else np.nan,
                "cre_loans":      float(y["cre_loans"])      if pd.notna(y["cre_loans"])      else np.nan,
                "cash":           float(y["cash"])           if pd.notna(y["cash"])           else np.nan,
                "tier1_yoy_pct":  float(y["tier1_yoy_pct"])  if pd.notna(y["tier1_yoy_pct"])  else np.nan,
            })
panel = pd.DataFrame(records)
# Compute intensity ratios after panel is built (safer than per-row divide)
panel["trading_intensity"] = panel["trading_assets"] / panel["tier1_capital"].replace(0, np.nan)
panel["cre_intensity"]      = panel["cre_loans"]      / panel["tier1_capital"].replace(0, np.nan)
panel["cash_intensity"]     = panel["cash"]           / panel["tier1_capital"].replace(0, np.nan)
panel["log_tier1"]          = np.log(panel["tier1_capital"].where(panel["tier1_capital"] > 0))

print(f"\nPanel: {len(panel):,} (event × bank) observations")
print(f"  Banks in panel: {panel['ticker'].nunique()}")
print(f"  Y-9C coverage:")
print(panel[['tier1_capital','trading_assets','cre_loans','trading_intensity','cre_intensity','tier1_yoy_pct']].notna().mean().to_string())

# ---- H3: Split banks by trading_ratio / cre_ratio (high vs low) ----
print("\n" + "=" * 70)
print("H3: Cross-Sectional Heterogeneity (by bank balance sheet characteristics)")
print("=" * 70)

for char in ["trading_intensity", "cre_intensity", "cash_intensity", "log_tier1"]:
    med = panel[char].median()
    panel[f"{char}_hilo"] = np.where(panel[char] > med, "high", "low")
    print(f"\n  By {char} (median split at {med:.3f}):")
    for label, sub in panel.groupby(f"{char}_hilo"):
        dov = sub[sub["class"]=="Dovish"]["car"]
        hawk = sub[sub["class"]=="Hawkish"]["car"]
        sp = dov.mean() - hawk.mean()
        t = stats.ttest_ind(dov, hawk, equal_var=False).statistic
        p = stats.ttest_ind(dov, hawk, equal_var=False).pvalue
        print(f"    {label:5s} (N={len(sub):4d}, banks={sub['ticker'].nunique():2d}):  "
              f"Dov={dov.mean()*100:+.3f}%  Hawk={hawk.mean()*100:+.3f}%  Spread={sp*100:+.3f}pp  t={t:+.2f}  p={p:.3f}")

# ---- H3 continuous: regression of bank CAR on LM% x trading_ratio ----
print("\n  Continuous interaction model (event level):")
# Collapse to event level: average across banks (equal-weighted)
# Then use spread between high-trading and low-trading subsamples
panel_d = panel[panel["class"]=="Dovish"]
panel_h = panel[panel["class"]=="Hawkish"]
for char in ["trading_intensity", "cre_intensity", "tier1_yoy_pct"]:
    med = panel[char].median()
    panel_d_high = panel_d[panel_d[char] > med].groupby("fomc_date")["car"].mean()
    panel_d_low = panel_d[panel_d[char] <= med].groupby("fomc_date")["car"].mean()
    panel_h_high = panel_h[panel_h[char] > med].groupby("fomc_date")["car"].mean()
    panel_h_low = panel_h[panel_h[char] <= med].groupby("fomc_date")["car"].mean()
    spread_high = (panel_d_high - panel_h_high).dropna()
    spread_low = (panel_d_low - panel_h_low).dropna()
    if len(spread_high) > 5 and len(spread_low) > 5:
        t = stats.ttest_ind(spread_high, spread_low, equal_var=False).statistic
        p = stats.ttest_ind(spread_high, spread_low, equal_var=False).pvalue
        print(f"    {char}: spread(high)={spread_high.mean()*100:+.3f}pp  spread(low)={spread_low.mean()*100:+.3f}pp  diff t={t:+.2f}  p={p:.3f}")

# ---- H5: Capital channel ----
print("\n" + "=" * 70)
print("H5: Capital Channel (Tier 1 capital buffer)")
print("=" * 70)
med_t1 = panel["tier1_capital"].median()
panel["low_capital"] = panel["tier1_capital"] < med_t1
for label, sub in [("Low capital (bottom half)", panel[panel["low_capital"]]),
                   ("High capital (top half)", panel[~panel["low_capital"]])]:
    dov = sub[sub["class"]=="Dovish"]["car"]
    hawk = sub[sub["class"]=="Hawkish"]["car"]
    sp = dov.mean() - hawk.mean()
    t = stats.ttest_ind(dov, hawk, equal_var=False).statistic
    p = stats.ttest_ind(dov, hawk, equal_var=False).pvalue
    print(f"  {label:30s}  N={len(sub):4d}  banks={sub['ticker'].nunique():2d}:  "
          f"Dov={dov.mean()*100:+.3f}%  Hawk={hawk.mean()*100:+.3f}%  Spread={sp*100:+.3f}pp  t={t:+.2f}  p={p:.3f}")

# H5: tier1_yoy_pct (capital depletion vs build-up)
print("\n  By tier1_yoy_pct (capital change YoY):")
med_yoy = panel["tier1_yoy_pct"].median()
panel["capital_depleting"] = panel["tier1_yoy_pct"] < med_yoy
for label, sub in [("Capital depleting", panel[panel["capital_depleting"]]),
                   ("Capital building",  panel[~panel["capital_depleting"]])]:
    dov = sub[sub["class"]=="Dovish"]["car"]
    hawk = sub[sub["class"]=="Hawkish"]["car"]
    sp = dov.mean() - hawk.mean()
    t = stats.ttest_ind(dov, hawk, equal_var=False).statistic
    p = stats.ttest_ind(dov, hawk, equal_var=False).pvalue
    print(f"  {label:30s}  N={len(sub):4d}:  "
          f"Dov={dov.mean()*100:+.3f}%  Hawk={hawk.mean()*100:+.3f}%  Spread={sp*100:+.3f}pp  t={t:+.2f}  p={p:.3f}")

# ---- Save ----
panel.to_csv(os.path.join(OUT, "v62_panel.csv"), index=False)
print(f"\nSaved panel: {OUT}\\v62_panel.csv")
