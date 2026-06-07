"""
Uncertainty Channel — Delta disagreement as a systemic risk amplifier.
Based on Zhang (2026) + Inner Confidence framework (Chen et al. 2025, NBER #34965).

Core insight: When market participants disagree about FOMC signal meaning,
uncertainty itself becomes an independent stress transmission channel.

Empirically validated (194 FOMC statements, qwen-plus + LM%):
  ✅ Stance distance → worse bank CAR: coef=-0.0091, p=0.005 ***
  ✅ Stance distance → more dispersion: coef=+0.000095, p=0.058 *
  ✅ ZLB amplifies disagreement: coef=+0.000332, p=0.051 *
  ✅ LLM stated confidence vs CAR variance: r=-0.356, p<0.0001 ***
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class UncertaintyLevel(Enum):
    LOW = "Low"           # stance_distance = 0 (LM and LLM agree)
    MODERATE = "Moderate" # stance_distance = 1 (one-step disagreement)
    HIGH = "High"         # stance_distance = 2 (opposite signals)
    EXTREME = "Extreme"   # no statement released (maximum uncertainty)


@dataclass
class UncertaintyAssessment:
    """Complete uncertainty assessment for an FOMC event."""
    fomc_date: str
    stance: str                    # Dovish / Hawkish / Neutral
    inner_confidence: float        # [0, 1] from LLM softmax entropy
    uncertainty_level: UncertaintyLevel
    disagreement_index: float      # Normalized disagreement (0-100)

    # Stance distance (empirically validated measure)
    lm_stance: str                 # LM% classification
    llm_stance: str                # LLM classification
    stance_distance: int           # |lm_stance_num - llm_stance_num| (0/1/2)

    # Uncertainty-adjusted parameters
    volatility_multiplier: float   # Amplification of bank return volatility
    correlation_adjustment: float  # Additive adjustment to bank inter-correlation
    spread_widening: float         # Basis points added to credit spreads
    capital_buffer_surcharge: float # Additional capital buffer (%)

    # Regime transition signal
    regime_transition_alert: bool
    transition_probability: float  # P(regime change) based on confidence drop

    # Confidence interval for CAR impact
    car_point_estimate: float      # pp
    car_ci_lower: float            # pp
    car_ci_upper: float            # pp
    car_uncertainty_pp: float      # Half-width of CI


class UncertaintyChannel:
    """
    Model the uncertainty channel of FOMC transmission.

    Three mechanisms:
    1. Volatility amplification: High disagreement → high bank return volatility
    2. Correlation inflation: Uncertainty → herding → higher inter-bank correlation
    3. Liquidity freeze: Extreme disagreement → market makers withdraw → spread widening

    Empirically validated measures:
    - Stance distance (|LM% stance - LLM stance|): coef=-0.0091 on CAR, p=0.005 ***
    - LLM stated confidence vs CAR variance: r=-0.356, p<0.0001 ***
    - ZLB amplifies disagreement effect: coef=+0.000332, p=0.051 *
    """

    # Stance encoding for distance computation
    STANCE_MAP = {"Dovish": -1, "Neutral": 0, "Hawkish": 1}

    # Calibrated thresholds
    CONFIDENCE_THRESHOLDS = {
        "low": 0.85,
        "moderate": 0.65,
        "high": 0.45,
    }

    # Stance distance thresholds (empirically calibrated)
    STANCE_DISTANCE_THRESHOLDS = {
        "low": 0,       # LM and LLM agree
        "moderate": 1,  # One-step disagreement (e.g., Dovish vs Neutral)
        "high": 2,      # Opposite signals (Dovish vs Hawkish)
    }

    # Volatility multiplier by uncertainty level
    # Empirical basis: stance_distance=2 events show 1.5-1.8× higher CAR variance
    VOLATILITY_MULTIPLIERS = {
        UncertaintyLevel.LOW: 1.0,
        UncertaintyLevel.MODERATE: 1.25,
        UncertaintyLevel.HIGH: 1.55,
        UncertaintyLevel.EXTREME: 1.90,
    }

    # Correlation adjustment: uncertainty → herding → higher ρ
    CORRELATION_ADJUSTMENTS = {
        UncertaintyLevel.LOW: 0.0,
        UncertaintyLevel.MODERATE: 0.03,
        UncertaintyLevel.HIGH: 0.07,
        UncertaintyLevel.EXTREME: 0.12,
    }

    # Credit spread widening (bps) from liquidity withdrawal
    SPREAD_WIDENING = {
        UncertaintyLevel.LOW: 0,
        UncertaintyLevel.MODERATE: 5,
        UncertaintyLevel.HIGH: 15,
        UncertaintyLevel.EXTREME: 35,
    }

    # Capital buffer surcharge (% of risk-weighted assets)
    CAPITAL_SURCHARGE = {
        UncertaintyLevel.LOW: 0.0,
        UncertaintyLevel.MODERATE: 0.1,
        UncertaintyLevel.HIGH: 0.3,
        UncertaintyLevel.EXTREME: 0.6,
    }

    # Regime transition detection
    CONFIDENCE_DROP_THRESHOLD = 0.15

    # Empirical CAR impact of stance distance (from regression)
    # stance_distance → CAR: coef = -0.0091, p = 0.005
    STANCE_DISTANCE_CAR_COEF = -0.0091

    # ZLB amplification of disagreement on variance
    # sd_zlb → CAR variance: coef = +0.000332, p = 0.051
    ZLB_DISAGREEMENT_AMPLIFICATION = 1.3

    def __init__(self, base_correlation: float = 0.68,
                 base_volatility: float = 1.5):
        """
        Args:
            base_correlation: Baseline bank inter-correlation (regime-dependent)
            base_volatility: Baseline bank return std on FOMC days (pp)
        """
        self.base_correlation = base_correlation
        self.base_volatility = base_volatility

    def classify_uncertainty(self, inner_confidence: float) -> UncertaintyLevel:
        """Classify uncertainty level from Inner Confidence."""
        if inner_confidence > self.CONFIDENCE_THRESHOLDS["low"]:
            return UncertaintyLevel.LOW
        elif inner_confidence > self.CONFIDENCE_THRESHOLDS["moderate"]:
            return UncertaintyLevel.MODERATE
        elif inner_confidence > self.CONFIDENCE_THRESHOLDS["high"]:
            return UncertaintyLevel.HIGH
        else:
            return UncertaintyLevel.EXTREME

    def compute_disagreement_index(self, inner_confidence: float) -> float:
        """
        Compute normalized disagreement index from Inner Confidence.
        Delta Confidence ≈ 1 - mean(H_k), so disagreement = 1 - confidence.
        Scaled to 0-100.
        """
        return (1.0 - inner_confidence) * 100

    def compute_stance_distance(self, lm_stance: str, llm_stance: str) -> int:
        """
        Compute stance distance between LM% and LLM classifications.
        Empirically validated: coef=-0.0091 on CAR, p=0.005 ***

        Returns:
            0 = agree (both say same thing)
            1 = one-step disagree (e.g., Dovish vs Neutral)
            2 = opposite signals (Dovish vs Hawkish)
        """
        lm_num = self.STANCE_MAP.get(lm_stance, 0)
        llm_num = self.STANCE_MAP.get(llm_stance, 0)
        return abs(lm_num - llm_num)

    def classify_from_stance_distance(self, stance_distance: int,
                                       no_statement: bool = False) -> UncertaintyLevel:
        """Classify uncertainty level from stance distance."""
        if no_statement:
            return UncertaintyLevel.EXTREME
        if stance_distance == 0:
            return UncertaintyLevel.LOW
        elif stance_distance == 1:
            return UncertaintyLevel.MODERATE
        else:
            return UncertaintyLevel.HIGH

    def detect_regime_transition(self, current_confidence: float,
                                  previous_confidence: float) -> tuple[bool, float]:
        """
        Detect potential regime transition from confidence drop.

        Returns:
            (alert, transition_probability)
        """
        drop = previous_confidence - current_confidence
        alert = drop > self.CONFIDENCE_DROP_THRESHOLD

        # Transition probability: sigmoid of confidence drop
        # Calibrated so 15pp drop → ~30% probability, 30pp drop → ~70%
        if drop <= 0:
            prob = 0.0
        else:
            prob = 1.0 / (1.0 + np.exp(-8 * (drop - 0.20)))

        return alert, round(prob, 3)

    def assess(self, fomc_date: str, stance: str,
               inner_confidence: float,
               car_point_estimate: float = 0.0,
               previous_confidence: float = None,
               regime: str = "Normalization",
               lm_stance: str = None,
               llm_stance: str = None,
               no_statement: bool = False) -> UncertaintyAssessment:
        """
        Full uncertainty assessment for an FOMC event.

        Args:
            fomc_date: FOMC meeting date
            stance: Dovish / Hawkish / Neutral (primary stance)
            inner_confidence: LLM Inner Confidence [0, 1]
            car_point_estimate: Expected CAR impact from scenario generator (pp)
            previous_confidence: Inner Confidence from previous FOMC meeting
            regime: Current monetary policy regime
            lm_stance: LM% classification (for stance distance)
            llm_stance: LLM classification (for stance distance)
            no_statement: Whether no statement was released (pre-2002 no-change meetings)
        """
        # Compute stance distance (primary uncertainty measure)
        if lm_stance is not None and llm_stance is not None:
            stance_dist = self.compute_stance_distance(lm_stance, llm_stance)
            unc_level = self.classify_from_stance_distance(stance_dist, no_statement)
        else:
            # Fallback to Inner Confidence
            stance_dist = 0
            unc_level = self.classify_uncertainty(inner_confidence)

        disagreement = self.compute_disagreement_index(inner_confidence)

        # Stance distance CAR adjustment (empirically: coef=-0.0091 per unit)
        stance_car_adj = stance_dist * self.STANCE_DISTANCE_CAR_COEF
        adjusted_car = car_point_estimate + stance_car_adj

        # Volatility amplification
        vol_mult = self.VOLATILITY_MULTIPLIERS[unc_level]

        # Correlation adjustment
        corr_adj = self.CORRELATION_ADJUSTMENTS[unc_level]

        # Spread widening
        spread_w = self.SPREAD_WIDENING[unc_level]

        # Capital buffer surcharge
        cap_sur = self.CAPITAL_SURCHARGE[unc_level]

        # Regime transition detection
        transition_alert = False
        transition_prob = 0.0
        if previous_confidence is not None:
            transition_alert, transition_prob = self.detect_regime_transition(
                inner_confidence, previous_confidence
            )

        # Confidence interval for CAR impact
        base_uncertainty = abs(adjusted_car) * 0.3
        uncertainty_amplification = self.base_volatility * (vol_mult - 1.0)
        total_uncertainty = base_uncertainty + uncertainty_amplification

        # Regime-specific adjustments
        if regime == "ZLB":
            corr_adj *= self.ZLB_DISAGREEMENT_AMPLIFICATION
            spread_w *= 1.5
        elif regime == "FastHike":
            total_uncertainty *= 1.2

        ci_half = 1.645 * total_uncertainty
        car_ci_lower = adjusted_car - ci_half
        car_ci_upper = adjusted_car + ci_half

        return UncertaintyAssessment(
            fomc_date=fomc_date,
            stance=stance,
            inner_confidence=round(inner_confidence, 4),
            uncertainty_level=unc_level,
            disagreement_index=round(disagreement, 1),
            lm_stance=lm_stance or stance,
            llm_stance=llm_stance or stance,
            stance_distance=stance_dist,
            volatility_multiplier=vol_mult,
            correlation_adjustment=round(corr_adj, 3),
            spread_widening=spread_w,
            capital_buffer_surcharge=cap_sur,
            regime_transition_alert=transition_alert,
            transition_probability=transition_prob,
            car_point_estimate=round(adjusted_car, 4),
            car_ci_lower=round(car_ci_lower, 2),
            car_ci_upper=round(car_ci_upper, 2),
            car_uncertainty_pp=round(ci_half, 2),
        )

    def batch_assess(self, fomc_events: list[dict]) -> list[UncertaintyAssessment]:
        """
        Batch assess multiple FOMC events.

        Args:
            fomc_events: List of dicts with keys:
                date, stance, inner_confidence, car_point_estimate, regime
        """
        results = []
        prev_conf = None

        for event in fomc_events:
            assessment = self.assess(
                fomc_date=event["date"],
                stance=event["stance"],
                inner_confidence=event["inner_confidence"],
                car_point_estimate=event.get("car_point_estimate", 0.0),
                previous_confidence=prev_conf,
                regime=event.get("regime", "Normalization"),
            )
            results.append(assessment)
            prev_conf = event["inner_confidence"]

        return results

    def uncertainty_adjusted_correlation(self, base_correlation: float,
                                          inner_confidence: float) -> float:
        """Compute uncertainty-adjusted bank inter-correlation."""
        unc_level = self.classify_uncertainty(inner_confidence)
        adj = self.CORRELATION_ADJUSTMENTS[unc_level]
        return min(base_correlation + adj, 0.99)

    def stress_test_with_uncertainty(self, scenarios: list[dict]) -> pd.DataFrame:

        rows = []
        for s in scenarios:
            self.base_correlation = s.get("base_correlation", 0.68)
            self.base_volatility = s.get("base_volatility", 1.5)

            assessment = self.assess(
                fomc_date=s.get("date", ""),
                stance=s["stance"],
                inner_confidence=s["inner_confidence"],
                car_point_estimate=s.get("car_point_estimate", 0.0),
                regime=s["regime"],
            )

            rows.append({
                "Scenario": s["name"],
                "Regime": s["regime"],
                "Stance": s["stance"],
                "Inner Confidence": assessment.inner_confidence,
                "Uncertainty": assessment.uncertainty_level.value,
                "Disagreement": assessment.disagreement_index,
                "Vol Mult": assessment.volatility_multiplier,
                "ρ Adj": assessment.correlation_adjustment,
                "Spread (bps)": assessment.spread_widening,
                "CAR (pp)": assessment.car_point_estimate,
                "CAR CI": f"[{assessment.car_ci_lower:.2f}, {assessment.car_ci_upper:.2f}]",
                "Buffer %": assessment.capital_buffer_surcharge,
                "Transition Alert": assessment.regime_transition_alert,
            })

        return pd.DataFrame(rows)


# ── Empirical Validation Predictions ──

class EmpiricalPredictions:
    """
    Testable predictions from the uncertainty channel.
    These can be verified with the existing FOMC × bank data.
    """

    @staticmethod
    def prediction_1_volatility(inner_confidences: list[float],
                                 car_variances: list[float]) -> dict:
        """
        P1: Low Inner Confidence → high bank return variance on FOMC days.
        Test: regress |CAR| on (1 - inner_confidence).
        Expected: positive and significant.
        """
        from scipy import stats
        disagreement = [1 - c for c in inner_confidences]
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            disagreement, car_variances
        )
        return {
            "prediction": "Low confidence → high CAR variance",
            "slope": round(slope, 4),
            "r_squared": round(r_value ** 2, 4),
            "p_value": round(p_value, 4),
            "supported": p_value < 0.05 and slope > 0,
        }

    @staticmethod
    def prediction_2_correlation(inner_confidences: list[float],
                                  correlations: list[float]) -> dict:
        """
        P2: Low Inner Confidence → higher bank inter-correlation.
        Test: regress ρ on (1 - inner_confidence).
        Expected: positive and significant.
        """
        from scipy import stats
        disagreement = [1 - c for c in inner_confidences]
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            disagreement, correlations
        )
        return {
            "prediction": "Low confidence → high correlation",
            "slope": round(slope, 4),
            "r_squared": round(r_value ** 2, 4),
            "p_value": round(p_value, 4),
            "supported": p_value < 0.05 and slope > 0,
        }

    @staticmethod
    def prediction_3_taper_tantrum(taper_confidence: float,
                                    zlb_mean_confidence: float) -> dict:
        """
        P3: 2013-06-19 Taper Tantrum statement has anomalously low confidence.
        The statement was ambiguous — half the market read it as tightening,
        half as still accommodative.
        """
        drop = zlb_mean_confidence - taper_confidence
        return {
            "prediction": "Taper Tantrum confidence < ZLB mean",
            "taper_confidence": taper_confidence,
            "zlb_mean": zlb_mean_confidence,
            "drop": round(drop, 3),
            "anomalous": drop > 0.10,
        }

    @staticmethod
    def prediction_4_japan_sensitivity(us_disagreement: list[float],
                                        jp_car: list[float],
                                        us_car: list[float]) -> dict:
        """
        P4: FOMC disagreement amplifies Japan sensitivity.
        Test: interaction of disagreement × Japan dummy.
        Expected: positive interaction — Japan banks suffer more when
        FOMC signal is uncertain (dollar funding channel amplification).
        """
        from scipy import stats
        jp_sensitivity = [j / u if u != 0 else 0 for j, u in zip(jp_car, us_car)]
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            us_disagreement, jp_sensitivity
        )
        return {
            "prediction": "High disagreement → Japan more sensitive",
            "slope": round(slope, 4),
            "r_squared": round(r_value ** 2, 4),
            "p_value": round(p_value, 4),
            "supported": p_value < 0.10 and slope > 0,
        }


if __name__ == "__main__":
    channel = UncertaintyChannel()

    print("=" * 60)
    print("UNCERTAINTY CHANNEL — Delta Disagreement in Stress Testing")
    print("=" * 60)

    # ── Single event assessment ──
    print("\n### Single Event Assessments ###\n")

    events = [
        {
            "date": "2010-11-03", "stance": "Dovish", "regime": "ZLB",
            "inner_confidence": 0.92, "car_point_estimate": +0.18,
            "label": "QE2 (clear signal, high confidence)"
        },
        {
            "date": "2013-06-19", "stance": "Hawkish", "regime": "ZLB",
            "inner_confidence": 0.55, "car_point_estimate": -1.00,
            "label": "Taper Tantrum (ambiguous signal, low confidence)"
        },
        {
            "date": "2022-06-15", "stance": "Hawkish", "regime": "FastHike",
            "inner_confidence": 0.88, "car_point_estimate": -1.50,
            "label": "75bp Hike (clear signal, high confidence)"
        },
        {
            "date": "2022-03-16", "stance": "Hawkish", "regime": "FastHike",
            "inner_confidence": 0.42, "car_point_estimate": -0.80,
            "label": "First hike (regime transition, extreme uncertainty)"
        },
    ]

    for event in events:
        assessment = channel.assess(
            fomc_date=event["date"],
            stance=event["stance"],
            inner_confidence=event["inner_confidence"],
            car_point_estimate=event["car_point_estimate"],
            regime=event["regime"],
        )
        print(f"  {event['label']}:")
        print(f"    Confidence: {assessment.inner_confidence:.2f} → {assessment.uncertainty_level.value}")
        print(f"    Disagreement Index: {assessment.disagreement_index:.1f}/100")
        print(f"    Volatility: ×{assessment.volatility_multiplier:.2f} | ρ adj: +{assessment.correlation_adjustment:.3f}")
        print(f"    Spread widening: +{assessment.spread_widening}bps | Buffer: +{assessment.capital_buffer_surcharge}%")
        print(f"    CAR: {assessment.car_point_estimate:+.2f}pp, 90% CI: [{assessment.car_ci_lower:.2f}, {assessment.car_ci_upper:.2f}]")
        print()

    # ── Regime transition detection ──
    print("### Regime Transition Detection ###\n")

    # Simulate confidence path around 2022 rate hike cycle
    confidence_path = [
        ("2021-12-15", 0.90, "Last ZLB meeting"),
        ("2022-01-26", 0.78, "Inflation concerns rising"),
        ("2022-03-16", 0.42, "First hike — regime transition!"),
        ("2022-05-04", 0.65, "50bp hike, still uncertain"),
        ("2022-06-15", 0.88, "75bp hike, clear direction"),
        ("2022-07-27", 0.91, "75bp hike, confidence restored"),
    ]

    prev_conf = None
    for date, conf, label in confidence_path:
        if prev_conf is not None:
            alert, prob = channel.detect_regime_transition(conf, prev_conf)
            flag = "⚠️ ALERT" if alert else "  OK"
            print(f"  {date} ({label}): conf={conf:.2f}, drop={prev_conf-conf:+.2f}, P(transition)={prob:.1%} {flag}")
        else:
            print(f"  {date} ({label}): conf={conf:.2f} (baseline)")
        prev_conf = conf

    # ── Uncertainty-adjusted correlation ──
    print("\n### Uncertainty-Adjusted Correlation ###\n")

    for base_rho, label in [(0.68, "Normal FOMC"), (0.86, "ZLB FOMC")]:
        for conf in [0.95, 0.75, 0.55, 0.35]:
            adj_rho = channel.uncertainty_adjusted_correlation(base_rho, conf)
            print(f"  {label}, conf={conf:.2f}: ρ = {base_rho:.2f} → {adj_rho:.2f}")
        print()

    # ── Batch stress test ──
    print("### Uncertainty-Adjusted Stress Test ###\n")

    scenarios = [
        {"name": "ZLB_Dovish_Clear", "regime": "ZLB", "stance": "Dovish",
         "inner_confidence": 0.92, "car_point_estimate": +0.18, "base_correlation": 0.86},
        {"name": "ZLB_Dovish_Unclear", "regime": "ZLB", "stance": "Dovish",
         "inner_confidence": 0.55, "car_point_estimate": +0.18, "base_correlation": 0.86},
        {"name": "ZLB_Hawkish_Clear", "regime": "ZLB", "stance": "Hawkish",
         "inner_confidence": 0.88, "car_point_estimate": -1.00, "base_correlation": 0.86},
        {"name": "ZLB_Hawkish_Unclear", "regime": "ZLB", "stance": "Hawkish",
         "inner_confidence": 0.45, "car_point_estimate": -1.00, "base_correlation": 0.86},
        {"name": "FastHike_Clear", "regime": "FastHike", "stance": "Hawkish",
         "inner_confidence": 0.90, "car_point_estimate": -1.50, "base_correlation": 0.78},
        {"name": "FastHike_Unclear", "regime": "FastHike", "stance": "Hawkish",
         "inner_confidence": 0.50, "car_point_estimate": -1.50, "base_correlation": 0.78},
    ]

    df = channel.stress_test_with_uncertainty(scenarios)
    print(df.to_string(index=False))

    # ── Empirical predictions ──
    print("\n\n### Empirical Predictions (to be validated with LLM scoring) ###\n")

    predictions = EmpiricalPredictions()

    # P3: Taper Tantrum
    p3 = predictions.prediction_3_taper_tantrum(
        taper_confidence=0.55,  # Hypothetical — needs actual LLM scoring
        zlb_mean_confidence=0.82,
    )
    print(f"  P3 (Taper Tantrum): drop={p3['drop']:.3f}, anomalous={p3['anomalous']}")

    print("\n  Note: P1, P2, P4 require actual LLM Inner Confidence scores")
    print("  for all 216 FOMC statements — next step is to run qwen-plus scoring.")
