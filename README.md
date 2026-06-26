# Flamingos

Tracking global coverage of Albania's Flamingo Revolution.

A Streamlit web app that aggregates, translates, and analyzes news coverage of the 2025-2026 Albanian protests — known as the Flamingo Revolution — across multiple languages and media ecosystems.

**Live app:** Deployed on Streamlit Cloud

## What it does

The app collects protest-related news from Albanian and international media, auto-translates everything to English, runs sentiment analysis, and classifies each article by thematic frame using Claude Haiku. This enables comparative analysis of how different countries and media ecosystems cover the same events.

### Tabs

- **Timeline Feed** — Chronological article feed with filters by category, language, and sentiment. Each card shows the translated title, original title, source, and sentiment score.
- **Diaspora Map** — Folium map of Albanian diaspora cities (NYC, Boston, London, Athens, Rome, Milan, Brussels, Munich, Istanbul, Zurich) with article counts and sentiment per city. Tirana marked as protest epicenter.
- **Foreign Media Coverage** — Volume and sentiment over time with interactive rangesliders. Breakdowns by country, language, and source. Country drill-down to browse individual articles.
- **Comparative Analysis** — Side-by-side framing comparison between Albanian and foreign media. Shows divergence in emphasis, framing over time (stacked area chart), country-level framing breakdown, and auto-generated key observations.

## Data pipeline

One-shot pipeline that scrapes, translates, scores, and tags articles.

### Sources
- **Albanian media RSS feeds**: Reporter.al, Panorama, Balkanweb, and others
- **International media RSS feeds**: Balkan Insight, DW, BBC, and others
- **Google News RSS search** in 5 languages: English, Albanian, Italian, Greek, German

### Enrichment
1. **Translation** — Google Translate via `deep-translator` (free, no API key)
2. **Sentiment analysis** — VADER on English-translated text. Dictionary-based, scores from -1.0 to +1.0. Known limitation: context-free, so words like "protected" or "freedom" can skew scores in protest coverage. Treated as a rough approximation.
3. **Theme tagging** — Claude Haiku classifies each article into one or more of 9 frames:
   - Environmental
   - Anti-Corruption
   - Democratic Opposition
   - Kushner / Trump
   - Violence & Crackdown
   - Diaspora Solidarity
   - Economic
   - International Response
   - Media & Misinformation

   Haiku also flags off-topic articles for removal. Articles are tagged individually (not in batches) for quality.

### Quality controls
- Off-topic articles flagged by Haiku are reviewed and deleted (38 caught on first run)
- Football/sports articles filtered out via keyword matching and manual review
- Albanian sources reclassified from foreign media when detected via Google News
- Country tagging based on outlet headquarters, with pan-international outlets (Reuters, Al Jazeera, Euronews, Balkan Insight) grouped as "International"
- HTML escaping on all user-generated content to prevent rendering issues

## Dataset

560 articles as of initial build. Stored in `data/flamingos.db` (SQLite).

| Field | Description |
|-------|-------------|
| title / title_en | Original and English-translated title |
| description / description_en | Original and translated description |
| source_name | News outlet name |
| source_country | Country code of outlet headquarters |
| language | Original language (en, sq, it, el, de) |
| category | albanian_media or foreign_media |
| sentiment_score / sentiment_label | VADER compound score and label |
| primary_frame | Dominant thematic frame (from Haiku) |
| themes | JSON array of all applicable frames |
| diaspora_city | Matched diaspora city, if any |

## Stack

- **App**: Streamlit, Plotly, Folium, Pandas
- **Translation**: deep-translator (Google Translate, free)
- **Sentiment**: vaderSentiment
- **Theme tagging**: Claude Haiku (claude-haiku-4-5-20251001)
- **Storage**: SQLite
- **Deployment**: Streamlit Cloud

## Running locally

```bash
cd ~/Projects/Flamingos
pip3 install -r requirements.txt
python3 -m streamlit run app.py --server.port 8504
```

To re-run the pipeline (requires `.env` with `ANTHROPIC_API_KEY`):

```bash
python3 -m pipeline.run_pipeline    # scrape + translate + sentiment
python3 -m pipeline.tag_themes      # Claude Haiku theme tagging
```

## Design

Visual identity based on the Flamingo Revolution's own protest aesthetics:
- **Pink** (#E91E8C) — primary color, from the flamingo symbol
- **Albanian red** (#E41E20) — from the national flag
- **Protest blue** (#2E5EAA) — from the modified protest flag
- **Warm blush background** (#FFF8F9) — light theme

The protest slogan *"Shqiperia nuk shitet"* (Albania is not for sale) appears in the footer.

## Known limitations

- **VADER sentiment is rough** — dictionary-based, no contextual understanding. Scores are a rough approximation, especially for protest coverage where emotionally charged words appear in neutral reporting contexts.
- **BPL anchoring in sources** — Google News RSS is the primary discovery mechanism. Coverage from outlets without strong web presence may be underrepresented.
- **One-time snapshot** — the pipeline was run once. Articles reflect a point-in-time collection, not a live feed.
- **Translation quality** — Google Translate handles Albanian, Italian, Greek, and German reasonably well but can miss nuance, especially in political terminology.
