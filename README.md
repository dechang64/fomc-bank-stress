# FOMC Communication and Bank Stress

**US, Japan, and the Pre/Post-2008 Regime Shift**

Dechang Xu (Soochow University) & Eileen Zhang (Xi'an Jiaotong-Liverpool University)

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
├── paper/                    # Latest paper + figures
│   ├── FOMC_BankStress_v80.docx
│   └── figures/              # 8 figures (Figure 1-7 + supplementary)
├── code/                     # Analysis scripts (chronological)
│   ├── 00_run_all.py         # Master runner
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
│   └── 12_build_v64_paper.py # Paper builder v6.4
├── data/                     # Processed datasets
│   ├── bank_events.csv       # 216 FOMC × 24 US banks CAR
│   ├── jp_bank_events.csv    # 216 FOMC × 11 JP banks CAR
│   ├── all_banks.csv         # US daily prices (24 banks + SPX + VIX)
│   ├── all_jp_banks.csv      # JP daily prices (11 banks + NK225 + TOPIX)
│   ├── y9c_complete.csv      # FR Y-9C quarterly (N=14, 2000-2025)
│   ├── prices_us/            # Individual US bank CSVs
│   └── prices_jp/            # Individual JP bank CSVs
├── results/                  # Pre-computed analysis results
│   ├── stress_era_results.json
│   ├── jp_h1_results.json
│   ├── jp_h1_by_bank.json
│   └── uncertainty_channel_results.json
├── dynamic/                  # 🆕 Dynamic Stress Test System
│   ├── app.py                # Streamlit dashboard (10 pages)
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
└── docs/                     # Cover letters, supplementary
```

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

## Channel Decomposition (v7.0+)

| | (1) NIM | (2) CRE | (3) Both | (4) Full |
|---|---|---|---|---|
| Dovish×NIM | −0.378*** | | −0.382*** | −0.373*** |
| Dovish×ZLB×NIM | +0.677*** | | +0.680*** | +0.677*** |
| Dovish×ZLB×CRE | | +0.268*** | +0.256** | +0.247** |
| FastHike×HTM | | | | −0.093*** |
| FastHike×NIM | | | | −0.966*** |
| N | 2,489 | 2,489 | 2,489 | 2,489 |

## Dynamic Stress Test System

A regime-conditional, FOMC-driven dynamic stress testing framework. All parameters calibrated from the paper's empirical estimates.

```bash
cd dynamic
pip install -r requirements.txt
streamlit run app.py
```

### Modules

| Module | Function | Key Parameter |
|---|---|---|
| `regime_detector` | ZLB/Normalization/FastHike | 6 regime boundary dates |
| `scenario_generator` | Regime-conditional scenarios | 9 auto-generated scenarios |
| `htm_risk_module` | HTM unrealized loss (H9) | SVB: $27.3B loss, 170.6% capital erosion |
| `shock_compensation` | Dual shock-compensation (H8) | ZLB/Dovish net +1.14pp |
| `correlation_engine` | Dynamic ρ | ZLB FOMC ρ=0.86 vs Normal ρ=0.68 |
| `cross_border` | International spillover | Japan ×1.57 |
| `reverse_stress_test` | Bootstrap reverse stress | ZLB/Hawkish P(loss)=88.5% |
| `fomc_parser` | Real-time LM% extraction | Loughran-McDonald dictionary |
| `uncertainty_channel` | Delta disagreement | Stance distance → capital buffer surcharge |

### Uncertainty Channel — Empirical Validation (v8.0)

194 FOMC statements scored with qwen-plus + LM% stance distance:

| Prediction | Result | Status |
|---|---|---|
| Stance distance → worse CAR | coef=−0.0091, p=0.005 | ✅ *** |
| Stance distance → more dispersion | coef=+0.000095, p=0.058 | ✅ * |
| ZLB amplifies disagreement | coef=+0.000332, p=0.051 | ✅ * |
| Stated confidence → CAR variance | r=−0.356, p<0.0001 | ✅ *** |
| Taper Tantrum: highest ambiguity | z-score=4.58 in ZLB subsample | ✅ Anomalous |

**Measurement**: LM-LLM stance distance (|LM% stance − LLM stance|) outperforms single-model logprobs (σ=0.016 too compressed), multi-model disagreement (>99% agreement within Qwen family), and temperature sampling (100% agreement).

## Replication

```bash
# 1. Download data
python code/01_fetch_us_banks.py
python code/09_fetch_jp_banks.py

# 2. Compute event-study CARs
python code/02_us_event_study.py
python code/10_jp_event_study.py

# 3. Run stress-era analysis (H1-H4)
python code/03_us_stress_era.py

# 4. Cross-sectional analysis (H3, H5)
python code/05_v62_h3_h5.py

# 5. FFIEC extension (H7)
python code/07_ffiec_dump.py
```

## Version History

| Version | Date | Changes |
|---|---|---|
| v6.0 | 2026-06-04 | Initial complete paper |
| v6.2 | 2026-06-05 | H3 (CRE) + H5 (Capital) cross-section |
| v6.4 | 2026-06-06 | FFIEC 031 extension (N=20), Japan banks |
| v7.0 | 2026-06-06 | Channel decomposition: NIM, CRE, HTM |
| v7.1 | 2026-06-07 | H4 quintile, Japan Table 7, Lu & Wu reference |
| v7.2 | 2026-06-07 | Table/Figure renumbering, figures embedded, Japan data corrected |
| v8.0 | 2026-06-07 | Uncertainty Channel (H10): stance distance, 194 statements, Tables 8-9 |

## Citation

```bibtex
@unpublished{xu2026fomc,
  title={FOMC Communication and Bank Stress: US, Japan, and the Pre/Post-2008 Regime Shift},
  author={Xu, Dechang and Zhang, Eileen},
  year={2026},
  note={Submitted to 2026 Federal Reserve Stress Testing Research Conference}
}
```

## License

Research data and code for academic use only. Bank price data sourced from Yahoo Finance and WRDS.
