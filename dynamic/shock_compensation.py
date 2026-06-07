"""
Shock-Compensation Engine — Dual-sided stress assessment.
Based on H8 (NIM compression channel) and the compensation mechanism.
"""
import yaml
import os
from dataclasses import dataclass
from typing import Literal


@dataclass
class BankShockProfile:
    """Complete shock-compensation profile for a bank."""
    ticker: str
    regime: str
    stance: str

    # Shock side
    nim_compression_pp: float = 0.0
    htm_unrealized_loss_pp: float = 0.0
    cre_deterioration_pp: float = 0.0
    total_shock_pp: float = 0.0

    # Compensation side
    qe_trading_income_pp: float = 0.0
    deposit_franchise_value_pp: float = 0.0
    capital_rebuilding_pp: float = 0.0
    total_compensation_pp: float = 0.0

    # Net
    net_effect_pp: float = 0.0
    net_direction: str = "Neutral"  # Positive / Negative / Neutral


class ShockCompensationEngine:
    """
    Dual shock-compensation framework.
    Unlike traditional stress tests that only measure losses,
    this engine also captures regime-conditional compensation effects.
    """

    def __init__(self, config_path: str = None):
        if config_path:
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            with open(os.path.join(os.path.dirname(__file__), "config.yaml")) as f:
                self.config = yaml.safe_load(f)

    def assess(self, ticker: str, regime: str, stance: str,
               nim_ratio: float, htm_ratio: float, cre_intensity: float,
               trading_ratio: float = 0.05, deposit_ratio: float = 0.7,
               tier1_yoy: float = 0.05) -> BankShockProfile:
        """Compute full shock-compensation profile for a bank."""

        ch = self.config["channels"]
        profile = BankShockProfile(ticker=ticker, regime=regime, stance=stance)

        # ── SHOCK SIDE ──
        # NIM compression
        if regime == "ZLB" and stance == "Dovish":
            # ZLB Dovish: NIM compression is a cost, but compensated by QE
            profile.nim_compression_pp = abs(ch["nim"]["dovish_nim"]) * nim_ratio * 100
        elif regime == "ZLB" and stance == "Hawkish":
            # ZLB Hawkish: NIM compression without compensation
            profile.nim_compression_pp = abs(ch["nim"]["dovish_nim"]) * nim_ratio * 100 * 1.5
        elif regime == "FastHike":
            # FastHike: NIM initially benefits but credit losses follow
            profile.nim_compression_pp = abs(ch["nim"]["fasthike_nim"]) * nim_ratio * 100

        # HTM unrealized loss
        if regime == "FastHike":
            profile.htm_unrealized_loss_pp = abs(ch["htm"]["fasthike_htm"]) * htm_ratio * 100
        elif regime == "ZLB" and stance == "Hawkish":
            # ZLB→Hawkish transition triggers HTM losses
            profile.htm_unrealized_loss_pp = abs(ch["htm"]["fasthike_htm"]) * htm_ratio * 100 * 0.5

        # CRE deterioration
        if regime == "FastHike":
            profile.cre_deterioration_pp = abs(ch["cre"]["dovish_cre"]) * cre_intensity * 100
        elif regime == "ZLB" and stance == "Hawkish":
            profile.cre_deterioration_pp = abs(ch["cre"]["dovish_cre"]) * cre_intensity * 100 * 0.8

        profile.total_shock_pp = (profile.nim_compression_pp +
                                   profile.htm_unrealized_loss_pp +
                                   profile.cre_deterioration_pp)

        # ── COMPENSATION SIDE ──
        if regime == "ZLB" and stance == "Dovish":
            # QE-driven compensation
            profile.qe_trading_income_pp = ch["nim"]["dovish_zlb_nim"] * nim_ratio * 100
            profile.deposit_franchise_value_pp = 0.1 * deposit_ratio  # Low rate = cheap deposits
            profile.capital_rebuilding_pp = 0.05 * max(tier1_yoy, 0)

        elif regime == "ZLB" and stance == "Hawkish":
            # No compensation in ZLB Hawkish
            profile.qe_trading_income_pp = 0.0
            profile.deposit_franchise_value_pp = -0.05 * deposit_ratio  # Deposit outflows
            profile.capital_rebuilding_pp = 0.0

        elif regime == "FastHike":
            # NIM initially benefits from rate hikes
            profile.qe_trading_income_pp = 0.1 * nim_ratio * 100  # Temporary NIM boost
            profile.deposit_franchise_value_pp = -0.1 * deposit_ratio  # Deposit competition
            profile.capital_rebuilding_pp = 0.0

        profile.total_compensation_pp = (profile.qe_trading_income_pp +
                                          profile.deposit_franchise_value_pp +
                                          profile.capital_rebuilding_pp)

        # ── NET EFFECT ──
        profile.net_effect_pp = profile.total_compensation_pp - profile.total_shock_pp
        if profile.net_effect_pp > 0.5:
            profile.net_direction = "Positive"
        elif profile.net_effect_pp < -0.5:
            profile.net_direction = "Negative"
        else:
            profile.net_direction = "Neutral"

        return profile


if __name__ == "__main__":
    engine = ShockCompensationEngine()

    print("=== Shock-Compensation Profiles ===\n")

    # Regional bank (high CRE, high HTM)
    for regime, stance in [("ZLB", "Dovish"), ("ZLB", "Hawkish"), ("FastHike", "Hawkish")]:
        p = engine.assess(
            ticker="REGIONAL",
            regime=regime, stance=stance,
            nim_ratio=0.035, htm_ratio=0.20, cre_intensity=0.35,
            trading_ratio=0.02, deposit_ratio=0.80,
        )
        print(f"  {regime}/{stance}:")
        print(f"    Shock: NIM={p.nim_compression_pp:.2f}pp + HTM={p.htm_unrealized_loss_pp:.2f}pp + CRE={p.cre_deterioration_pp:.2f}pp = {p.total_shock_pp:.2f}pp")
        print(f"    Comp:  QE={p.qe_trading_income_pp:.2f}pp + Dep={p.deposit_franchise_value_pp:.2f}pp + Cap={p.capital_rebuilding_pp:.2f}pp = {p.total_compensation_pp:.2f}pp")
        print(f"    Net: {p.net_effect_pp:+.2f}pp ({p.net_direction})")
        print()

    # GSIB (low CRE, low HTM, high trading)
    print("--- GSIB (JPM-like) ---\n")
    for regime, stance in [("ZLB", "Dovish"), ("FastHike", "Hawkish")]:
        p = engine.assess(
            ticker="GSIB",
            regime=regime, stance=stance,
            nim_ratio=0.025, htm_ratio=0.05, cre_intensity=0.15,
            trading_ratio=0.15, deposit_ratio=0.60,
        )
        print(f"  {regime}/{stance}: Net = {p.net_effect_pp:+.2f}pp ({p.net_direction})")
