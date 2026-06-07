#!/usr/bin/env python3
"""
11_v64_merge_h3h5.py  (v2 - bank-level cross-section)
Build bank-level cross-section panel from Y-9C + FFIEC 031.
- Y-9C banks: time-averaged ratios using cre_loans/tier1_capital (total_assets is NULL in this WRDS)
- FFIEC banks: time-averaged ratios using high_risk_cre/total_assets
- H1 spread per bank from v62_panel.csv (event-level pre-DFAST average)

Output: bank-level H3/H5 with N=20 (H3) / N=17 (H5)
"""
import os, json
import numpy as np
import pandas as pd
from scipy import stats

ROOT = r"C:\Users\decha\Desktop\fomc_banks"
Y9C_PATH = os.path.join(ROOT, "wrds", "raw", "y9c_quarterly.csv")
FFIEC_PATH = os.path.join(ROOT, "wrds", "raw", "ffiec_quarterly.csv")
V62_PANEL = os.path.join(ROOT, "results", "v62_panel.csv")
H1_BANK = os.path.join(ROOT, "data_proc", "h1_per_bank.json")
OUT_H = os.path.join(ROOT, "data_proc", "h3h5_v64.json")
OUT_P = os.path.join(ROOT, "data_proc", "panel_v64.csv")

# --- RSSD -> ticker ---
RSSD_TICKER = {
    # Y-9C (BHC RSSD)
    1039502: "JPM", 1073757: "BAC", 1951350: "C", 1120754: "WFC",
    1119794: "USB", 1069778: "PNC", 1131787: "TFC", 1111435: "STT",
    1037003: "MTB", 1068195: "KEY", 1132449: "CFG", 1070345: "FITB",
    1086533: "RF", 1199611: "NTRS", 2380443: "GS",
    # FFIEC (subsidiary bank RSSD)
    1456501: "MS", 112837: "COF", 541101: "BK",
    3150447: "SCHW", 280110: "KEY_FFIEC", 3284070: "ALLY",
}
TICKER_RSSD_Y9C = {1039502, 1073757, 1951350, 1120754, 1119794, 1069778, 1131787,
                   1111435, 1037003, 1068195, 1132449, 1070345, 1086533, 1199611, 2380443}
RSSD_TICKER[280110] = "KEY"  # normalize

# --- 1. Load data ---
y9c = pd.read_csv(Y9C_PATH, low_memory=False)
y9c["report_date"] = pd.to_datetime(y9c["report_date"], errors="coerce")
y9c["rssd9001"] = y9c["rssd9001"].astype(int)
y9c["ticker"] = y9c["rssd9001"].map(RSSD_TICKER)
y9c = y9c.dropna(subset=["ticker"])
y9c["source"] = "Y9C"
print(f"Y-9C: {len(y9c):,} rows, {y9c['ticker'].nunique()} banks")

ffi = pd.read_csv(FFIEC_PATH, low_memory=False)
ffi["report_date"] = pd.to_datetime(ffi["report_date"], errors="coerce")
ffi["rssd9001"] = ffi["rssd9001"].astype(int)
ffi["ticker"] = ffi["rssd9001"].map(RSSD_TICKER)
ffi = ffi.dropna(subset=["ticker"])
ffi["source"] = "FFIEC"
print(f"FFIEC: {len(ffi):,} rows, {ffi['ticker'].nunique()} banks")

# --- 2. Bank-level time-averaged ratios ---
def bank_avg(df, ticker_col="ticker"):
    """Aggregate to bank-level time-averaged ratios."""
    out = df.groupby(ticker_col).agg(
        N_quarters=("report_date", "count"),
        cre_mean=("cre_loans", "mean"),
        ta_mean=("total_assets", "mean"),
        tier1_mean=("tier1_capital", "mean"),
        tier1_yoy_mean=("tier1_yoy_pct", "mean"),
    ).reset_index()
    return out

y9c_avg = bank_avg(y9c)
y9c_avg["cre_intensity"] = y9c_avg["cre_mean"] / y9c_avg["tier1_mean"]  # Y-9C has no total_assets
y9c_avg["tier1_growth"] = y9c_avg["tier1_yoy_mean"]
y9c_avg["source"] = "Y9C"
print(f"\nY-9C bank-level: {len(y9c_avg)} banks")
print(y9c_avg[["ticker","N_quarters","cre_mean","tier1_mean","cre_intensity","tier1_growth"]].to_string(index=False))

ffi_avg = bank_avg(ffi)
ffi_avg["cre_intensity"] = ffi_avg["cre_mean"] / ffi_avg["ta_mean"]  # FFIEC has total_assets
ffi_avg["tier1_growth"] = ffi_avg["tier1_yoy_mean"]
ffi_avg["source"] = "FFIEC"
print(f"\nFFIEC bank-level: {len(ffi_avg)} banks")
print(ffi_avg[["ticker","N_quarters","cre_mean","ta_mean","cre_intensity","tier1_growth"]].to_string(index=False))

# --- 3. Load H1 per-bank spread ---
with open(H1_BANK) as f: h1_bank = json.load(f)
# h1_bank is list of {bank, spread, t, p, ...}
bank_spreads = {b["bank"]: b["spread"] for b in h1_bank}
print(f"\nH1 spreads: {len(bank_spreads)} banks")

# --- 4. Build bank-level panel with H1 spread ---
panel_y = y9c_avg.copy()
panel_y["h1_spread"] = panel_y["ticker"].map(bank_spreads)
panel_y = panel_y.dropna(subset=["h1_spread"])

panel_f = ffi_avg.copy()
panel_f["h1_spread"] = panel_f["ticker"].map(bank_spreads)
panel_f = panel_f.dropna(subset=["h1_spread"])

panel = pd.concat([panel_y, panel_f], ignore_index=True, sort=False)
print(f"\nCombined bank-level panel: {len(panel)} banks (Y-9C: {len(panel_y)}, FFIEC: {len(panel_f)})")
print(panel[["ticker","source","N_quarters","cre_intensity","tier1_growth","h1_spread"]].to_string(index=False))

# --- 5. H3 cross-section: spread ~ cre_intensity ---
def split_test(df, col, label):
    out = {"label": label, "N": int(len(df))}
    df_clean = df.dropna(subset=["h1_spread", col])
    if len(df_clean) < 4:
        out["error"] = "too few"
        return out
    med = df_clean[col].median()
    high = df_clean[df_clean[col] > med]["h1_spread"]
    low = df_clean[df_clean[col] <= med]["h1_spread"]
    t, p = stats.ttest_ind(high, low, equal_var=False)
    out["N_high"] = int(len(high))
    out["N_low"] = int(len(low))
    out["median_split"] = float(med)
    out["high_spread"] = float(high.mean())
    out["low_spread"] = float(low.mean())
    out["t_welch"] = float(t)
    out["p_welch"] = float(p)
    # OLS: spread = a + b * characteristic
    from numpy.linalg import lstsq
    X = np.column_stack([np.ones(len(df_clean)), df_clean[col].values])
    y = df_clean["h1_spread"].values
    coef, _, _, _ = lstsq(X, y, rcond=None)
    out["ols_const"] = float(coef[0])
    out["ols_beta"] = float(coef[1])
    return out

print("\n=== H3 cross-section (bank-level) ===")
h3_y9c = split_test(panel_y, "cre_intensity", "H3_y9c_only")
print(f"  Y-9C only (N=14): high={h3_y9c.get('high_spread', 0)*100:+.3f}pp (N={h3_y9c.get('N_high','?')}) "
      f"low={h3_y9c.get('low_spread', 0)*100:+.3f}pp (N={h3_y9c.get('N_low','?')}) "
      f"t={h3_y9c.get('t_welch',0):.2f} p={h3_y9c.get('p_welch',0):.3f}")
h3_full = split_test(panel, "cre_intensity", "H3_full")
print(f"  Full N=20: high={h3_full.get('high_spread', 0)*100:+.3f}pp (N={h3_full.get('N_high','?')}) "
      f"low={h3_full.get('low_spread', 0)*100:+.3f}pp (N={h3_full.get('N_low','?')}) "
      f"t={h3_full.get('t_welch',0):.2f} p={h3_full.get('p_welch',0):.3f}")

print("\n=== H5 cross-section (bank-level) ===")
h5_y9c = split_test(panel_y, "tier1_growth", "H5_y9c_only")
print(f"  Y-9C only (N=14): high_cap={h5_y9c.get('high_spread', 0)*100:+.3f}pp (N={h5_y9c.get('N_high','?')}) "
      f"low_cap={h5_y9c.get('low_spread', 0)*100:+.3f}pp (N={h5_y9c.get('N_low','?')}) "
      f"t={h5_y9c.get('t_welch',0):.2f} p={h5_y9c.get('p_welch',0):.3f}")
# FFIEC has T1 for only 3 banks (COF, BK, KEY)
h5_full = split_test(panel, "tier1_growth", "H5_full")
print(f"  Full N={h5_full.get('N','?')}: high_cap={h5_full.get('high_spread', 0)*100:+.3f}pp (N={h5_full.get('N_high','?')}) "
      f"low_cap={h5_full.get('low_spread', 0)*100:+.3f}pp (N={h5_full.get('N_low','?')}) "
      f"t={h5_full.get('t_welch',0):.2f} p={h5_full.get('p_welch',0):.3f}")

# --- 6. Save ---
out = {
    "N_total_banks": int(panel["ticker"].nunique()),
    "N_y9c": int(panel_y.shape[0]),
    "N_ffiec": int(panel_f.shape[0]),
    "H3": {
        "y9c_only": h3_y9c,
        "full": h3_full,
    },
    "H5": {
        "y9c_only": h5_y9c,
        "full": h5_full,
    },
    "panel": panel.to_dict(orient="records"),
}
with open(OUT_H, "w") as f:
    json.dump(out, f, indent=2, default=str)
panel.to_csv(OUT_P, index=False)
print(f"\nSaved -> {OUT_H}")
print(f"Panel  -> {OUT_P}")
print(f"\n{'='*60}\nv6.4 bank-level H3/H5 complete\n{'='*60}")
