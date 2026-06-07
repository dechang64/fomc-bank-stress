"""
Multi-Model Disagreement Scorer — The REAL Delta technique.
Uses 3+ LLMs to classify FOMC statements and measures their disagreement.

Key insight: Instead of one model's compressed logprobs (σ=0.016),
use CLASSIFICATION DISAGREEMENT across models as the uncertainty signal.
This has natural variance and is theoretically grounded in:
  - Delta Confidence (Chen et al. 2025): mean(max(P_k))
  - Crowd uncertainty: disagreement = uncertainty
  - Wisdom of crowds: when experts disagree, the truth is uncertain

Models used:
  1. qwen-plus (baseline)
  2. qwen-turbo (smaller, faster, different inductive bias)
  3. qwen-max (larger, more nuanced)
  4. qwen3.6-plus (newer version, different training data)
  5. qwen3.7-max (latest, potentially different perspective)

Disagreement measures:
  - Entropy of classification distribution: H = -Σ p_k log(p_k)
  - Max agreement: max(p_k) — 1.0 = unanimous, 0.33 = maximum disagreement
  - Directional disagreement: some say Dovish, some say Hawkish (most dangerous)
"""
import json
import os
import time
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from openai import OpenAI
from collections import Counter
from score_fomc_inner_confidence import clean_statement

# ── Config ──
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

MODELS = [
    "qwen-plus",
    "qwen-turbo",
    "qwen-max",
    "qwen3.6-plus",
    "qwen3.7-max",
]

PROMPT_TEMPLATE = """You are an expert monetary policy analyst. Classify the following FOMC statement as one of: Dovish, Hawkish, or Neutral.

A **Dovish** statement signals accommodation, easing, or patience on rate hikes.
A **Hawkish** statement signals tightening, concern about inflation, or readiness to raise rates.
A **Neutral** statement is balanced with no clear directional signal.

Also rate your confidence in this classification on a scale of 0-100%.

FOMC Date: {date}
Statement:
{statement}

Respond in EXACTLY this format:
Classification: [Dovish/Hawkish/Neutral]
Confidence: [0-100]%
Reasoning: [1-2 sentences]"""


def classify_with_model(client: OpenAI, model: str, statement: str, date: str) -> dict:
    """Classify FOMC statement with a specific model."""
    prompt = PROMPT_TEMPLATE.format(date=date, statement=statement[:3000])

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Low but not zero — allows some variation
            max_tokens=200,
        )

        text = response.choices[0].message.content.strip()

        # Parse classification
        classification = "Unknown"
        for line in text.split("\n"):
            if "Classification:" in line:
                cls = line.split("Classification:")[1].strip()
                if cls in ["Dovish", "Hawkish", "Neutral"]:
                    classification = cls
                break

        # Parse confidence
        confidence = 0.5
        for line in text.split("\n"):
            if "Confidence:" in line:
                try:
                    conf_str = line.split("Confidence:")[1].strip().replace("%", "")
                    confidence = float(conf_str) / 100.0
                except:
                    pass
                break

        # Parse reasoning
        reasoning = ""
        for line in text.split("\n"):
            if "Reasoning:" in line:
                reasoning = line.split("Reasoning:")[1].strip()
                break

        return {
            "model": model,
            "classification": classification,
            "confidence": confidence,
            "reasoning": reasoning,
        }

    except Exception as e:
        return {
            "model": model,
            "classification": "Error",
            "confidence": 0.0,
            "reasoning": str(e),
        }


def compute_disagreement(classifications: list[dict]) -> dict:
    """
    Compute disagreement metrics from multi-model classifications.
    
    Returns:
        entropy: Shannon entropy of classification distribution
        max_agreement: Fraction of models agreeing on most common class
        directional_disagreement: True if some say Dovish AND some say Hawkish
        dominant_class: Most common classification
        classification_distribution: {Dovish: n, Hawkish: n, Neutral: n}
    """
    valid = [c["classification"] for c in classifications if c["classification"] in ["Dovish", "Hawkish", "Neutral"]]
    
    if not valid:
        return {
            "entropy": 0.0,
            "max_agreement": 0.0,
            "directional_disagreement": False,
            "dominant_class": "Unknown",
            "classification_distribution": {},
        }

    counts = Counter(valid)
    n = len(valid)
    probs = {k: v / n for k, v in counts.items()}

    # Shannon entropy (normalized to [0, 1])
    entropy = -sum(p * np.log2(p) for p in probs.values() if p > 0)
    max_entropy = np.log2(3)  # 3 classes
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

    # Max agreement
    max_agreement = max(probs.values())

    # Directional disagreement (most dangerous)
    has_dovish = "Dovish" in probs and probs["Dovish"] > 0
    has_hawkish = "Hawkish" in probs and probs["Hawkish"] > 0
    directional_disagreement = has_dovish and has_hawkish

    return {
        "entropy": round(normalized_entropy, 4),
        "max_agreement": round(max_agreement, 4),
        "directional_disagreement": directional_disagreement,
        "dominant_class": counts.most_common(1)[0][0],
        "classification_distribution": dict(counts),
    }


def main():
    parser = argparse.ArgumentParser(description="Multi-model FOMC disagreement scoring")
    parser.add_argument("--batch-size", type=int, default=30, help="Statements per batch")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay between API calls (seconds)")
    parser.add_argument("--models", nargs="+", default=MODELS, help="Models to use")
    args = parser.parse_args()

    data_dir = Path(__file__).parent.parent / "data"
    client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL)

    # Load statements
    with open(data_dir / "fomc_statements_all.json") as f:
        statements_raw = json.load(f)

    events = pd.read_csv(data_dir / "bank_events.csv")
    fomc_dates = sorted(events["fomc_date"].tolist())

    # Clean statements
    statements = {}
    for d in fomc_dates:
        if d in statements_raw:
            text = clean_statement(statements_raw[d])
            if len(text) > 100:
                statements[d] = text

    available = sorted(statements.keys())
    print(f"FOMC events: {len(fomc_dates)}")
    print(f"Statements available: {len(available)}")
    print(f"Models: {args.models}")

    # Checkpoint
    ckpt_path = data_dir / "fomc_multimodel_checkpoint.json"
    if args.resume and ckpt_path.exists():
        with open(ckpt_path) as f:
            checkpoint = json.load(f)
        completed = checkpoint.get("completed", {})
        print(f"Resuming: {len(completed)}/{len(available)} already scored")
    else:
        completed = {}

    # Score
    to_score = [d for d in available if d not in completed]
    print(f"To score: {len(to_score)}")

    count = 0
    for d in to_score:
        # Classify with each model
        classifications = []
        for model in args.models:
            result = classify_with_model(client, model, statements[d], d)
            classifications.append(result)
            time.sleep(args.delay)

        # Compute disagreement
        disagreement = compute_disagreement(classifications)

        completed[d] = {
            "date": d,
            "classifications": classifications,
            "disagreement": disagreement,
        }

        count += 1
        if count % 10 == 0:
            print(f"  [{count}/{len(to_score)}] {d}: "
                  f"{disagreement['dominant_class']} "
                  f"(agreement={disagreement['max_agreement']:.2f}, "
                  f"entropy={disagreement['entropy']:.3f})"
                  f"{' ⚠️ DIRECTIONAL' if disagreement['directional_disagreement'] else ''}")

        # Save checkpoint
        if count % args.batch_size == 0:
            with open(ckpt_path, "w") as f:
                json.dump({"completed": completed}, f)
            print(f"  Checkpoint saved: {len(completed)}/{len(available)}")

    # Final save
    with open(ckpt_path, "w") as f:
        json.dump({"completed": completed}, f)

    # Build output DataFrame
    rows = []
    for d, data in completed.items():
        dis = data["disagreement"]
        rows.append({
            "fomc_date": d,
            "dominant_class": dis["dominant_class"],
            "max_agreement": dis["max_agreement"],
            "entropy": dis["entropy"],
            "directional_disagreement": dis["directional_disagreement"],
            "n_dovish": dis["classification_distribution"].get("Dovish", 0),
            "n_hawkish": dis["classification_distribution"].get("Hawkish", 0),
            "n_neutral": dis["classification_distribution"].get("Neutral", 0),
            "n_models": len(data["classifications"]),
        })

    df = pd.DataFrame(rows)
    output_path = data_dir / "fomc_multimodel_disagreement.csv"
    df.to_csv(output_path, index=False)

    print(f"\n✅ Done! {len(completed)} statements scored by {len(args.models)} models")
    print(f"Results: {output_path}")

    # Quick stats
    if len(df) > 0:
        print(f"\n=== Multi-Model Disagreement Stats ===")
        print(f"Max agreement: mean={df['max_agreement'].mean():.3f}, std={df['max_agreement'].std():.3f}")
        print(f"Entropy: mean={df['entropy'].mean():.3f}, std={df['entropy'].std():.3f}")
        print(f"Directional disagreement: {df['directional_disagreement'].mean():.1%}")
        print(f"\nClassification distribution (dominant):")
        print(df["dominant_class"].value_counts().to_string())


if __name__ == "__main__":
    main()
