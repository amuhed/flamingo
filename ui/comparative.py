"""Comparative view: Albanian media vs foreign media framing."""

import html as html_mod
import json
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pipeline.sources import COUNTRY_NAMES

PINK = "#E91E8C"
RED = "#E41E20"
BLUE = "#2E5EAA"

THEME_LABELS = {
    "environmental": "Environmental",
    "anti_corruption": "Anti-Corruption",
    "democratic_opposition": "Democratic Opposition",
    "kushner_trump": "Kushner / Trump",
    "violence_crackdown": "Violence & Crackdown",
    "diaspora_solidarity": "Diaspora Solidarity",
    "economic": "Economic",
    "international_response": "International Response",
    "media_misinformation": "Media & Misinformation",
    "off_topic": "Off-Topic",
}

THEME_COLORS = {
    "environmental": "#4CAF50",
    "anti_corruption": "#FF9800",
    "democratic_opposition": "#2E5EAA",
    "kushner_trump": "#E41E20",
    "violence_crackdown": "#9C27B0",
    "diaspora_solidarity": "#E91E8C",
    "economic": "#00BCD4",
    "international_response": "#607D8B",
    "media_misinformation": "#795548",
    "off_topic": "#BDBDBD",
}


def _explode_themes(df):
    """Expand the themes JSON column into individual rows."""
    rows = []
    for _, row in df.iterrows():
        themes_raw = row.get("themes", "[]")
        try:
            themes = json.loads(themes_raw) if isinstance(themes_raw, str) else themes_raw
        except (json.JSONDecodeError, TypeError):
            themes = []
        for theme in themes:
            rows.append({"theme": theme, "category": row["category"],
                         "source_country": row.get("source_country", ""),
                         "date": row.get("date", None)})
    return pd.DataFrame(rows)


def render_comparative(df):
    """Render the comparative analysis tab."""
    st.markdown("""
    <h2 style="margin-bottom:2px;">
        <span style="color:#E91E8C;">\U0001f50d</span> Comparative Analysis
    </h2>
    <p style="color:#777; font-size:0.9em; margin-top:0;">
        How Albanian and foreign media frame the same protests differently
    </p>
    """, unsafe_allow_html=True)

    if df.empty or "primary_frame" not in df.columns:
        st.info("Theme tagging hasn't been run yet. Run the pipeline first.")
        return

    tagged = df[df["primary_frame"].notna() & (df["primary_frame"] != "off_topic")].copy()
    if tagged.empty:
        st.info("No tagged articles found.")
        return

    tagged["date"] = pd.to_datetime(tagged["published_date"], errors="coerce")

    albanian = tagged[tagged["category"] == "albanian_media"]
    foreign = tagged[tagged["category"] == "foreign_media"]

    # --- Side-by-side primary frame distribution ---
    st.markdown(f'<h3 style="color:{PINK};">Primary Framing: Albanian vs Foreign Media</h3>',
                unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#777; font-size:0.85em;">What angle does each media ecosystem lead with?</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    for col, subset, label in [(col1, albanian, "Albanian Media"), (col2, foreign, "Foreign Media")]:
        with col:
            if subset.empty:
                st.info(f"No {label} articles tagged.")
                continue
            frame_counts = subset["primary_frame"].value_counts().reset_index()
            frame_counts.columns = ["frame", "count"]
            frame_counts["label"] = frame_counts["frame"].map(
                lambda x: THEME_LABELS.get(x, x))
            frame_counts["pct"] = (frame_counts["count"] / frame_counts["count"].sum() * 100).round(1)
            frame_counts = frame_counts.sort_values("count", ascending=True)

            colors = [THEME_COLORS.get(f, "#999") for f in frame_counts["frame"]]

            fig = go.Figure(go.Bar(
                x=frame_counts["count"],
                y=frame_counts["label"],
                orientation="h",
                marker_color=colors,
                text=frame_counts.apply(lambda r: f"{r['count']} ({r['pct']}%)", axis=1),
                textposition="auto",
            ))
            fig.update_layout(
                template="plotly_white",
                height=350,
                margin=dict(l=10, r=10, t=30, b=10),
                title=dict(text=f"{label} ({len(subset)} articles)", font=dict(size=14)),
                xaxis_title="",
                yaxis_title="",
            )
            st.plotly_chart(fig, use_container_width=True)

    # --- Key divergences ---
    st.markdown(f'<h3 style="color:{PINK};">Framing Divergence</h3>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#777; font-size:0.85em;">Where Albanian and foreign media disagree most on emphasis</p>',
        unsafe_allow_html=True,
    )

    if not albanian.empty and not foreign.empty:
        al_pct = (albanian["primary_frame"].value_counts(normalize=True) * 100).to_dict()
        fo_pct = (foreign["primary_frame"].value_counts(normalize=True) * 100).to_dict()

        all_frames = sorted(set(list(al_pct.keys()) + list(fo_pct.keys())))
        divergence = []
        for frame in all_frames:
            if frame == "off_topic":
                continue
            al_val = al_pct.get(frame, 0)
            fo_val = fo_pct.get(frame, 0)
            divergence.append({
                "frame": frame,
                "label": THEME_LABELS.get(frame, frame),
                "Albanian Media %": round(al_val, 1),
                "Foreign Media %": round(fo_val, 1),
                "Difference": round(al_val - fo_val, 1),
            })

        div_df = pd.DataFrame(divergence).sort_values("Difference")

        fig_div = go.Figure()
        fig_div.add_trace(go.Bar(
            y=div_df["label"],
            x=div_df["Albanian Media %"],
            name="Albanian Media",
            orientation="h",
            marker_color=RED,
            opacity=0.8,
        ))
        fig_div.add_trace(go.Bar(
            y=div_df["label"],
            x=div_df["Foreign Media %"],
            name="Foreign Media",
            orientation="h",
            marker_color=BLUE,
            opacity=0.8,
        ))
        fig_div.update_layout(
            template="plotly_white",
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),
            barmode="group",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis_title="% of articles",
            yaxis_title="",
        )
        st.plotly_chart(fig_div, use_container_width=True)

    # --- Framing over time ---
    st.markdown(f'<h3 style="color:{PINK};">Framing Over Time</h3>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#777; font-size:0.85em;">How dominant narratives shift as events unfold</p>',
        unsafe_allow_html=True,
    )

    time_source = st.radio(
        "Show:", ["All Media", "Albanian Media", "Foreign Media"],
        horizontal=True, key="comp_time_source",
    )

    if time_source == "Albanian Media":
        time_df = albanian
    elif time_source == "Foreign Media":
        time_df = foreign
    else:
        time_df = tagged

    if not time_df.empty:
        time_df = time_df.dropna(subset=["date"])
        time_df["date_day"] = time_df["date"].dt.date

        daily_frames = time_df.groupby(["date_day", "primary_frame"]).size().reset_index(name="count")
        daily_frames["date_day"] = pd.to_datetime(daily_frames["date_day"])
        daily_frames["label"] = daily_frames["primary_frame"].map(
            lambda x: THEME_LABELS.get(x, x))

        color_map = {THEME_LABELS.get(k, k): v for k, v in THEME_COLORS.items()}

        fig_time = px.area(
            daily_frames, x="date_day", y="count", color="label",
            labels={"date_day": "Date", "count": "Articles", "label": "Frame"},
            color_discrete_map=color_map,
        )
        fig_time.update_layout(
            template="plotly_white",
            height=400,
            margin=dict(l=20, r=20, t=10, b=20),
            xaxis_title="",
            yaxis_title="Articles per day",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig_time, use_container_width=True)

    # --- Country-level framing ---
    st.markdown(f'<h3 style="color:{PINK};">How Different Countries Frame the Protests</h3>',
                unsafe_allow_html=True)

    country_frames = foreign.groupby(["source_country", "primary_frame"]).size().reset_index(name="count")
    if not country_frames.empty:
        # Only show countries with 5+ articles
        country_totals = country_frames.groupby("source_country")["count"].sum()
        big_countries = country_totals[country_totals >= 5].index
        country_frames = country_frames[country_frames["source_country"].isin(big_countries)]

        country_frames["country_name"] = country_frames["source_country"].map(
            lambda x: COUNTRY_NAMES.get(x, x))
        country_frames["label"] = country_frames["primary_frame"].map(
            lambda x: THEME_LABELS.get(x, x))

        # Normalize to percentages
        totals = country_frames.groupby("country_name")["count"].transform("sum")
        country_frames["pct"] = (country_frames["count"] / totals * 100).round(1)

        color_map = {THEME_LABELS.get(k, k): v for k, v in THEME_COLORS.items()}

        fig_cf = px.bar(
            country_frames, x="country_name", y="pct", color="label",
            labels={"country_name": "Country", "pct": "% of articles", "label": "Frame"},
            color_discrete_map=color_map,
        )
        fig_cf.update_layout(
            template="plotly_white",
            height=450,
            margin=dict(l=20, r=20, t=10, b=20),
            barmode="stack",
            xaxis_title="",
            yaxis_title="% of articles",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig_cf, use_container_width=True)

    # --- Key takeaways box ---
    if not albanian.empty and not foreign.empty:
        st.markdown(f'<h3 style="color:{PINK};">Key Observations</h3>', unsafe_allow_html=True)

        al_top = albanian["primary_frame"].mode().iloc[0] if not albanian.empty else "N/A"
        fo_top = foreign["primary_frame"].mode().iloc[0] if not foreign.empty else "N/A"

        al_top_label = THEME_LABELS.get(al_top, al_top)
        fo_top_label = THEME_LABELS.get(fo_top, fo_top)

        al_kushner_pct = al_pct.get("kushner_trump", 0)
        fo_kushner_pct = fo_pct.get("kushner_trump", 0)

        st.markdown(f"""
        <div style="background:white; border:1px solid rgba(233,30,140,0.15); border-radius:10px;
            padding:16px 20px; line-height:1.7; color:#444;">
            <strong style="color:{RED};">Albanian media</strong> primarily frames the protests as
            <strong>{html_mod.escape(al_top_label)}</strong>, while
            <strong style="color:{BLUE};">foreign media</strong> leads with
            <strong>{html_mod.escape(fo_top_label)}</strong>.<br>
            The Kushner/Trump angle accounts for <strong>{fo_kushner_pct:.0f}%</strong> of foreign coverage
            vs <strong>{al_kushner_pct:.0f}%</strong> in Albanian media.<br>
            <em style="color:#999;">These frames reflect editorial emphasis, not article quality or accuracy.</em>
        </div>
        """, unsafe_allow_html=True)
