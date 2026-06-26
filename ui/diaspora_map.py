"""Diaspora map view showing protest coverage by city."""

import html as html_mod
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from pipeline.sources import DIASPORA_CITIES

# Flamingo palette for map
PINK = "#E91E8C"
RED = "#E41E20"
BLUE = "#2E5EAA"
SOFT_PINK = "#F8BBD0"


def render_map(df):
    """Render the diaspora map tab."""
    st.markdown("""
    <h2 style="margin-bottom:2px;">
        <span style="color:#E91E8C;">\U0001f30d</span> Diaspora Map
    </h2>
    <p style="color:#777; font-size:0.9em; margin-top:0;">
        Albanian communities worldwide standing in solidarity &mdash; from five continents
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

    # Count articles per diaspora city
    city_articles = df[df["diaspora_city"].notna()].groupby("diaspora_city").agg(
        article_count=("id", "count"),
        avg_sentiment=("sentiment_score", "mean"),
    ).reset_index()

    # Build map — warm-toned tiles
    m = folium.Map(
        location=[42.0, 15.0],
        zoom_start=4,
        tiles="CartoDB positron",
    )

    for city_info in DIASPORA_CITIES:
        city = city_info["city"]
        is_tirana = city == "Tirana"
        match = city_articles[city_articles["diaspora_city"] == city]

        if is_tirana:
            # Tirana gets a special flamingo-pink pulsing marker
            folium.CircleMarker(
                location=[city_info["lat"], city_info["lon"]],
                radius=18,
                tooltip="<b>Tirana</b> — Epicenter of the Flamingo Revolution",
                color=PINK,
                fill=True,
                fill_color=PINK,
                fill_opacity=0.4,
                weight=3,
            ).add_to(m)
            folium.CircleMarker(
                location=[city_info["lat"], city_info["lon"]],
                radius=8,
                color=RED,
                fill=True,
                fill_color=RED,
                fill_opacity=0.8,
                weight=2,
            ).add_to(m)
            continue

        if not match.empty:
            count = int(match.iloc[0]["article_count"])
            avg_sent = float(match.iloc[0]["avg_sentiment"])
            radius = min(max(count * 3, 8), 30)

            # Get articles for popup
            city_df = df[df["diaspora_city"] == city].sort_values(
                "published_date", ascending=False
            ).head(5)
            popup_html = f"""
            <div style="font-family:sans-serif; min-width:200px;">
                <div style="font-size:14px; font-weight:bold; color:#E91E8C; margin-bottom:4px;">
                    \U0001f9a9 {city}
                </div>
                <div style="font-size:12px; color:#666; margin-bottom:8px;">
                    {count} articles &middot; Sentiment: {avg_sent:+.2f}
                </div>
                <hr style="border:none; border-top:1px solid #eee; margin:4px 0;">
            """
            for _, row in city_df.iterrows():
                title = html_mod.escape((row.get("title_en") or row.get("title", ""))[:55])
                popup_html += f'<div style="font-size:11px; margin:3px 0;"><a href="{row["url"]}" target="_blank" style="color:#E91E8C;">{title}</a></div>'
            popup_html += "</div>"

            # Pink circles for diaspora cities
            folium.CircleMarker(
                location=[city_info["lat"], city_info["lon"]],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"\U0001f9a9 {city}: {count} articles",
                color=PINK,
                fill=True,
                fill_color=PINK,
                fill_opacity=0.5,
                weight=2,
            ).add_to(m)
        else:
            # Dim cities with no coverage yet
            pop_est = city_info.get("population_est")
            tooltip = f"{city} (est. {pop_est:,} Albanians)" if pop_est else city
            folium.CircleMarker(
                location=[city_info["lat"], city_info["lon"]],
                radius=6,
                tooltip=tooltip,
                color=SOFT_PINK,
                fill=True,
                fill_color=SOFT_PINK,
                fill_opacity=0.2,
                weight=1,
            ).add_to(m)

    st_folium(m, width=None, height=520, use_container_width=True)

    # Stats below map
    if not city_articles.empty:
        st.markdown("""
        <h3 style="color:#E91E8C; margin-top:16px;">\U0001f4ca Coverage by City</h3>
        """, unsafe_allow_html=True)

        display = city_articles.sort_values("article_count", ascending=False).copy()
        display.columns = ["City", "Articles", "Avg Sentiment"]
        display["Avg Sentiment"] = display["Avg Sentiment"].apply(lambda x: f"{x:+.2f}")
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("No articles have been matched to specific diaspora cities yet.")

    # Diaspora articles feed
    diaspora_df = df[df["diaspora_city"].notna()].sort_values("published_date", ascending=False)
    if not diaspora_df.empty:
        st.markdown(f"""
        <h3 style="color:#E91E8C; margin-top:16px;">
            \U0001f9a9 Diaspora Coverage ({len(diaspora_df)} articles)
        </h3>
        """, unsafe_allow_html=True)

        for _, row in diaspora_df.head(20).iterrows():
            city = html_mod.escape(row["diaspora_city"])
            title = html_mod.escape(row.get("title_en") or row.get("title", "Untitled"))
            source = html_mod.escape(row.get("source_name", ""))
            url = row.get("url", "#")
            st.markdown(
                f'<div style="padding:6px 0; border-bottom:1px solid rgba(233,30,140,0.1);">'
                f'<span style="color:#E91E8C; font-weight:600;">\U0001f4cd {city}</span> &mdash; '
                f'<a href="{url}" target="_blank" style="color:inherit !important; text-decoration:none;">{title}</a> '
                f'<span style="color:#777; font-size:0.8em;">({source})</span></div>',
                unsafe_allow_html=True,
            )
