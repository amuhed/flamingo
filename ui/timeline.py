"""Timeline feed view for articles."""

import html
import streamlit as st
import pandas as pd
from pipeline.sources import LANG_NAMES

# Flamingo Revolution palette
SENTIMENT_COLORS = {
    "positive": "#2E5EAA",   # protest blue
    "negative": "#E41E20",   # Albanian red
    "neutral": "#888888",
}

CATEGORY_LABELS = {
    "albanian_media": "\U0001f1e6\U0001f1f1 Albanian Media",
    "foreign_media": "\U0001f310 Foreign Media",
    "diaspora": "\U0001f9a9 Diaspora",
}


def render_article_card(row):
    """Render a single article as a styled card."""
    sentiment = row.get("sentiment_label", "neutral")
    color = SENTIMENT_COLORS.get(sentiment, "#888")
    score = row.get("sentiment_score", 0)

    lang = LANG_NAMES.get(row.get("language", ""), row.get("language", ""))
    source = row.get("source_name", "Unknown")
    cat = CATEGORY_LABELS.get(row.get("category", ""), row.get("category", ""))

    date_str = ""
    if pd.notna(row.get("published_date")):
        try:
            dt = pd.to_datetime(row["published_date"])
            date_str = dt.strftime("%b %d, %Y")
        except Exception:
            date_str = str(row["published_date"])[:10]

    title_en = html.escape(row.get("title_en") or row.get("title", "Untitled"))
    title_orig = html.escape(row.get("title", ""))
    desc_en = html.escape(row.get("description_en") or row.get("description", ""))
    url = row.get("url", "#")
    source = html.escape(source)

    orig_line = ""
    if row.get("language") != "en" and title_orig and title_orig != title_en:
        orig_line = title_orig

    city = row.get("diaspora_city", "")
    city_badge = f'<span style="background:rgba(233,30,140,0.15); color:#E91E8C; padding:1px 8px; border-radius:10px; font-size:0.75em; margin-left:6px;">\U0001f4cd {html.escape(city)}</span>' if city else ""

    # Sentiment pill
    sent_icon = {
        "positive": "\U0001f7e2",
        "negative": "\U0001f534",
        "neutral": "\u26aa",
    }.get(sentiment, "\u26aa")

    st.markdown(f"""
    <div style="
        border-left: 4px solid {color};
        padding: 14px 18px;
        margin-bottom: 10px;
        background: white;
        border-radius: 0 12px 12px 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    ">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; flex-wrap:wrap; gap:4px;">
            <span style="font-size:0.78em; color:#888;">
                {source} &middot; {cat} &middot; {lang}{city_badge}
            </span>
            <span style="font-size:0.78em; color:#999;">{date_str}</span>
        </div>
        <div style="font-size:1.05em; font-weight:600; margin-bottom:4px; line-height:1.3; color:#2D2D2D;">
            <a href="{url}" target="_blank" style="text-decoration:none; color:#2D2D2D !important;">
                {title_en}
            </a>
        </div>
        {"<div style='font-size:0.82em; color:#999; font-style:italic; margin-bottom:5px;'>" + orig_line + "</div>" if orig_line else ""}
        <div style="font-size:0.88em; color:#666; margin-bottom:8px; line-height:1.4;">
            {desc_en[:280]}{"..." if len(desc_en) > 280 else ""}
        </div>
        <span style="font-size:0.72em; background:{color}18; color:{color}; padding:3px 10px;
            border-radius:12px; border:1px solid {color}33; font-weight:500;">
            {sent_icon} {sentiment.upper()} ({score:+.2f})
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_timeline(df):
    """Render the timeline feed tab."""
    st.markdown("""
    <h2 style="margin-bottom:2px;">
        <span style="color:#E91E8C;">\U0001f4f0</span> Timeline Feed
    </h2>
    <p style="color:#777; font-size:0.9em; margin-top:0;">
        Latest coverage of the Flamingo Revolution, auto-translated and sentiment-scored
    </p>
    <div style="background:white; border:1px solid rgba(233,30,140,0.15); border-radius:10px;
        padding:12px 16px; margin:8px 0 16px 0; font-size:0.82em; color:#666; line-height:1.5;">
        <strong style="color:#E91E8C;">About sentiment scores:</strong>
        Each article is auto-translated to English, then scored using VADER (Valence Aware Dictionary for Sentiment Reasoning).
        Scores range from <strong>-1.0</strong> (most negative) to <strong>+1.0</strong> (most positive).
        Scores above +0.05 are labeled <span style="color:#2E5EAA;">positive</span>,
        below -0.05 are <span style="color:#E41E20;">negative</span>,
        and in between are neutral. Sentiment reflects the tone of the text, not a judgment on the protests themselves.
        <br><em style="color:#999;">Note: VADER is dictionary-based and does not understand context. Words like "protected" or "freedom" may skew scores positive even in protest coverage. Treat scores as a rough approximation.</em>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("No articles found. Run the pipeline first.")
        return

    # Filters in a clean row
    col1, col2, col3 = st.columns(3)
    with col1:
        categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
        cat_filter = st.selectbox("Category", categories, key="tl_cat",
                                  format_func=lambda x: CATEGORY_LABELS.get(x, x) if x != "All" else "\U0001f9a9 All")
    with col2:
        languages = ["All"] + sorted(df["language"].dropna().unique().tolist())
        lang_filter = st.selectbox("Language", languages, key="tl_lang",
                                   format_func=lambda x: LANG_NAMES.get(x, x) if x != "All" else "All Languages")
    with col3:
        sentiments = ["All", "positive", "neutral", "negative"]
        sent_labels = {"All": "All Sentiments", "positive": "\U0001f7e2 Positive", "neutral": "\u26aa Neutral", "negative": "\U0001f534 Negative"}
        sent_filter = st.selectbox("Sentiment", sentiments, key="tl_sent",
                                   format_func=lambda x: sent_labels.get(x, x))

    search = st.text_input("Search articles", key="tl_search",
                           placeholder="\U0001f50d Search titles, descriptions, keywords...")

    filtered = df.copy()
    if cat_filter != "All":
        filtered = filtered[filtered["category"] == cat_filter]
    if lang_filter != "All":
        filtered = filtered[filtered["language"] == lang_filter]
    if sent_filter != "All":
        filtered = filtered[filtered["sentiment_label"] == sent_filter]
    if search:
        mask = (
            filtered["title_en"].str.contains(search, case=False, na=False)
            | filtered["description_en"].str.contains(search, case=False, na=False)
            | filtered["title"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]

    st.markdown(
        f'<p style="color:#E91E8C; font-size:0.85em; font-weight:500;">'
        f'Showing {len(filtered)} of {len(df)} articles</p>',
        unsafe_allow_html=True,
    )

    # Sort by date descending
    filtered = filtered.sort_values("published_date", ascending=False).reset_index(drop=True)

    # Paginate
    per_page = 20
    total_pages = max(1, (len(filtered) + per_page - 1) // per_page)
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, key="tl_page")
    start = (page - 1) * per_page
    page_df = filtered.iloc[start : start + per_page]

    for _, row in page_df.iterrows():
        render_article_card(row)
