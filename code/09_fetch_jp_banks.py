#!/usr/bin/env python3
"""
01_fetch_jp_banks.py
Pull daily prices for major Japanese banks (megabanks + regionals)
from Yahoo Finance. Match to FOMC dates.

Japanese megabanks (the "Big 3" + Shinsei, Aozora, regionals):
  8306.T  MUFG Bank (Mitsubishi UFJ Financial Group)
  8411.T  Mizuho Financial Group
  8316.T  Sumitomo Mitsui Financial Group
  8309.T  Sumitomo Mitsui Trust Holdings
  8308.T  Resona Holdings
  8331.T  Chiba Bank
  8334.T  Gunma Bank
  8358.T  Suruga Bank
  8418.T  Yamaguchi Financial Group
  7164.T  National Federation of Agricultural Cooperative Associations (Zenkyoren) — n/a

Time zone: FOMC at 2pm ET = next morning JST. Day 0 in our event window
should be the next Nikkei trading day (consistent with how the v6.1 FOMC_StressTest
paper handled the timezone issue).
"""
import os, time
import pandas as pd
import yfinance as yf
from datetime import datetime

OUT = "data"
os.makedirs(OUT, exist_ok=True)

JP_BANKS = {
    "MUFG":   "8306.T",   # Mitsubishi UFJ Financial Group
    "Mizuho": "8411.T",   # Mizuho Financial Group
    "SMFG":   "8316.T",   # Sumitomo Mitsui Financial Group
    "SMTH":   "8309.T",   # Sumitomo Mitsui Trust Holdings
    "Resona": "8308.T",   # Resona Holdings
    "Chiba":  "8331.T",   # Chiba Bank
    "Gunma":  "8334.T",   # Gunma Bank
    "Suruga": "8358.T",   # Suruga Bank
    "Yamaguchi": "8418.T", # Yamaguchi FG
    "Shizuoka": "8355.T", # Shizuoka Bank
    "Concordia": "7186.T", # Concordia Financial Group
    "Hokuhoku": "8377.T",  # Hokuhoku Financial Group
    # Index for benchmarking
    "NK225":  "^N225",    # Nikkei 225
    "TOPIX":  "1306.T",   # TOPIX ETF
    "USDJPY": "JPY=X",    # USD/JPY
    "TPX_Banks": "1615.T", # TOPIX Banks ETF
}

START = "1993-06-01"
END   = "2026-02-15"

def fetch(name, t):
    cache = os.path.join(OUT, f"{name}.csv")
    if os.path.exists(cache):
        df = pd.read_csv(cache, index_col=0, parse_dates=True)
        print(f"  {name:10s} ({t:8s}) cached  N={len(df):5d}  {df.index.min().date()} -> {df.index.max().date()}")
        return df
    print(f"  {name:10s} ({t:8s}) fetching ...", end=" ", flush=True)
    try:
        df = yf.download(t, start=START, end=END, auto_adjust=True, progress=False)
        if df is None or len(df) == 0:
            print("FAILED (empty)")
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        df = df[["Close"]].copy()
        df.columns = [name]
        df.to_csv(cache)
        print(f"OK  N={len(df):5d}  {df.index.min().date()} -> {df.index.max().date()}")
        return df
    except Exception as e:
        print(f"FAILED ({e})")
        return None

def main():
    print("=" * 70)
    print("FOMC × Japanese Banks: Daily Price Fetch")
    print("=" * 70)
    print(f"Banks: {len(JP_BANKS)-4}, Benchmarks: 4 (NK225, TOPIX, USDJPY, TPX_Banks)")
    print(f"Period: {START} -> {END}\n")
    out = {}
    for name, t in JP_BANKS.items():
        out[name] = fetch(name, t)
        time.sleep(0.4)
    all_df = None
    for name, df in out.items():
        if df is None: continue
        all_df = df if all_df is None else all_df.join(df, how="outer")
    if all_df is not None:
        all_df.sort_index(inplace=True)
        all_df.to_csv(os.path.join(OUT, "all_jp_banks.csv"))
        print()
        print(f"Merged: {len(all_df):,} rows  {all_df.index.min().date()} -> {all_df.index.max().date()}")
        nulls = all_df.isna().sum()
        print(f"Nulls: {nulls[nulls>0].to_dict()}")
    print("\nDone.")

if __name__ == "__main__":
    main()
