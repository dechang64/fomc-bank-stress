"""
FOMC Statement Parser — Real-time LM% extraction from FOMC statements.
Uses Loughran-McDonald dictionary to compute positive word percentage.
"""
import re
from dataclasses import dataclass
from typing import Optional

# Core Loughran-McDonald positive words relevant to FOMC context
LM_POSITIVE_WORDS = {
    "able", "abundance", "abundant", "accelerated", "accelerates",
    "accelerating", "acceleration", "accommodate", "accommodating",
    "accomplish", "accomplished", "accomplishes", "accomplishing",
    "achieve", "achieved", "achievement", "achievements", "achieving",
    "adequate", "advancement", "advancements", "advance", "advanced",
    "advances", "advancing", "advantage", "advantageous", "advantageously",
    "advantages", "beneficial", "beneficially", "benefit", "benefited",
    "benefiting", "benefits", "best", "better", "bolster", "bolstered",
    "bolstering", "bolsters", "boost", "boosted", "boosting", "boosts",
    "bright", "brighter", "brightest", "brilliant", "brilliantly",
    "constructive", "constructively", "demonstrated", "encouraged",
    "encouraging", "enhance", "enhanced", "enhancement", "enhances",
    "enhancing", "exceed", "exceeded", "exceeding", "exceeds",
    "excellent", "excellently", "exceptional", "exceptionally",
    "favorable", "favorably", "firmed", "gained", "gaining",
    "gains", "good", "great", "greater", "greatest", "greatly",
    "growing", "growth", "healthy", "improved", "improvement",
    "improvements", "improves", "improving", "increase", "increased",
    "increases", "increasing", "increasingly", "optimistic",
    "outperform", "outperformed", "outperforming", "outperforms",
    "positive", "positively", "progress", "progressed", "progresses",
    "progressing", "progressive", "progressively", "prosperity",
    "prosperous", "rebound", "rebounded", "recover", "recovered",
    "recovering", "recovery", "resilient", "solid", "solidly",
    "stability", "stabilization", "stabilize", "stabilized",
    "stabilizes", "stabilizing", "stable", "strength", "strengthen",
    "strengthened", "strengthening", "strengthens", "strong",
    "stronger", "strongest", "strongly", "succeed", "succeeded",
    "succeeding", "succeeds", "success", "successes", "successful",
    "successfully", "sustainable", "upward", "upwardly", "upwards",
}

# FOMC-specific hawkish/dovish indicator words
HAWKISH_WORDS = {
    "inflationary", "tightening", "tighten", "tightened",
    "raising", "raised", "raise", "hike", "hiked", "hikes",
    "restrictive", "concern", "concerned", "vigilant",
    "overheating", "unsustainable", "accelerating inflation",
}

DOVISH_WORDS = {
    "accommodative", "easing", "eased", "ease", "cut", "cuts",
    "lowering", "lowered", "supportive", "stimulus", "stimulatory",
    "quantitative easing", "asset purchases", "forward guidance",
    "patient", "measured", "gradual", "data dependent",
}


@dataclass
class FOMCParseResult:
    """Parsed FOMC statement with sentiment metrics."""
    date: str
    lm_pct: float
    n_positive: int
    n_total: int
    stance: str  # Dovish / Hawkish / Neutral
    hawkish_count: int
    dovish_count: int
    key_phrases: list[str]


class FOMCParser:
    """Parse FOMC statements and compute LM% sentiment."""

    # Stance thresholds (calibrated to 1994-2025 sample)
    DOVISH_THRESHOLD = 3.5   # LM% > 3.5 = Dovish
    HAWKISH_THRESHOLD = 1.5  # LM% < 1.5 = Hawkish

    def parse(self, statement_text: str, date: str = "") -> FOMCParseResult:
        """Parse an FOMC statement and extract sentiment."""

        # Tokenize
        words = re.findall(r'\b[a-z]+\b', statement_text.lower())
        n_total = len(words)

        if n_total == 0:
            return FOMCParseResult(
                date=date, lm_pct=0.0, n_positive=0, n_total=0,
                stance="Neutral", hawkish_count=0, dovish_count=0,
                key_phrases=[],
            )

        # Count LM positive words
        n_positive = sum(1 for w in words if w in LM_POSITIVE_WORDS)
        lm_pct = (n_positive / n_total) * 100

        # Count FOMC-specific hawkish/dovish words
        hawkish_count = sum(1 for w in words if w in HAWKISH_WORDS)
        dovish_count = sum(1 for w in words if w in DOVISH_WORDS)

        # Stance classification
        if lm_pct > self.DOVISH_THRESHOLD:
            stance = "Dovish"
        elif lm_pct < self.HAWKISH_THRESHOLD:
            stance = "Hawkish"
        else:
            stance = "Neutral"

        # Extract key phrases (sentences containing hawkish/dovish words)
        sentences = re.split(r'[.!?]', statement_text)
        key_phrases = []
        for sent in sentences:
            sent_lower = sent.lower().strip()
            if any(w in sent_lower for w in HAWKISH_WORDS | DOVISH_WORDS):
                if len(sent.strip()) > 20:
                    key_phrases.append(sent.strip()[:100])

        return FOMCParseResult(
            date=date,
            lm_pct=round(lm_pct, 2),
            n_positive=n_positive,
            n_total=n_total,
            stance=stance,
            hawkish_count=hawkish_count,
            dovish_count=dovish_count,
            key_phrases=key_phrases[:5],
        )


if __name__ == "__main__":
    parser = FOMCParser()

    # Test with real FOMC statement excerpts
    statements = [
        ("2024-12-11", """
            The Federal Reserve decided to lower the target range for the federal funds rate
            by 25 basis points to 4.25-4.50 percent. Recent indicators suggest that economic
            activity has continued to expand at a solid pace. Job gains have slowed in recent
            months but remain strong, and the unemployment rate remains low.
            Inflation has made progress toward the Committee's 2 percent objective
            but remains somewhat elevated. The Committee judges that the risks to achieving
            its employment and inflation goals are roughly in balance.
        """),
        ("2022-06-15", """
            The Federal Reserve decided to raise the target range for the federal funds rate
            by 75 basis points to 1.50-1.75 percent. Inflation remains elevated, reflecting
            supply and demand imbalances related to the pandemic, higher energy prices, and
            broader price pressures. The Committee is strongly committed to returning inflation
            to its 2 percent objective. The Committee anticipates that ongoing increases in
            the target range will be appropriate.
        """),
        ("2010-11-03", """
            The Federal Reserve will maintain the target range for the federal funds rate
            at 0 to 1/4 percent. To promote a stronger pace of economic recovery and to help
            ensure that inflation over time is at levels consistent with its mandate, the
            Committee decided to expand its holdings of securities. The Committee will maintain
            its existing policy of reinvesting principal payments from its securities holdings
            and will purchase a further $600 billion of longer-term Treasury securities by
            the end of the second quarter of 2011.
        """),
    ]

    print("=== FOMC Statement Parsing ===\n")
    for date, text in statements:
        result = parser.parse(text, date)
        print(f"  {result.date}: LM%={result.lm_pct:.2f} | Stance={result.stance}")
        print(f"    Positive: {result.n_positive}/{result.n_total} | Hawkish: {result.hawkish_count} | Dovish: {result.dovish_count}")
        if result.key_phrases:
            print(f"    Key phrases: {result.key_phrases[0][:80]}...")
        print()
