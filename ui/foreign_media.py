"""Foreign media coverage analysis over time with sentiment."""

import html as html_mod
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pipeline.sources import COUNTRY_NAMES, LANG_NAMES

# Flamingo Revolution palette
PINK = "#E91E8C"
PINK_LIGHT = "#FF69B4"
RED = "#E41E20"
BLUE = "#2E5EAA"
SOFT_PINK = "#F8BBD0"

SENTIMENT_COLORS = {
    "positive": BLUE,
    "negative": RED,
    "neutral": "#888888",
}

# Custom color scale: pink to red
FLAMINGO_SCALE = [
    [0, "#F8BBD0"],
    [0.25, "#FF69B4"],
    [0.5, "#E91E8C"],
    [0.75, "#C2185B"],
    [1, "#E41E20"],
]

# For sentiment: blue (positive) through pink (neutral) to red (negative)
SENTIMENT_SCALE = [
    [0, "#E41E20"],
    [0.25, "#E91E8C"],
    [0.5, "#F8BBD0"],
    [0.75, "#7BAAF7"],
    [1, "#2E5EAA"],
]

PLOTLY_TEMPLATE = "plotly_white"
CHART_MARGINS = dict(l=20, r=20, t=10, b=20)


def render_foreign_media(df):
    """Render the foreign media coverage tab."""
    st.markdown("""
    <h2 style="margin-bottom:2px;">
        <span style="color:#E91E8C;">\U0001f4ca</span> Foreign Media Coverage
    </h2>
    <p style="color:#777; font-size:0.9em; margin-top:0;">
        How the world is covering the Flamingo Revolution &mdash; sentiment analysis across countries and languages
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

    foreign = df[df["category"] == "foreign_media"].copy()

    if foreign.empty:
        st.info("No foreign media articles found. Run the pipeline first.")
        return

    # Parse dates
    foreign["date"] = pd.to_datetime(foreign["published_date"], errors="coerce")
    foreign = foreign.dropna(subset=["date"])
    foreign["date_day"] = foreign["date"].dt.date

    # Date range selector
    min_date = foreign["date"].min().date()
    max_date = foreign["date"].max().date()
    date_range = st.slider(
        "Date range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="MMM DD, YYYY",
        key="fm_date_range",
    )
    foreign = foreign[(foreign["date"].dt.date >= date_range[0]) & (foreign["date"].dt.date <= date_range[1])]

    # --- Coverage volume over time ---
    st.markdown(f'<h3 style="color:{PINK};">Coverage Volume Over Time</h3>', unsafe_allow_html=True)
    daily = foreign.groupby("date_day").size().reset_index(name="articles")
    daily["date_day"] = pd.to_datetime(daily["date_day"])

    fig_vol = px.bar(
        daily, x="date_day", y="articles",
        labels={"date_day": "Date", "articles": "Articles"},
        color_discrete_sequence=[PINK],
    )
    fig_vol.update_layout(
        template=PLOTLY_TEMPLATE,
        height=300,
        margin=CHART_MARGINS,
        xaxis_title="",
        yaxis_title="Articles per day",
        bargap=0.3,
    )
    fig_vol.update_traces(marker_line_width=0, opacity=0.85)
    st.plotly_chart(fig_vol, use_container_width=True)

    # --- Sentiment over time ---
    st.markdown(f'<h3 style="color:{PINK};">Sentiment Trend</h3>', unsafe_allow_html=True)
    daily_sent = foreign.groupby("date_day").agg(
        avg_sentiment=("sentiment_score", "mean"),
        count=("id", "count"),
    ).reset_index()
    daily_sent["date_day"] = pd.to_datetime(daily_sent["date_day"])

    fig_sent = go.Figure()
    # Area fill
    fig_sent.add_trace(go.Scatter(
        x=daily_sent["date_day"],
        y=daily_sent["avg_sentiment"],
        mode="lines+markers",
        name="Avg Sentiment",
        line=dict(color=PINK, width=3),
        marker=dict(size=7, color=PINK, line=dict(width=1, color="white")),
        fill="tozeroy",
        fillcolor="rgba(233, 30, 140, 0.1)",
    ))
    fig_sent.add_hline(y=0, line_dash="dash", line_color="rgba(0,0,0,0.15)")
    fig_sent.update_layout(
        template=PLOTLY_TEMPLATE,
        height=300,
        margin=CHART_MARGINS,
        xaxis_title="",
        yaxis_title="Sentiment Score",
        yaxis=dict(range=[-1, 1]),
        showlegend=False,
    )
    st.plotly_chart(fig_sent, use_container_width=True)

    # Two columns for country charts
    col1, col2 = st.columns(2)

    with col1:
        # --- Coverage by country ---
        st.markdown(f'<h3 style="color:{PINK};">Coverage by Country</h3>', unsafe_allow_html=True)
        country_counts = foreign["source_country"].value_counts().reset_index()
        country_counts.columns = ["country", "articles"]
        country_counts["country_name"] = country_counts["country"].map(
            lambda x: COUNTRY_NAMES.get(x, x)
        )

        fig_country = px.bar(
            country_counts, x="country_name", y="articles",
            labels={"country_name": "Country", "articles": "Articles"},
            color="articles",
            color_continuous_scale=FLAMINGO_SCALE,
        )
        fig_country.update_layout(
            template=PLOTLY_TEMPLATE,
            height=350,
            margin=CHART_MARGINS,
            showlegend=False,
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_country, use_container_width=True)

    with col2:
        # --- Sentiment by country ---
        st.markdown(f'<h3 style="color:{PINK};">Sentiment by Country</h3>', unsafe_allow_html=True)
        country_sent = foreign.groupby("source_country").agg(
            avg_sentiment=("sentiment_score", "mean"),
            articles=("id", "count"),
        ).reset_index()
        country_sent["country_name"] = country_sent["source_country"].map(
            lambda x: COUNTRY_NAMES.get(x, x)
        )
        country_sent = country_sent.sort_values("avg_sentiment")

        fig_cs = px.bar(
            country_sent, x="country_name", y="avg_sentiment",
            labels={"country_name": "Country", "avg_sentiment": "Avg Sentiment"},
            color="avg_sentiment",
            color_continuous_scale=SENTIMENT_SCALE,
            range_color=[-1, 1],
        )
        fig_cs.update_layout(
            template=PLOTLY_TEMPLATE,
            height=350,
            margin=CHART_MARGINS,
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_cs, use_container_width=True)

    # --- Language breakdown ---
    col3, col4 = st.columns(2)

    with col3:
        st.markdown(f'<h3 style="color:{PINK};">Coverage by Language</h3>', unsafe_allow_html=True)
        lang_counts = foreign["language"].value_counts().reset_index()
        lang_counts.columns = ["language", "articles"]
        lang_counts["language_name"] = lang_counts["language"].map(
            lambda x: LANG_NAMES.get(x, x)
        )

        # Flamingo-themed pie colors
        pie_colors = [PINK, RED, BLUE, PINK_LIGHT, SOFT_PINK, "#C2185B", "#7BAAF7"]
        fig_lang = px.pie(
            lang_counts, names="language_name", values="articles",
            color_discrete_sequence=pie_colors,
        )
        fig_lang.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hole=0.35,
            marker=dict(line=dict(color="rgba(0,0,0,0.3)", width=1)),
        )
        fig_lang.update_layout(
            template=PLOTLY_TEMPLATE,
            height=350,
            margin=CHART_MARGINS,
        )
        st.plotly_chart(fig_lang, use_container_width=True)

    with col4:
        # --- Top sources ---
        st.markdown(f'<h3 style="color:{PINK};">Top Foreign Sources</h3>', unsafe_allow_html=True)
        top_sources = foreign.groupby("source_name").agg(
            articles=("id", "count"),
            avg_sentiment=("sentiment_score", "mean"),
        ).reset_index().sort_values("articles", ascending=False).head(12)
        top_sources["avg_sentiment"] = top_sources["avg_sentiment"].apply(lambda x: f"{x:+.2f}")
        top_sources.columns = ["Source", "Articles", "Avg Sentiment"]
        st.dataframe(top_sources, use_container_width=True, hide_index=True, height=350)

    # --- Country drill-down ---
    st.markdown(f'<h3 style="color:{PINK};">Browse by Country</h3>', unsafe_allow_html=True)

    country_options = foreign["source_country"].value_counts().reset_index()
    country_options.columns = ["code", "count"]
    country_choices = {
        f"{COUNTRY_NAMES.get(row['code'], row['code'])} ({row['count']})": row["code"]
        for _, row in country_options.iterrows()
    }
    selected_label = st.selectbox(
        "Select a country to see its articles",
        options=list(country_choices.keys()),
        key="fm_country_drill",
    )
    selected_code = country_choices[selected_label]
    country_name = COUNTRY_NAMES.get(selected_code, selected_code)

    country_df = foreign[foreign["source_country"] == selected_code].sort_values(
        "published_date", ascending=False
    )

    st.markdown(
        f'<p style="color:#E91E8C; font-size:0.85em; font-weight:500;">'
        f'{len(country_df)} articles from {html_mod.escape(country_name)}</p>',
        unsafe_allow_html=True,
    )

    for _, row in country_df.iterrows():
        title = html_mod.escape(row.get("title_en") or row.get("title", "Untitled"))
        source = html_mod.escape(row.get("source_name", ""))
        url = row.get("url", "#")
        score = row.get("sentiment_score", 0)
        label = row.get("sentiment_label", "neutral")
        color = SENTIMENT_COLORS.get(label, "#888")
        date_str = ""
        if pd.notna(row.get("published_date")):
            try:
                date_str = pd.to_datetime(row["published_date"]).strftime("%b %d, %Y")
            except Exception:
                date_str = str(row["published_date"])[:10]

        st.markdown(f"""
        <div style="background:white; border-left:3px solid {color}; padding:10px 14px;
            margin-bottom:8px; border-radius:0 8px 8px 0; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                <span style="font-size:0.78em; color:#888;">{source}</span>
                <span style="font-size:0.78em; color:#999;">{date_str}</span>
            </div>
            <a href="{url}" target="_blank" style="text-decoration:none; color:#2D2D2D !important;
                font-weight:600; font-size:0.95em; line-height:1.3;">
                {title}
            </a>
            <div style="margin-top:6px;">
                <span style="font-size:0.72em; background:{color}18; color:{color}; padding:2px 8px;
                    border-radius:10px; border:1px solid {color}33; font-weight:500;">
                    {label.upper()} ({score:+.2f})
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
