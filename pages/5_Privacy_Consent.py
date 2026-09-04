"""
5_Privacy_Consent.py
--------------------
Privacy information and therapist-sharing consent controls.
"""

import sys
from pathlib import Path
from datetime import datetime

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_manager import load_entries

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Privacy & Consent — Wellness Journal",
    page_icon="🔒",
    layout="centered",
)

st.title("🔒 Privacy & Consent")
st.caption("Understand how your data is stored and control what is shared.")
st.divider()

# ---------------------------------------------------------------------------
# Privacy information
# ---------------------------------------------------------------------------
st.subheader("How your data is stored")

st.markdown(
    """
**All data is stored locally on your device.**

- Your journal entries (mood, stress, sleep, and notes) are saved as a CSV file
  in the `data/` folder of this application on your computer.
- No data is automatically sent to any external server, cloud service,
  or third party.
- The only time data leaves your device is when **you** explicitly request an
  AI Insight (see the AI Insights page), in which case a statistical summary
  of your wellness scores is sent to the Google Gemini API.
  Your raw personal notes are sent only if you request the "Notes Themes" feature.

**You are in control.** You can:
- Delete individual entries on the **Journal History** page.
- Export your data as a CSV at any time from the **Journal History** page.
- Delete all data by removing the `data/journal_entries.csv` file from your device.

**There is no account registration, login, or cloud sync** in this application.
All processing happens on your machine.
"""
)

st.divider()

# ---------------------------------------------------------------------------
# Therapist sharing — optional, disabled by default
# ---------------------------------------------------------------------------
st.subheader("Therapist sharing (optional)")

st.info(
    "Sharing with a therapist is **optional and disabled by default.** "
    "No report is generated or considered shareable until you give explicit consent below.",
    icon="ℹ️",
)

# Use session state so the toggle persists within the session
if "therapist_sharing_consent" not in st.session_state:
    st.session_state.therapist_sharing_consent = False

consent = st.toggle(
    "I consent to generating a summary report suitable for sharing with my therapist",
    value=st.session_state.therapist_sharing_consent,
    help=(
        "Enabling this only creates a downloadable summary on this page. "
        "Nothing is sent anywhere automatically."
    ),
)
st.session_state.therapist_sharing_consent = consent

if consent:
    st.success(
        "Consent given. You can generate and download a summary report below.",
        icon="✅",
    )

    df = load_entries()

    if df.empty:
        st.warning("No journal entries available to include in the report.", icon="📝")
    else:
        import pandas as pd

        df["date"] = pd.to_datetime(df["date"])
        df_sorted = df.sort_values("date", ascending=False)

        # Date range selector for report
        st.markdown("**Select the date range for the report:**")
        min_d = df_sorted["date"].min().date()
        max_d = df_sorted["date"].max().date()

        rc1, rc2 = st.columns(2)
        with rc1:
            report_start = st.date_input("Report from", value=min_d, min_value=min_d, max_value=max_d, key="r_start")
        with rc2:
            report_end = st.date_input("Report to", value=max_d, min_value=min_d, max_value=max_d, key="r_end")

        report_df = df_sorted[
            (df_sorted["date"].dt.date >= report_start)
            & (df_sorted["date"].dt.date <= report_end)
        ]

        if report_df.empty:
            st.warning("No entries in the selected date range.", icon="📅")
        else:
            # Build plain-text report
            lines = [
                "MENTAL HEALTH WELLNESS JOURNAL — SUMMARY REPORT",
                "=" * 50,
                f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
                f"Period: {report_start.strftime('%B %d, %Y')} to {report_end.strftime('%B %d, %Y')}",
                f"Total entries: {len(report_df)}",
                "",
                "DISCLAIMER: This report is generated from a personal wellness journaling",
                "application. The data reflects self-reported wellness scores and personal",
                "notes. It is NOT a clinical assessment, medical diagnosis, or professional",
                "mental health evaluation. It is intended as supplementary context for",
                "discussion with a qualified healthcare provider.",
                "",
                "AVERAGES",
                "-" * 30,
                f"  Average mood (1–10):          {report_df['mood'].mean():.1f}",
                f"  Average stress (1–10):        {report_df['stress'].mean():.1f}",
                f"  Average sleep (hours):        {report_df['sleep_hours'].mean():.1f}",
                f"  Average sleep quality (1–10): {report_df['sleep_quality'].mean():.1f}",
                "",
                "ENTRY-BY-ENTRY LOG",
                "-" * 30,
            ]
            for _, row in report_df.sort_values("date").iterrows():
                lines.append(f"\nDate: {row['date'].strftime('%Y-%m-%d')}")
                lines.append(f"  Mood: {int(row['mood'])}/10  |  Stress: {int(row['stress'])}/10")
                lines.append(f"  Sleep: {row['sleep_hours']:.1f} hrs  |  Sleep quality: {int(row['sleep_quality'])}/10")
                if row["notes"] and str(row["notes"]).strip():
                    lines.append(f"  Notes: {str(row['notes'])}")

            lines += [
                "",
                "=" * 50,
                "END OF REPORT",
                "This report was generated by the Wellness Journal application.",
                "Pattern flags in this application use rule-based thresholds and are",
                "wellness indicators only — not medical diagnoses.",
            ]

            report_text = "\n".join(lines)
            report_filename = (
                f"wellness_report_{report_start.strftime('%Y%m%d')}_"
                f"{report_end.strftime('%Y%m%d')}.txt"
            )

            st.download_button(
                label="⬇️ Download Therapist Report (.txt)",
                data=report_text.encode("utf-8"),
                file_name=report_filename,
                mime="text/plain",
                type="primary",
            )
            st.caption(
                "The downloaded file contains your personal notes. "
                "Share it only with your chosen healthcare provider."
            )

else:
    st.warning(
        "Therapist sharing is currently **disabled**. "
        "Enable the toggle above if you would like to generate a shareable report.",
        icon="🔒",
    )

# ---------------------------------------------------------------------------
# Data disclaimer
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Important disclaimers")

st.markdown(
    """
**This application is for personal wellness tracking only.**

- It is **not** a medical device, clinical tool, or substitute for professional
  mental health care.
- Wellness pattern flags are based on simple rule-based thresholds and are
  **not** diagnoses of any mental health condition.
- AI-generated insights are produced by a general-purpose language model and
  are **not** clinical advice.
- If you are in crisis or need immediate help, please contact a qualified
  healthcare provider or an emergency service in your region.

**Resources:**
- 🆘 Crisis helpline (UK): **116 123** (Samaritans, free, 24/7)
- 🆘 Crisis helpline (US): **988** (Suicide & Crisis Lifeline)
- 🆘 Emergency services: **999** (UK) / **911** (US)
"""
)
