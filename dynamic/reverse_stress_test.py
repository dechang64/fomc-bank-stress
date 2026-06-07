"""
Reverse Stress Test — Bootstrap-based reverse stress testing.
Based on §7 of Zhang (2026): CVaR and scenario analysis.
"""
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class ReverseStressResult:
    """Result of a reverse stress test scenario."""
    scenario_name: str
    regime: str
    stance: str
    duration_years: int
    n_simulations: int

    # Distribution statistics
    mean_cum_car_pct: float
    std_cum_car_pct: float
    cvar_95_pct: float
    p_loss_pct: float
    p_loss_gt10_pct: float

    # Most vulnerable bank
    most_vulnerable: str
    most_vulnerable_p_loss: float

    # Confidence interval
    ci_5_pct: float
    ci_95_pct: float


class ReverseStressTest:
    """
    Reverse stress test using bootstrap simulation.
    Calibrated to empirical FOMC-event CAR distributions.
    """

    # Empirical parameters from paper
    REGIME_PARAMS = {
        "ZLB_Dovish": {"mean": 0.18, "std": 1.2, "n_events": 49},
        "ZLB_Hawkish": {"mean": -1.00, "std": 1.8, "n_events": 49},
        "Normal_Dovish": {"mean": -0.82, "std": 1.5, "n_events": 76},
        "Normal_Hawkish": {"mean": 0.30, "std": 1.3, "n_events": 76},
        "FastHike_Hawkish": {"mean": -1.50, "std": 2.0, "n_events": 11},
    }

    # Bank-specific vulnerability (from paper Table)
    BANK_VULNERABILITY = {
        "C": 0.579,     # Citi: 57.9% P(loss) in ZLB Hawkish
        "BK": 0.595,    # Bank of NY Mellon: 59.5%
        "SCHW": 0.52,   # Schwab
        "KEY": 0.48,    # KeyCorp
        "CFG": 0.45,    # Citizens Financial
        "JPM": 0.15,    # JPMorgan: low vulnerability
        "GS": 0.12,     # Goldman: low vulnerability
    }

    def simulate(self, regime: str, stance: str, duration_years: int = 7,
                 n_simulations: int = 10000, seed: int = 42) -> ReverseStressResult:
        """Run bootstrap reverse stress test."""

        np.random.seed(seed)

        key = f"{regime}_{stance}"
        if key == "Normalization_Dovish":
            key = "Normal_Dovish"
        elif key == "Normalization_Hawkish":
            key = "Normal_Hawkish"

        params = self.REGIME_PARAMS.get(key, {"mean": 0.0, "std": 1.5, "n_events": 50})

        # Number of FOMC events per year (~8)
        events_per_year = 8
        total_events = events_per_year * duration_years

        # Simulate cumulative CAR paths
        cum_cars = np.zeros(n_simulations)
        for i in range(n_simulations):
            # Each event: draw from regime-conditional distribution
            event_cars = np.random.normal(params["mean"], params["std"], total_events)
            cum_cars[i] = np.sum(event_cars)

        # Statistics
        mean_cum = np.mean(cum_cars)
        std_cum = np.std(cum_cars, ddof=1)
        cvar_95 = np.percentile(cum_cars, 5)
        p_loss = np.mean(cum_cars < 0) * 100
        p_loss_gt10 = np.mean(cum_cars < -10) * 100
        ci_5 = np.percentile(cum_cars, 5)
        ci_95 = np.percentile(cum_cars, 95)

        # Most vulnerable bank
        if regime == "ZLB" and stance == "Hawkish":
            vuln_bank = max(self.BANK_VULNERABILITY, key=self.BANK_VULNERABILITY.get)
            vuln_p_loss = self.BANK_VULNERABILITY[vuln_bank] * 100
        else:
            vuln_bank = "N/A"
            vuln_p_loss = 0.0

        return ReverseStressResult(
            scenario_name=f"{regime}_{stance}_{duration_years}yr",
            regime=regime,
            stance=stance,
            duration_years=duration_years,
            n_simulations=n_simulations,
            mean_cum_car_pct=round(mean_cum, 1),
            std_cum_car_pct=round(std_cum, 1),
            cvar_95_pct=round(cvar_95, 1),
            p_loss_pct=round(p_loss, 1),
            p_loss_gt10_pct=round(p_loss_gt10, 1),
            most_vulnerable=vuln_bank,
            most_vulnerable_p_loss=round(vuln_p_loss, 1),
            ci_5_pct=round(ci_5, 1),
            ci_95_pct=round(ci_95, 1),
        )


if __name__ == "__main__":
    rst = ReverseStressTest()

    print("=== Reverse Stress Test Results ===\n")

    scenarios = [
        ("ZLB", "Dovish", 7),
        ("ZLB", "Hawkish", 7),
        ("Normalization", "Dovish", 7),
        ("Normalization", "Hawkish", 7),
        ("FastHike", "Hawkish", 2),
    ]

    for regime, stance, years in scenarios:
        r = rst.simulate(regime, stance, years)
        print(f"  {r.scenario_name}:")
        print(f"    E[cum CAR] = {r.mean_cum_car_pct:+.1f}% | CVaR(5%) = {r.cvar_95_pct:.1f}%")
        print(f"    P(loss) = {r.p_loss_pct:.1f}% | P(loss>10%) = {r.p_loss_gt10_pct:.1f}%")
        print(f"    90% CI: [{r.ci_5_pct:.1f}%, {r.ci_95_pct:.1f}%]")
        if r.most_vulnerable != "N/A":
            print(f"    Most vulnerable: {r.most_vulnerable} (P={r.most_vulnerable_p_loss:.1f}%)")
        print()
