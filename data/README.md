# FOMC Bank Stress Test — Data Files

## bank_events.csv
216 FOMC meetings × 24 US DFAST banks
- `fomc_date`: FOMC meeting date
- `d0`, `d1`: Trading days [0, +1] for CAR computation
- `lm_pct`: Loughran-McDonald positive word percentage
- `sentiment`: Dovish / Hawkish / Neutral (based on LM%)
- `{TICKER}_ar0`, `{TICKER}_ar1`: Abnormal returns on day 0, day 1
- `{TICKER}_car01`: CAR[0,+1] = ar0 + ar1
- `{TICKER}_alpha`, `{TICKER}_beta`: Market model parameters (estimation window [-150, -11])

## jp_bank_events.csv
216 FOMC meetings × 11 Japanese banks
- Same structure as bank_events.csv
- Market model uses TOPIX as benchmark
- Banks: MUFG, Mizuho, SMFG, SMTH, Resona, Chiba, Gunma, Suruga, Yamaguchi, Concordia, Hokuhoku

## all_banks.csv
Daily prices for 24 US banks + market indices (1993-2026)
- Columns: Date, JPM, BAC, C, WFC, GS, MS, USB, PNC, TFC, COF, BK, STT, SCHW, MTB, KEY, CFG, FITB, RF, TD, BCS, NTRS, BMO, RY, GS, ALLY, SPX, VIX, TNX, DXY, USB_10Y

## all_jp_banks.csv
Daily prices for 11 Japanese banks + indices (1993-2026)
- Columns: Date, MUFG, Mizuho, SMFG, SMTH, Resona, Chiba, Gunma, Suruga, Yamaguchi, Concordia, Hokuhoku, NK225, TOPIX, USDJPY, TPX_Banks

## y9c_complete.csv
FR Y-9C quarterly data for 14 US BHCs (2000-2025, N=1,782)
- Key variables: htm_securities, afs_securities, net_interest_income, total_assets, total_deposits, tier1_capital, tier1_ratio, nim, htm_ratio, afs_ratio, deposit_ratio, equity_ratio, tier1_yoy, nim_change
