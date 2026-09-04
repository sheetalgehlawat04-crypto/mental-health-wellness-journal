"""
pattern_detection.py
--------------------
Rule-based wellness pattern detection for the Mental Health Wellness Journal.

PURPOSE
-------
This module flags potentially concerning wellness patterns based on transparent,
documented thresholds.  These flags are WELLNESS INDICATORS ONLY and are NOT
medical diagnoses, clinical assessments, or professional mental health advice.
Users are encouraged to consult a qualified healthcare provider if they have
concerns about their mental health.

DOCUMENTED THRESHOLDS
---------------------
| Pattern                  | Threshold                                        |
|--------------------------|--------------------------------------------------|
| Sustained low mood       | Average mood <= 4 over the last 7 days with      |
|                          | at least 5 entries in that window                |
| Sustained high stress    | Average stress >= 7 over the last 7 days with    |
|                          | at least 5 entries in that window                |
| Chronic poor sleep       | Average sleep hours < 6 over the last 7 days     |
|                          | with at least 5 entries in that window           |
| Very low mood spike      | Any single entry with mood <= 2                  |
| Very high stress spike   | Any single entry with stress >= 9               |
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

import pandas as pd

# ---------------------------------------------------------------------------
# Threshold constants (change these to adjust sensitivity)
# ---------------------------------------------------------------------------

LOW_MOOD_THRESHOLD = 4          # avg mood at or below this → flag
HIGH_STRESS_THRESHOLD = 7       # avg stress at or above this → flag
LOW_SLEEP_HOURS_THRESHOLD = 6.0 # avg sleep hours below this → flag

LOW_MOOD_SPIKE = 2              # single-entry mood at or below this → spike flag
HIGH_STRESS_SPIKE = 9           # single-entry stress at or above this → spike flag

WINDOW_DAYS = 7                 # rolling window length
MIN_ENTRIES_IN_WINDOW = 5       # minimum entries required to trigger a sustained flag

DISCLAIMER = (
    "⚠️ **Disclaimer:** The patterns shown here are wellness indicators based on "
    "simple rule-based thresholds. They are **not** medical diagnoses, clinical "
    "assessments, or professional mental health advice. If you have concerns about "
    "your mental health, please consult a qualified healthcare provider."
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PatternFlag:
    """Represents a single detected wellness pattern."""
    pattern_id: str
    title: str
    description: str
    severity: str          # "info" | "warning" | "alert"
    threshold_note: str


@dataclass
class DetectionResult:
    flags: list[PatternFlag] = field(default_factory=list)
    disclaimer: str = DISCLAIMER
    window_days: int = WINDOW_DAYS
    entries_analysed: int = 0

    @property
    def has_concerns(self) -> bool:
        return len(self.flags) > 0

    @property
    def alert_count(self) -> int:
        return sum(1 for f in self.flags if f.severity == "alert")

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.flags if f.severity == "warning")


# ---------------------------------------------------------------------------
# Detection logic
# ---------------------------------------------------------------------------

def detect_patterns(df: pd.DataFrame) -> DetectionResult:
    """
    Analyse the journal entries DataFrame and return a DetectionResult with
    any triggered PatternFlag objects.

    Parameters
    ----------
    df : pd.DataFrame
        As returned by data_manager.load_entries().

    Returns
    -------
    DetectionResult
    """
    result = DetectionResult()

    if df.empty:
        return result

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")

    result.entries_analysed = len(df)

    # --- Recent window -------------------------------------------------------
    latest_date = df["date"].max()
    window_start = latest_date - timedelta(days=WINDOW_DAYS - 1)
    recent = df[df["date"] >= window_start]
    n_recent = len(recent)

    # --- Sustained low mood --------------------------------------------------
    if n_recent >= MIN_ENTRIES_IN_WINDOW:
        avg_mood = recent["mood"].mean()
        if avg_mood <= LOW_MOOD_THRESHOLD:
            result.flags.append(
                PatternFlag(
                    pattern_id="sustained_low_mood",
                    title="Sustained Low Mood Detected",
                    description=(
                        f"Your average mood over the last {WINDOW_DAYS} days is "
                        f"**{avg_mood:.1f}/10** ({n_recent} entries), which is at or "
                        f"below the low-mood threshold of {LOW_MOOD_THRESHOLD}/10."
                    ),
                    severity="alert",
                    threshold_note=(
                        f"Threshold: average mood ≤ {LOW_MOOD_THRESHOLD} over {WINDOW_DAYS} days "
                        f"with at least {MIN_ENTRIES_IN_WINDOW} entries."
                    ),
                )
            )

    # --- Sustained high stress -----------------------------------------------
    if n_recent >= MIN_ENTRIES_IN_WINDOW:
        avg_stress = recent["stress"].mean()
        if avg_stress >= HIGH_STRESS_THRESHOLD:
            result.flags.append(
                PatternFlag(
                    pattern_id="sustained_high_stress",
                    title="Sustained High Stress Detected",
                    description=(
                        f"Your average stress over the last {WINDOW_DAYS} days is "
                        f"**{avg_stress:.1f}/10** ({n_recent} entries), which is at or "
                        f"above the high-stress threshold of {HIGH_STRESS_THRESHOLD}/10."
                    ),
                    severity="alert",
                    threshold_note=(
                        f"Threshold: average stress ≥ {HIGH_STRESS_THRESHOLD} over {WINDOW_DAYS} days "
                        f"with at least {MIN_ENTRIES_IN_WINDOW} entries."
                    ),
                )
            )

    # --- Chronic poor sleep --------------------------------------------------
    if n_recent >= MIN_ENTRIES_IN_WINDOW:
        avg_sleep = recent["sleep_hours"].mean()
        if avg_sleep < LOW_SLEEP_HOURS_THRESHOLD:
            result.flags.append(
                PatternFlag(
                    pattern_id="chronic_poor_sleep",
                    title="Consistently Low Sleep Duration",
                    description=(
                        f"Your average sleep over the last {WINDOW_DAYS} days is "
                        f"**{avg_sleep:.1f} hours** ({n_recent} entries), which is below "
                        f"the recommended threshold of {LOW_SLEEP_HOURS_THRESHOLD} hours."
                    ),
                    severity="warning",
                    threshold_note=(
                        f"Threshold: average sleep < {LOW_SLEEP_HOURS_THRESHOLD} hours over "
                        f"{WINDOW_DAYS} days with at least {MIN_ENTRIES_IN_WINDOW} entries."
                    ),
                )
            )

    # --- Single-entry spikes -------------------------------------------------
    low_mood_entries = df[df["mood"] <= LOW_MOOD_SPIKE]
    if not low_mood_entries.empty:
        dates_str = ", ".join(
            low_mood_entries["date"].dt.strftime("%b %d").tolist()[-3:]
        )
        result.flags.append(
            PatternFlag(
                pattern_id="very_low_mood_spike",
                title="Very Low Mood Recorded",
                description=(
                    f"You recorded a mood of {LOW_MOOD_SPIKE}/10 or lower on: {dates_str}."
                ),
                severity="warning",
                threshold_note=(
                    f"Threshold: any single entry with mood ≤ {LOW_MOOD_SPIKE}."
                ),
            )
        )

    high_stress_entries = df[df["stress"] >= HIGH_STRESS_SPIKE]
    if not high_stress_entries.empty:
        dates_str = ", ".join(
            high_stress_entries["date"].dt.strftime("%b %d").tolist()[-3:]
        )
        result.flags.append(
            PatternFlag(
                pattern_id="very_high_stress_spike",
                title="Very High Stress Recorded",
                description=(
                    f"You recorded a stress level of {HIGH_STRESS_SPIKE}/10 or higher on: {dates_str}."
                ),
                severity="warning",
                threshold_note=(
                    f"Threshold: any single entry with stress ≥ {HIGH_STRESS_SPIKE}."
                ),
            )
        )

    return result
