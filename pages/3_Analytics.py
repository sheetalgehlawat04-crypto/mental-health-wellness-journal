"""
3_Analytics.py
--------------
Analytics dashboard: wellness trends, summaries, and pattern detection.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_manager import load_entries
from utils import analytics as an
from utils.pattern_detection import detect_patterns, DISCLAIMER

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Analytics — Wellness Journal",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Wellness Analytics")
st.caption(
    "Visualise your mood, stress, and sleep trends over time. "
    "All analytics are generated locally from your personal data."
)
st.divider()

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
df = load_entries()

if df.empty:
    st.info(
        "No journal entries yet. Head to **Journal Entry** to start tracking!",
        icon="📝",
    )
    st.stop()

# Need at least 2 entries for meaningful charts
if len(df) < 2:
    st.warning(
        "You have only 1 entry so far. Add a few more entries to see trends and charts.",
        icon="📈",
    )

# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------
summary = an.compute_summary(df)

st.subheader("Overall summary")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total entries", summary.get("total_entries", 0))
m2.metric("Avg mood", f"{summary.get('avg_mood', '—')}/10")
m3.metric("Avg stress", f"{summary.get('avg_stress', '—')}/10")
m4.metric("Avg sleep", f"{summary.get('avg_sleep_hours', '—')} hrs")
m5.metric("Avg sleep quality", f"{summary.get('avg_sleep_quality', '—')}/10")

if "date_range_start" in summary:
    st.caption(
        f"Data from **{summary['date_range_start']}** to **{summary['date_range_end']}**"
    )

st.divider()

# ---------------------------------------------------------------------------
# Pattern detection alerts
# ---------------------------------------------------------------------------
st.subheader("⚡ Wellness Pattern Flags")
result = detect_patterns(df)

st.info(result.disclaimer, icon="ℹ️")

if not result.has_concerns:
    st.success(
        "No concerning patterns detected in your recent entries. Keep it up!",
        icon="✅",
    )
else:
    for flag in result.flags:
        if flag.severity == "alert":
            container = st.error
            icon = "🚨"
        else:
            container = st.warning
            icon = "⚠️"

        with container(icon=icon):
            st.markdown(f"**{flag.title}**")
            st.markdown(flag.description)
            st.caption(f"Threshold rule: {flag.threshold_note}")

st.divider()

# ---------------------------------------------------------------------------
# Trend charts
# ---------------------------------------------------------------------------
st.subheader("Trends over time")

if len(df) >= 2:
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Mood", "Stress", "Sleep"])

    with tab1:
        st.plotly_chart(an.chart_combined_overview(df), use_container_width=True)

    with tab2:
        st.plotly_chart(an.chart_mood_trend(df), use_container_width=True)
        st.caption(
            "Dashed line = 7-day rolling average. "
            "Mood is rated 1 (very low) to 10 (excellent)."
        )

    with tab3:
        st.plotly_chart(an.chart_stress_trend(df), use_container_width=True)
        st.caption(
            "Dashed line = 7-day rolling average. "
            "Stress is rated 1 (very calm) to 10 (extremely stressed)."
        )

    with tab4:
        st.plotly_chart(an.chart_sleep_trend(df), use_container_width=True)
        st.caption(
            "Bars = sleep hours (left axis). "
            "Line = sleep quality rating 1–10 (right axis)."
        )
else:
    st.info("Add more entries to see trend charts.", icon="📈")

st.divider()

# ---------------------------------------------------------------------------
# Weekly summary
# ---------------------------------------------------------------------------
weekly = an.compute_weekly_summary(df)

st.subheader("Weekly averages")
if weekly.empty or len(weekly) < 1:
    st.info("Not enough data for weekly summaries yet.", icon="📅")
else:
    st.plotly_chart(an.chart_weekly_bar(weekly), use_container_width=True)

    with st.expander("View weekly data table"):
        disp = weekly.copy()
        disp["week_start"] = disp["week_start"].dt.strftime("%b %d, %Y")
        disp = disp.rename(
            columns={
                "week_start": "Week Starting",
                "avg_mood": "Avg Mood",
                "avg_stress": "Avg Stress",
                "avg_sleep_hours": "Avg Sleep (hrs)",
                "avg_sleep_quality": "Avg Sleep Quality",
                "entry_count": "Entries",
            }
        )
        st.dataframe(disp, use_container_width=True, hide_index=True)

st.divider()

# ---------------------------------------------------------------------------
# Monthly summary
# ---------------------------------------------------------------------------
monthly = an.compute_monthly_summary(df)

st.subheader("Monthly averages")
if monthly.empty or len(monthly) < 1:
    st.info("Not enough data for monthly summaries yet.", icon="📅")
else:
    st.plotly_chart(an.chart_monthly_bar(monthly), use_container_width=True)

    with st.expander("View monthly data table"):
        disp = monthly.rename(
            columns={
                "month": "Month",
                "avg_mood": "Avg Mood",
                "avg_stress": "Avg Stress",
                "avg_sleep_hours": "Avg Sleep (hrs)",
                "avg_sleep_quality": "Avg Sleep Quality",
                "entry_count": "Entries",
            }
        )
        st.dataframe(disp, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Footer note
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "📌 Analytics are derived from your local journal data only. "
    "No data is sent to any external server by the analytics module. "
    "Pattern flags are wellness indicators and are not medical diagnoses."
)
