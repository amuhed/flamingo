"""Scrape news articles from RSS feeds and Google News."""

import time
import hashlib
import sqlite3
from datetime import datetime
from urllib.parse import quote

import feedparser
import requests

from pipeline.sources import (
    ALBANIAN_FEEDS,
    INTERNATIONAL_FEEDS,
    GOOGLE_NEWS_SEARCHES,
    FILTER_KEYWORDS,
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

DB_PATH = "data/flamingos.db"


def init_db():
    """Create the articles table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url_hash TEXT UNIQUE,
            title TEXT,
            title_en TEXT,
            description TEXT,
            description_en TEXT,
            url TEXT,
            source_name TEXT,
            source_country TEXT,
            language TEXT,
            published_date TEXT,
            scraped_date TEXT,
            sentiment_score REAL,
            sentiment_label TEXT,
            category TEXT,
            diaspora_city TEXT
        )
    """)
    conn.commit()
    conn.close()


def _url_hash(url):
    return hashlib.md5(url.encode()).hexdigest()


def _matches_keywords(text, lang="en"):
    """Check if text contains any protest-related keywords."""
    if not text:
        return False
    text_lower = text.lower()
    # Always check English keywords as fallback
    for kw in FILTER_KEYWORDS.get("en", []):
        if kw in text_lower:
            return True
    # Check language-specific keywords
    if lang != "en":
        for kw in FILTER_KEYWORDS.get(lang, []):
            if kw in text_lower:
                return True
    return False


def _parse_date(entry):
    """Extract published date from a feed entry."""
    for field in ("published_parsed", "updated_parsed"):
        parsed = entry.get(field)
        if parsed:
            try:
                return datetime(*parsed[:6]).isoformat()
            except Exception:
                pass
    for field in ("published", "updated"):
        val = entry.get(field)
        if val:
            return val
    return datetime.now().isoformat()


def _entry_to_article(entry, source_name, source_country, lang, category):
    """Convert a feed entry to an article dict."""
    url = entry.get("link", "")
    title = entry.get("title", "")
    # Get description, stripping HTML tags
    desc = entry.get("summary", entry.get("description", ""))
    if desc and "<" in desc:
        from bs4 import BeautifulSoup
        desc = BeautifulSoup(desc, "html.parser").get_text(separator=" ", strip=True)

    return {
        "url_hash": _url_hash(url),
        "title": title,
        "description": desc[:2000] if desc else "",
        "url": url,
        "source_name": source_name,
        "source_country": source_country,
        "language": lang,
        "published_date": _parse_date(entry),
        "scraped_date": datetime.now().isoformat(),
        "category": category,
    }


def fetch_rss_feed(feed_info, category="albanian_media", filter_keywords=True):
    """Fetch and parse an RSS feed, returning matching articles."""
    url = feed_info["url"]
    lang = feed_info["lang"]
    articles = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        for entry in feed.entries:
            article = _entry_to_article(
                entry, feed_info["name"], feed_info["country"], lang, category
            )
            text = f"{article['title']} {article['description']}"
            if not filter_keywords or _matches_keywords(text, lang):
                articles.append(article)
    except Exception as e:
        print(f"  Error fetching {feed_info['name']}: {e}")
    return articles


def fetch_google_news(search_info):
    """Fetch articles from Google News RSS search."""
    query = quote(search_info["query"])
    hl = search_info["hl"]
    url = f"https://news.google.com/rss/search?q={query}&hl={hl}&gl=US&ceid=US:{hl}"
    articles = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        for entry in feed.entries:
            source_name = entry.get("source", {}).get("title", "Google News")
            article = _entry_to_article(
                entry, source_name, "INT", search_info["lang"], "foreign_media"
            )
            articles.append(article)
    except Exception as e:
        print(f"  Error fetching Google News '{search_info['query']}': {e}")
    return articles


def save_articles(articles):
    """Save articles to SQLite, skipping duplicates."""
    conn = sqlite3.connect(DB_PATH)
    saved = 0
    for article in articles:
        try:
            conn.execute(
                """INSERT OR IGNORE INTO articles
                   (url_hash, title, description, url, source_name, source_country,
                    language, published_date, scraped_date, category)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    article["url_hash"],
                    article["title"],
                    article["description"],
                    article["url"],
                    article["source_name"],
                    article["source_country"],
                    article["language"],
                    article["published_date"],
                    article["scraped_date"],
                    article["category"],
                ),
            )
            if conn.total_changes:
                saved += 1
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()
    return saved


def scrape_all():
    """Run the full scraping pipeline."""
    import os
    os.makedirs("data", exist_ok=True)
    init_db()
    all_articles = []

    print("=== Fetching Albanian media feeds ===")
    for feed in ALBANIAN_FEEDS:
        print(f"  {feed['name']}...")
        # Don't filter Albanian media — they're likely all relevant
        articles = fetch_rss_feed(feed, category="albanian_media", filter_keywords=False)
        print(f"    Found {len(articles)} articles")
        all_articles.extend(articles)
        time.sleep(1)

    print("\n=== Fetching international media feeds ===")
    for feed in INTERNATIONAL_FEEDS:
        print(f"  {feed['name']}...")
        articles = fetch_rss_feed(feed, category="foreign_media", filter_keywords=True)
        print(f"    Found {len(articles)} articles")
        all_articles.extend(articles)
        time.sleep(1)

    print("\n=== Fetching Google News searches ===")
    for search in GOOGLE_NEWS_SEARCHES:
        print(f"  '{search['query']}' ({search['lang']})...")
        articles = fetch_google_news(search)
        print(f"    Found {len(articles)} articles")
        all_articles.extend(articles)
        time.sleep(2)  # Be gentle with Google

    saved = save_articles(all_articles)
    print(f"\n=== Total: {len(all_articles)} fetched, {saved} new saved ===")
    return all_articles
