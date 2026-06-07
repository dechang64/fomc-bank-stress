"""
Cross-Border Transmission Module — International spillover effects.
Based on H6: Japan effect 57% larger than US effect.
"""
import numpy as np
from dataclasses import dataclass


@dataclass
class CrossBorderImpact:
    """Cross-border impact assessment."""
    source_regime: str
    source_stance: str
    us_car_pp: float
    jp_car_pp: float
    japan_multiplier: float
    dollar_funding_stress: float
    fx_impact_pp: float
    total_international_pp: float


class CrossBorderModule:
    """
    Assess international transmission of FOMC shocks.
    Key finding: Japanese banks are 57% more sensitive to FOMC signals than US banks.
    """

    JAPAN_MULTIPLIER = 1.57

    # USD funding channel parameters
    DOLLAR_FUNDING_BASELINE = 0.15  # pp per FOMC event

    # FX channel: USDJPY sensitivity
    FX_SENSITIVITY = 0.05  # pp per 1% USDJPY move

    def assess(self, regime: str, stance: str,
               us_car_pp: float, usdjpy_move_pct: float = 0.0) -> CrossBorderImpact:
        """Assess cross-border impact of an FOMC event."""

        # Japan direct effect (amplified)
        jp_car_pp = us_car_pp * self.JAPAN_MULTIPLIER

        # Dollar funding channel
        if stance == "Hawkish":
            dollar_stress = self.DOLLAR_FUNDING_BASELINE * 2  # Hawkish = tighter USD
        elif stance == "Dovish":
            dollar_stress = -self.DOLLAR_FUNDING_BASELINE * 0.5  # Dovish = easier USD
        else:
            dollar_stress = 0.0

        # FX channel
        fx_impact = self.FX_SENSITIVITY * usdjpy_move_pct

        # Total international (beyond direct equity effect)
        total_intl = dollar_stress + fx_impact

        return CrossBorderImpact(
            source_regime=regime,
            source_stance=stance,
            us_car_pp=us_car_pp,
            jp_car_pp=round(jp_car_pp, 3),
            japan_multiplier=self.JAPAN_MULTIPLIER,
            dollar_funding_stress=round(dollar_stress, 3),
            fx_impact_pp=round(fx_impact, 3),
            total_international_pp=round(total_intl, 3),
        )

    def systemicty_score(self, regime: str, stance: str) -> float:
        """
        Compute a cross-border systemicity score (0-100).
        Higher = more systemic risk from international transmission.
        """
        score = 0.0

        # Base: regime amplification
        if regime == "ZLB" and stance == "Hawkish":
            score += 60  # Most dangerous
        elif regime == "FastHike":
            score += 50
        elif regime == "ZLB" and stance == "Dovish":
            score += 20  # Low risk
        else:
            score += 30

        # Japan amplification
        score *= self.JAPAN_MULTIPLIER / 1.5  # Normalize

        # Cap at 100
        return min(score, 100.0)


if __name__ == "__main__":
    cb = CrossBorderModule()

    print("=== Cross-Border Impact Assessment ===\n")

    scenarios = [
        ("ZLB", "Dovish", 0.18, -1.0),
        ("ZLB", "Hawkish", -1.00, 2.5),
        ("FastHike", "Hawkish", -1.50, 3.0),
        ("Normalization", "Dovish", -0.82, -0.5),
    ]

    for regime, stance, us_car, fx_move in scenarios:
        impact = cb.assess(regime, stance, us_car, fx_move)
        score = cb.systemicty_score(regime, stance)
        print(f"  {regime}/{stance}:")
        print(f"    US CAR: {impact.us_car_pp:+.2f}pp → JP CAR: {impact.jp_car_pp:+.2f}pp (×{impact.japan_multiplier})")
        print(f"    Dollar funding: {impact.dollar_funding_stress:+.3f}pp | FX: {impact.fx_impact_pp:+.3f}pp")
        print(f"    Systemicity score: {score:.0f}/100")
        print()
