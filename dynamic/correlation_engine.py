"""
Dynamic Correlation Engine — Regime-conditional bank inter-correlation.
Based on: ZLB FOMC ρ=0.86 vs Non-ZLB FOMC ρ=0.68.
"""
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class CorrelationMatrix:
    """Regime-conditional correlation matrix for a set of banks."""
    banks: list[str]
    regime: str
    is_fomc_day: bool
    base_correlation: float
    matrix: np.ndarray

    def systemic_risk_index(self) -> float:
        """Compute a systemic risk index from the correlation matrix."""
        n = len(self.banks)
        # Average off-diagonal correlation
        total = 0.0
        count = 0
        for i in range(n):
            for j in range(i + 1, n):
                total += self.matrix[i, j]
                count += 1
        avg_corr = total / count if count > 0 else 0

        # Eigenvalue-based concentration (largest eigenvalue / sum)
        eigenvalues = np.linalg.eigvalsh(self.matrix)
        concentration = eigenvalues[-1] / np.sum(eigenvalues) if np.sum(eigenvalues) > 0 else 0

        # Composite index: high correlation + high concentration = high systemic risk
        return (avg_corr * 0.6 + concentration * 0.4) * 100


class CorrelationEngine:
    """Generate regime-conditional correlation matrices."""

    # From paper: Table 5 and §5.2
    REGIME_CORRELATIONS = {
        ("ZLB", True): 0.86,
        ("ZLB", False): 0.75,
        ("Normalization", True): 0.68,
        ("Normalization", False): 0.55,
        ("FastHike", True): 0.78,
        ("FastHike", False): 0.62,
    }

    # Bank-specific correlation adjustments (from paper's ΔCoVaR analysis)
    BANK_ADJUSTMENTS = {
        "JPM": 1.05,   # SIFI: higher correlation
        "BAC": 1.08,
        "C": 1.12,     # Citi: highest vulnerability
        "WFC": 1.06,
        "GS": 0.95,    # Investment bank: lower correlation with commercials
        "MS": 0.93,
        "SCHW": 1.15,  # High deposit base: higher systemic linkage
        "BK": 1.10,
    }

    def generate(self, banks: list[str], regime: str,
                 is_fomc_day: bool = True,
                 idiosyncratic_noise: float = 0.05) -> CorrelationMatrix:
        """Generate a regime-conditional correlation matrix."""

        n = len(banks)
        base_rho = self.REGIME_CORRELATIONS.get((regime, is_fomc_day), 0.65)

        # Build correlation matrix with bank-specific adjustments
        matrix = np.ones((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                adj_i = self.BANK_ADJUSTMENTS.get(banks[i], 1.0)
                adj_j = self.BANK_ADJUSTMENTS.get(banks[j], 1.0)
                rho = min(base_rho * (adj_i + adj_j) / 2, 0.99)

                # Add small noise for realism
                rho += np.random.normal(0, idiosyncratic_noise)
                rho = np.clip(rho, 0.1, 0.99)

                matrix[i, j] = rho
                matrix[j, i] = rho

        # Ensure positive semi-definite
        eigenvalues = np.linalg.eigvalsh(matrix)
        if np.min(eigenvalues) < 0:
            # Project to nearest PSD matrix
            matrix = self._nearest_psd(matrix)

        return CorrelationMatrix(
            banks=banks,
            regime=regime,
            is_fomc_day=is_fomc_day,
            base_correlation=base_rho,
            matrix=matrix,
        )

    def compare_regimes(self, banks: list[str]) -> dict:
        """Compare correlation structures across regimes."""
        results = {}
        for regime in ["ZLB", "Normalization", "FastHike"]:
            for is_fomc in [True, False]:
                cm = self.generate(banks, regime, is_fomc)
                key = f"{regime}_{'FOMC' if is_fomc else 'NonFOMC'}"
                results[key] = {
                    "base_rho": cm.base_correlation,
                    "systemic_index": cm.systemic_risk_index(),
                }
        return results

    @staticmethod
    def _nearest_psd(matrix: np.ndarray) -> np.ndarray:
        """Project to nearest positive semi-definite matrix."""
        eigvals, eigvecs = np.linalg.eigh(matrix)
        eigvals = np.maximum(eigvals, 1e-8)
        return eigvecs @ np.diag(eigvals) @ eigvecs.T


if __name__ == "__main__":
    engine = CorrelationEngine()

    banks = ["JPM", "BAC", "C", "WFC", "GS", "MS", "SCHW", "BK"]

    print("=== Regime-Conditional Correlation ===\n")

    comparison = engine.compare_regimes(banks)
    for key, vals in comparison.items():
        print(f"  {key}: ρ={vals['base_rho']:.2f} | Systemic Index={vals['systemic_index']:.1f}")

    # ZLB FOMC correlation matrix
    print("\n=== ZLB FOMC Correlation Matrix (sample) ===")
    cm = engine.generate(banks[:5], "ZLB", True)
    print(f"  Banks: {cm.banks}")
    print(f"  Base ρ: {cm.base_correlation:.2f}")
    for i in range(5):
        row = " ".join(f"{cm.matrix[i, j]:.2f}" for j in range(5))
        print(f"  {cm.banks[i]:>4}: {row}")
