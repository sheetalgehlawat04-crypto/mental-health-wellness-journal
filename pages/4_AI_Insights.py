"""
4_AI_Insights.py
----------------
AI-powered wellness insights page using Google Gemini 2.5 Flash.

All AI outputs are clearly labelled and include a disclaimer.
The AI is used only for wellness reflection — not medical diagnosis.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_manager import load_entries
from utils.ai_insights import (
    generate_trend_summary,
    generate_notes_themes,
    generate_weekly_reflection,
    is_api_key_configured,
    AI_DISCLAIMER,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Insights — Wellness Journal",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 AI Wellness Insights")
st.caption(
    "Gemini 2.5 Flash generates gentle, reflective wellness summaries based on "
    "your journal data. These insights are for personal reflection only."
)
st.divider()

# ---------------------------------------------------------------------------
# API key status check
# ---------------------------------------------------------------------------
if not is_api_key_configured():
    st.warning(
        "**Gemini API key not configured.**\n\n"
        "To use AI Insights, add your Gemini API key to the `.env` file in the "
        "project root:\n\n"
        "```\nGEMINI_API_KEY=your_actual_key_here\n```\n\n"
        "Then restart the Streamlit app. You can get a free API key at "
        "[Google AI Studio](https://aistudio.google.com/app/apikey).",
        icon="🔑",
    )

# ---------------------------------------------------------------------------
# AI disclaimer (always visible)
# ---------------------------------------------------------------------------
st.info(AI_DISCLAIMER)
st.divider()

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
df = load_entries()

if df.empty:
    st.info(
        "No journal entries found. Add entries on the **Journal Entry** page first.",
        icon="📝",
    )
    st.stop()

entry_count = len(df)
st.caption(f"Using {entry_count} journal {'entry' if entry_count == 1 else 'entries'} as context.")

# ---------------------------------------------------------------------------
# Section 1 — Trend summary
# ---------------------------------------------------------------------------
st.subheader("📈 Wellness Trend Summary")
st.write(
    "Get an AI-generated reflection on your mood, stress, and sleep patterns "
    "from your recent journal entries."
)

if st.button("✨ Generate Trend Summary", type="primary", disabled=not is_api_key_configured()):
    with st.spinner("Gemini is reflecting on your wellness data…"):
        success, text = generate_trend_summary(df)
    if success:
        st.success("Trend summary generated.", icon="✅")
        st.markdown(text)
    else:
        st.error(f"Could not generate summary: {text}", icon="❌")

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Journal notes themes
# ---------------------------------------------------------------------------
st.subheader("📝 Journal Notes Themes")
st.write(
    "Discover recurring themes and emotions in your journal notes. "
    "The AI will NOT quote your notes directly — it identifies patterns only."
)

notes_available = df["notes"].dropna().apply(lambda x: str(x).strip()).any()

if not notes_available:
    st.info("No journal notes written yet. Add notes in your entries to use this feature.", icon="📓")
else:
    if st.button(
        "🔍 Identify Themes in My Notes",
        type="primary",
        disabled=not is_api_key_configured(),
    ):
        with st.spinner("Gemini is reading your journal themes…"):
            success, text = generate_notes_themes(df)
        if success:
            st.success("Theme summary generated.", icon="✅")
            st.markdown(text)
        else:
            st.error(f"Could not generate themes: {text}", icon="❌")

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Weekly reflection
# ---------------------------------------------------------------------------
st.subheader("🗓️ Weekly Wellness Reflection")
st.write(
    "Get a personalised weekly reflection covering the last 7 days of entries. "
    "Highlights good moments and gently acknowledges challenging ones."
)

import pandas as pd
df_dated = df.copy()
df_dated["date"] = pd.to_datetime(df_dated["date"])
last_7 = df_dated.sort_values("date").tail(7)
week_count = len(last_7)

st.caption(f"Last {week_count} entries will be used for the weekly reflection.")

if week_count < 3:
    st.warning("Add at least 3 entries to get a meaningful weekly reflection.", icon="📅")
else:
    if st.button(
        "🌟 Generate Weekly Reflection",
        type="primary",
        disabled=not is_api_key_configured(),
    ):
        with st.spinner("Gemini is writing your weekly reflection…"):
            success, text = generate_weekly_reflection(df)
        if success:
            st.success("Weekly reflection generated.", icon="✅")
            st.markdown(text)
        else:
            st.error(f"Could not generate reflection: {text}", icon="❌")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "🔒 **Privacy note:** When you request an AI insight, a statistical summary "
    "of your wellness data (averages and ranges — not your raw notes) is sent to "
    "the Google Gemini API. For Notes Themes, anonymised note text is sent. "
    "No personally identifying information is included. "
    "AI requests are only made when you click a button above."
)
