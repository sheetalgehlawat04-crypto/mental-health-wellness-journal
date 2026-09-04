"""
app.py
------
Main entry point for the Mental Health Wellness Journal application.

Run with:
    streamlit run app.py
"""

import sys
from pathlib import Path

import streamlit as st

# Ensure utils package is importable from all pages
sys.path.insert(0, str(Path(__file__).parent))

# ---------------------------------------------------------------------------
# Page & theme configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Wellness Journal",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": (
            "**Mental Health Wellness Journal**\n\n"
            "A private wellness journaling application for tracking mood, stress, "
            "and sleep. For personal use only — not a medical device.\n\n"
            "AI insights powered by Google Gemini 2.5 Flash."
        ),
    },
)

# ---------------------------------------------------------------------------
# Welcome page content
# ---------------------------------------------------------------------------
st.title("🌿 Mental Health Wellness Journal")
st.subheader("Your private space for daily wellbeing reflection")

st.markdown(
    """
Welcome! This application helps you track how you're feeling day-to-day,
visualise patterns over time, and — optionally — get gentle, AI-assisted
wellness reflections.

---

**Navigate using the sidebar** to access each section of the app:

| Page | What you'll find |
|---|---|
| 📓 **Journal Entry** | Record today's mood, stress, sleep, and notes |
| 📚 **Journal History** | Browse and review all past entries |
| 📊 **Analytics** | Trend charts, weekly & monthly summaries, pattern flags |
| 🤖 **AI Insights** | Gemini 2.5 Flash wellness reflections (requires API key) |
| 🔒 **Privacy & Consent** | Data storage info and optional therapist report |

---
"""
)

# ---------------------------------------------------------------------------
# Quick-start cards
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.info(
        "**📓 New entry?**\n\nHead to *Journal Entry* in the sidebar to log today's wellness.",
        icon="✏️",
    )

with col2:
    st.info(
        "**📊 Check your trends?**\n\nVisit *Analytics* to see your mood, stress, and sleep over time.",
        icon="📈",
    )

with col3:
    st.info(
        "**🤖 AI reflection?**\n\nGo to *AI Insights* after adding a few entries to get personalised reflections.",
        icon="✨",
    )

st.divider()

# ---------------------------------------------------------------------------
# Entry count summary (if data already exists)
# ---------------------------------------------------------------------------
try:
    from utils.data_manager import load_entries
    df = load_entries()
    if not df.empty:
        import pandas as pd
        df["date"] = pd.to_datetime(df["date"])
        latest = df.sort_values("date").iloc[-1]
        st.success(
            f"You have **{len(df)}** journal {'entry' if len(df) == 1 else 'entries'}. "
            f"Most recent: **{latest['date'].strftime('%B %d, %Y')}** — "
            f"Mood {int(latest['mood'])}/10, Stress {int(latest['stress'])}/10.",
            icon="🌱",
        )
    else:
        st.info(
            "No entries yet — click **Journal Entry** in the sidebar to get started!",
            icon="🌱",
        )
except Exception:
    pass

# ---------------------------------------------------------------------------
# Disclaimer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "⚠️ This application is for personal wellness tracking only. "
    "It is not a medical device, clinical assessment tool, or substitute for "
    "professional mental health care. If you are in crisis, please contact "
    "emergency services or a crisis helpline."
)
