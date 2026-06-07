"""
Score FOMC statements with LLM Inner Confidence.
Uses qwen-plus via DashScope API (OpenAI-compatible).

For each FOMC statement:
1. Ask LLM to classify as Dovish/Hawkish/Neutral
2. Extract token-level softmax probabilities → Inner Confidence
3. Compute Delta Confidence = mean(max(P_k))

Based on Chen et al. (2025, NBER #34965):
  Inner Confidence ≈ 1 - mean(normalized_entropy)
  Delta Confidence ≈ mean(max(P_k))
  Correlation between the two: r = 0.972
"""
import json
import os
import time
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from openai import OpenAI

# ── Config ──
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen-plus"

PROMPT_TEMPLATE = """You are an expert monetary policy analyst. Classify the following FOMC statement as one of: Dovish, Hawkish, or Neutral.

A **Dovish** statement signals accommodation, easing, or patience on rate hikes.
A **Hawkish** statement signals tightening, rate hikes, or concern about inflation.
A **Neutral** statement is balanced with no clear directional signal.

Also provide your confidence level (0-100%) in your classification.

FOMC Statement (Date: {date}):
---
{statement}
---

Respond in EXACTLY this format:
Classification: [Dovish/Hawkish/Neutral]
Confidence: [0-100]
Reasoning: [1-2 sentences]"""


def get_llm_classification(client: OpenAI, statement: str, date: str) -> dict:
    """Get LLM classification with logprobs for Inner Confidence."""
    prompt = PROMPT_TEMPLATE.format(date=date, statement=statement[:3000])

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.1,  # Low temperature for consistency
            logprobs=True,
            top_logprobs=5,
        )

        # Extract classification from response
        content = response.choices[0].message.content.strip()

        # Parse classification
        classification = "Unknown"
        confidence = 50.0
        reasoning = ""

        for line in content.split("\n"):
            line = line.strip()
            if line.lower().startswith("classification:"):
                cls_text = line.split(":", 1)[1].strip()
                for stance in ["Dovish", "Hawkish", "Neutral"]:
                    if stance.lower() in cls_text.lower():
                        classification = stance
                        break
            elif line.lower().startswith("confidence:"):
                try:
                    conf_text = line.split(":", 1)[1].strip().replace("%", "")
                    confidence = float(conf_text)
                    confidence = max(0, min(100, confidence))
                except ValueError:
                    pass
            elif line.lower().startswith("reasoning:"):
                reasoning = line.split(":", 1)[1].strip()

        # Compute Inner Confidence from logprobs
        inner_confidence = compute_inner_confidence(response)

        return {
            "date": date,
            "classification": classification,
            "stated_confidence": confidence / 100.0,
            "inner_confidence": inner_confidence,
            "reasoning": reasoning,
            "raw_response": content,
            "status": "success",
        }

    except Exception as e:
        return {
            "date": date,
            "classification": "Error",
            "stated_confidence": 0.0,
            "inner_confidence": 0.0,
            "reasoning": str(e),
            "raw_response": "",
            "status": "error",
        }


def compute_inner_confidence(response) -> float:
    """
    Compute Inner Confidence from token-level logprobs.
    Inner Confidence = mean(max(P_k)) across tokens.
    
    Following Chen et al. (2025):
    - For each token, get the probability of the top-1 choice
    - Average across all generated tokens
    - Higher = more confident
    """
    try:
        logprobs_content = response.choices[0].logprobs
        if logprobs_content is None or logprobs_content.content is None:
            return 0.5  # Default if no logprobs

        max_probs = []
        for token_logprob in logprobs_content.content:
            if token_logprob.logprob is not None:
                # logprob is log2(probability) for qwen
                # Convert to probability
                prob = np.exp(token_logprob.logprob)
                max_probs.append(prob)

        if not max_probs:
            return 0.5

        # Inner Confidence = mean of max probabilities
        inner_conf = np.mean(max_probs)
        return float(np.clip(inner_conf, 0.0, 1.0))

    except Exception:
        return 0.5


def clean_statement(raw_text: str) -> str:
    """Extract actual FOMC statement from scraped web page text."""
    # Priority-ordered opening phrases (most specific first)
    OPENINGS = [
        "Information received since",
        "For release at",
        "Consistent with its statutory mandate",
        "Consistent with its",
        "In light of the",
        "Against the backdrop",
        "The Committee decided",
    ]

    # Find the earliest REAL opening phrase
    best_idx = len(raw_text)
    for opening in OPENINGS:
        idx = raw_text.find(opening)
        if idx != -1 and idx < best_idx:
            best_idx = idx

    if best_idx < len(raw_text):
        text = raw_text[best_idx:]
    else:
        # Fallback: look for 'Federal Open Market Committee' in second half
        mid = len(raw_text) // 2
        idx = raw_text.find("Federal Open Market Committee", mid)
        if idx != -1:
            start = raw_text.rfind(".", 0, idx)
            text = raw_text[start + 1 :].strip() if start != -1 else raw_text[idx:]
        else:
            text = raw_text

    # Remove trailing boilerplate
    for end_marker in [
        "Return to top",
        "Back to top",
        "Last Update",
        "Implementation Note",
        "Voting for",
        "Voting against",
    ]:
        idx = text.find(end_marker)
        if idx != -1 and idx > len(text) * 0.5:
            text = text[:idx]

    # Clean HTML artifacts
    text = text.replace("&amp;", "&").replace("&#x27;", "'")
    text = text.replace("&nbsp;", " ").replace("\u00a0", " ")
    text = text.replace("&#160;", " ").replace("Share", "")

    return text.strip()


def main():
    parser = argparse.ArgumentParser(description="Score FOMC statements with LLM Inner Confidence")
    parser.add_argument("--batch-size", type=int, default=50, help="Statements per batch")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--delay", type=float, default=0.15, help="Delay between API calls (seconds)")
    args = parser.parse_args()

    # ── Load data ──
    data_dir = Path(__file__).parent.parent / "data"

    with open(data_dir / "fomc_statements_all.json") as f:
        statements_raw = json.load(f)

    events = pd.read_csv(data_dir / "bank_events.csv")
    fomc_dates = events["fomc_date"].tolist()
    lm_pcts = dict(zip(events["fomc_date"], events["lm_pct"]))
    sentiments = dict(zip(events["fomc_date"], events["sentiment"]))

    # Clean statements
    statements = {}
    for date, raw_text in statements_raw.items():
        if date in fomc_dates:
            statements[date] = clean_statement(raw_text)

    print(f"FOMC events: {len(fomc_dates)}")
    print(f"Statements available: {len(statements)}")
    print(f"Missing statements: {len(fomc_dates) - len(statements)}")

    # ── Checkpoint ──
    ckpt_path = data_dir / "fomc_inner_confidence_checkpoint.json"
    if args.resume and ckpt_path.exists():
        with open(ckpt_path) as f:
            checkpoint = json.load(f)
        completed = checkpoint.get("completed", {})
        print(f"Resuming: {len(completed)}/{len(statements)} already scored")
    else:
        completed = {}

    # ── Score ──
    client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL)

    to_score = [d for d in sorted(statements.keys()) if d not in completed]
    print(f"To score: {len(to_score)}")

    if not to_score:
        print("All statements already scored!")
        return

    batch_count = 0
    for i, date in enumerate(to_score):
        result = get_llm_classification(client, statements[date], date)
        completed[date] = result

        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{len(to_score)}] {date}: {result['classification']} "
                  f"(inner={result['inner_confidence']:.3f}, stated={result['stated_confidence']:.2f})")

        # Save checkpoint every 50
        if (i + 1) % args.batch_size == 0:
            with open(ckpt_path, "w") as f:
                json.dump({"completed": completed}, f, indent=2)
            batch_count += 1
            print(f"  ✅ Checkpoint saved ({len(completed)} total)")

        time.sleep(args.delay)

    # ── Final save ──
    with open(ckpt_path, "w") as f:
        json.dump({"completed": completed}, f, indent=2)

    # ── Build results DataFrame ──
    rows = []
    for date in sorted(completed.keys()):
        r = completed[date]
        rows.append({
            "fomc_date": date,
            "lm_pct": lm_pcts.get(date, np.nan),
            "lm_sentiment": sentiments.get(date, "Unknown"),
            "llm_classification": r["classification"],
            "llm_stated_confidence": r["stated_confidence"],
            "inner_confidence": r["inner_confidence"],
            "reasoning": r.get("reasoning", ""),
        })

    df = pd.DataFrame(rows)
    output_path = data_dir / "fomc_inner_confidence.csv"
    df.to_csv(output_path, index=False)

    print(f"\n✅ Done! {len(completed)} statements scored")
    print(f"Results: {output_path}")

    # ── Quick stats ──
    if len(df) > 0:
        print(f"\n=== Quick Stats ===")
        print(f"Inner Confidence: mean={df['inner_confidence'].mean():.3f}, "
              f"std={df['inner_confidence'].std():.3f}")
        print(f"Classification distribution:")
        print(df["llm_classification"].value_counts().to_string())

        # Agreement with LM%
        agree = (df["lm_sentiment"] == df["llm_classification"]).mean()
        print(f"\nLM% vs LLM agreement: {agree:.1%}")


if __name__ == "__main__":
    main()
