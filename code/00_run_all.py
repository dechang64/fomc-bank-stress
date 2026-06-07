#!/usr/bin/env python3
"""00_run_all.py - Full replication pipeline for v6.4."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
steps = [
    ("01_fetch_us_banks.py",    "Fetch US DFAST bank prices (Yahoo)"),
    ("02_us_event_study.py",    "FOMC x US bank CAR[0,+1]"),
    ("03_us_stress_era.py",     "US H1-H4 + regime decomposition"),
    ("05_v62_h3_h5.py",         "US Y-9C cross-section H3 + H5 (event-level)"),
    ("07_ffiec_dump.py",        "FFIEC 031 dump for 6 additional US BHCs (run on WRDS Cloud)"),
    ("08_v64_merge_h3h5.py",    "Merge Y-9C + FFIEC, bank-level H3/H5 robustness"),
    ("09_fetch_jp_banks.py",    "Fetch Japan bank prices (Yahoo)"),
    ("10_jp_event_study.py",    "FOMC x Japan bank CAR[0,+1]"),
    ("11_build_v63_paper.py",   "Build v6.3 paper (US + Japan, FFIEC optional)"),
    ("12_build_v64_paper.py",   "Build v6.4 paper (US + Japan + FFIEC)"),
]
print("=" * 70); print("FOMC Bank Stress Paper v6.4 -- Full Pipeline"); print("=" * 70)
for s, l in steps:
    print(f"\n[{l}]  -> {s}")
    r = subprocess.run([sys.executable, os.path.join("code", s)], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-1500:]); print(r.stderr[-1500:]); sys.exit(1)
    print(r.stdout[-800:])
print("\nPipeline complete. v6.4 paper at paper/FOMC_BankStress_v64.docx")
