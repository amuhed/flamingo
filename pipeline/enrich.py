"""Enrich articles with translation and sentiment analysis."""

import sqlite3
from pipeline.translate import translate_to_english
from pipeline.sentiment import analyze_sentiment
from pipeline.sources import DIASPORA_CITIES

DB_PATH = "data/flamingos.db"

# Keywords that indicate diaspora-related content
DIASPORA_KEYWORDS = [
    "diaspora", "diasporë", "abroad", "jashtë", "emigrant",
    "new york", "london", "athens", "rome", "milan", "munich",
    "brussels", "istanbul", "zurich", "boston",
    "united states", "shtetet e bashkuara", "greqi", "itali",
    "gjermani", "britani", "zvicër",
]

CITY_KEYWORDS = {
    "New York City": ["new york", "nyc", "manhattan", "bronx"],
    "Boston": ["boston"],
    "London": ["london", "londër"],
    "Athens": ["athens", "athinë", "athinës", "greqi"],
    "Rome": ["rome", "romë"],
    "Milan": ["milan", "milano"],
    "Brussels": ["brussels", "bruksel"],
    "Munich": ["munich", "mynih", "münchen"],
    "Istanbul": ["istanbul", "stamboll"],
    "Zurich": ["zurich", "zyrih", "zürich"],
}


def _detect_diaspora_city(text):
    """Try to match article text to a diaspora city."""
    if not text:
        return None
    text_lower = text.lower()
    for city, keywords in CITY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return city
    return None


def enrich_all():
    """Translate and analyze sentiment for all articles missing enrichment."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, title, description, language FROM articles WHERE title_en IS NULL"
    ).fetchall()

    print(f"Enriching {len(rows)} articles...")
    for i, row in enumerate(rows):
        title = row["title"] or ""
        desc = row["description"] or ""
        lang = row["language"] or "en"

        # Translate
        if lang == "en":
            title_en = title
            desc_en = desc
        else:
            title_en = translate_to_english(title, source_lang=lang if lang != "auto" else "auto")
            desc_en = translate_to_english(desc, source_lang=lang if lang != "auto" else "auto")

        # Sentiment on English text
        combined = f"{title_en}. {desc_en}" if desc_en else title_en
        score, label = analyze_sentiment(combined)

        # Detect diaspora city
        all_text = f"{title} {desc} {title_en} {desc_en}"
        city = _detect_diaspora_city(all_text)

        # Check if diaspora-related
        is_diaspora = city is not None
        if not is_diaspora:
            text_lower = all_text.lower()
            is_diaspora = any(kw in text_lower for kw in DIASPORA_KEYWORDS)

        conn.execute(
            """UPDATE articles SET
               title_en=?, description_en=?, sentiment_score=?, sentiment_label=?,
               diaspora_city=?
               WHERE id=?""",
            (title_en, desc_en, score, label, city, row["id"]),
        )

        if (i + 1) % 10 == 0:
            print(f"  Enriched {i + 1}/{len(rows)}")
            conn.commit()

    conn.commit()
    conn.close()
    print(f"Enrichment complete.")
