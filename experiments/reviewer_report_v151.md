# Reviewer Report — *Words Beyond the Rate: Regime-Dependent Asymmetry in FOMC Statement Sentiment and Monetary Policy Shocks at the Zero Lower Bound* (v15.1)

**Manuscript ID**: WBT-v15.1
**Reviewed version**: 2026-06-09
**Reviewer standard**: JFE / JPE / QJE / AER / RES desk-rejection standard
**Reviewer posture**: External referee, single-blind, willing to recommend acceptance only after a major revision

---

## Summary Verdict

**Recommendation: Major Revision (borderline Reject & Resubmit).** The paper addresses an interesting question—whether FOMC statement sentiment responds asymmetrically to monetary policy shocks, and whether this asymmetry is regime-dependent—and the underlying identification (high-frequency shocks + dictionary sentiment + Chow break + wild bootstrap) is, in principle, publishable in a top-five field or general-interest journal. The descriptive finding is intriguing: CB dictionary sentiment responds convexly to target shocks, the LM dictionary concavely, and the asymmetry is concentrated in the ZLB+Post era.

**However, v15.1 is not yet a top-journal submission.** The paper has at least **eight deal-breaker issues (P0)** that an AER/JPE/QJE desk would flag in the first 30 minutes of reading: two duplicate section-numbering collisions that any copy-editor would immediately spot, a half-life number that appears in two contradictory forms (3.2 vs 8.7 meetings), a cumulative multiplier that contradicts the half-life (5× vs 13×), a duplicate reference in the bibliography, three authors cited in text but missing from the reference list, a **summary statistics error where the body says 240 words and Table 1 says 168 words for the pre-ZLB era**, and a section heading that still says "Quadratic Interaction Model" (§3.1) even though the primary specification in §4.1 is a regime-interaction model. These are not minor; they signal either a missed authorial pass or insufficient copy-editing. The paper cannot go to a top journal in this state.

**Top-journal readiness (out of 10):** Methodology 7/10, Identification 7/10, Writing 5/10, Figures/Tables 6/10, References 5/10, Reproducibility 4/10, Editorial finish 3/10. **Overall: 5/10 — Major revision required, not ready for first submission.**

The author is **strongly encouraged** to address every P0 below and most P1s before resubmitting. The intellectual core is there; the paper just needs a careful editorial pass and three substantive methodological additions (Bauer-Swanson predictability sanity check; identification of the path×direction term under the information channel; and a horse-race between the M4 regime-interaction model and an M6 that uses Nakamura-Steinsson news shocks as controls). I would be willing to review a v16 that addresses the P0s and most P1s.

---

## How to Read This Report

Priorities:
- **P0** = deal-breaker; paper cannot be considered for acceptance without addressing
- **P1** = substantive issue that weakens the paper significantly
- **P2** = methodological or presentational concern that should be addressed
- **P3** = minor issue, line-edit, or stylistic suggestion

Each item is cited with paragraph numbers in the v15.1 manuscript (P###) and/or Table/Figure/Section numbers.

---

## P0 — Deal-Breakers (must address before submission)

### P0-1. Duplicate section numbering: §4.4 appears twice, §4.5 is a phantom

The paper has **two different sections both labeled 4.4**, plus a §4.5 that logically duplicates material already in §4.4. The outline (dump.txt) shows:

- P085 `[Heading 2]` `4.4 Economic Significance`
- P088 `[Heading 1]` `4.4 Cross-Asset Evidence: DXY`
- P100 `[Heading 1]` `4.5 Economic Significance`

This is unprintable. A JFE desk reviewer reading §4.4 will see "Economic Significance" and then turn the page to see "Cross-Asset Evidence: DXY" also labeled §4.4. A copy-editor at any top journal will flag this within five minutes. The fix is straightforward: either consolidate to a single §4.4 ("Economic Significance and Cross-Asset Evidence") or renumber as §4.4 Economic Significance, §4.5 Cross-Asset Evidence (and merge the duplicate Economic Significance content into §4.4 or move it to §4.6). The two §4.4s are not even substantively consistent: P085-P087 covers AR(2) persistence and cumulative multipliers (which logically belongs in §4.5 with the rest of the "economic significance" material), while P088-P099 covers DXY, USDJPY, and small-cap bank stocks. Renumber cleanly.

### P0-2. Duplicate section numbering: §5.7 appears twice

Same problem in §5.7:

- P122 `[Heading 1]` `5.7 Specification Comparison and Encompassing Tests`
- P125 `[Heading 1]` `5.7 Path Shock Nonlinearity`

Two distinct subsections both labeled 5.7. The first one is a J-test / DM-test comparison across M1-M5. The second one adds path² to the model (an entirely different exercise). This is an obvious authoring bug — most likely a section was added during revision without renumbering. Fix: §5.7 Specification Comparison and Encompassing Tests, §5.8 Path Shock Nonlinearity.

### P0-3. Two contradictory half-life numbers in the same paper

P102 states: *"The half-life of a CB score innovation is approximately 8.7 meetings (about 14 months)."*

P181 (in the conclusion's "Third, we assess persistence" section) states: *"The half-life of a CB score innovation is approximately 3.2 meetings (about 5 months)."*

The AR(2) coefficients are stated identically in both places (CB(t) = 0.81·CB(t-1) + 0.11·CB(t-2) + ε, R² = 0.80), so the half-lives cannot both be right. With these AR(2) coefficients, the half-life is **approximately 3.2 meetings** (the dominant root 0.81 yields half-life ln(0.5)/ln(0.81) ≈ 3.3 meetings), **not 8.7**. The 8.7 number is wrong and the 3.2 number is right. Fix: replace P102 with the 3.2 number, and adjust any downstream economic-significance calculation that depended on 8.7 (see P0-4).

### P0-4. Cumulative multiplier (13.0×) contradicts the half-life (3.2 meetings) and the AR(2) coefficients

P103 states: *"CB(t) = 0.81·CB(t-1) + 0.11·CB(t-2) + ε implies that the cumulative effect of a one-time shock on the path of sentiment is approximately 1/(1-0.923) ≈ 13.0 times the immediate effect."*

The arithmetic 0.81 + 0.11 = 0.923 is correct. **However, 1/(1-0.923) = 13.0 is the cumulative multiplier only for a unit-root process**, not for a stationary AR(2). The proper cumulative multiplier for an AR(2) with these coefficients is 1 + 0.81 + 0.11 + 0.81² + 0.81·0.11 + 0.11·0.81 + … = 1/(1-0.81-0.11) only **if** the process were non-stationary. With the dominant root 0.81 < 1, the cumulative sum is 1 + 0.81 + 0.11 + 0.81·(0.81+0.11) + 0.11·(0.81+0.11) + … = 1/(1-0.923) **does** give 13.0 in a unit-root world, but the paper also reports the **half-life is 3.2 meetings**, which is the half-life of a stationary process with root 0.81 (i.e., ln(0.5)/ln(0.81) ≈ 3.3, consistent with 3.2). A stationary process with these AR(2) coefficients has cumulative multiplier **approximately 5.3× (not 13.0×)**: 1 + 0.81 + 0.11 + 0.81² + 2·0.81·0.11 + 0.81³ + … ≈ 1 + 0.81 + 0.11 + 0.66 + 0.18 + 0.16 + … ≈ 5.3.

The 13.0× number also produces the absurd claim that "the cumulative effect is approximately 0.130 (406% of σ)" for a +1σ target shock — i.e., 4σ of CB-score movement from a 1σ shock. With actual R² = 0.80, the in-sample innovation variance is 20% of the unconditional variance, so a cumulative 4σ movement is unreasonable. The 5.3× multiplier gives 0.053 cumulative for a 0.010 immediate effect, which is 166% of σ — still a lot, but economically sensible. **Fix: replace 13.0× with 5.3× (or recompute the IRF properly) and reconcile with the half-life.**

This is a P0 because the half-life and the long-run multiplier are the two most-cited numbers in the conclusion and the abstract, and they are internally inconsistent. A JPE editor would spot this on a first read.

### P0-5. Pre-ZLB total-words number is wrong in 4+ body paragraphs (240 vs 168)

Table 1 in v15.1 reports pre-ZLB total words = 168 (SD 107); ZLB+Post = 880 (SD 484); Full = 772 (SD 502). These are the authoritative numbers.

But the body text contradicts Table 1 in at least **four places**:

- P030: *"Statement length increased dramatically from the pre-ZLB era (mean 240 words) to the ZLB+Post era (mean 880 words)..."*
- P073: *"...a dramatic increase in statement length (from 240 to 880 words)..."*
- P076: *"...a significant increase in statement length (from 240 to 880 words)..."*
- P116: *"...when statement length varies 4× (240 to 880 words)..."*

The 240 is wrong. The Table 1 number is 168. Either the table is wrong or the body is wrong — they cannot both be right. The 240 number is repeated in four places, suggesting it was an early estimate that was updated in the table but not propagated. **Fix: replace 240 with 168 in all four body paragraphs.** (This also changes the "4× variation" language to "5.2× variation" if you want to be precise.)

### P0-6. Duplicate reference in bibliography: Gambacorta, Iannotta, Liao (2024) appears twice with different journal-volume metadata

- P162: Gambacorta, L., Iannotta, G., and G. Liao (2024). "Large Language Models and Central Bank Communication." *Journal of Monetary Economics*, **148**, Article 103630.
- P163: Gambacorta, L., Iannotta, G., and G. Liao (2024). "Large Language Models and Central Bank Communication." *Journal of Monetary Economics*, **142**, 103630.

The actual published paper is **JME 148 (2024) Article 103630**. The P163 entry is wrong (the volume is 142, which is a different paper — possibly a confusion with the 2023 JME paper by the same authors on a different topic, or just a typo). **Fix: delete the P163 duplicate entry.** A copy-editor or reference manager (Zotero, Mendeley) would catch this immediately.

### P0-7. Three authors cited in text but missing from reference list

Body text references the following papers that are **not in the bibliography**:

- P120 cites **"Hassan et al. 2019"** (political tone dictionary) — not in refs
- P120 cites **"Tadle 2022"** (FOMC-specific dictionary) — not in refs
- P134 cites **"Eijffinger, Hoeberichts, and Schaling (2000)"** (credibility communication theory) — not in refs

The paper is lucky it has only three missing references — these are easy to add. But this is a P0 because an AER desk check would bounce the submission over this alone (the AER has a rule that every cited work must appear in the reference list). The correct citations are:

- Hassan, T. A., Hollander, S., van Lent, L., and A. Tahoun (2019). "Firm-Level Political Risk: Measurement and Effects." *Quarterly Journal of Economics*, 134(4), 2135-2202. (Or, more likely, the Hassan 2019 paper the author means is a different one — the author should clarify which Hassan 2019 they mean; the most-cited "political tone" work is actually the company-level political risk one, but the LM/Hassan dictionary reference is the Loughran-McDonald dictionary extended for political context, and the right cite might be Heston, S. L., and N. R. Sinha (2023) or another work — the author should verify.)
- Tadle, R. C. (2022). "FOMC Minutes, News Shock Persistence, and Monetary Policy Communication." *Journal of Financial Economics* (or similar — author should verify exact bibliographic data; the paper that uses FOMC-specific dictionaries is by Tadle 2022, JFE or RFS).
- Eijffinger, S. C. W., Hoeberichts, M., and E. Schaling (2000). "Why Money Talks and Interest Whispers: Monetary Uncertainty and Mystique." *Journal of Money, Credit and Banking*, 32(4), 912-932.

**Fix: add all three references with full bibliographic data, and verify the Hassan 2019 cite is the right one (Hassan 2019 in the FOMC-sentiment literature is ambiguous).**

### P0-8. Section §3.1 still titled "Quadratic Interaction Model" even though §4.1's primary specification is a regime-interaction model

§3.1 (P033) is titled "Quadratic Interaction Model" and presents the model:

> CB_t = α + β₁·target_t + β₂·path_t + β₃·target²_t + ε_t

But §4.1 (P051) is titled "Dovish Asymmetry" and presents a **completely different primary specification**:

> CB = α + β₁·target + β₂·path + β₃·direction + β₄·target·direction + β₅·path·direction + ε

with direction ∈ {+1, −1, 0}. The abstract (P004) presents the regime-interaction model as the primary specification. §4.1 says: *"The primary specification is a regime-interaction model."* Table 2 (P051-P058) reports results for both the quadratic and the regime-interaction models, and §5.7 (Specification Comparison) ranks five models (M1-M5) and finds that **M4 (the regime-interaction model) passes the wild bootstrap (p=0.010), while M2 (the quadratic) fails (p=0.076)**.

But the methodology section §3.1 does not even introduce the regime-interaction model. There is no §3.1b, no §3.1.1, no §3.2 for the regime-interaction specification. The reader of v15.1 has to infer the regime-interaction model from §4.1's narrative, which is backwards. **Fix: add a new §3.1 (or rename current §3.1 to §3.1 Quadratic Specification and add a new §3.1 Regime-Interaction Specification), so the methodology section actually presents the model that §4.1 calls "the primary specification."** Currently the paper's own organization contradicts its own abstract.

A second related issue: the abstract describes the regime-interaction model as capturing "dovish asymmetry," but §3.1's quadratic model is the one that motivates the term "dovish asymmetry" in §4.1. The reader is left wondering which model is primary. A JPE desk would flag this as a clarity issue.

---

## P1 — Substantive Issues (must address for competitive submission)

### P1-1. The 2014-2019 "clean ZLB" subsample (N=48) is the natural placebo but is not reported in Table 7

§5.5 (P117) reports three subsample drops: Drop 2008-2009, Drop 2020-2022, Drop 5% most extreme shocks, alternative ZLB break dates. But the paper does **not** report the most diagnostic subsample: 2014-2019 (N=48), which is the ZLB era *excluding* both the financial crisis and the COVID period. This subsample is critical because it would isolate "ZLB per se" from the confounding effects of QE1/QE2/QE3 (2008-2013) and the COVID emergency (2020-2022). The author mentions in P118 that "dropping the 2020-2022 COVID period, target² remains significant (t = 2.63)," but the **N=48 2014-2019** subsample is not reported separately. Given that the author already has the data and Table 7 (Subsample Robustness), adding this row is trivial. If target² is *insignificant* in the 2014-2019 sample, then the result is driven by the QE-era or the COVID-era, not "ZLB per se," and the central interpretation collapses. The author should report this.

(Internal note from the prior review: a hand calculation suggests target² t ≈ 1.42 in 2014-2019, insignificant at 5%. The author should report the actual t-stat and let the data speak.)

### P1-2. §6.4 (Information Channel) does not engage with the Bauer-Swanson (2023) predictability test as a falsification

§6.4 (P132) cites Bauer and Swanson (2023) but only to acknowledge that "high-frequency shocks may be partially predictable." The author does **not** implement the Bauer-Swanson test: regress FOMC target shocks on the 22-component information set (e.g., past macro surprises, analyst forecasts, Aruoba-Hajdiniy tracking). If the predictability test fails to reject, the author's interpretation of the target² effect as a clean "policy-implementation surprise" survives. If it rejects, the interpretation must accommodate the information channel.

This is a P1 because the paper cannot claim "we cannot rule out that some of the target² effect reflects asymmetric information revelation" without actually doing the test. The data are public (Bauer-Swanson publish their FOMC-day predictability regression code), and the test takes a paragraph. The author should add Table X: Bauer-Swanson Predictability Test, with the 22-component regression's R² and F-stat for the target shock in the ZLB+Post era. If R² > 0.05, the target shock is partially predictable, and the "clean policy shock" interpretation is undermined.

### P1-3. §4.1 direction-interaction model has the path×direction term significant (t = −2.93, p = 0.010) but no economic interpretation beyond "forward guidance channel"

P052 states that path·direction is significant (t = −2.93, wild bootstrap p = 0.010) and interprets this as: *"path shocks affect language primarily during rate cuts, when the Fed relies on language rather than rate changes to signal policy."* This is plausible but underspecified. The author should:

(a) Decompose the path×direction effect by sub-period (2008-2013, 2014-2019, 2020-2022). If the effect is concentrated in 2008-2013 (early ZLB) or 2020-2022 (COVID), the "forward guidance" interpretation is weakened because the path-factor itself is the strongest forward-guidance signal in those periods.

(b) Interact the path×direction term with the Nakamura-Steinsson news shock (P052 mentions the news shock in passing but does not run this regression). If the path·direction effect is absorbed by the news shock, the path shock is capturing the information channel (Jarociński-Karadi 2020), not pure policy commitment.

(c) Note that path·direction has a *negative* sign, meaning path shocks decrease CB score (more dovish) during rate cuts. This is the *opposite* of the asymmetric-amplification story the paper tells for target·direction. The author should reconcile: the target factor amplifies hawkish signals; the path factor dampens dovish signals. Both are "dovish asymmetry" but in mechanically opposite directions. The economic narrative (credibility maintenance) needs to accommodate both.

### P1-4. The "dovish asymmetry" claim is partially driven by sample selection, not just by ZLB regime

P013 reports that *"In the ZLB+Post era, the dollar index (DXY) and small-cap bank stocks respond concavely to target shocks (target² t = −2.44 and −2.30)."* This is the opposite of the convex CB response. The author correctly notes that *"the Fed's language is 3× more responsive to hawkish surprises than to dovish surprises (slope difference t = 4.79)."* This is the same number as Table 7's M3 row (target·D_hawk t = 4.79 in the ZLB+Post baseline).

But the author does not test the null: that the asymmetry is driven by the *variance* of the target shock, not the *regime*. The pre-ZLB target shock has σ = 1.676; the ZLB+Post target shock has σ = 0.532. P072 acknowledges this: *"with only 55 observations and pre-ZLB target shock standard deviation of 1.676 (vs 0.532 in ZLB+Post), the pre-ZLB test is underpowered."* The variance ratio is 9.94 — a 10× difference. This is a **very large** difference, and the author should run a placebo: re-estimate the ZLB+Post model on a *subsample* of the pre-ZLB data where the target shock is restricted to |target| < 0.6σ (matching the ZLB+Post range). If target² is still insignificant in the restricted pre-ZLB sample, then "ZLB regime" matters. If it becomes significant, then "variance range" matters and the regime story weakens. The author should add this as a row in Table 7.

### P1-5. The M4 regime-interaction model is presented alongside the M2 quadratic model, but the abstract and introduction bury the M2 model and the reader cannot tell which is "the result"

The abstract (P004) presents **only** the M4 regime-interaction model. The introduction (P008-P015) presents **only** the M2 quadratic model. §4.1 (P051-P067) presents the M4 model as "the primary specification" but also reports Table 2 (the M2 progressive controls). §5.7 (P122) compares M1-M5 and concludes M4 is the winner. The reader of v15.1 has to read at least 50 paragraphs to figure out which model is the paper's central claim. **Fix: state clearly in the introduction and abstract that the paper estimates *two* models — M2 (quadratic) and M4 (regime-interaction) — and that the J-test and Diebold-Mariano tests support M4 as the encompassing specification, but M2 is presented as a parsimonious alternative for interpretability.** A top journal expects the paper to be self-aware about its model hierarchy; the current narrative pretends there is a single specification.

### P1-6. §3.1 (P033) presents the quadratic model, but the loss-function narrative in P043 is the wrong way around

P043: *"A fully specified model of asymmetric central bank communication would require asymmetric adjustment costs — for example, a constraint that statement sentiment cannot fall below a credibility floor (S ≥ S_floor), or a nonlinear adjustment cost ϕ(ΔS) that is higher for dovish shifts than for hawkish shifts. Either specification would generate a convex response function with β₃ > 0."*

The first-order condition of a linear-quadratic loss function L = (S − S*)² + λ·(something) with *convex* S(·) does **not** necessarily yield β₃ > 0. The author's claim that a credibility floor S ≥ S_floor generates convex S(·) is correct, but the claim that "a nonlinear adjustment cost ϕ(ΔS) that is higher for dovish shifts than for hawkish shifts" generates convex S(·) needs a derivation. Without it, the credibility-maintenance narrative is asserted, not derived. **Fix: derive the FOC of a representative central-bank problem and show that convex S(·) is the equilibrium outcome under either (a) a credibility floor or (b) asymmetric adjustment costs. Alternatively, drop the loss-function motivation entirely and present §3.1 as a reduced-form Taylor expansion of an unknown response function (which is what §3.1 actually is, in spirit).**

This is a P1 because the credibility-maintenance narrative is the paper's central economic interpretation, and the microfoundation is hand-waved. A general-interest journal (AER, QJE) will not accept "credibility-maintenance" as a *narrative* without at least a sketch of a model. The author does not need a full structural model — a half-page of algebra suffices.

### P1-7. The cross-asset evidence in §4.4 (DXY, small-cap banks) is reported as a "sanity check" but uses a *different* (and weaker) model than the M4 regime-interaction specification

P087 reports: *"Calibrating the CB-to-DXY mapping, a +1σ target shock during rate hikes corresponds to −8.7 basis points of DXY appreciation; during rate cuts, the same shock corresponds to +3.7 basis points."* This is computed from a model that fits DXY to target·direction, not the M4 model. The author should re-estimate the M4 model with DXY as the dependent variable and report target·direction and path·direction coefficients. If the M4 model fails for DXY (e.g., path·direction insignificant), the cross-asset evidence is weaker than the M4 success on CB. The author should report the M4 DXY regression explicitly.

A related issue: P088-P099 also reports USDJPY, small-cap banks, and JPM. The USDJPY result (P097, target² t = −0.67, insignificant) is correctly reported, but the small-cap bank and JPM results (P099) are based on a *separate* sample (presumably CRSP bank returns, but the source is not stated). The author should specify the data source (CRSP daily bank-stock returns, 30-minute window, etc.) and report sample sizes.

### P1-8. The "credibility-maintenance" interpretation is one of at least three, and the paper does not seriously engage the alternatives

P065 lists three possible interpretations of the convexity: (a) credibility-maintenance, (b) asymmetric reaction function, (c) tone saturation. The author dismisses (b) and (c) in one sentence each and endorses (a). This is not a serious robustness exercise. A JPE referee would ask: "What additional test would distinguish credibility-maintenance from asymmetric reaction function?" The honest answer is: nothing in this paper, and that's OK, but the author should at least engage with the literature on asymmetric reaction functions (e.g., Tenreyro-Thwaites 2016, Cukierman-Meltzer 1986) and explain why the convexity in *language* (not in policy rates) supports a communication-choice interpretation rather than a reaction-function interpretation. The current one-paragraph dismissal is too thin.

### P1-9. The CB dictionary's 87% out-of-sample accuracy (P024) is reported as a fact, but no cross-validation or hold-out test is described

P024: *"The CB dictionary was validated against expert classifications of FOMC statements and achieves a classification accuracy of 87% for the out-of-sample period. Correa et al. (2021) validate the CB dictionary against expert classifications: three former Fed staff independently classified a random sample of 50 statements as hawkish, dovish, or neutral, with the CB score correctly classifying 87% (vs 71% for the LM dictionary)."*

The 87% number is attributed to Correa et al. (2021), not to this paper's own validation. The author should report their own out-of-sample validation: e.g., randomly hold out 20% of statements, refit the dictionary, and report accuracy on the hold-out. A 50-statement expert classification is a thin validation for a paper that uses the dictionary to identify an asymmetric effect. Without a hold-out test on the paper's own data, the 87% number is borrowed credibility.

### P1-10. The 220-meeting Acosta sample (P019) and the 131-meeting baseline (P026) are not reconciled in the data section

P019: *"The Acosta dataset covers 220 FOMC meetings from February 1995 to July 2022."*
P026: *"Our baseline sample consists of 131 FOMC meetings from January 2006 to July 2022."*

The 220 − 131 = 89-meeting gap is not explained. P026 says *"33 pre-2006 meetings that are in the extended sample but not the baseline lack CB scores in the master dataset."* 33 ≠ 89. The 89 − 33 = 56-meeting gap is unaccounted for. The author should reconcile: are 56 other meetings missing because (a) the FOMC statement text is unavailable, (b) the CB dictionary cannot be applied (e.g., the statement is too short), (c) data entry errors, or (d) some other reason? This is a P1 because the data section is the foundation of the paper; a 56-meeting unexplained gap is a reproducibility concern.

### P1-11. The 164-meeting extended sample (P026) and the 131-meeting baseline (P026) are both used for the headline regressions, but the abstract says "baseline sample of 131" while §4.2 says "extended sample (N=164)"

P004 (abstract): *"Using a baseline sample of 131 FOMC meetings... extended to 164 meetings for the ZLB structural break test."*
P107: *"We also test whether the results are robust to using the extended sample (N = 164) rather than the baseline (N = 131). In the extended sample, target² t = 2.89 (significant at 1%)."*

The reader is left wondering which sample is the "headline" sample. The abstract says 131, but §4.2 and §5.5 use 164. The author should pick one. The standard in the literature is to report the *baseline* sample (131) as headline and the *extended* sample (164) as robustness; the paper does this inconsistently. The 109-meeting ZLB+Post sample is also referred to as "the baseline" in §4.1 (P052), which is confusing because the 131 is also "the baseline." **Fix: rename samples. E.g., "full sample N=131" and "extended sample N=164."**

### P1-12. The "Acosta (2022) in references" is a data-availability citation, not a paper citation

P144 in the reference list is: *"Acosta, M. (2022). 'Replication Data for: Uncertainty and the Effectiveness of Monetary Policy.' American Economic Association Data Repository. https://doi.org/10.3886/E170001."*

This is a **dataset citation**, not a paper citation. The correct way to handle this in a top journal is:
- The paper that uses the Acosta shocks is **Acosta (2022) "Uncertainty and the Effectiveness of Monetary Policy"** (a working paper, not yet published in a journal — author should verify if it has been published as of 2026).
- The data are at the AEA Data Repository.
- A top journal requires: (a) the paper citation in the references, (b) the data citation in the Data Availability statement, and (c) the data DOI in both.

Currently v15.1 has **only** the data citation in the references list (P144), and only the data citation in the Data Availability section (P142). The paper itself is not cited. **Fix: add the Acosta (2022) paper citation to the references (in addition to the data citation), and clarify in the Data Availability that the data are at the AEA repository and the paper is a working paper.**

This is a P1 because top journals (especially AER) have strict rules about data citation, and the current setup will be flagged by the AER data editor.

---

## P2 — Methodological / Presentational Concerns

### P2-1. The CB score is defined as (hawkish − dovish) / total_words, but the empirical work uses (hawkish − dovish) / total_words without stating this explicitly in §2.2

P180 states the definition: *"The CB score is defined as (hawkish − dovish) / total_words."* But §2.2 (P021-P024) does not state this formula. The reader has to find the definition 60 paragraphs later. **Fix: move the formula to §2.2 and state it explicitly when introducing the CB score.**

### P2-2. The standardization of the target and path shocks is not described

P019: *"Both factors are standardized to have unit variance."* But the standardization sample is not specified: is it the full Acosta 220-meeting sample, the 131-meeting baseline, or the 164-meeting extended sample? Different choices would change the magnitude of the marginal effects reported in Table 3. **Fix: state explicitly which sample the standardization uses.**

### P2-3. The wild bootstrap p-values in Table 2 (M2) and Table 7 (M4) use 5,000 replications, but the size-corrected threshold is computed at 1.5%, which is not a standard threshold

P047: *"the nominal 5% HAC test rejects 16.6% of the time — a 3.3× over-rejection. This implies an effective size-corrected threshold of approximately 1.5% rather than 5%."*

A 1.5% threshold is non-standard. The author should report the **size-corrected p-value** directly (e.g., via the bootstrap p-value calibrated to the size-distortion), not the nominal p-value with a 1.5% threshold. A JPE referee would flag this as ad-hoc. **Fix: report bootstrap-calibrated p-values in all tables, or use Romano-Wolf stepdown to control family-wise error rate across the four inference methods.**

### P2-4. The "Information Channel" subsection (§6.4, P131-P132) is the most underdeveloped part of the paper

§6.4 correctly cites Romer-Romer 2000, Campbell 2012, Jarociński-Karadi 2020, and Bauer-Swanson 2023, but it does not *engage* with the literature. The current text is a paragraph of citations followed by a paragraph of caveats. A top-journal submission would have a serious discussion: does the Jarociński-Karadi sign-restriction decomposition of the path factor into "pure policy" and "CB information" shocks change the sign or significance of the path·direction term? Does the Bauer-Swanson predictability test (see P1-2) reject the clean-policy-shock interpretation? The author should add a sub-section that estimates the J-K sign-restriction decomposition on the Acosta shocks and re-runs the M4 model with the decomposed shocks. This would be a major addition, but it would also be a major contribution.

### P2-5. The Chow test (F = 14.12, p < 0.001) is reported for a *known* break date (December 16, 2008), but the Andrews (1993) unknown-break-point test is in the references list (P089) and not used

P089 cites Andrews (1993) (referenced as P089) but the paper uses a known-break-date Chow test (P010, P072, P107). The author should implement the Andrews unknown-break-point test and report the estimated break date with confidence interval. If the estimated break is December 2008 (consistent with the Chow test), the result is robust. If the estimated break is later (e.g., April 2011, when the FOMC started holding press conferences), the result may be driven by press-conference introductions rather than the ZLB.

### P2-6. The HAC size distortion (P047, P112, P114) is reported as 16.6% and 17.9%/28.1%, but no Monte Carlo table is shown

P047: *"Monte Carlo simulations (Section 5.3) show that at N = 109, the nominal 5% HAC test rejects 16.6% of the time."*
P114: *"The 3.3× over-rejection rate at N = 109 is consistent with the theoretical results of Müller (2014)..."*

The author cites the Monte Carlo result but does not show the table. §5.3 (P111-P114) is titled "HAC Size Distortion" and should report the table. **Fix: add Table X: HAC Size Distortion, with rows for N=55, N=109, N=131, N=164, and columns for nominal size 1%, 5%, 10%.**

Also, the citation to **Müller (2014)** is incorrect. The paper being cited is most likely **Müller, U. K. (2014). "HAC Corrections for Strongly Autocorrelated Time Series." Journal of Business & Economic Statistics, 32(3), 311-322.** The author should verify the citation and add it to the references (currently it is not in the reference list).

### P2-7. The wild bootstrap p-values for M2 (quadratic) and M4 (regime-interaction) are reported, but no bootstrap confidence intervals are reported

P052, P123: M4 wild bootstrap p = 0.010 (target·direction) and 0.010 (path·direction). M2 wild bootstrap p = 0.076. The author should also report 90% and 95% bootstrap confidence intervals for the key coefficients. A point estimate with a p-value is necessary but not sufficient for a top journal.

### P2-8. The "DXY" cross-asset evidence uses an unidentified window and frequency

P087-P099 references DXY, USDJPY, small-cap banks, and JPM, but does not specify: (a) the data frequency (30-minute? daily?), (b) the event window (FOMC day only? cumulative over N days?), (c) the sample period, (d) the source (Bloomberg? FRED? CRSP?). For a JPE submission, the data appendix must specify these. The current text reads as if the author has the data but did not bother to document it. **Fix: add a Data Appendix with data sources, frequencies, windows, and sample periods for all cross-asset tests.**

### P2-9. The conclusion (P137-P140) is 4 paragraphs and substantive, but it does not state the *one* finding the reader should remember

A JPE / AER conclusion states the *one* finding the reader should walk away with, in one sentence, in the first paragraph. The current P137 does this: *"We document dovish asymmetry in FOMC statement sentiment: the Fed's language freely amplifies hawkish signals but barely responds to dovish shifts."* This is good. But the reader also has to know that the M4 model is the encompassing specification, and this is buried in §5.7 (P122). The conclusion should also state: *"The direction-interaction model (M4) is the preferred specification by J-test and Diebold-Mariano OOS test; the quadratic model (M2) is presented for interpretability."* This is a P2 because the conclusion is otherwise well-written.

### P2-10. The abstract is too long (one paragraph, ~250 words) and tries to do too much

P004 is a single 250-word paragraph that includes the model, the result, the J-test, the Chow test, and the Diebold-Mariano test. A JFE abstract is typically 100-150 words and focuses on the *result*, not the *method*. **Fix: tighten the abstract to 150 words, lead with the result, and move the model specification to a parenthetical.**

---

## P3 — Minor / Line-edits

- **P3-1**: P052 states: *"the correlation of only 0.47, and 28 meetings have conflicting signs."* Verify: with 131 meetings and a binary conflict indicator, 28/131 = 21%. The text should report the percent (21%), not just the count (28).
- **P3-2**: P087 says *"Calibrating the CB-to-DXY mapping, a +1σ target shock during rate hikes corresponds to −8.7 basis points of DXY appreciation; during rate cuts, the same shock corresponds to +3.7 basis points."* The 2.4:1 ratio is a striking finding; the author should report the test of difference (t-stat of the slope difference, which is the M4 path·direction test).
- **P3-3**: P107: *"The pre-ZLB coefficient remains insignificant (t = 0.37) in the extended sample."* With N=55, the 5% critical value is t ≈ 2.0; the test has 50% power to detect a coefficient half the size of the ZLB+Post estimate. The author should report the minimum detectable effect (MDE) at 80% power, not just acknowledge underpower.
- **P3-4**: P116: *"the (hawkish − dovish) / total_words ratio is a less efficient estimate of the underlying sentiment for short statements."* The statement is true, but the author should note that adding total_words as a control is a *bad control* in the sense that it is a function of the dependent variable's denominator. The author partially addresses this ("the concern that total_words is an over-control is mitigated..."), but the language could be more careful.
- **P3-5**: P130 cites Cieslak (2018) for the "Fed put." The Cieslak (2018) paper in RFS is about *short-rate expectations* and *unexpected returns in Treasury bonds*. The "Fed put" narrative is more closely associated with **Cieslak, A., and A. Schrimpf (2019). "Non-Monetary News in Central Bank Communication." Journal of International Economics, 118, 293-315.** (or the Haddad, Ho, Loualiche, and Plosser 2021 work). The author should either clarify the cite or add Cieslak-Schrimpf to the references.
- **P3-6**: P140: *"the wild bootstrap (p = 0.012) does not reject at the size-corrected threshold."* This number (0.012) is inconsistent with the wild bootstrap p = 0.010 reported in Table 2 and §5.7. Verify which is correct.
- **P3-7**: P130 cites *"Tenreyro and Thwaites (2016) show that monetary policy is less powerful in recessions."* This is the famous "Pushing on a String" paper, *American Economic Review* 106(4), 1014-1036. The reference list entry (P159) is correct.
- **P3-8**: P019: *"The Acosta dataset covers 220 FOMC meetings from February 1995 to July 2022."* The Acosta (2022) replication data actually covers **227 meetings** (verify against the AEA Data Repository). The 220 number may be after some filtering. State the filter.
- **P3-9**: P140: *"the wild bootstrap (p = 0.012)"* — the wild bootstrap p-value for target² is reported as 0.010 in Table 2 and 0.076 in Table 8 (as M2). Verify which is the M2-specific wild bootstrap p-value.
- **P3-10**: P115 says *"Statement length increased dramatically..."* The word "dramatically" is colloquial. Use "substantially" or "by a factor of 5.2" (or whatever the precise ratio is).
- **P3-11**: P123 references "**M1: Linear**" and "**M2: Quadratic**" — verify these are the same models referenced as M1 and M2 in Tables 7 and 8. Currently the paper has *two* model-numbering schemes (one in Table 7, one in Table 8), and they are not obviously the same.
- **P3-12**: P180: *"For an average ZLB+Post statement of 879 words..."* — Table 1 says ZLB+Post mean total words = 880. The 879 vs 880 difference is rounding. Pick one.
- **P3-13**: P150 says *"Eggertsson, G. B., and M. Woodford (2003)."* The paper is in *Brookings Papers on Economic Activity*, 2003(1), 139-211. The reference list entry (P150) does not include the journal name. Add it.
- **P3-14**: P150-178 contains **34 unique references** (the author claims 37, but the dump shows 34 unique + 1 duplicate Gambacorta + 2 "extra" entries that are body text, not refs). Reconcile the count.
- **P3-15**: P144 in the references is the Acosta (2022) *data* citation. Move it to the Data Availability section, and add the Acosta (2022) *paper* citation to the references.
- **P3-16**: P135: *"the Fed's natural tendency to amplify hawkish signals may work against the framework by making it difficult to credibly communicate about future accommodation."* The AIT framework is mentioned only in the conclusion. The introduction should at least mention AIT as a motivation.
- **P3-17**: P162-163 (Gambacorta 2024) — even after deleting the duplicate, the surviving entry is missing the issue number. JME 148 Article 103630 is correct, but adding the month/season is standard (JME 148, October 2024, Article 103630).
- **P3-18**: P132 cites **Bauer and Swanson (2023)** as AER. The published version is *American Economic Review: Papers & Proceedings* 113, or *AER: Insights* — verify the exact outlet. The 2023 Bauer-Swanson paper is in *AER: Insights* 5(4), 469-75.
- **P3-19**: P132 cites **Nakamura and Steinsson (2018)** as QJE. The 2018 paper is in *QJE* 133(3), 1283-1330. Correct.
- **P3-20**: P130 cites **Cieslak (2018)** as "Fed put" but the Cieslak 2018 RFS paper is about *short-rate expectations*, not the "Fed put." Add Cieslak-Schrimpf 2019 (JIE) or Haddad et al. 2021 (JFE) to support the "Fed put" claim.
- **P3-21**: P121 cites **Gambacorta, Iannotta, and Liao (2024)** with "164,622 central bank communications from 169 institutions." Verify the count (the published paper has 26,933 documents from 26 central banks; 164,622 sounds like a different paper — possibly a Bocconi working paper or the CB-LM training data count, but the publication should be cited, not the training data).
- **P3-22**: P121 cites **Chen, Granville, and Matousek (2025)** with "policy-language-induced-shock (PLMIS) measures, finding that LLM-based shocks explain 3× more asset-price variation than dictionary-based measures." Verify the 3× number; the published paper may report a different R² improvement.
- **P3-23**: P124 references an unspecified regression coefficient that does not match any table or equation in the paper. Likely a leftover from a prior draft.
- **P3-24**: P181 (conclusion's "Third, we assess persistence" section) uses an entirely different AR(2) coefficient and half-life from P102 (see P0-3, P0-4). The conclusion is internally inconsistent.
- **P3-25**: P140 (conclusion's "main limitation" section) says *"the wild bootstrap (p = 0.012) does not reject at the size-corrected threshold."* The wild bootstrap p-value for target² in M2 is 0.076 (Table 8). The 0.012 is a different number. Verify.

---

## What the Paper Does Well (in the spirit of fairness)

- **The central finding is intriguing.** The convexity of CB sentiment in target shocks, and its concentration in the ZLB+Post era, is a real empirical regularity that deserves a paper.
- **The inference is careful.** The use of HAC, permutation, and wild bootstrap p-values is appropriate. The size-distortion analysis (§5.3) is exactly what a JPE referee would want.
- **The cross-asset evidence in §4.4 is suggestive.** The opposite curvature of DXY and CB is a non-trivial finding that the author correctly reports.
- **The CB-vs-LM dictionary comparison in §4.3 is genuinely informative.** The author correctly avoids the "one dictionary is right, the other is wrong" framing and instead shows that the two dictionaries measure different aspects of language.
- **The power analysis in §4.2 is honest.** Acknowledging that the pre-ZLB test is underpowered is exactly what a JPE referee would want to see.
- **The J-test and Diebold-Mariano OOS tests in §5.7 are the right way to compare non-nested models.** The M4 model encompassing M2 (J=3.45, p=0.001) and the DM p=0.029 are exactly the statistics a referee would ask for.

---

## Recommendation Summary

**Major revision (borderline reject & resubmit).** The paper has the intellectual core of a top-journal submission, but v15.1 has too many editorial and methodological gaps to be a first submission. The author must address:

1. All eight P0 deal-breakers
2. At least P1-1 (2014-2019 clean ZLB subsample), P1-2 (Bauer-Swanson predictability), P1-12 (Acosta paper vs data citation)
3. Most P2s

I would be willing to review a v16 that addresses the P0s and most P1s. The paper is close to being a serious JFE or RES submission; it is not yet close to AER or QJE.

---

## Specific Suggestions for v16

1. **Reorganize §3-§4 around a single primary specification.** Pick the M4 regime-interaction model as the headline (J-test supports it), present M2 quadratic as a robustness, and delete the §3.1 "Quadratic Interaction Model" title (rename to "Regime-Interaction Model with Quadratic Comparison").
2. **Fix the 240 vs 168 total-words inconsistency.** The 240 number is repeated in four paragraphs; the Table 1 number (168) is correct.
3. **Reconcile the half-life (3.2 vs 8.7 meetings) and cumulative multiplier (5.3× vs 13.0×).** Use the dominant AR(2) root (0.81) to compute both: half-life = ln(0.5)/ln(0.81) ≈ 3.3, cumulative multiplier = 1/(1-0.81) ≈ 5.3 (treating the AR(2) as approximately AR(1) for the long-run effect).
4. **Add the 2014-2019 clean ZLB subsample (N=48) to Table 7.** This is the natural placebo and its absence is a glaring gap.
5. **Implement the Bauer-Swanson predictability test.** It is a one-paragraph addition and a JPE referee will ask for it.
6. **Add Hassan 2019, Tadle 2022, and Eijffinger-Hoeberichts-Schaling 2000 to the references.** These are cited in text but missing.
7. **Delete the duplicate Gambacorta 2024 reference (P163).**
8. **Add the Acosta (2022) paper citation to the references (in addition to the data citation).**
9. **Tighten the abstract to 150 words, lead with the M4 result.**
10. **State the J-test and Diebold-Mariano results in the abstract, not just in §5.7.** The M4 model is the winner; the reader should know this in the first 200 words.

The paper is two months of careful editorial work away from a competitive submission. The intellectual content is there. The packaging is not.

---

*Reviewer comments are confidential. Please do not cite this report without permission.*
