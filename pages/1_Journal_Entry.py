"""
1_Journal_Entry.py
------------------
Daily wellness journal entry page.
"""

import sys
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

# Make the utils package importable when running as a page
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_manager import (
    save_entry,
    load_entries,
    get_entry_for_date,
)

# ---------------------------------------------------------------------------
# Helper label functions
# ---------------------------------------------------------------------------

def _mood_label(v: int) -> str:
    labels = {
        1: "😞 Very low", 2: "😟 Low", 3: "😕 Below average",
        4: "😐 Slightly low", 5: "🙂 Neutral", 6: "😊 Okay",
        7: "😄 Good", 8: "😁 Very good", 9: "🤩 Great", 10: "🥳 Excellent",
    }
    return labels.get(v, "")


def _stress_label(v: int) -> str:
    labels = {
        1: "😌 Very calm", 2: "🧘 Calm", 3: "😌 Mostly calm",
        4: "🙂 Mild stress", 5: "😐 Moderate", 6: "😟 Noticeable",
        7: "😰 High", 8: "😤 Very high", 9: "😩 Overwhelming", 10: "🔥 Extreme",
    }
    return labels.get(v, "")


def _sleep_label(v: int) -> str:
    labels = {
        1: "😴 Very poor", 2: "😪 Poor", 3: "😕 Below average",
        4: "😐 Fair", 5: "🙂 Okay", 6: "😊 Decent",
        7: "😄 Good", 8: "😁 Very good", 9: "🤩 Excellent", 10: "🥳 Perfect",
    }
    return labels.get(v, "")


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Journal Entry — Wellness Journal",
    page_icon="📓",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("📓 Daily Wellness Entry")
st.caption(
    "Record your mood, stress, sleep, and personal reflections. "
    "Your data stays private on your device."
)
st.divider()

# ---------------------------------------------------------------------------
# Date selector
# ---------------------------------------------------------------------------
today = date.today()
selected_date = st.date_input(
    "Entry date",
    value=today,
    max_value=today,
    help="You can backfill entries for previous days.",
)
date_str = selected_date.strftime("%Y-%m-%d")

# Check if an entry already exists for the selected date
existing = get_entry_for_date(date_str)
if existing:
    st.info(
        f"An entry already exists for **{selected_date.strftime('%B %d, %Y')}**. "
        "Submitting this form will **replace** that entry.",
        icon="ℹ️",
    )

# ---------------------------------------------------------------------------
# Pre-populate from existing entry (if editing)
# ---------------------------------------------------------------------------
default_mood = int(existing["mood"]) if existing else 5
default_stress = int(existing["stress"]) if existing else 5
default_sleep_h = float(existing["sleep_hours"]) if existing else 7.0
default_sleep_q = int(existing["sleep_quality"]) if existing else 5
default_notes = str(existing["notes"]) if existing else ""

# ---------------------------------------------------------------------------
# Entry form
# ---------------------------------------------------------------------------
with st.form("entry_form", clear_on_submit=False):
    st.subheader("How are you feeling today?")

    col1, col2 = st.columns(2)

    with col1:
        mood = st.slider(
            "Mood",
            min_value=1,
            max_value=10,
            value=default_mood,
            help="1 = Very low / sad   |   10 = Excellent / joyful",
        )
        st.caption(_mood_label(mood))

    with col2:
        stress = st.slider(
            "Stress level",
            min_value=1,
            max_value=10,
            value=default_stress,
            help="1 = Very calm   |   10 = Extremely stressed",
        )
        st.caption(_stress_label(stress))

    st.subheader("Sleep last night")
    col3, col4 = st.columns(2)

    with col3:
        sleep_hours = st.number_input(
            "Hours of sleep",
            min_value=0.0,
            max_value=24.0,
            value=default_sleep_h,
            step=0.5,
            format="%.1f",
        )

    with col4:
        sleep_quality = st.slider(
            "Sleep quality",
            min_value=1,
            max_value=10,
            value=default_sleep_q,
            help="1 = Very poor   |   10 = Excellent / refreshed",
        )
        st.caption(_sleep_label(sleep_quality))

    st.subheader("Personal journal notes")
    notes = st.text_area(
        "Write anything on your mind (optional)",
        value=default_notes,
        height=160,
        placeholder="Today I felt… Something that helped me was… I am grateful for…",
        help="Your notes are private and stored only on your device.",
    )

    submitted = st.form_submit_button(
        "💾 Save Entry", type="primary", use_container_width=True
    )

# ---------------------------------------------------------------------------
# Handle submission
# ---------------------------------------------------------------------------
if submitted:
    success, message = save_entry(
        date=date_str,
        mood=mood,
        stress=stress,
        sleep_hours=sleep_hours,
        sleep_quality=sleep_quality,
        notes=notes,
    )
    if success:
        st.success(f"✅ {message}", icon="✅")
        st.balloons()
    else:
        st.error(f"❌ {message}")

# ---------------------------------------------------------------------------
# Recent entries preview
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Recent entries")
df = load_entries()
if df.empty:
    st.info("No entries yet. Add your first entry above!", icon="📝")
else:
    df["date"] = pd.to_datetime(df["date"])
    recent = df.sort_values("date", ascending=False).head(5)
    for _, row in recent.iterrows():
        with st.expander(f"📅 {row['date'].strftime('%A, %B %d, %Y')}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Mood", f"{int(row['mood'])}/10")
            c2.metric("Stress", f"{int(row['stress'])}/10")
            c3.metric("Sleep", f"{row['sleep_hours']:.1f} hrs")
            c4.metric("Sleep Quality", f"{int(row['sleep_quality'])}/10")
            if row["notes"] and str(row["notes"]).strip():
                st.markdown("**Notes:**")
                st.write(row["notes"])
