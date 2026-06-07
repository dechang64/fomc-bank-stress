"""
HTM Risk Module — Computes unrealized losses on HTM securities.
Based on H9: FastHike×HTM = −0.093 (t = −8.16).
"""
import numpy as np
from dataclasses import dataclass


@dataclass
class HTMRiskAssessment:
    """HTM risk assessment for a single bank."""
    ticker: str
    htm_securities: float          # $ value of HTM portfolio
    htm_ratio: float               # HTM / Total Assets
    afs_ratio: float               # AFS / Total Assets
    duration_years: float          # Effective duration of HTM portfolio
    tier1_capital: float           # Tier 1 capital
    rate_shock_bps: float          # Rate shock in basis points

    # Computed
    htm_unrealized_loss: float = 0.0
    capital_erosion_pct: float = 0.0
    afs_unrealized_gain: float = 0.0
    breach_threshold: bool = False
    risk_level: str = "Low"        # Low / Medium / High / Critical

    def compute(self):
        """Compute HTM risk metrics."""
        # Unrealized loss = -Duration × Δr × Portfolio value
        delta_r = self.rate_shock_bps / 10000  # Convert bps to decimal
        self.htm_unrealized_loss = -self.duration_years * delta_r * self.htm_securities

        # Capital erosion
        if self.tier1_capital > 0:
            self.capital_erosion_pct = abs(self.htm_unrealized_loss) / self.tier1_capital * 100

        # AFS comparison (already marked to market, so gain from rate shock is small)
        self.afs_unrealized_gain = 0.0003 * self.rate_shock_bps / 500  # Near zero from paper

        # Risk classification
        if self.capital_erosion_pct > 100:
            self.risk_level = "Critical"  # HTM losses exceed capital → SVB territory
            self.breach_threshold = True
        elif self.capital_erosion_pct > 50:
            self.risk_level = "High"
            self.breach_threshold = True
        elif self.capital_erosion_pct > 25:
            self.risk_level = "Medium"
        else:
            self.risk_level = "Low"

        return self


class HTMRiskModule:
    """Assess HTM unrealized loss risk for a portfolio of banks."""

    # Empirical coefficients from Xu & Zhang (2026)
    FASTHIKE_HTM_COEFF = -0.0933   # t = -8.16
    FASTHIKE_AFS_COEFF = +0.0003   # t = +2.87

    def assess_bank(self, ticker: str, htm_securities: float, total_assets: float,
                    afs_securities: float, tier1_capital: float,
                    duration: float = 5.0, rate_shock_bps: float = 500) -> HTMRiskAssessment:
        """Assess HTM risk for a single bank."""
        assessment = HTMRiskAssessment(
            ticker=ticker,
            htm_securities=htm_securities,
            htm_ratio=htm_securities / total_assets if total_assets > 0 else 0,
            afs_ratio=afs_securities / total_assets if total_assets > 0 else 0,
            duration_years=duration,
            tier1_capital=tier1_capital,
            rate_shock_bps=rate_shock_bps,
        )
        return assessment.compute()

    def assess_portfolio(self, banks: list[dict],
                         rate_shock_bps: float = 500) -> list[HTMRiskAssessment]:
        """Assess HTM risk for a portfolio of banks."""
        results = []
        for b in banks:
            a = self.assess_bank(
                ticker=b["ticker"],
                htm_securities=b.get("htm_securities", 0),
                total_assets=b.get("total_assets", 1),
                afs_securities=b.get("afs_securities", 0),
                tier1_capital=b.get("tier1_capital", 1),
                duration=b.get("duration", 5.0),
                rate_shock_bps=rate_shock_bps,
            )
            results.append(a)
        return results

    def panel_regression_impact(self, htm_ratio: float, rate_shock_bps: float = 500) -> float:
        """
        Estimate CAR impact using the panel regression coefficient.
        FastHike×HTM = -0.093 means: for each 1pp increase in HTM ratio,
        CAR decreases by 0.093pp during FastHike.
        """
        shock_multiplier = rate_shock_bps / 500  # Scale to empirical calibration
        return self.FASTHIKE_HTM_COEFF * htm_ratio * 100 * shock_multiplier  # Convert to pp


if __name__ == "__main__":
    module = HTMRiskModule()

    # SVB-like scenario
    print("=== SVB-like Bank Assessment ===")
    svb = module.assess_bank(
        ticker="SVB_PROXY",
        htm_securities=91e9,      # $91B HTM (SVB 2022 Q4)
        total_assets=212e9,       # $212B total assets
        afs_securities=27e9,      # $27B AFS
        tier1_capital=16e9,       # $16B Tier 1
        duration=6.0,             # ~6 year duration
        rate_shock_bps=500,
    )
    print(f"  HTM unrealized loss: ${svb.htm_unrealized_loss/1e9:.1f}B")
    print(f"  Capital erosion: {svb.capital_erosion_pct:.1f}%")
    print(f"  Risk level: {svb.risk_level}")
    print(f"  Breach threshold: {svb.breach_threshold}")

    # Diversified bank
    print("\n=== Diversified Bank (JPM-like) ===")
    jpm = module.assess_bank(
        ticker="JPM",
        htm_securities=30e9,
        total_assets=3800e9,
        afs_securities=200e9,
        tier1_capital=210e9,
        duration=4.0,
        rate_shock_bps=500,
    )
    print(f"  HTM unrealized loss: ${jpm.htm_unrealized_loss/1e9:.1f}B")
    print(f"  Capital erosion: {jpm.capital_erosion_pct:.1f}%")
    print(f"  Risk level: {jpm.risk_level}")

    # Panel regression impact
    print("\n=== Panel Regression CAR Impact ===")
    for htm_r in [0.05, 0.10, 0.15, 0.20, 0.35]:
        car_impact = module.panel_regression_impact(htm_r, 500)
        print(f"  HTM ratio={htm_r:.0%}: CAR impact = {car_impact:+.3f}pp")
