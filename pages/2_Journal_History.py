"""
2_Journal_History.py
--------------------
Browse, review, and delete past journal entries.
"""

import sys
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_manager import load_entries, delete_entry

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Journal History — Wellness Journal",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Journal History")
st.caption("Review your past wellness entries. Your notes are private and stored only on your device.")
st.divider()

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
df = load_entries()

if df.empty:
    st.info(
        "No journal entries yet. Head to **Journal Entry** to record your first entry!",
        icon="📝",
    )
    st.stop()

df["date"] = pd.to_datetime(df["date"])
df_sorted = df.sort_values("date", ascending=False).reset_index(drop=True)

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
st.subheader("Filter entries")

col_a, col_b, col_c = st.columns(3)

min_date = df_sorted["date"].min().date()
max_date = df_sorted["date"].max().date()

with col_a:
    filter_start = st.date_input(
        "From date", value=min_date, min_value=min_date, max_value=max_date
    )
with col_b:
    filter_end = st.date_input(
        "To date", value=max_date, min_value=min_date, max_value=max_date
    )
with col_c:
    mood_filter = st.select_slider(
        "Minimum mood",
        options=list(range(1, 11)),
        value=1,
    )

# Apply filters
mask = (
    (df_sorted["date"].dt.date >= filter_start)
    & (df_sorted["date"].dt.date <= filter_end)
    & (df_sorted["mood"] >= mood_filter)
)
filtered = df_sorted[mask].reset_index(drop=True)

st.caption(f"Showing **{len(filtered)}** of **{len(df_sorted)}** entries.")
st.divider()

# ---------------------------------------------------------------------------
# Entry display
# ---------------------------------------------------------------------------
if filtered.empty:
    st.warning("No entries match the selected filters.", icon="🔍")
else:
    for _, row in filtered.iterrows():
        date_label = row["date"].strftime("%A, %B %d, %Y")

        with st.expander(f"📅 {date_label}  |  Mood {int(row['mood'])}/10  |  Stress {int(row['stress'])}/10"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("😊 Mood", f"{int(row['mood'])}/10")
            c2.metric("😰 Stress", f"{int(row['stress'])}/10")
            c3.metric("💤 Sleep", f"{row['sleep_hours']:.1f} hrs")
            c4.metric("⭐ Sleep Quality", f"{int(row['sleep_quality'])}/10")

            if row["notes"] and str(row["notes"]).strip():
                st.markdown("---")
                st.markdown("**📝 Personal notes:**")
                st.write(str(row["notes"]))
            else:
                st.caption("No notes for this entry.")

            st.markdown("---")
            date_str = row["date"].strftime("%Y-%m-%d")
            del_key = f"del_{date_str}"

            if st.button(
                f"🗑️ Delete entry for {row['date'].strftime('%b %d, %Y')}",
                key=del_key,
                type="secondary",
            ):
                success, msg = delete_entry(date_str)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Summary table")

display_df = filtered.copy()
display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
display_df = display_df.rename(
    columns={
        "date": "Date",
        "mood": "Mood",
        "stress": "Stress",
        "sleep_hours": "Sleep (hrs)",
        "sleep_quality": "Sleep Quality",
        "notes": "Notes",
        "entry_timestamp": "Saved At",
    }
)
# Truncate notes for table display
display_df["Notes"] = display_df["Notes"].apply(
    lambda x: (str(x)[:60] + "…") if isinstance(x, str) and len(str(x)) > 60 else x
)

st.dataframe(
    display_df[["Date", "Mood", "Stress", "Sleep (hrs)", "Sleep Quality", "Notes"]],
    use_container_width=True,
    hide_index=True,
)

# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Export data")
csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download entries as CSV",
    data=csv_data,
    file_name=f"wellness_journal_export_{date.today().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    help="Download your wellness data as a CSV file for personal records.",
)
st.caption(
    "Exported files contain your personal notes. Keep them in a secure location."
)
