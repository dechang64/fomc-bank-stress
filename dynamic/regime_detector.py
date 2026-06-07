"""
Regime Detector — Identifies current monetary policy regime.
ZLB / Normalization / FastHike based on Fed Funds Rate and FOMC dates.
"""
import os
import yaml
from datetime import datetime, date
from typing import Literal

Regime = Literal["ZLB", "Normalization", "FastHike", "Unknown"]

with open(os.path.join(os.path.dirname(__file__), "config.yaml")) as f:
    CONFIG = yaml.safe_load(f)


class RegimeDetector:
    """Classify any date into a monetary policy regime."""

    def __init__(self, config_path: str = None):
        if config_path:
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = CONFIG

        self.zlb_periods = [
            (self.config["regime"]["zlb_start"], self.config["regime"]["zlb_end"]),
            (self.config["regime"]["zlb2_start"], self.config["regime"]["zlb2_end"]),
        ]
        self.fasthike_period = (
            self.config["regime"]["fasthike_start"],
            self.config["regime"]["fasthike_end"],
        )

    def detect(self, d: date | str) -> Regime:
        """Classify a date into a regime."""
        if isinstance(d, str):
            d = datetime.strptime(d, "%Y-%m-%d").date()
        elif isinstance(d, datetime):
            d = d.date()

        # Check ZLB periods first (they overlap with FastHike start)
        for start, end in self.zlb_periods:
            s = datetime.strptime(start, "%Y-%m-%d").date()
            e = datetime.strptime(end, "%Y-%m-%d").date()
            if s <= d <= e:
                return "ZLB"

        # Check FastHike
        fs = datetime.strptime(self.fasthike_period[0], "%Y-%m-%d").date()
        fe = datetime.strptime(self.fasthike_period[1], "%Y-%m-%d").date()
        if fs <= d <= fe:
            return "FastHike"

        return "Normalization"

    def detect_fomc(self, fomc_date: date | str, lm_pct: float) -> dict:
        """Full regime + signal classification for an FOMC meeting."""
        regime = self.detect(fomc_date)
        is_dovish = lm_pct > 3.5  # median LM% threshold
        is_hawkish = lm_pct < 1.5

        # Signal meaning depends on regime
        if regime == "ZLB":
            signal_meaning = "liquidity" if is_dovish else "distress"
        else:
            signal_meaning = "distress" if is_dovish else "accommodation"

        return {
            "date": str(fomc_date),
            "regime": regime,
            "lm_pct": lm_pct,
            "stance": "Dovish" if is_dovish else "Hawkish" if is_hawkish else "Neutral",
            "signal_meaning": signal_meaning,
        }

    def get_regime_correlation(self, regime: Regime, is_fomc_day: bool = True) -> float:
        """Get bank inter-correlation for a given regime."""
        corr = self.config["correlation"]
        if is_fomc_day:
            return corr["zlb_fomc"] if regime == "ZLB" else corr["non_zlb_fomc"]
        else:
            return corr["zlb_nonfomc"] if regime == "ZLB" else corr["non_zlb_nonfomc"]

    def get_regime_spread(self, regime: Regime, stance: str) -> float:
        """Get expected dovish-hawkish spread for a regime × stance."""
        sig = self.config["fomc_signals"]
        if stance == "Dovish":
            return sig["dovish_spread"]["zlb"] if regime == "ZLB" else sig["dovish_spread"]["non_zlb"]
        elif stance == "Hawkish":
            return sig["hawkish_spread"]["zlb"] if regime == "ZLB" else sig["hawkish_spread"]["non_zlb"]
        return 0.0


if __name__ == "__main__":
    det = RegimeDetector()

    # Test key dates
    test_dates = [
        ("2013-06-19", "Taper Tantrum"),
        ("2020-03-15", "COVID Emergency Cut"),
        ("2022-06-15", "75bp Hike"),
        ("2024-12-11", "Recent Normalization"),
        ("2010-11-03", "QE2 Announcement"),
    ]

    print("=== Regime Detection ===")
    for d, label in test_dates:
        regime = det.detect(d)
        print(f"  {d} ({label}): {regime}")

    # Test FOMC signal interpretation
    print("\n=== Signal Interpretation ===")
    for d, lm, label in [
        ("2010-11-03", 5.2, "QE2 (ZLB, Dovish)"),
        ("2022-06-15", 0.5, "75bp Hike (FastHike, Hawkish)"),
        ("2006-06-29", 1.0, "Pre-crisis (Normal, Hawkish)"),
    ]:
        info = det.detect_fomc(d, lm)
        print(f"  {label}: regime={info['regime']}, stance={info['stance']}, meaning={info['signal_meaning']}")
