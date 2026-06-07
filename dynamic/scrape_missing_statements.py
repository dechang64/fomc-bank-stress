"""
Scrape missing FOMC statements from federalreserve.gov.
Covers the 70 dates missing from fomc_statements_all.json.
"""
import json
import re
import time
import urllib.request
from pathlib import Path
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent.parent / "data"


def scrape_statement(date_str: str) -> str | None:
    """Scrape FOMC statement from federalreserve.gov for a given date."""
    date_compact = date_str.replace("-", "")
    url = f"https://www.federalreserve.gov/newsevents/pressreleases/monetary{date_compact}a.htm"

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode("utf-8", errors="replace")

        soup = BeautifulSoup(html, "html.parser")

        # Find the statement content div
        content = soup.find("div", class_="col-md-8 col-xs-12")
        if content is None:
            content = soup.find("div", id="article")
        if content is None:
            content = soup.find("main")

        if content:
            text = content.get_text(separator=" ", strip=True)
            return text
        else:
            # Fallback: extract all text from body
            body = soup.find("body")
            if body:
                return body.get_text(separator=" ", strip=True)

        return None

    except urllib.error.HTTPError:
        return None
    except Exception as e:
        print(f"  Error scraping {date_str}: {e}")
        return None


def main():
    # Load existing statements
    with open(DATA_DIR / "fomc_statements_all.json") as f:
        statements = json.load(f)

    # Load event dates
    import pandas as pd
    events = pd.read_csv(DATA_DIR / "bank_events.csv")
    fomc_dates = set(events["fomc_date"].tolist())

    # Also load curated excerpts
    import sys
    sys.path.insert(0, "/tmp/monetary-policy-lab/mp-research-platform/data")
    try:
        from fomc_statements import FOMC_STATEMENTS
    except ImportError:
        FOMC_STATEMENTS = {}

    # Find missing dates
    missing = sorted(set(fomc_dates) - set(statements.keys()))
    print(f"Missing statements: {len(missing)}")

    # First, fill from curated excerpts
    filled_from_excerpts = 0
    for d in missing:
        if d in FOMC_STATEMENTS:
            statements[d] = FOMC_STATEMENTS[d]
            filled_from_excerpts += 1

    print(f"Filled from curated excerpts: {filled_from_excerpts}")

    # Update missing list
    still_missing = sorted(set(fomc_dates) - set(statements.keys()))
    print(f"Still missing (need scraping): {len(still_missing)}")

    # Scrape remaining
    scraped = 0
    failed = []
    for d in still_missing:
        print(f"  Scraping {d}...", end=" ")
        text = scrape_statement(d)
        if text and len(text) > 200:
            statements[d] = text
            scraped += 1
            print(f"OK ({len(text)} chars)")
        else:
            failed.append(d)
            print("FAILED")
        time.sleep(0.5)  # Be polite

    print(f"\n✅ Scraped: {scraped}")
    print(f"❌ Failed: {len(failed)}")
    if failed:
        print(f"Failed dates: {failed}")

    # Save updated statements
    with open(DATA_DIR / "fomc_statements_all.json", "w") as f:
        json.dump(statements, f, indent=2, ensure_ascii=False)

    # Final coverage
    final_coverage = len(set(fomc_dates) & set(statements.keys()))
    print(f"\nFinal coverage: {final_coverage}/{len(fomc_dates)} ({final_coverage/len(fomc_dates)*100:.1f}%)")


if __name__ == "__main__":
    main()
