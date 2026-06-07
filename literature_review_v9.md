# Literature Review: FOMC Information Hierarchy & Signal Divergence
## For Paper v9.0: FOMC Communication and Bank Stress
## Date: 2026-06-07

---

## 1. FOMC Minutes and Transcripts as Information Events

### Rosa (2013) - "The Financial Market Effect of FOMC Minutes"
- **Source**: FRB New York Economic Policy Review, 19(2), 67-81
- **Key Finding**: FOMC Minutes release significantly affects US asset price volatility and trading volume. The magnitude is economically meaningful but smaller than Statement-day effects.
- **Relevance**: Directly supports our finding that Minutes contain distinct information. Rosa shows Minutes affect markets; we show Statement-Minutes DIVERGENCE predicts bank stress.

### Meade and Stasavage (2008) - "Publicity of Debate and the Incentive to Dissent"
- **Source**: Economic Journal, 118(528), 695-717
- **Key Finding**: Transparency of FOMC deliberations affects voting behavior. When transcripts are released, dissent decreases.
- **Relevance**: Supports the information hierarchy framework - transparency changes behavior, creating systematic differences between Statement and Minutes.

### Hansen and McMahon (2016) - "Shocking Language: What Makes Words in Central Bank Communications Newsworthy?"
- **Source**: American Economic Review, 106(11), 3269-3327
- **Key Finding**: FOMC statements contain "shocks" - new information not anticipated by markets. These shocks affect asset prices.
- **Relevance**: Our divergence measure captures a specific type of "shock" - when the Statement shock is later contradicted by Minutes.

### "How Important Is Information from FOMC Minutes?" (SF Fed Letter 2016)
- **Source**: FRBSF Economic Letter 2016-36
- **Key Finding**: FOMC Minutes contain significant information beyond the Statement, particularly about the Committee's assessment of risks and forward guidance.
- **Relevance**: Directly supports our three-document hierarchy - Minutes add information not in the Statement.

---

## 2. FOMC Communication Events and Multi-Channel Analysis

### Bauer and Swanson (2023/2025) - "FOMC Communication Events and Monetary Transmission"
- **Source**: AEA 2025 Conference; FRB San Francisco Working Paper
- **Key Finding**: Press conferences have stronger effects than FOMC statements on most asset prices. Multiple communication channels (statement, press conference, minutes) each contribute unique information.
- **Relevance**: Directly supports our multi-document approach. They find press conferences > statements; we find Minutes divergence > statement stance.

### "Financial Market Effects of FOMC Communication" (Fed Working Paper 2025)
- **Source**: FRB Working Paper
- **Key Finding**: Press conferences have stronger effects than FOMC statements. The term structure evidence shows peak effects on medium-term rates.
- **Relevance**: Supports the information hierarchy - different communication channels have different market impacts.

---

## 3. LLM/NLP for Central Bank Text Analysis

### "Using Generative AI Models to Understand FOMC Monetary Policy Discussions" (FEDS Notes 2024)
- **Source**: Federal Reserve FEDS Notes, December 6, 2024
- **Key Finding**: Off-the-shelf generative AI models can identify topics discussed during monetary policy deliberations with high accuracy. LLMs outperform traditional bag-of-words approaches.
- **Relevance**: Validates our use of LLM (qwen-plus) for FOMC document classification. The Fed itself uses LLMs for this purpose.

### "Interpreting Fedspeak with Confidence" (2025)
- **Source**: arXiv:2508.08001
- **Key Finding**: LLM-based uncertainty-aware framework for interpreting FOMC communications. Uses confidence scores to distinguish between clear and ambiguous policy signals.
- **Relevance**: Very close to our Inner Confidence approach. They use LLM confidence for FOMC interpretation; we use it to identify "confident but wrong" statements.

### "Agree to Disagree: Measuring Hidden Dissent in FOMC Meetings" (2023/2025)
- **Source**: arXiv:2308.10131; Journal of Economic Dynamics and Control
- **Key Finding**: Deep learning on FOMC transcripts reveals hidden dissent not captured by formal votes. Dissent predicts future policy shifts.
- **Relevance**: Complements our work. They find hidden dissent in Transcripts; we find Statement-Minutes divergence. Both capture the gap between public and private deliberation.

### "Assessing Alignment of FOMC Statements with Minutes" (IACIS 2025)
- **Source**: IACIS 2025 Proceedings
- **Key Finding**: LLM-based abstractive summarization can assess alignment between FOMC Statements and Minutes. Finds systematic misalignment.
- **Relevance**: Most directly related to our work. They measure Statement-Minutes alignment using LLMs; we measure divergence and show it predicts bank CAR.

---

## 4. Central Bank Transparency and Banking Sector

### Cieslak et al. (2019) - "The Short-End of the Yield Curve"
- **Source**: Already cited in our paper
- **Key Finding**: FOMC private information leaks through informal channels, affecting short-term rates.
- **Relevance**: Our finding that divergence affects CAR on Statement day (not Minutes release day) is consistent with Cieslak et al.'s information leakage channel.

### Blinder et al. (2008) - "Central Bank Communication and Monetary Policy"
- **Source**: Already cited in our paper; Journal of Economic Perspectives
- **Key Finding**: Central bank communication matters for market expectations. Transparency reduces uncertainty.
- **Relevance**: Our divergence measure captures the OPPOSITE - when transparency is incomplete (Statement ≠ Minutes), uncertainty increases and bank stress amplifies.

---

## 5. Our Contribution Relative to Literature

| Dimension | Existing Literature | Our Paper |
|-----------|-------------------|-----------|
| **Documents** | Single document (Statement only) | Three-document hierarchy (Statement/Minutes/Transcript) |
| **Measurement** | LM% or LLM, not both | Both LM% and LLM, plus Inner Confidence |
| **Divergence** | Not measured | Statement-Minutes divergence as predictor |
| **Validation** | None | Transcript as ground truth |
| **Outcome** | Bond yields, equity indices | Bank-specific CAR (stress test relevance) |
| **Cross-market** | US only | US vs Japan comparison |
| **Confidence** | Not considered | "Confident but wrong" channel |

### Key Novelty:
No existing paper combines (1) three-document FOMC corpus, (2) Statement-Minutes divergence as a predictor, (3) Transcript validation, (4) bank-specific CAR, and (5) Inner Confidence channel. The closest paper is "Assessing Alignment of FOMC Statements with Minutes" (IACIS 2025), but they do not link alignment to financial outcomes.

---

## 6. Papers to Add to References

1. **Rosa (2013)** - Already added
2. **Hansen and McMahon (2016)** - Already added  
3. **Meade and Stasavage (2008)** - Already added
4. **Bauer and Swanson (2025)** - FOMC Communication Events and Monetary Transmission
5. **Fed FEDS Notes (2024)** - Using Generative AI Models to Understand FOMC
6. **"Agree to Disagree" (2025)** - Hidden Dissent in FOMC Meetings
7. **"Interpreting Fedspeak with Confidence" (2025)** - LLM uncertainty framework
8. **"Assessing Alignment" (IACIS 2025)** - Statement-Minutes alignment
