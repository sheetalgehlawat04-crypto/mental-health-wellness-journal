"""
ai_insights.py
--------------
Handles all interactions with the Google Gemini 2.5 Flash model for the
Mental Health Wellness Journal.

IMPORTANT — SCOPE BOUNDARIES
------------------------------
The AI is used ONLY for appropriate wellness-support purposes:
  - Summarising journal entry trends in a non-clinical, reflective tone
  - Generating gentle, non-prescriptive wellness reflections
  - Offering broadly applicable self-care prompts based on aggregated patterns

The AI is explicitly instructed to:
  - NOT diagnose any mental health condition
  - NOT provide clinical treatment recommendations
  - NOT make specific medical or therapeutic claims
  - Recommend professional support when themes are concerning

All AI-generated text is clearly labelled as such in the UI.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# Load .env from project root (one level above utils/)
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

# ---------------------------------------------------------------------------
# Model setup
# ---------------------------------------------------------------------------

MODEL_NAME = "gemini-3.6-flash"

AI_DISCLAIMER = (
    "🤖 **AI-Generated Insight** — The text below is produced by an AI model "
    "(Google Gemini 2.5 Flash) and is intended for general wellness reflection only. "
    "It is **not** a medical diagnosis, clinical assessment, or professional mental "
    "health advice. Please consult a qualified healthcare provider for any health concerns."
)

_SYSTEM_PROMPT = """You are a compassionate wellness journal assistant.
Your role is to help users reflect on their mood, stress, and sleep patterns
in a gentle, non-clinical way.

Rules you MUST follow:
1. Do NOT diagnose any mental health conditions.
2. Do NOT recommend specific medications, clinical treatments, or therapy modalities.
3. Do NOT make definitive statements about a user's mental health status.
4. DO speak in a warm, calm, supportive tone.
5. DO acknowledge patterns you observe without catastrophising.
6. DO encourage professional support if themes appear consistently distressing.
7. Keep your response concise (150–250 words unless a longer summary is requested).
8. Use plain language suitable for a general audience.
"""


def _get_client():
    """Return a configured Gemini GenerativeModel or raise a clear error."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Please add your Gemini API key to the "
            ".env file (see .env.example for the format)."
        )
    try:
        import google.generativeai as genai  # lazy import
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=_SYSTEM_PROMPT,
        )
        return model
    except ImportError:
        raise ImportError(
            "google-generativeai package is not installed. "
            "Run: pip install google-generativeai"
        )


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def _build_trend_summary_prompt(df: pd.DataFrame) -> str:
    """Build a prompt summarising recent journal statistics for the AI."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").tail(14)  # last 14 entries max

    lines = [
        "Here are the user's recent wellness journal statistics (aggregated — "
        "no personally identifying information):\n"
    ]
    lines.append(f"Number of entries reviewed: {len(df)}")
    lines.append(f"Date range: {df['date'].min().strftime('%b %d')} to {df['date'].max().strftime('%b %d, %Y')}")
    lines.append(f"Average mood (1–10): {df['mood'].mean():.1f}")
    lines.append(f"Average stress (1–10): {df['stress'].mean():.1f}")
    lines.append(f"Average sleep hours: {df['sleep_hours'].mean():.1f}")
    lines.append(f"Average sleep quality (1–10): {df['sleep_quality'].mean():.1f}")
    lines.append(f"Mood range: {int(df['mood'].min())} – {int(df['mood'].max())}")
    lines.append(f"Stress range: {int(df['stress'].min())} – {int(df['stress'].max())}")

    lines.append(
        "\nPlease provide a brief, warm wellness reflection based on these patterns. "
        "Identify what is going well, note any areas that deserve gentle attention, "
        "and offer one or two broadly applicable self-care thoughts. "
        "Do not diagnose or prescribe."
    )
    return "\n".join(lines)


def _build_notes_summary_prompt(notes_list: list[str]) -> str:
    """Build a prompt for summarising anonymised journal note themes."""
    combined = "\n---\n".join(n for n in notes_list if n.strip())
    if not combined:
        return ""
    return (
        "The following are recent journal notes from a personal wellness journal. "
        "Please identify recurring themes, emotions, or topics in a gentle, "
        "reflective summary. Do not quote the notes directly. Do not diagnose. "
        "Keep your response to around 150 words.\n\n"
        f"Notes:\n{combined}"
    )


def _build_weekly_reflection_prompt(df: pd.DataFrame) -> str:
    """Build a prompt for a weekly wellness reflection."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").tail(7)

    if df.empty:
        return ""

    lines = [
        "Please write a short, encouraging weekly wellness reflection for someone "
        "based on the following data from their past 7 days:\n"
    ]
    for _, row in df.iterrows():
        lines.append(
            f"- {row['date'].strftime('%A %b %d')}: "
            f"Mood {int(row['mood'])}/10, Stress {int(row['stress'])}/10, "
            f"Sleep {row['sleep_hours']:.1f} hrs (quality {int(row['sleep_quality'])}/10)"
        )
    lines.append(
        "\nHighlight positive moments, acknowledge challenging days without alarm, "
        "and close with one gentle wellness suggestion. "
        "Tone: warm, calm, encouraging. Length: ~200 words."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_trend_summary(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Generate an AI wellness summary of the recent journal trends.

    Returns
    -------
    (success: bool, text: str)
    """
    if df.empty:
        return False, "No journal entries found. Add some entries first."
    try:
        model = _get_client()
        prompt = _build_trend_summary_prompt(df)
        response = model.generate_content(prompt)
        return True, response.text
    except EnvironmentError as e:
        return False, str(e)
    except Exception as e:
        return False, f"AI service error: {e}"


def generate_notes_themes(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Generate a thematic summary of the user's recent journal notes.

    Returns
    -------
    (success: bool, text: str)
    """
    if df.empty:
        return False, "No journal entries found."
    notes = df["notes"].dropna().tolist()
    notes = [n for n in notes if n.strip()]
    if not notes:
        return False, "No journal notes have been written yet."
    try:
        model = _get_client()
        prompt = _build_notes_summary_prompt(notes[-14:])  # last 14 entries
        if not prompt:
            return False, "No notes to summarise."
        response = model.generate_content(prompt)
        return True, response.text
    except EnvironmentError as e:
        return False, str(e)
    except Exception as e:
        return False, f"AI service error: {e}"


def generate_weekly_reflection(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Generate a weekly wellness reflection.

    Returns
    -------
    (success: bool, text: str)
    """
    if df.empty:
        return False, "No journal entries found."
    try:
        model = _get_client()
        prompt = _build_weekly_reflection_prompt(df)
        if not prompt:
            return False, "Not enough data for a weekly reflection."
        response = model.generate_content(prompt)
        return True, response.text
    except EnvironmentError as e:
        return False, str(e)
    except Exception as e:
        return False, f"AI service error: {e}"


def is_api_key_configured() -> bool:
    """Return True if a non-placeholder API key is present."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    return bool(api_key) and api_key != "your_gemini_api_key_here"
