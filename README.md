# FOMC Communication and Bank Stress

**US, Japan, and the Pre/Post-2008 Regime Shift**

Eileen Zhang

*Submitted to: 2026 Federal Reserve Stress Testing Research Conference (Boston, Nov 5-6)*

---

## Abstract

We test whether FOMC statement language functions as a real-time indicator of bank stress, using 216 FOMC meetings (1994–2025) matched to daily returns of 24 US DFAST banks and 11 Japanese banks. The central finding is a sharp pre/post-2008 regime shift in BOTH the US and Japan: the dovish-hawkish bank-return spread is significantly negative pre-DFAST (US: −0.89pp, Japan: −1.40pp) but collapses to insignificance in the DFAST era.

Channel decomposition reveals four independent transmission mechanisms:
- **NIM Compression Channel** (H8): ZLB periods, high-NIM banks benefit from dovish FOMC (β=+0.68, p<0.001)
- **HTM Unrealized Loss Channel** (H9): FastHike periods, high-HTM banks suffer (β=−0.093, t=−8.16, p<0.001) — the strongest coefficient in the entire study
- **CRE Sensitivity Channel**: Operates during ZLB but dominated by HTM during FastHike
- **Uncertainty Channel** (H10): When LM% and LLM disagree on FOMC signal direction, stance distance predicts worse bank CAR (coef=−0.0091, p=0.005) and higher dispersion (p=0.058), with ZLB amplification (p=0.051)

The HTM vs AFS comparison constitutes a natural quasi-experiment: identical cash flows, different accounting treatment, starkly different risk profiles (FastHike×HTM t=−6.26 vs FastHike×AFS t=+2.87).

## Repository Structure

```
fomc-bank-stress/
├── experiments/              # 🆕 Experiment tracking (config + results per version)
│   ├── manifest.yaml         # All experiments index (v6.2 → v15.1)
│   └── v15_1_recovered_experiments/  # Current best
│       └── config.yaml       # Input data, model spec, key results
├── code/                     # Analysis scripts (chronological)
│   ├── run_experiment.py     # 🆕 Run/list experiments
│   ├── 00_run_all.py         # Master runner (v6.4 pipeline)
│   ├── 01_fetch_us_banks.py  # Download US bank price data
│   ├── 02_us_event_study.py  # US event study + CAR computation
│   ├── 03_us_stress_era.py   # H1/H2/H4 stress era analysis
│   ├── 04_build_v10.py       # Paper builder v1.0
│   ├── 05_v62_h3_h5.py       # H3 (CRE) + H5 (Capital) cross-section
│   ├── 06_build_v62_paper.py # Paper builder v6.2
│   ├── 07_ffiec_dump.py      # FFIEC 031 Call Report data
│   ├── 08_v64_merge_h3h5.py  # Merge H3/H5 into paper
│   ├── 09_fetch_jp_banks.py  # Download Japan bank data
│   ├── 10_jp_event_study.py  # Japan event study
│   ├── 11_build_v63_paper.py # Paper builder v6.3
│   ├── 12_build_v64_paper.py # Paper builder v6.4
│   ├── 13-18_*.py            # v10.0 Plans A-D (HTM, NIM, Aggregate, Kuttner)
│   ├── llm_classify_*.py     # LLM classification (Minutes + Transcripts)
│   └── scrape_fomc_minutes.py
├── data/                     # All datasets (in git)
│   ├── bank_events.csv       # 216 FOMC × 24 US banks CAR
│   ├── jp_bank_events.csv    # 216 FOMC × 11 JP banks CAR
│   ├── all_banks.csv         # US daily prices (24 banks + SPX + VIX)
│   ├── all_jp_banks.csv      # JP daily prices (11 banks + NK225 + TOPIX)
│   ├── y9c_complete.csv      # FR Y-9C quarterly (N=14, 2000-2025)
│   ├── fomc_paper_regression_data.csv  # Main regression dataset
│   ├── acosta_shocks.xlsx    # HF monetary policy shocks
│   ├── cb_dictionary_v2.json # Central bank dictionary
│   ├── lm_dictionary.json    # Full Loughran-McDonald dictionary
│   ├── press_conf/           # 89 FOMC press conference PDFs
│   └── ...                   # LLM checkpoints, sentiment scores, etc.
├── results/                  # Pre-computed analysis results (JSON)
├── dynamic/                  # Dynamic Stress Test System (Streamlit)
│   ├── app.py                # Dashboard (10+ pages)
│   ├── regime_detector.py    # ZLB/Normalization/FastHike classification
│   ├── scenario_generator.py # Regime-conditional scenario generation
│   ├── htm_risk_module.py    # HTM unrealized loss assessment (H9)
│   ├── shock_compensation.py # Dual shock-compensation engine (H8)
│   ├── correlation_engine.py # Dynamic bank inter-correlation
│   ├── cross_border.py       # International spillover (Japan ×1.57)
│   ├── reverse_stress_test.py# Bootstrap reverse stress testing
│   ├── fomc_parser.py        # Real-time LM% extraction
│   ├── uncertainty_channel.py# Delta disagreement channel
│   ├── score_fomc_inner_confidence.py  # LLM Inner Confidence scoring
│   ├── config.yaml           # All parameters calibrated from v7.2
│   └── requirements.txt
└── paper/                    # (NOT in git — local only)
```

## Experiment Tracking

Every paper version is registered as an experiment with input data, model specification, and key results.

```bash
# List all experiments
python code/run_experiment.py

# Show details + data availability for latest experiment
python code/run_experiment.py --latest

# Show specific experiment
python code/run_experiment.py experiments/v15_1_recovered_experiments/
```

### Adding a New Experiment

1. Create directory: `experiments/v16_your_experiment/`
2. Copy `config.yaml` from the latest experiment
3. Update: input_data, model, expected results
4. (Optional) Add `run.py` for one-click reproduction
5. Register in `experiments/manifest.yaml`

## Key Results

| Hypothesis | Finding | Statistic |
|---|---|---|
| H1 (Full Sample) | Dovish = lower bank returns | −0.89pp (t=−2.13)** |
| H2 (Regime Shift) | Pre-DFAST >> DFAST-era | 22× ratio, both US & Japan |
| H3 (CRE Cross-Section) | High-CRE banks more sensitive | −0.483pp (t=−3.17)*** |
| H4 (Quintile Response) | Directionally increasing | Spearman ρ=0.70 |
| H5 (Capital Channel) | Capital-building banks more sensitive | −0.483pp (t=−3.08)*** |
| H6 (International) | Japan 57% stronger than US | −1.40pp vs −0.89pp |
| H7 (FFIEC Extension) | Robust to N=20 | Sign preserved |
| H8 (NIM Channel) | ZLB compensation effect | Dovish×ZLB×NIM = +0.68*** |
| H9 (HTM Channel) | FastHike devastation | FastHike×HTM = −0.093 (t=−8.16)*** |
| H10 (Uncertainty) | Stance distance → worse CAR | coef=−0.0091, p=0.005*** |

### Latest: Direction-Interaction Model (v15.1)

| Test | Result |
|---|---|
| target × direction | t=2.83*** |
| path × direction | t=−1.91* |
| J-test vs D_hawk | Direction model ENCOMPASSES D_hawk |
| Spanning test | CB predicts DXY beyond shocks (t=−2.16) |
| LM% placebo | Both interactions insignificant |
| HAC distortion | 3.6× (target), 5.6× (path) → use bootstrap |

## Replication

```bash
# Full pipeline (v6.4)
python code/00_run_all.py

# Or step by step:
python code/01_fetch_us_banks.py    # Download US bank prices
python code/02_us_event_study.py    # Compute CARs
python code/03_us_stress_era.py     # H1-H4 analysis
python code/05_v62_h3_h5.py         # Cross-sectional (H3, H5)

# v10.0 Plans A-D:
python code/13_htm_afs_quasi_experiment.py
python code/15_nim_microfoundation.py
python code/16_aggregate_mapping.py
python code/18_kuttner_surprise.py

# LLM classification:
python code/scrape_fomc_minutes.py
python code/llm_classify_minutes.py
python code/llm_classify_transcripts.py

# Dynamic stress test dashboard:
cd dynamic && streamlit run app.py
```

## Version History

| Version | Date | Changes |
|---|---|---|
| v6.0 | 2026-06-04 | Initial complete paper |
| v6.2 | 2026-06-05 | H3 (CRE) + H5 (Capital) cross-section |
| v6.4 | 2026-06-06 | FFIEC 031 extension (N=20), Japan banks |
| v7.0 | 2026-06-06 | Channel decomposition: NIM, CRE, HTM |
| v8.0 | 2026-06-07 | Uncertainty Channel (H10): stance distance |
| v10.0 | 2026-06-07 | Plans A-D: HTM quasi-experiment, NIM, Aggregate, Kuttner |
| v10.4 | 2026-06-08 | CB-only main table + Rate Cut recovery |
| v11.0 | 2026-06-08 | LLM horse race, 81.5% orthogonal shocks |
| v12.0 | 2026-06-08 | LM% bias correction + regime analysis |
| v13.4 | 2026-06-09 | Post-audit: quadratic model (target²) |
| v14.1 | 2026-06-09 | Interaction model (target×D_hawk), passes wild bootstrap |
| v15.0 | 2026-06-09 | Direction model — J-test proves it encompasses D_hawk |
| v15.1 | 2026-06-09 | Recovered all experiments + 3 new (spanning, calibration, placebo) |

## Citation

```bibtex
@unpublished{zhang2026fomc,
  title={FOMC Communication and Bank Stress: US, Japan, and the Pre/Post-2008 Regime Shift},
  author={Zhang, Eileen},
  year={2026},
  note={Submitted to 2026 Federal Reserve Stress Testing Research Conference}
}
```

## License

Research data and code for academic use only. Bank price data sourced from Yahoo Finance and WRDS.
