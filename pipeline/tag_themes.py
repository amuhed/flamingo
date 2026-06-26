"""Theme tagging using Claude Haiku with quality checks."""

import json
import os
import sqlite3
import time

import anthropic
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "data/flamingos.db"

THEMES = [
    "environmental",        # Vjosa-Narta, wetland, flamingos, biodiversity, ecosystem
    "anti_corruption",      # Government corruption, oligarchy, cronyism, nepotism
    "democratic_opposition", # Democracy, rights, elections, freedom, civil society
    "kushner_trump",        # Kushner resort deal, Trump family, US political connections
    "violence_crackdown",   # Police, tear gas, arrests, clashes, repression
    "diaspora_solidarity",  # Protests abroad, diaspora communities, international support
    "economic",             # Tourism, development, economy, jobs, investment
    "international_response", # EU, US government, diplomatic statements, sanctions
    "media_misinformation", # Fact-checks, fake news, mislabeled content, propaganda
]

SYSTEM_PROMPT = """You are a political science research assistant classifying news articles about the 2025-2026 Albanian protests (the "Flamingo Revolution").

For each article, determine:
1. **primary_frame**: The single most dominant framing/angle. Must be one of the allowed themes.
2. **themes**: All applicable themes (1-3 max). Must be from the allowed themes list.

Allowed themes:
- environmental: Vjosa-Narta wetland, flamingos, biodiversity, ecosystem protection
- anti_corruption: Government corruption, oligarchy, cronyism, state capture
- democratic_opposition: Democracy, civil rights, elections, freedom of assembly, opposition politics
- kushner_trump: Kushner resort deal, Trump family involvement, US political connections
- violence_crackdown: Police violence, tear gas, arrests, clashes, state repression
- diaspora_solidarity: Protests abroad, diaspora communities rallying, international Albanian support
- economic: Tourism development, economic impact, jobs, foreign investment
- international_response: EU/US/international diplomatic statements, foreign policy, sanctions
- media_misinformation: Fact-checks, fake news debunking, mislabeled content, propaganda claims

Rules:
- Choose themes based on the CONTENT of the article, not just keywords
- An article about "protected area" is environmental, not positive sentiment
- An article mentioning Kushner as context but focusing on protests is democratic_opposition, not kushner_trump
- If the article is clearly NOT about the Albanian protests at all, set primary_frame to "off_topic" and themes to ["off_topic"]
- Be conservative: only tag themes that are clearly present, not merely implied

Respond with valid JSON only, no markdown:
{"primary_frame": "theme_name", "themes": ["theme1", "theme2"]}"""


def tag_batch(client, articles):
    """Tag a batch of articles. Returns list of (id, primary_frame, themes)."""
    results = []
    for article in articles:
        aid = article["id"]
        title = article["title_en"] or article["title"] or ""
        desc = article["description_en"] or article["description"] or ""
        source = article["source_name"] or ""
        category = article["category"] or ""

        user_msg = f"""Source: {source} ({category})
Title: {title}
Description: {desc[:500]}"""

        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=150,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            text = response.content[0].text.strip()
            # Parse JSON, handling potential markdown wrapping
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            data = json.loads(text)

            primary = data.get("primary_frame", "")
            themes = data.get("themes", [])

            # Quality check: validate against allowed themes
            valid_themes = THEMES + ["off_topic"]
            if primary not in valid_themes:
                primary = "democratic_opposition"  # safe default
            themes = [t for t in themes if t in valid_themes]
            if not themes:
                themes = [primary]
            if primary not in themes:
                themes.insert(0, primary)

            results.append((aid, primary, themes))
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract what we can
            results.append((aid, "democratic_opposition", ["democratic_opposition"]))
        except Exception as e:
            print(f"    Error tagging article {aid}: {e}")
            results.append(None)
            time.sleep(2)

    return [r for r in results if r is not None]


def tag_all():
    """Tag all untagged articles with themes."""
    client = anthropic.Anthropic()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, title, title_en, description, description_en, source_name, category "
        "FROM articles WHERE primary_frame IS NULL"
    ).fetchall()

    print(f"Tagging {len(rows)} articles with Claude Haiku...")
    articles = [dict(r) for r in rows]

    tagged = 0
    off_topic_ids = []
    for i, article in enumerate(articles):
        results = tag_batch(client, [article])
        for aid, primary, themes in results:
            if primary == "off_topic":
                off_topic_ids.append(aid)
            conn.execute(
                "UPDATE articles SET primary_frame=?, themes=? WHERE id=?",
                (primary, json.dumps(themes), aid),
            )
            tagged += 1

        if (i + 1) % 20 == 0:
            conn.commit()
            print(f"  Tagged {i + 1}/{len(articles)}")
        time.sleep(0.1)  # Rate limiting

    conn.commit()

    # Report off-topic
    if off_topic_ids:
        print(f"\nFound {len(off_topic_ids)} off-topic articles (IDs: {off_topic_ids})")
        print("Review these — they may need deletion.")

    # Quality report
    print(f"\nTagged {tagged} articles. Theme distribution:")
    dist = conn.execute(
        "SELECT primary_frame, COUNT(*) as cnt FROM articles "
        "WHERE primary_frame IS NOT NULL GROUP BY primary_frame ORDER BY cnt DESC"
    ).fetchall()
    for row in dist:
        print(f"  {row[0]:25} | {row[1]:4}")

    conn.close()
    print("\nTheme tagging complete.")


if __name__ == "__main__":
    tag_all()
