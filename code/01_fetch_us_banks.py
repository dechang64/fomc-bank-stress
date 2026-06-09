#!/usr/bin/env python3
"""
01_fetch_banks.py
Fetch daily prices for 22 CCAR (DFAST) banks.
Period: 1994-01-01 to 2026-02-15.

The 22 DFAST banks (2025 list, from FRB):
  1. JPMorgan Chase (JPM)
  2. Bank of America (BAC)
  3. Citigroup (C)
  4. Wells Fargo (WFC)
  5. Goldman Sachs (GS)
  6. Morgan Stanley (MS)
  7. U.S. Bancorp (USB)
  8. PNC Financial (PNC)
  9. Truist Financial (TFC)
 10. Capital One (COF)
 11. TD Group (TD) - US listings
 12. BMO (BMO) - US listings
 13. RBC (RY) - US listings
 14. Barclays (BCS) - US listings
 15. Bank of New York Mellon (BK)
 16. State Street (STT)
 17. Charles Schwab (SCHW)
 18. M&T Bank (MTB)
 19. KeyCorp (KEY)
 20. Citizens Financial (CFG)
 21. Fifth Third Bancorp (FITB)
 22. Regions Financial (RF)

Note: Some banks (Ally, Discover, Northern Trust, HSBC NA) were also in 2024 DFAST.
We'll include the 22 above and also pull a few extras.
"""
import os, time, json
import pandas as pd
import yfinance as yf
from datetime import datetime

OUT = "data"
os.makedirs(OUT, exist_ok=True)

# Bank tickers
BANKS = {
    # G-SIBs (8)
    "JPM":  "JPM",
    "BAC":  "BAC",
    "C":    "C",
    "WFC":  "WFC",
    "GS":   "GS",
    "MS":   "MS",
    # Other large US banks
    "USB":  "USB",
    "PNC":  "PNC",
    "TFC":  "TFC",
    "COF":  "COF",
    "BK":   "BK",
    "STT":  "STT",
    "SCHW": "SCHW",
    "MTB":  "MTB",
    "KEY":  "KEY",
    "CFG":  "CFG",
    "FITB": "FITB",
    "RF":   "RF",
    # Foreign GSIBs (US listings)
    "TD":   "TD",
    "BMO":  "BMO",
    "RY":   "RY",
    "BCS":  "BCS",
    # Extras (also stress-tested)
    "ALLY": "ALLY",
    "DFS":  "DFS",
    "NTRS": "NTRS",
}

# Benchmark + context
CONTEXT = {
    "SPX": "^GSPC",
    "VIX": "^VIX",
    "TNX": "^TNX",
    "DXY": "DX-Y.NYB",
    "USB_2Y": "^USTY2",
    "USB_10Y": "^TNX",
}

TICKERS = {**BANKS, **CONTEXT}
START = "1993-06-01"
END   = "2026-02-15"

def fetch(name, t):
    cache = os.path.join(OUT, f"{name}.csv")
    if os.path.exists(cache):
        df = pd.read_csv(cache, index_col=0, parse_dates=True)
        print(f"  {name:6s} ({t:12s}) cached  N={len(df):4d}  {df.index.min().date()} -> {df.index.max().date()}")
        return df
    print(f"  {name:6s} ({t:12s}) fetching ...", end=" ", flush=True)
    try:
        df = yf.download(t, start=START, end=END, auto_adjust=True, progress=False)
        if df is None or len(df) == 0:
            print("FAILED")
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        df = df[["Close"]].copy()
        df.columns = [name]
        df.to_csv(cache)
        print(f"OK  N={len(df):4d}  {df.index.min().date()} -> {df.index.max().date()}")
        return df
    except Exception as e:
        print(f"FAILED ({e})")
        return None

def main():
    print("=" * 70)
    print("FOMC Bank Stress-Test Paper: Daily Price Fetch")
    print("=" * 70)
    print(f"Banks: {len(BANKS)}, Context: {len(CONTEXT)}")
    print(f"Period: {START} -> {END}\n")
    out = {}
    for name, t in TICKERS.items():
        out[name] = fetch(name, t)
        time.sleep(0.4)
    # Merge
    all_df = None
    for name, df in out.items():
        if df is None: continue
        all_df = df if all_df is None else all_df.join(df, how="outer")
    if all_df is not None:
        all_df.sort_index(inplace=True)
        all_df.to_csv(os.path.join(OUT, "all_banks.csv"))
        print()
        print(f"Merged: {len(all_df)} rows  {all_df.index.min().date()} -> {all_df.index.max().date()}")
        nulls = all_df.isna().sum()
        print(f"Nulls per col: {nulls[nulls>0].to_dict()}")
    print("\nDone.")

if __name__ == "__main__":
    main()
