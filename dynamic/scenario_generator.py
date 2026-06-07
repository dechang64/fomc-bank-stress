"""
Scenario Generator — Regime-conditional stress test scenarios.
Generates shock parameters based on current monetary policy regime.
"""
import yaml
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
from regime_detector import RegimeDetector, Regime

import os


@dataclass
class StressScenario:
    """A complete stress test scenario with regime-conditional parameters."""
    name: str
    regime: Regime
    stance: str  # Dovish / Hawkish / Neutral
    rate_shock_bps: float = 0.0
    dovish_hawkish_spread_pp: float = 0.0
    nim_shock_pp: float = 0.0
    htm_unrealized_loss_pp: float = 0.0
    cre_spread_widening_bps: float = 0.0
    bank_correlation: float = 0.68
    covar_multiplier: float = 1.0
    p_loss_pct: float = 0.0
    description: str = ""


class ScenarioGenerator:
    """Generate stress scenarios conditioned on monetary policy regime."""

    def __init__(self, config_path: str = None):
        if config_path:
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            with open(os.path.join(os.path.dirname(__file__), "config.yaml")) as f:
                self.config = yaml.safe_load(f)
        self.detector = RegimeDetector(config_path)

    def generate(self, regime: Regime, stance: str = "Dovish",
                 rate_shock_bps: float = 0.0,
                 nim_ratio: float = 0.0, htm_ratio: float = 0.0,
                 cre_intensity: float = 0.0) -> StressScenario:
        """Generate a regime-conditional stress scenario."""

        ch = self.config["channels"]
        corr = self.config["correlation"]
        cov = self.config["covar"]

        # Base spread
        spread = self.detector.get_regime_spread(regime, stance)

        # NIM channel
        nim_shock = 0.0
        if regime == "ZLB" and stance == "Dovish":
            nim_shock = ch["nim"]["dovish_zlb_nim"] * nim_ratio  # Compensation
        elif regime == "ZLB" and stance == "Hawkish":
            nim_shock = -abs(ch["nim"]["dovish_nim"]) * nim_ratio  # No compensation
        elif regime == "FastHike":
            nim_shock = ch["nim"]["fasthike_nim"] * nim_ratio  # Suffer
        else:
            nim_shock = ch["nim"]["dovish_nim"] * nim_ratio

        # HTM channel
        htm_loss = 0.0
        if regime == "FastHike":
            htm_loss = ch["htm"]["fasthike_htm"] * htm_ratio * (rate_shock_bps / 500)
        elif regime == "ZLB" and stance == "Hawkish":
            # ZLB→Hawkish transition triggers HTM losses
            htm_loss = ch["htm"]["fasthike_htm"] * htm_ratio * (rate_shock_bps / 500) * 0.5

        # CRE channel
        cre_shock = 0.0
        if regime == "ZLB" and stance == "Dovish":
            cre_shock = ch["cre"]["dovish_zlb_cre"] * cre_intensity
        elif regime == "FastHike":
            cre_shock = -abs(ch["cre"]["dovish_cre"]) * cre_intensity

        # Correlation
        is_fomc = True
        bank_corr = self.detector.get_regime_correlation(regime, is_fomc)

        # CoVaR
        covar_mult = cov["zlb_amplification"] if regime == "ZLB" else cov["non_zlb_baseline"]

        # P(loss) from reverse stress test
        p_loss = 0.0
        if regime == "ZLB" and stance == "Hawkish":
            p_loss = self.config["reverse_stress"]["zlb_hawkish_7yr"]["p_loss"]
        elif regime == "ZLB" and stance == "Dovish":
            p_loss = self.config["reverse_stress"]["zlb_dovish_7yr"]["p_loss"]

        # Description
        desc = f"{regime} regime, {stance} FOMC stance"
        if rate_shock_bps > 0:
            desc += f", +{rate_shock_bps}bps rate shock"
        if htm_loss != 0:
            desc += f", HTM unrealized loss: {htm_loss:.2f}pp"

        return StressScenario(
            name=f"{regime}_{stance}_{abs(rate_shock_bps)}bp",
            regime=regime,
            stance=stance,
            rate_shock_bps=rate_shock_bps,
            dovish_hawkish_spread_pp=spread,
            nim_shock_pp=nim_shock,
            htm_unrealized_loss_pp=htm_loss,
            cre_spread_widening_bps=cre_shock * 100,
            bank_correlation=bank_corr,
            covar_multiplier=covar_mult,
            p_loss_pct=p_loss,
            description=desc,
        )

    def generate_all_scenarios(self, nim_ratio: float = 0.03,
                                htm_ratio: float = 0.15,
                                cre_intensity: float = 0.3) -> list[StressScenario]:
        """Generate the full set of standard scenarios."""
        scenarios = []

        # Standard DFAST-style scenarios
        for regime in ["Normalization", "ZLB", "FastHike"]:
            for stance in ["Dovish", "Hawkish"]:
                rate_shock = 0
                if regime == "FastHike":
                    rate_shock = 500
                elif regime == "ZLB" and stance == "Hawkish":
                    rate_shock = 300  # ZLB→Hawkish transition

                s = self.generate(regime, stance, rate_shock,
                                  nim_ratio, htm_ratio, cre_intensity)
                scenarios.append(s)

        # Special: ZLB→Hawkish transition (most dangerous)
        s = self.generate("ZLB", "Hawkish", 300, nim_ratio, htm_ratio, cre_intensity)
        s.name = "ZLB_Hawkish_Transition"
        s.description = "ZLB→Hawkish transition (most dangerous systemic scenario)"
        scenarios.append(s)

        return scenarios


if __name__ == "__main__":
    gen = ScenarioGenerator()

    print("=== Standard Scenarios ===")
    scenarios = gen.generate_all_scenarios()
    for s in scenarios:
        print(f"\n  {s.name}: {s.description}")
        print(f"    Spread: {s.dovish_hawkish_spread_pp:+.2f}pp | NIM: {s.nim_shock_pp:+.3f}pp | HTM: {s.htm_unrealized_loss_pp:+.3f}pp")
        print(f"    Correlation: {s.bank_correlation:.2f} | CoVaR×: {s.covar_multiplier:.2f} | P(loss): {s.p_loss_pct:.1f}%")

    # Custom scenario: SVB-like
    print("\n\n=== SVB-like Scenario (FastHike, Hawkish, high HTM) ===")
    svb = gen.generate("FastHike", "Hawkish", rate_shock_bps=500,
                       nim_ratio=0.025, htm_ratio=0.35, cre_intensity=0.25)
    print(f"  {svb.description}")
    print(f"  HTM unrealized loss: {svb.htm_unrealized_loss_pp:+.3f}pp")
    print(f"  NIM shock: {svb.nim_shock_pp:+.3f}pp")
    print(f"  Bank correlation: {svb.bank_correlation:.2f}")
