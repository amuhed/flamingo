"""One-shot pipeline runner: scrape, translate, analyze."""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.scraper import scrape_all
from pipeline.enrich import enrich_all


def main():
    print("=" * 60)
    print("FLAMINGOS - Albanian Diaspora Protest News Pipeline")
    print("=" * 60)

    print("\nStep 1: Scraping news sources...")
    scrape_all()

    print("\nStep 2: Translating and analyzing sentiment...")
    enrich_all()

    print("\nPipeline complete!")


if __name__ == "__main__":
    main()
