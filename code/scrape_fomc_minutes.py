"""
Scrape FOMC Minutes from federalreserve.gov using agent-browser CLI.
Batch processing with checkpoint/resume support.
"""
import json, os, subprocess, re, time

CKPT_PATH = 'data/fomc_minutes_checkpoint.json'
URLS_PATH = 'data/fomc_minutes_urls.json'
BATCH_SIZE = 20  # per session

def load_checkpoint():
    if os.path.exists(CKPT_PATH):
        with open(CKPT_PATH) as f:
            return json.load(f)
    return {'completed': {}, 'failed': []}

def save_checkpoint(ckpt):
    with open(CKPT_PATH, 'w') as f:
        json.dump(ckpt, f, ensure_ascii=False, indent=2)

def scrape_minutes(url, date_str):
    """Scrape a single FOMC Minutes page using agent-browser."""
    try:
        # Open the page
        result = subprocess.run(
            ['agent-browser', 'open', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None, f"open failed: {result.stderr[:100]}"
        
        # Extract text from #article element
        result = subprocess.run(
            ['agent-browser', 'eval', 
             "document.getElementById('article') ? document.getElementById('article').innerText : document.body.innerText"],
            capture_output=True, text=True, timeout=15
        )
        
        if result.returncode != 0:
            return None, f"eval failed: {result.stderr[:100]}"
        
        text = result.stdout.strip().strip('"')
        
        # Verify it's actually Minutes content
        if 'Minutes of the Federal Open Market Committee' not in text and 'minutes' not in text.lower()[:200]:
            return None, "Not a valid Minutes page"
        
        # Clean up: remove attendance list, keep substantive content
        # Find the start of actual discussion
        lines = text.split('\n')
        content_lines = []
        in_content = False
        for line in lines:
            if any(kw in line for kw in ['Staff Review', 'Participants\' Views', 'Committee Policy Action', 
                                          'Voting for', 'Voting against']):
                in_content = True
            if in_content:
                content_lines.append(line)
        
        if content_lines:
            clean_text = '\n'.join(content_lines)
        else:
            clean_text = text  # fallback to full text
        
        return clean_text, None
        
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except Exception as e:
        return None, str(e)[:100]

def main():
    with open(URLS_PATH) as f:
        urls = json.load(f)
    
    ckpt = load_checkpoint()
    completed = ckpt['completed']
    failed = ckpt['failed']
    
    remaining = {k: v for k, v in urls.items() 
                 if k not in completed and k not in failed}
    
    print(f"Total: {len(urls)}, Completed: {len(completed)}, Failed: {len(failed)}, Remaining: {len(remaining)}")
    
    if not remaining:
        print("All done!")
        return
    
    # Process in batches
    batch = dict(list(remaining.items())[:BATCH_SIZE])
    print(f"Processing batch of {len(batch)}...")
    
    for i, (date_str, url) in enumerate(batch.items()):
        print(f"  [{i+1}/{len(batch)}] {date_str}...", end=' ', flush=True)
        text, error = scrape_minutes(url, date_str)
        
        if text:
            completed[date_str] = text
            print(f"OK ({len(text)} chars)")
        else:
            failed.append(date_str)
            print(f"FAILED: {error}")
        
        # Save checkpoint every 5
        if (i + 1) % 5 == 0:
            save_checkpoint(ckpt)
            print(f"  Checkpoint saved ({len(completed)} completed)")
        
        time.sleep(1)  # Rate limit
    
    # Final save
    save_checkpoint(ckpt)
    print(f"\nBatch complete. Total: {len(completed)} completed, {len(failed)} failed")

if __name__ == '__main__':
    main()
