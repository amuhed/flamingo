"""Flamingos - Albanian Diaspora Protest News Tracker"""

import sys
import os
import sqlite3

import streamlit as st
import pandas as pd

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.timeline import render_timeline
from ui.diaspora_map import render_map
from ui.foreign_media import render_foreign_media
from ui.comparative import render_comparative

DB_PATH = "data/flamingos.db"


st.set_page_config(
    page_title="Flamingos - Albanian Protest Tracker",
    page_icon="\U0001f9a9",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Flamingo Revolution color palette
# Pink: #E91E8C (primary), #FF69B4 (light), #C2185B (deep)
# Red: #E41E20 (Albanian flag red)
# Black: #1A1A2E (dark base)
# Blue: #2E5EAA (protest flag blue)
# Accents: #F8BBD0 (soft pink), #FCE4EC (blush bg)

st.markdown("""
<style>
    /* Base layout */
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .block-container { padding-top: 1rem; }

    /* Links in flamingo pink */
    a { color: #E91E8C !important; }
    a:hover { color: #FF69B4 !important; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(233, 30, 140, 0.05);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 24px;
        border-radius: 10px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #E91E8C, #C2185B) !important;
        color: white !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid rgba(233,30,140,0.18);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(233,30,140,0.06);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85em !important;
        color: #666 !important;
    }
    [data-testid="stMetricValue"] {
        color: #E91E8C !important;
        font-weight: 700 !important;
    }

    /* Selectbox and input styling */
    .stSelectbox > div > div,
    .stTextInput > div > div > input {
        border-color: rgba(233,30,140,0.2) !important;
        border-radius: 8px !important;
        background: white !important;
    }
    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div:focus-within {
        border-color: #E91E8C !important;
        box-shadow: 0 0 0 1px #E91E8C !important;
    }

    /* Dataframe styling */
    .stDataFrame { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# Header with flamingo branding
st.markdown("""
<div style="text-align:center; padding: 20px 0 24px 0;">
    <div style="font-size: 3em; margin-bottom: 4px;">
        \U0001f9a9
    </div>
    <h1 style="margin: 0; font-size: 2.4em;
        background: linear-gradient(135deg, #E91E8C, #E41E20);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;">
        Flamingos
    </h1>
    <p style="color:#777; font-size: 1.05em; margin-top: 4px;">
        Tracking Global Coverage of Albania's Flamingo Revolution
    </p>
    <div style="width:60px; height:3px; background: linear-gradient(90deg, #E91E8C, #2E5EAA);
        margin: 12px auto 0; border-radius: 2px;"></div>
</div>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def load_data():
    """Load articles from SQLite into a DataFrame."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM articles ORDER BY published_date DESC", conn)
    conn.close()
    return df


df = load_data()

# Summary metrics
if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Articles", len(df))
    with col2:
        albanian = len(df[df["category"] == "albanian_media"])
        st.metric("Albanian Media", albanian)
    with col3:
        foreign = len(df[df["category"] == "foreign_media"])
        st.metric("Foreign Media", foreign)
    with col4:
        langs = df["language"].nunique()
        st.metric("Languages", langs)

st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

# Tabs with flamingo emoji labels
tab1, tab2, tab3, tab4 = st.tabs([
    "\U0001f4f0  Timeline",
    "\U0001f30d  Diaspora Map",
    "\U0001f4ca  Foreign Media",
    "\U0001f50d  Comparative Analysis",
])

with tab1:
    render_timeline(df)

with tab2:
    render_map(df)

with tab3:
    render_foreign_media(df)

with tab4:
    render_comparative(df)

# Footer
st.markdown("""
<div style="margin-top: 40px; padding: 20px 0; border-top: 1px solid rgba(233,30,140,0.15);
    text-align:center; color:#777; font-size:0.8em;">
    <span style="font-size:1.2em;">\U0001f9a9</span><br>
    <strong style="color:#E91E8C;">Flamingos</strong> &mdash;
    Shqiperia nuk shitet &middot; Albania is not for sale<br>
    <span style="color:#999; font-size:0.9em; margin-top:4px; display:inline-block;">
        Data from public RSS feeds & Google News &middot;
        Translations via Google Translate &middot; Sentiment via VADER
    </span>
</div>
""", unsafe_allow_html=True)
