"""
data_manager.py
---------------
Handles all local data persistence for the Mental Health Wellness Journal.

Storage:  A single CSV file located at  data/journal_entries.csv
          relative to the project root.  The file is created automatically
          on first use.

Schema
------
date            : str  (YYYY-MM-DD)
mood            : int  (1–10)
stress          : int  (1–10)
sleep_hours     : float (0.0–24.0)
sleep_quality   : int  (1–10)
notes           : str  (free text, may be empty)
entry_timestamp : str  (ISO-8601 datetime of when the record was saved)
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_FILE = DATA_DIR / "journal_entries.csv"

COLUMNS = [
    "date",
    "mood",
    "stress",
    "sleep_hours",
    "sleep_quality",
    "notes",
    "entry_timestamp",
]

NUMERIC_COLS = ["mood", "stress", "sleep_hours", "sleep_quality"]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_data_dir() -> None:
    """Create the data directory if it does not already exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _empty_df() -> pd.DataFrame:
    """Return an empty DataFrame with the correct schema."""
    return pd.DataFrame(columns=COLUMNS)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_entries() -> pd.DataFrame:
    """
    Load all journal entries from disk.

    Returns
    -------
    pd.DataFrame
        DataFrame with all historical entries.  Returns an empty DataFrame
        (with correct columns) if no data file exists yet.
    """
    _ensure_data_dir()
    if not DATA_FILE.exists():
        return _empty_df()

    try:
        df = pd.read_csv(DATA_FILE, dtype={"notes": str})
        # Coerce numeric columns; invalid values become NaN
        for col in NUMERIC_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        # Parse date column
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime(
                "%Y-%m-%d"
            )
        # Fill missing notes with empty string
        df["notes"] = df["notes"].fillna("")
        # Drop rows where all key numeric fields are NaN (corrupt rows)
        df = df.dropna(subset=["mood", "stress", "sleep_hours", "sleep_quality"], how="all")
        return df.reset_index(drop=True)
    except Exception:
        # If the file is unreadable/corrupt, return empty so the app still works
        return _empty_df()


def save_entry(
    date: str,
    mood: int,
    stress: int,
    sleep_hours: float,
    sleep_quality: int,
    notes: str,
) -> tuple[bool, str]:
    """
    Save a single journal entry to disk.

    Parameters
    ----------
    date          : Entry date as 'YYYY-MM-DD'
    mood          : Mood rating 1–10
    stress        : Stress rating 1–10
    sleep_hours   : Sleep duration in hours (0–24)
    sleep_quality : Sleep quality rating 1–10
    notes         : Free-text journal notes

    Returns
    -------
    (success: bool, message: str)
    """
    _ensure_data_dir()

    # --- Validation -----------------------------------------------------------
    errors = []
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        errors.append("Date is not in YYYY-MM-DD format.")

    if not (1 <= int(mood) <= 10):
        errors.append("Mood must be between 1 and 10.")
    if not (1 <= int(stress) <= 10):
        errors.append("Stress must be between 1 and 10.")
    if not (0.0 <= float(sleep_hours) <= 24.0):
        errors.append("Sleep hours must be between 0 and 24.")
    if not (1 <= int(sleep_quality) <= 10):
        errors.append("Sleep quality must be between 1 and 10.")

    if errors:
        return False, "Validation errors: " + "; ".join(errors)

    # --- Build new row --------------------------------------------------------
    new_row = pd.DataFrame(
        [
            {
                "date": date,
                "mood": int(mood),
                "stress": int(stress),
                "sleep_hours": float(sleep_hours),
                "sleep_quality": int(sleep_quality),
                "notes": str(notes).strip(),
                "entry_timestamp": datetime.now().isoformat(timespec="seconds"),
            }
        ]
    )

    # --- Append or create file -----------------------------------------------
    if DATA_FILE.exists():
        existing = load_entries()
        # Remove any existing entry for the same date (allow re-entry for a day)
        existing = existing[existing["date"] != date]
        combined = pd.concat([existing, new_row], ignore_index=True)
    else:
        combined = new_row

    combined.to_csv(DATA_FILE, index=False)
    return True, f"Entry for {date} saved successfully."


def delete_entry(date: str) -> tuple[bool, str]:
    """
    Delete the entry for a given date.

    Returns
    -------
    (success: bool, message: str)
    """
    df = load_entries()
    if df.empty or date not in df["date"].values:
        return False, f"No entry found for {date}."
    df = df[df["date"] != date]
    df.to_csv(DATA_FILE, index=False)
    return True, f"Entry for {date} deleted."


def get_entry_for_date(date: str) -> dict | None:
    """Return the entry dict for a given date, or None if not found."""
    df = load_entries()
    rows = df[df["date"] == date]
    if rows.empty:
        return None
    return rows.iloc[0].to_dict()


def entry_exists_for_today() -> bool:
    """Return True if an entry already exists for today's date."""
    today = datetime.now().strftime("%Y-%m-%d")
    return get_entry_for_date(today) is not None
