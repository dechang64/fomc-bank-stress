"""
FOMC Dynamic Stress Test Dashboard
===================================
Streamlit app for regime-conditional bank stress testing.
Based on Zhang (2026) — FOMC Communication and Bank Stress.

Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
import os
import sys

# Add dynamic/ to path
sys.path.insert(0, os.path.dirname(__file__))

from regime_detector import RegimeDetector
from scenario_generator import ScenarioGenerator
from htm_risk_module import HTMRiskModule
from shock_compensation import ShockCompensationEngine
from correlation_engine import CorrelationEngine
from cross_border import CrossBorderModule
from reverse_stress_test import ReverseStressTest
from fomc_parser import FOMCParser
from uncertainty_channel import UncertaintyChannel

# ── Page Config ──
st.set_page_config(
    page_title="FOMC Dynamic Stress Test",
    page_icon="🏦",
    layout="wide",
)

# ── Load Config ──
@st.cache_resource
def load_config():
    with open(os.path.join(os.path.dirname(__file__), "config.yaml")) as f:
        return yaml.safe_load(f)

config = load_config()

# ── Initialize Modules ──
@st.cache_resource
def init_modules():
    return {
        "detector": RegimeDetector(),
        "generator": ScenarioGenerator(),
        "htm": HTMRiskModule(),
        "shock": ShockCompensationEngine(),
        "corr": CorrelationEngine(),
        "cross": CrossBorderModule(),
        "reverse": ReverseStressTest(),
        "parser": FOMCParser(),
        "uncertainty": UncertaintyChannel(),
    }

mods = init_modules()

# ── Sidebar ──
st.sidebar.title("🏦 FOMC Stress Test")
st.sidebar.caption("Based on Zhang (2026)")

page = st.sidebar.radio("Navigate", [
    "🏠 Dashboard",
    "💬 Sentiment Analysis",
    "📊 Regime Detector",
    "⚡ Scenario Generator",
    "💰 HTM Risk Module",
    "⚖️ Shock vs Compensation",
    "🔗 Correlation Engine",
    "🌏 Cross-Border",
    "🔄 Reverse Stress Test",
    "🎲 Uncertainty Channel",
    "📝 FOMC Parser",
])

# ── Dashboard ──
if page == "🏠 Dashboard":
    st.title("FOMC Dynamic Stress Test System")
    st.markdown("**Regime-conditional bank stress testing based on FOMC communication**")
    st.markdown("---")

    # Regime overview
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("ZLB Periods", "2", "2008-2015, 2020-2022")
    with col2:
        st.metric("FastHike Period", "1", "2022-2023")
    with col3:
        st.metric("Total FOMC Events", "216", "1994-2025")

    st.markdown("### Key Findings")

    findings = pd.DataFrame({
        "Channel": ["Implementation", "Forward Guidance", "LM% Placebo",
                     "ZLB Structural Break", "OOS Prediction"],
        "Finding": [
            "target×direction: language amplifies hawkish signals (t = 3.73)",
            "path×direction: path shocks matter during rate cuts (t = −2.93)",
            "LM% misses both channels (t = −1.05, −0.98); opposite sign",
            "Chow test F = 14.12, p < 0.001: ZLB-specific",
            "Direction model is only spec with DM p = 0.029",
        ],
        "Key stat": ["t = 3.73***", "t = −2.93***", "R² = 0.020 vs 0.182", "F = 14.12***", "DM p = 0.029**"],
    })
    st.dataframe(findings, use_container_width=True, hide_index=True)

    st.markdown("### Regime-Dependent Sentiment Response")
    st.markdown("""
    | Regime | Target Shock Effect | Path Shock Effect | Economic Magnitude |
    |--------|--------------------|--------------------|---------------------|
    | **Rate Hike** | +0.015/σ (t = 4.72) | −0.003/σ (negligible) | 12.5 net hawkish words → −8.7bp DXY |
    | **Rate Hold** | +0.003/σ (baseline) | +0.003/σ (baseline) | Baseline |
    | **Rate Cut** | −0.006/σ (attenuated) | +0.007/σ (FG channel) | −5.2 net hawkish words → +3.7bp DXY |
    """)

# ── Sentiment Analysis ──
elif page == "💬 Sentiment Analysis":
    st.title("💬 Sentiment Analysis")
    st.markdown("**Regime-Dependent Asymmetry in FOMC Statement Sentiment**")
    st.markdown("*Words Beyond the Rate v15.1 — Direction-Interaction Model*")
    st.markdown("---")

    st.markdown("### Model Specification")
    st.markdown("""
    **CB = α + β₁·target + β₂·path + β₃·direction + β₄·target×direction + β₅·path×direction + ε**

    where direction = +1 (hike), 0 (hold), −1 (cut).
    """)
    st.markdown("- **target×direction** (Implementation Channel): Language amplifies hawkish signals during rate hikes")
    st.markdown("- **path×direction** (Forward Guidance Channel): Path shocks affect language during rate cuts, when FG substitutes for rate changes")

    st.markdown("---")
    st.markdown("### Main Results (ZLB+Post, N = 109)")

    results = pd.DataFrame({
        "Variable": ["target", "path", "direction", "target×direction", "path×direction"],
        "Coefficient": ["0.003", "0.003", "−0.003", "0.012", "−0.006"],
        "HAC t-stat": ["1.14", "0.67", "−0.38", "3.73***", "−2.93***"],
        "Wild bootstrap p": ["—", "—", "—", "0.033", "0.010"],
        "Permutation p": ["—", "—", "—", "<0.001", "0.016"],
    })
    st.dataframe(results, use_container_width=True, hide_index=True)
    st.caption("HAC(4) standard errors. ***, **, * denote 1%, 5%, 10% significance.")

    st.markdown("---")
    st.markdown("### Model Comparison (Davidson-MacKinnon J-test)")

    comparison = pd.DataFrame({
        "Model": ["M1: Linear", "M2: Quadratic", "M3: D_hawk interact", "M4: Direction interact", "M5: Piecewise"],
        "R²": [0.027, 0.072, 0.138, 0.182, 0.138],
        "Adj R²": [0.008, 0.046, 0.113, 0.142, 0.113],
        "Wild bootstrap p": ["—", "0.076", "0.010", "0.033 / 0.010", "—"],
        "OOS DM p": ["—", "0.520", "0.055", "0.029", "0.055"],
        "Passes all?": ["—", "❌", "Marginal", "✅", "Marginal"],
    })
    st.dataframe(comparison, use_container_width=True, hide_index=True)
    st.caption("M4 encompasses M3: J-test ŷ(M4)→M3 t=3.45, p=0.001; reverse t=0.28, p=0.776")

    st.markdown("---")
    st.markdown("### Progressive Controls")

    controls = pd.DataFrame({
        "Specification": ["(1) Baseline", "(2) + FF surprise", "(3) + LM% control",
                          "(4) + Total words", "(5) + All controls"],
        "target×dir t": [3.73, 3.83, 3.75, 2.85, 2.83],
        "path×dir t": [-2.93, -1.85, -2.88, -2.61, -1.91],
        "R²": [0.182, 0.186, 0.182, 0.545, 0.548],
    })
    st.dataframe(controls, use_container_width=True, hide_index=True)
    st.caption("Both interaction terms survive all controls. Total words absorbs variation but target×dir remains significant.")

    st.markdown("---")
    st.markdown("### LM% Placebo")

    placebo = pd.DataFrame({
        "Dependent Variable": ["CB Score V2", "LM% (full dict)"],
        "target×direction t": [3.73, -1.05],
        "path×direction t": [-2.93, -0.98],
        "R²": [0.182, 0.020],
    })
    st.dataframe(placebo, use_container_width=True, hide_index=True)
    st.caption("LM% not only misses both channels—it produces insignificant coefficients with wrong sign. FG channel requires domain-specific dictionary.")

    st.markdown("---")
    st.markdown("### Economic Significance")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Hawkish Amplification", "2.4×", "hike vs cut target response")
    with col2:
        st.metric("CB Innovation Half-life", "3.2 meetings", "~5 months")
    with col3:
        st.metric("DXY Impact (hike)", "−8.7 bp", "per +1σ target shock")

    st.markdown("""
    | Regime | +1σ Target → ΔCB | Net Hawkish Words | DXY Impact |
    |--------|-------------------|-------------------|------------|
    | Rate Hike | +0.014 (72% of σ_CB) | +12.5 words | −8.7 bp |
    | Rate Cut | −0.006 (30% of σ_CB) | −5.2 words | +3.7 bp |
    """)

    st.markdown("---")
    st.markdown("### ZLB Structural Break")
    st.markdown("""
    - **Pre-ZLB** (1995-2008, N=55): No regime-dependent sentiment response
    - **ZLB+Post** (2008-2022, N=109): Both target×direction and path×direction significant
    - **Chow test**: F = 14.12, p < 0.001
    - **Interpretation**: Forward guidance makes path shocks relevant for sentiment
      only in the ZLB era, when the Fed relies on language rather than rate changes.
    """)

# ── Regime Detector ──
elif page == "📊 Regime Detector":
    st.title("📊 Regime Detector")
    st.markdown("Classify any date into a monetary policy regime")

    test_date = st.text_input("Enter date (YYYY-MM-DD)", value="2022-06-15")
    lm_pct = st.slider("LM% (positive word %)", 0.0, 8.0, 2.5, 0.1)

    if st.button("Detect Regime"):
        info = mods["detector"].detect_fomc(test_date, lm_pct)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Regime", info["regime"])
        with col2:
            st.metric("Stance", info["stance"])
        with col3:
            st.metric("Signal Meaning", info["signal_meaning"])

        # Correlation
        corr = mods["detector"].get_regime_correlation(info["regime"], True)
        st.metric("Bank Inter-Correlation (FOMC day)", f"{corr:.2f}")

# ── Scenario Generator ──
elif page == "⚡ Scenario Generator":
    st.title("⚡ Scenario Generator")
    st.markdown("Generate regime-conditional stress test scenarios")

    col1, col2 = st.columns(2)
    with col1:
        regime = st.selectbox("Regime", ["Normalization", "ZLB", "FastHike"])
        stance = st.selectbox("FOMC Stance", ["Dovish", "Hawkish"])
    with col2:
        rate_shock = st.slider("Rate Shock (bps)", 0, 1000, 500, 50)
        nim_ratio = st.slider("NIM Ratio", 0.01, 0.06, 0.03, 0.005)
        htm_ratio = st.slider("HTM Ratio", 0.0, 0.40, 0.15, 0.01)
        cre_intensity = st.slider("CRE Intensity", 0.0, 0.50, 0.25, 0.05)

    if st.button("Generate Scenario"):
        scenario = mods["generator"].generate(
            regime, stance, rate_shock, nim_ratio, htm_ratio, cre_intensity
        )

        st.markdown(f"### Scenario: {scenario.name}")
        st.markdown(f"*{scenario.description}*")

        metrics = pd.DataFrame({
            "Parameter": ["Dovish-Hawkish Spread", "NIM Shock", "HTM Unrealized Loss",
                          "CRE Spread Widening", "Bank Correlation", "CoVaR Multiplier",
                          "P(Loss)"],
            "Value": [f"{scenario.dovish_hawkish_spread_pp:+.2f}pp",
                      f"{scenario.nim_shock_pp:+.3f}pp",
                      f"{scenario.htm_unrealized_loss_pp:+.3f}pp",
                      f"{scenario.cre_spread_widening_bps:+.1f}bps",
                      f"{scenario.bank_correlation:.2f}",
                      f"{scenario.covar_multiplier:.2f}×",
                      f"{scenario.p_loss_pct:.1f}%"],
        })
        st.dataframe(metrics, use_container_width=True, hide_index=True)

    # All scenarios comparison
    st.markdown("---")
    st.markdown("### All Standard Scenarios")
    all_scenarios = mods["generator"].generate_all_scenarios(nim_ratio, htm_ratio, cre_intensity)
    rows = []
    for s in all_scenarios:
        rows.append({
            "Scenario": s.name,
            "Regime": s.regime,
            "Stance": s.stance,
            "Spread (pp)": s.dovish_hawkish_spread_pp,
            "NIM (pp)": s.nim_shock_pp,
            "HTM (pp)": s.htm_unrealized_loss_pp,
            "Correlation": s.bank_correlation,
            "P(Loss)%": s.p_loss_pct,
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── HTM Risk Module ──
elif page == "💰 HTM Risk Module":
    st.title("💰 HTM Risk Module")
    st.markdown("Assess unrealized losses on Held-to-Maturity securities")
    st.markdown("*Based on H9: FastHike×HTM = −0.093 (t = −8.16)*")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Bank Parameters")
        ticker = st.text_input("Ticker", "SVB_PROXY")
        htm_sec = st.number_input("HTM Securities ($B)", value=91.0)
        total_assets = st.number_input("Total Assets ($B)", value=212.0)
        afs_sec = st.number_input("AFS Securities ($B)", value=27.0)
    with col2:
        tier1 = st.number_input("Tier 1 Capital ($B)", value=16.0)
        duration = st.slider("Effective Duration (years)", 1.0, 10.0, 6.0, 0.5)
        rate_shock = st.slider("Rate Shock (bps)", 100, 1000, 500, 50)

    if st.button("Assess HTM Risk"):
        assessment = mods["htm"].assess_bank(
            ticker=ticker,
            htm_securities=htm_sec * 1e9,
            total_assets=total_assets * 1e9,
            afs_securities=afs_sec * 1e9,
            tier1_capital=tier1 * 1e9,
            duration=duration,
            rate_shock_bps=rate_shock,
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("HTM Unrealized Loss", f"${assessment.htm_unrealized_loss/1e9:.1f}B")
        with col2:
            st.metric("Capital Erosion", f"{assessment.capital_erosion_pct:.1f}%")
        with col3:
            color = "🔴" if assessment.risk_level in ["Critical", "High"] else "🟡" if assessment.risk_level == "Medium" else "🟢"
            st.metric("Risk Level", f"{color} {assessment.risk_level}")

        if assessment.breach_threshold:
            st.error(f"⚠️ HTM losses exceed {100 if assessment.risk_level=='Critical' else 50}% of Tier 1 capital!")

    # Sensitivity analysis
    st.markdown("---")
    st.markdown("### HTM Ratio Sensitivity (Panel Regression)")
    htm_ratios = np.arange(0.02, 0.40, 0.02)
    car_impacts = [mods["htm"].panel_regression_impact(r, 500) for r in htm_ratios]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=htm_ratios * 100, y=car_impacts,
        mode='lines+markers',
        name='CAR Impact (FastHike, 500bp)',
        line=dict(color='#e74c3c', width=2),
    ))
    fig.update_layout(
        title="CAR Impact vs HTM Ratio (FastHike × 500bp shock)",
        xaxis_title="HTM Ratio (%)",
        yaxis_title="CAR Impact (pp)",
        template="plotly_white",
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Shock vs Compensation ──
elif page == "⚖️ Shock vs Compensation":
    st.title("⚖️ Shock vs Compensation")
    st.markdown("Dual-sided stress assessment: losses AND compensation effects")

    col1, col2 = st.columns(2)
    with col1:
        regime = st.selectbox("Regime", ["ZLB", "FastHike", "Normalization"], key="sc_regime")
        stance = st.selectbox("Stance", ["Dovish", "Hawkish"], key="sc_stance")
    with col2:
        nim_ratio = st.slider("NIM Ratio", 0.01, 0.06, 0.035, 0.005, key="sc_nim")
        htm_ratio = st.slider("HTM Ratio", 0.0, 0.40, 0.20, 0.01, key="sc_htm")
        cre_intensity = st.slider("CRE Intensity", 0.0, 0.50, 0.35, 0.05, key="sc_cre")

    if st.button("Compute Shock-Compensation"):
        profile = mods["shock"].assess(
            ticker="BANK", regime=regime, stance=stance,
            nim_ratio=nim_ratio, htm_ratio=htm_ratio, cre_intensity=cre_intensity,
        )

        # Bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Shock",
            x=["NIM Compression", "HTM Unrealized Loss", "CRE Deterioration"],
            y=[profile.nim_compression_pp, profile.htm_unrealized_loss_pp, profile.cre_deterioration_pp],
            marker_color='#e74c3c',
        ))
        fig.add_trace(go.Bar(
            name="Compensation",
            x=["QE Trading Income", "Deposit Franchise", "Capital Rebuilding"],
            y=[profile.qe_trading_income_pp, profile.deposit_franchise_value_pp, profile.capital_rebuilding_pp],
            marker_color='#2ecc71',
        ))
        fig.update_layout(
            title=f"Shock vs Compensation: {regime}/{stance}",
            barmode='group',
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Shock", f"{profile.total_shock_pp:.2f}pp")
        with col2:
            st.metric("Total Compensation", f"{profile.total_compensation_pp:.2f}pp")
        with col3:
            st.metric("Net Effect", f"{profile.net_effect_pp:+.2f}pp", delta=profile.net_direction)

# ── Correlation Engine ──
elif page == "🔗 Correlation Engine":
    st.title("🔗 Correlation Engine")
    st.markdown("Regime-conditional bank inter-correlation")
    st.markdown("*ZLB FOMC ρ=0.86 vs Non-ZLB FOMC ρ=0.68*")

    banks = ["JPM", "BAC", "C", "WFC", "GS", "MS", "SCHW", "BK"]

    col1, col2 = st.columns(2)
    with col1:
        regime = st.selectbox("Regime", ["ZLB", "Normalization", "FastHike"], key="ce_regime")
    with col2:
        is_fomc = st.checkbox("FOMC Day", value=True)

    cm = mods["corr"].generate(banks, regime, is_fomc)

    # Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=cm.matrix,
        x=banks, y=banks,
        colorscale="RdBu_r",
        zmin=0.3, zmax=1.0,
        text=np.round(cm.matrix, 2),
        texttemplate="%{text:.2f}",
    ))
    fig.update_layout(
        title=f"Correlation Matrix: {regime} {'FOMC' if is_fomc else 'Non-FOMC'} (base ρ={cm.base_correlation:.2f})",
        template="plotly_white",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.metric("Systemic Risk Index", f"{cm.systemic_risk_index():.1f}/100")

# ── Cross-Border ──
elif page == "🌏 Cross-Border":
    st.title("🌏 Cross-Border Transmission")
    st.markdown("International spillover effects (Japan 57% more sensitive)")

    col1, col2 = st.columns(2)
    with col1:
        regime = st.selectbox("Regime", ["ZLB", "FastHike", "Normalization"], key="cb_regime")
        stance = st.selectbox("Stance", ["Dovish", "Hawkish"], key="cb_stance")
    with col2:
        us_car = st.number_input("US CAR (pp)", value=-1.0)
        usdjpy_move = st.number_input("USDJPY Move (%)", value=2.5)

    impact = mods["cross"].assess(regime, stance, us_car, usdjpy_move)
    score = mods["cross"].systemicty_score(regime, stance)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("US CAR", f"{impact.us_car_pp:+.2f}pp")
    with col2:
        st.metric("Japan CAR", f"{impact.jp_car_pp:+.2f}pp", delta=f"×{impact.japan_multiplier}")
    with col3:
        st.metric("Systemicity Score", f"{score:.0f}/100")

# ── Reverse Stress Test ──
elif page == "🔄 Reverse Stress Test":
    st.title("🔄 Reverse Stress Test")
    st.markdown("Bootstrap-based reverse stress testing")

    col1, col2 = st.columns(2)
    with col1:
        regime = st.selectbox("Regime", ["ZLB", "FastHike", "Normalization"], key="rst_regime")
        stance = st.selectbox("Stance", ["Dovish", "Hawkish"], key="rst_stance")
    with col2:
        years = st.slider("Duration (years)", 1, 10, 7)
        n_sims = st.selectbox("Simulations", [1000, 5000, 10000], index=2)

    if st.button("Run Reverse Stress Test"):
        with st.spinner("Running bootstrap simulation..."):
            result = mods["reverse"].simulate(regime, stance, years, n_sims)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("E[cum CAR]", f"{result.mean_cum_car_pct:+.1f}%")
        with col2:
            st.metric("CVaR(5%)", f"{result.cvar_95_pct:.1f}%")
        with col3:
            st.metric("P(Loss)", f"{result.p_loss_pct:.1f}%")
        with col4:
            st.metric("P(Loss>10%)", f"{result.p_loss_gt10_pct:.1f}%")

        if result.most_vulnerable != "N/A":
            st.warning(f"⚠️ Most vulnerable: {result.most_vulnerable} (P(loss)={result.most_vulnerable_p_loss:.1f}%)")

# ── Uncertainty Channel ──
elif page == "🎲 Uncertainty Channel":
    st.title("🎲 Uncertainty Channel")
    st.markdown("**Delta Disagreement as a Systemic Risk Amplifier**")
    st.markdown("*Based on Inner Confidence (Chen et al. 2025, NBER #34965)*")

    st.markdown("""
    When market participants **disagree** about FOMC signal meaning, uncertainty itself
    becomes an independent stress transmission channel:
    - High disagreement → High volatility → Trading desk losses
    - High disagreement → Banks can't hedge → Forced selling
    - High disagreement → Funding market freeze → Cross-border amplification
    """)

    st.markdown("---")

    # Single event assessment
    st.markdown("### Single Event Assessment")
    col1, col2 = st.columns(2)
    with col1:
        fomc_date = st.text_input("FOMC Date", value="2013-06-19", key="uc_date")
        stance = st.selectbox("Stance", ["Dovish", "Hawkish", "Neutral"], key="uc_stance")
        lm_stance = st.selectbox("LM% Classification", ["Dovish", "Hawkish", "Neutral"], index=0, key="uc_lm")
        llm_stance = st.selectbox("LLM Classification", ["Dovish", "Hawkish", "Neutral"], index=1, key="uc_llm")
    with col2:
        inner_conf = st.slider("Inner Confidence", 0.1, 1.0, 0.55, 0.05, key="uc_conf")
        car_estimate = st.number_input("CAR Point Estimate (pp)", value=-1.0, key="uc_car")
        no_stmt = st.checkbox("No statement released (pre-2002)", key="uc_nostmt")

    if st.button("Assess Uncertainty", key="uc_btn"):
        assessment = mods["uncertainty"].assess(
            fomc_date=fomc_date,
            stance=stance,
            inner_confidence=inner_conf,
            car_point_estimate=car_estimate,
            base_correlation=0.86 if "ZLB" in fomc_date else 0.68,
            lm_stance=lm_stance,
            llm_stance=llm_stance,
            no_statement=no_stmt,
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Inner Confidence", f"{assessment.inner_confidence:.2f}")
        with col2:
            st.metric("Uncertainty Level", assessment.uncertainty_level.value)
        with col3:
            st.metric("Stance Distance", f"{assessment.stance_distance}")
        with col4:
            st.metric("Volatility Multiplier", f"×{assessment.volatility_multiplier:.2f}")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("LM% Stance", assessment.lm_stance)
        with col2:
            st.metric("LLM Stance", assessment.llm_stance)
        with col3:
            st.metric("ρ Adjustment", f"+{assessment.correlation_adjustment:.3f}")
        with col4:
            st.metric("Capital Buffer", f"+{assessment.capital_buffer_surcharge:.1f}%")

        st.markdown(f"**CAR**: {assessment.car_point_estimate:+.4f}pp, "
                    f"90% CI: [{assessment.car_ci_lower:.2f}, {assessment.car_ci_upper:.2f}]pp")

        if assessment.regime_transition_alert:
            st.error("⚠️ REGIME TRANSITION ALERT — Confidence drop exceeds threshold!")

    # Regime transition detection
    st.markdown("---")
    st.markdown("### Regime Transition Detection")
    st.markdown("Track Inner Confidence across consecutive FOMC meetings")

    conf_values = st.text_input(
        "Confidence sequence (comma-separated, oldest first)",
        value="0.90, 0.78, 0.42, 0.65, 0.88, 0.91",
        key="uc_seq"
    )

    if st.button("Detect Transitions", key="uc_trans_btn"):
        confs = [float(x.strip()) for x in conf_values.split(",")]

        rows = []
        for i in range(len(confs)):
            if i == 0:
                rows.append({
                    "Meeting": f"t+{i}",
                    "Confidence": f"{confs[i]:.2f}",
                    "Drop": "N/A",
                    "P(Transition)": "N/A",
                    "Alert": "—",
                })
            else:
                alert, prob = mods["uncertainty"].detect_regime_transition(confs[i], confs[i-1])
                drop = confs[i-1] - confs[i]
                rows.append({
                    "Meeting": f"t+{i}",
                    "Confidence": f"{confs[i]:.2f}",
                    "Drop": f"{drop:.3f}",
                    "P(Transition)": f"{prob:.1%}",
                    "Alert": "⚠️ ALERT" if alert else "OK",
                })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Uncertainty-adjusted correlation
    st.markdown("---")
    st.markdown("### Uncertainty-Adjusted Correlation")
    st.markdown("Higher disagreement → Higher bank inter-correlation → More systemic risk")

    base_rho = st.slider("Base Correlation (ρ)", 0.50, 0.95, 0.68, 0.01, key="uc_rho")
    conf_slider = st.slider("Inner Confidence", 0.1, 1.0, 0.55, 0.05, key="uc_rho_conf")

    adj_rho = mods["uncertainty"].uncertainty_adjusted_correlation(base_rho, conf_slider)
    st.metric("Adjusted ρ", f"{adj_rho:.3f}", delta=f"+{adj_rho - base_rho:.3f}")

    # Comparison table
    st.markdown("---")
    st.markdown("### Uncertainty-Adjusted Stress Test Comparison")

    scenarios = [
        {"name": "ZLB/Dovish (Clear)", "regime": "ZLB", "stance": "Dovish",
         "inner_confidence": 0.92, "car_point_estimate": 0.18, "base_correlation": 0.86},
        {"name": "ZLB/Dovish (Unclear)", "regime": "ZLB", "stance": "Dovish",
         "inner_confidence": 0.55, "car_point_estimate": 0.18, "base_correlation": 0.86},
        {"name": "ZLB/Hawkish (Clear)", "regime": "ZLB", "stance": "Hawkish",
         "inner_confidence": 0.88, "car_point_estimate": -1.00, "base_correlation": 0.86},
        {"name": "ZLB/Hawkish (Unclear)", "regime": "ZLB", "stance": "Hawkish",
         "inner_confidence": 0.45, "car_point_estimate": -1.00, "base_correlation": 0.86},
        {"name": "FastHike/Hawkish (Clear)", "regime": "FastHike", "stance": "Hawkish",
         "inner_confidence": 0.90, "car_point_estimate": -1.50, "base_correlation": 0.78},
        {"name": "FastHike/Hawkish (Unclear)", "regime": "FastHike", "stance": "Hawkish",
         "inner_confidence": 0.50, "car_point_estimate": -1.50, "base_correlation": 0.78},
    ]

    df = mods["uncertainty"].stress_test_with_uncertainty(scenarios)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── FOMC Parser ──
elif page == "📝 FOMC Parser":
    st.title("📝 FOMC Statement Parser")
    st.markdown("Extract LM% sentiment from FOMC statements in real-time")

    statement = st.text_area("Paste FOMC Statement", height=200, value="""The Federal Reserve decided to raise the target range for the federal funds rate by 75 basis points to 1.50-1.75 percent. Inflation remains elevated, reflecting supply and demand imbalances related to the pandemic, higher energy prices, and broader price pressures. The Committee is strongly committed to returning inflation to its 2 percent objective.""")

    if st.button("Parse Statement"):
        result = mods["parser"].parse(statement, "Today")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("LM%", f"{result.lm_pct:.2f}")
        with col2:
            st.metric("Stance", result.stance)
        with col3:
            st.metric("Positive Words", f"{result.n_positive}/{result.n_total}")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Hawkish Words", result.hawkish_count)
        with col2:
            st.metric("Dovish Words", result.dovish_count)

        if result.key_phrases:
            st.markdown("### Key Phrases")
            for phrase in result.key_phrases:
                st.markdown(f"- {phrase}")

# ── Footer ──
st.sidebar.markdown("---")
st.sidebar.markdown("Zhang (2026)")
st.sidebar.markdown("*Regime-Dependent Asymmetry in FOMC Statement Sentiment*")
st.sidebar.markdown("[GitHub](https://github.com/dechang64/fomc-bank-stress)")
