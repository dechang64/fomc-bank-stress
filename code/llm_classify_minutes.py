"""
LLM classification of FOMC Minutes using DashScope/Qwen API.
Classifies each Minutes as Dovish/Neutral/Hawkish with confidence and reasoning.
"""
import json, os, time, re
from openai import OpenAI

# Config
DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY', '')
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
MODEL = "qwen-plus"

CKPT_PATH = 'data/fomc_minutes_llm_checkpoint.json'
MINUTES_PATH = 'data/fomc_minutes_text_checkpoint.json'

SYSTEM_PROMPT = """You are an expert monetary policy analyst. Classify the FOMC Minutes text as one of:
- Dovish: Discussion leans toward easing, rate cuts, accommodative policy, concerns about growth/employment
- Hawkish: Discussion leans toward tightening, rate hikes, restrictive policy, concerns about inflation
- Neutral: Balanced discussion, no clear directional bias

Also provide:
1. Your confidence level (0-100%)
2. A brief reasoning (1-2 sentences)

Output format:
Classification: [Dovish/Neutral/Hawkish]
Confidence: [number]%
Reasoning: [text]"""

def classify_minutes(date, text):
    """Classify a single Minutes document."""
    # Truncate to ~4000 chars to fit context window (Minutes are long)
    # Focus on the policy discussion section
    truncated = text[:4000] if len(text) > 4000 else text
    
    user_prompt = f"""Classify this FOMC Minutes excerpt from the meeting of {date}:

{truncated}"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        raw = response.choices[0].message.content.strip()
        
        # Parse response
        classification = "Unknown"
        confidence = 0.5
        reasoning = ""
        
        class_match = re.search(r'Classification:\s*(Dovish|Neutral|Hawkish)', raw, re.IGNORECASE)
        if class_match:
            classification = class_match.group(1).capitalize()
        
        conf_match = re.search(r'Confidence:\s*(\d+)', raw)
        if conf_match:
            confidence = int(conf_match.group(1)) / 100
        
        reason_match = re.search(r'Reasoning:\s*(.+)', raw, re.DOTALL)
        if reason_match:
            reasoning = reason_match.group(1).strip()
        
        # Compute inner confidence from token probabilities
        inner_conf = 0.5
        if hasattr(response.choices[0], 'logprobs') and response.choices[0].logprobs:
            try:
                tokens = response.choices[0].logprobs.content
                if tokens:
                    probs = [t.logprob for t in tokens if t.logprob is not None]
                    if probs:
                        import math
                        avg_prob = math.exp(sum(probs) / len(probs))
                        inner_conf = avg_prob
            except:
                pass
        
        return {
            'date': date,
            'classification': classification,
            'stated_confidence': confidence,
            'inner_confidence': inner_conf,
            'reasoning': reasoning,
            'raw_response': raw,
            'status': 'success'
        }
        
    except Exception as e:
        return {
            'date': date,
            'classification': 'Error',
            'stated_confidence': 0,
            'inner_confidence': 0,
            'reasoning': str(e)[:200],
            'raw_response': '',
            'status': 'error'
        }

def main():
    # Load Minutes text
    with open(MINUTES_PATH) as f:
        minutes = json.load(f)['completed']
    
    # Load checkpoint
    if os.path.exists(CKPT_PATH):
        with open(CKPT_PATH) as f:
            checkpoint = json.load(f)
    else:
        checkpoint = {'completed': {}}
    
    completed = checkpoint['completed']
    remaining = {k: v for k, v in minutes.items() if k not in completed}
    
    print(f"Total: {len(minutes)}, Completed: {len(completed)}, Remaining: {len(remaining)}")
    
    if not remaining:
        print("All done!")
        return
    
    # Process in batches
    BATCH_SIZE = 30
    batch = dict(list(remaining.items())[:BATCH_SIZE])
    print(f"Processing batch of {len(batch)}...")
    
    for i, (date, text) in enumerate(batch.items()):
        print(f"  [{i+1}/{len(batch)}] {date}...", end=' ', flush=True)
        result = classify_minutes(date, text)
        
        if result['status'] == 'success':
            completed[date] = result
            print(f"{result['classification']} (conf={result['stated_confidence']:.0%})")
        else:
            completed[date] = result  # Save error too
            print(f"ERROR: {result['reasoning'][:50]}")
        
        # Checkpoint every 10
        if (i + 1) % 10 == 0:
            with open(CKPT_PATH, 'w') as f:
                json.dump(checkpoint, f, ensure_ascii=False)
            print(f"  Checkpoint: {len(completed)} completed")
        
        time.sleep(0.15)  # Rate limit
    
    # Final save
    with open(CKPT_PATH, 'w') as f:
        json.dump(checkpoint, f, ensure_ascii=False)
    
    print(f"\nBatch done. Total: {len(completed)} completed")

if __name__ == '__main__':
    main()
