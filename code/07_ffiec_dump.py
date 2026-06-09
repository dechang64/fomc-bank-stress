#!/usr/bin/env python3
"""
ffiec_dump_standalone.py  (v6 - cast Decimal, KeyBank search, skip trust subs)

Fixes from v5:
  1. WRDS returns rcfd*/rcon* columns as decimal.Decimal (exact precision).
     Casting to float in SQL to enable ratio computation.
  2. KeyCorp's subsidiary is "KeyBank NA" - search "KEYBANK" instead of "KEYCORP".
  3. For SCHW, filter out "TRUST" subsidiaries (custody banks don't have full
     commercial bank data) - prefer the main "CHARLES SCHWAB BANK, SSB".
"""
import os, sys, subprocess
try:
    import wrds
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "wrds"])
    import wrds
import pandas as pd
import numpy as np
from sqlalchemy import text

OUT = os.path.expanduser("~/wrds_raw")
os.makedirs(OUT, exist_ok=True)
print(f"Output: {OUT}")

conn = wrds.Connection()
print("Connected\n")

def run_sql(sql, params=None):
    if params:
        result = conn.connection.execute(text(sql), params)
    else:
        result = conn.connection.execute(text(sql))
    cols = list(result.keys())
    rows = result.fetchall()
    return pd.DataFrame(rows, columns=cols)

def find_col_in(schema, table, candidates, sample_limit=1):
    try:
        sample = run_sql(f"SELECT * FROM {schema}.{table} LIMIT {sample_limit}")
        actual = set(c.lower() for c in sample.columns)
    except Exception as e:
        return None, f"cannot read: {str(e)[:100]}"
    for cand in candidates:
        if cand.lower() in actual:
            return cand, "ok"
    return None, "none of candidates found"

# === Sanity test ===
print("=== Sanity: SELECT 1 ===")
try:
    test = run_sql("SELECT 1 AS ok")
    print(f"  OK: {test.to_dict('records')}")
except Exception as e:
    print(f"  FAILED: {e}"); sys.exit(1)

# === Step 0: Discover columns ===
print("\n=== Step 0: Discover FFIEC column names ===")
SCHEMA = "bank"
rssd_col, _ = find_col_in(SCHEMA, "wrds_call_rcfd_1", ["rssd9001"])
date_col, _ = find_col_in(SCHEMA, "wrds_call_rcfd_1", ["rssd9999"])
name_col, _ = find_col_in(SCHEMA, "wrds_call_rcfd_1", ["rssd9017"])
type_col, _ = find_col_in(SCHEMA, "wrds_call_rcfd_1", ["rssd9050"])
print(f"  rssd: {rssd_col}  date: {date_col}  name: {name_col}  type: {type_col}")

rcfd2_discoveries = {}
for alias, cands in [
    ("total_assets",    ["rcfd2170", "rcfd_2170"]),
    ("tier1_capital",   ["rcfd8274", "rcfd_8274"]),
    ("total_equity",    ["rcfd3210", "rcfd_3210"]),
    ("noninterest_income",["rcfd1410", "rcfd_1410"]),
    ("trading_assets",  ["rcfd3545", "rcfd_3545"]),
    ("cash",            ["rcfd3814", "rcfd_3814"]),
    ("tier1_rwa",       ["rcfdb989", "rcfd_b989"]),
]:
    col, msg = find_col_in(SCHEMA, "wrds_call_rcfd_2", cands)
    rcfd2_discoveries[alias] = col

rcfd1_discoveries = {}
for alias, cands in [
    ("high_risk_cre",   ["rcfd5369", "rcfd_5369"]),
    ("htm_securities",  ["rcfd1754", "rcfd_1754"]),
]:
    col, msg = find_col_in(SCHEMA, "wrds_call_rcfd_1", cands)
    rcfd1_discoveries[alias] = col

rcon2_discoveries = {}
for alias, cands in [
    ("total_deposits",  ["rcon2200", "rcon_2200"]),
]:
    col, msg = find_col_in(SCHEMA, "wrds_call_rcon_2", cands)
    rcon2_discoveries[alias] = col

print("  All columns discovered.")

# === Step 1: Find subsidiary bank RSSDs ===
# v6: improved search patterns + filter for trust/custody subsidiaries
print("\n=== Step 1: Find subsidiary BANK RSSDs (v6) ===")
# Use multiple search patterns per BHC; first match wins (after trust-filter)
BHC_SEARCH = [
    # (ticker, search_patterns, skip_substrings)
    ("MS",   ["MORGAN STANLEY BANK"],                     ["TRUST", "DEAN WITTER"]),
    ("COF",  ["CAPITAL ONE"],                              ["TRUST"]),
    ("BK",   ["BANK OF NEW YORK MELLON"],                  ["TRUST"]),
    ("SCHW", ["CHARLES SCHWAB BANK", "CHARLES SCHWAB"],    ["TRUST", "SIGNATURE", "PREMIER"]),
    ("KEY",  ["KEYBANK"],                                  ["TRUST"]),
    ("ALLY", ["ALLY BANK"],                                []),
]

bank_rssd_map = {}
for ticker, patterns, skip_subs in BHC_SEARCH:
    print(f"\n  {ticker} (search: {patterns}, skip: {skip_subs}):")
    found = []
    for pat in patterns:
        like_pattern = "%" + pat + "%"
        skip_clause = ""
        if skip_subs:
            skip_terms = " AND ".join(f"{name_col} NOT ILIKE '%{s}%'" for s in skip_subs)
            skip_clause = f" AND {skip_terms}"
        res = run_sql(f"""
            SELECT {rssd_col} AS rssd, {name_col} AS name, {type_col} AS entity_type,
                   COUNT(*) AS n_quarters
            FROM {SCHEMA}.wrds_call_rcfd_1
            WHERE {name_col} ILIKE :pattern{skip_clause}
              AND {date_col} BETWEEN '2000-03-31' AND '2025-12-31'
            GROUP BY {rssd_col}, {name_col}, {type_col}
            ORDER BY n_quarters DESC
            LIMIT 10
        """, params={"pattern": like_pattern})
        for _, r in res.iterrows():
            entry = (int(r['rssd']), r['name'], r['entity_type'], int(r['n_quarters']))
            if entry not in found:
                found.append(entry)
        if found:
            break  # stop searching more patterns once we have candidates
    if not found:
        print(f"    !! NO banks found")
        bank_rssd_map[ticker] = []
        continue
    # Print candidates
    for rssd, name, et, nq in found[:5]:
        print(f"      rssd={rssd:>10}  type={et:>5}  n_q={nq:>4}  name={name[:60]}")
    bank_rssd_map[ticker] = found

# Pick best (most quarters)
print("\n  Selected bank RSSD per BHC:")
bank_rssd_list = []
BHC_TICKER_NAME = {
    "MS": "Morgan Stanley",
    "COF": "Capital One",
    "BK": "BNY Mellon",
    "SCHW": "Charles Schwab",
    "KEY": "KeyCorp",
    "ALLY": "Ally",
}
for ticker, _, _ in BHC_SEARCH:
    cands = bank_rssd_map.get(ticker, [])
    if not cands:
        print(f"    {ticker:6s}  -- NO BANK FOUND")
        continue
    best = max(cands, key=lambda x: x[3])
    bank_rssd, bank_name, et, nq = best
    bank_rssd_list.append((bank_rssd, ticker, BHC_TICKER_NAME[ticker], bank_name, nq))
    print(f"    {ticker:6s}  bank_rssd={bank_rssd:>10}  n_q={nq:>4}  bank={bank_name[:55]}")

if not bank_rssd_list:
    print("\n!! No bank RSSDs found."); sys.exit(1)

rssd_csv = ",".join(str(r[0]) for r in bank_rssd_list)
rssd_to_ticker = {r[0]: r[1] for r in bank_rssd_list}
rssd_to_name = {r[0]: r[3] for r in bank_rssd_list}

# === Step 2: Pull FFIEC 031 (CAST to float to avoid Decimal error) ===
print("\n=== Step 2: Pull FFIEC 031 (CAST decimal -> float) ===")

def select_with_cast(discoveries):
    """Build SELECT clause with ::float cast on all numeric columns."""
    parts = [f"{rssd_col} AS rssd9001", f"{date_col} AS report_date"]
    for alias, col in discoveries.items():
        if col:
            parts.append(f"{col}::float AS {alias}")
    return ", ".join(parts)

# 2a. RCFD_2
sel2_sql = select_with_cast(rcfd2_discoveries)
print(f"\n  Pulling rcfd_2: {list(rcfd2_discoveries.keys())}")
rcfd2 = run_sql(f"""
    SELECT {sel2_sql}
    FROM {SCHEMA}.wrds_call_rcfd_2
    WHERE {rssd_col} IN ({rssd_csv})
      AND {date_col} BETWEEN '2000-03-31' AND '2025-12-31'
""")
print(f"    Got {len(rcfd2):,} rows, {rcfd2['rssd9001'].nunique()} banks")

# 2b. RCFD_1
sel1_sql = select_with_cast(rcfd1_discoveries)
print(f"\n  Pulling rcfd_1: {list(rcfd1_discoveries.keys())}")
rcfd1 = run_sql(f"""
    SELECT {sel1_sql}
    FROM {SCHEMA}.wrds_call_rcfd_1
    WHERE {rssd_col} IN ({rssd_csv})
      AND {date_col} BETWEEN '2000-03-31' AND '2025-12-31'
""")
print(f"    Got {len(rcfd1):,} rows, {rcfd1['rssd9001'].nunique()} banks")

# 2c. RCON_2
sel_d_sql = select_with_cast(rcon2_discoveries)
print(f"\n  Pulling rcon_2: {list(rcon2_discoveries.keys())}")
rcon2 = run_sql(f"""
    SELECT {sel_d_sql}
    FROM {SCHEMA}.wrds_call_rcon_2
    WHERE {rssd_col} IN ({rssd_csv})
      AND {date_col} BETWEEN '2000-03-31' AND '2025-12-31'
""")
print(f"    Got {len(rcon2):,} rows, {rcon2['rssd9001'].nunique()} banks")

# === Step 3: Merge ===
print("\n=== Step 3: Merge ===")
ffiec = rcfd2.merge(rcfd1, on=['rssd9001','report_date'], how='outer') \
            .merge(rcon2, on=['rssd9001','report_date'], how='outer')
ffiec['source'] = 'FFIEC_031'
print(f"  Merged: {len(ffiec):,} rows, {ffiec['rssd9001'].nunique()} banks")

# === Step 4: Compute ratios (use .loc to avoid warnings) ===
print("\n=== Step 4: Compute ratios ===")
ffiec = ffiec.copy()  # explicit copy to avoid chained assignment
ffiec.loc[:, 'report_date'] = pd.to_datetime(ffiec['report_date'], errors='coerce')
ffiec.loc[:, 'rssd9001'] = ffiec['rssd9001'].astype(int)
ffiec.loc[:, 'ticker'] = ffiec['rssd9001'].map(rssd_to_ticker)
ffiec.loc[:, 'bank_name'] = ffiec['rssd9001'].map(rssd_to_name)

if 'high_risk_cre' in ffiec.columns:
    ffiec.loc[:, 'cre_loans'] = ffiec['high_risk_cre'].astype(float)
    print(f"  CRE proxy: high_risk_cre (rcfd5369), {ffiec['cre_loans'].notna().sum():,} non-null")
else:
    ffiec.loc[:, 'cre_loans'] = np.nan

# Make sure all denominator columns are float
for col in ['total_assets', 'tier1_capital', 'total_equity', 'trading_assets', 'cash']:
    if col in ffiec.columns:
        ffiec.loc[:, col] = pd.to_numeric(ffiec[col], errors='coerce')

ffiec.loc[:, 'cre_ratio']    = ffiec['cre_loans']        / ffiec['total_assets'].replace(0, np.nan)
ffiec.loc[:, 'tier1_ratio']  = ffiec['tier1_capital']    / ffiec['total_assets'].replace(0, np.nan)
ffiec.loc[:, 'equity_ratio'] = ffiec['total_equity']     / ffiec['total_assets'].replace(0, np.nan)
ffiec.loc[:, 'trading_ratio']= ffiec['trading_assets']   / ffiec['total_assets'].replace(0, np.nan)
ffiec.loc[:, 'cash_ratio']   = ffiec['cash']             / ffiec['total_assets'].replace(0, np.nan)

ffiec = ffiec.sort_values(['rssd9001','report_date']).reset_index(drop=True)
ffiec.loc[:, 'tier1_lag4q'] = ffiec.groupby('rssd9001')['tier1_capital'].shift(4)
ffiec.loc[:, 'tier1_yoy_pct'] = (ffiec['tier1_capital'] - ffiec['tier1_lag4q']) / ffiec['tier1_lag4q'].replace(0, np.nan)

# === Step 5: Save ===
out_path = os.path.join(OUT, "ffiec_quarterly.csv")
ffiec.to_csv(out_path, index=False)
print(f"\nSaved -> {out_path}")
print(f"  {len(ffiec):,} rows, {ffiec['rssd9001'].nunique()} banks")
print(f"  Date range: {ffiec['report_date'].min().date()} to {ffiec['report_date'].max().date()}")
print(f"\nPer-bank stats:")
for ticker, _, _ in BHC_SEARCH:
    sub = ffiec[ffiec['ticker'] == ticker]
    if len(sub) == 0:
        print(f"  {ticker:6s}  NO DATA"); continue
    g_nona = sub.dropna(subset=['total_assets'])
    cre_str = f"{g_nona.cre_ratio.median()*100:>5.1f}%" if g_nona['cre_ratio'].notna().any() else "  N/A"
    t1_str  = f"{g_nona.tier1_ratio.median()*100:>5.1f}%" if g_nona['tier1_ratio'].notna().any() else "  N/A"
    bn = g_nona.bank_name.iloc[0][:50] if 'bank_name' in g_nona.columns else '?'
    print(f"  {ticker:6s}  bank_rssd={g_nona.rssd9001.iloc[0]:>10}  "
          f"quarters={len(g_nona):>3}  "
          f"TA median={g_nona.total_assets.median()/1e6:>8.1f}B  "
          f"CRE% median={cre_str}  "
          f"T1% median={t1_str}  "
          f"bank={bn}")

conn.close()
print("\n=== FFIEC dump complete ===")
print("""
Next steps:
1. Download ~/wrds_raw/ffiec_quarterly.csv to:
   data\\ffiec_quarterly.csv
2. Tell assistant 'FFIEC ready'
""")
