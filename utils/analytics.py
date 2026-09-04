"""
analytics.py
------------
Computes summary statistics and builds Plotly charts for the wellness journal.

All functions accept a pd.DataFrame produced by data_manager.load_entries()
and return either a dict of stats or a plotly.graph_objs.Figure object.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# Palette — calm, non-clinical colours
# ---------------------------------------------------------------------------
COLOUR_MOOD = "#5B9BD5"
COLOUR_STRESS = "#ED7D31"
COLOUR_SLEEP_HRS = "#70AD47"
COLOUR_SLEEP_Q = "#9DC3E6"
CHART_BG = "#FAFAFA"
GRID_COLOUR = "#EBEBEB"


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _sort_by_date(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def _rolling_mean(series: pd.Series, window: int = 7) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()


# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------

def compute_summary(df: pd.DataFrame) -> dict:
    """
    Return a dict of scalar summary statistics over all available entries.

    Keys
    ----
    total_entries, avg_mood, avg_stress, avg_sleep_hours, avg_sleep_quality,
    min_mood, max_mood, min_stress, max_stress,
    min_sleep_hours, max_sleep_hours,
    date_range_start, date_range_end
    """
    if df.empty:
        return {}

    df = _sort_by_date(df)
    return {
        "total_entries": len(df),
        "avg_mood": round(df["mood"].mean(), 1),
        "avg_stress": round(df["stress"].mean(), 1),
        "avg_sleep_hours": round(df["sleep_hours"].mean(), 1),
        "avg_sleep_quality": round(df["sleep_quality"].mean(), 1),
        "min_mood": int(df["mood"].min()),
        "max_mood": int(df["mood"].max()),
        "min_stress": int(df["stress"].min()),
        "max_stress": int(df["stress"].max()),
        "min_sleep_hours": round(float(df["sleep_hours"].min()), 1),
        "max_sleep_hours": round(float(df["sleep_hours"].max()), 1),
        "date_range_start": df["date"].min().strftime("%B %d, %Y"),
        "date_range_end": df["date"].max().strftime("%B %d, %Y"),
    }


def compute_weekly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate entries by ISO calendar week.
    Returns a DataFrame with columns:
    week_start, avg_mood, avg_stress, avg_sleep_hours, avg_sleep_quality, entry_count
    """
    if df.empty:
        return pd.DataFrame()

    df = _sort_by_date(df)
    df["week_start"] = df["date"].dt.to_period("W").apply(lambda p: p.start_time)
    weekly = (
        df.groupby("week_start")
        .agg(
            avg_mood=("mood", "mean"),
            avg_stress=("stress", "mean"),
            avg_sleep_hours=("sleep_hours", "mean"),
            avg_sleep_quality=("sleep_quality", "mean"),
            entry_count=("mood", "count"),
        )
        .round(1)
        .reset_index()
    )
    return weekly


def compute_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate entries by calendar month.
    Returns a DataFrame with columns:
    month, avg_mood, avg_stress, avg_sleep_hours, avg_sleep_quality, entry_count
    """
    if df.empty:
        return pd.DataFrame()

    df = _sort_by_date(df)
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = (
        df.groupby("month")
        .agg(
            avg_mood=("mood", "mean"),
            avg_stress=("stress", "mean"),
            avg_sleep_hours=("sleep_hours", "mean"),
            avg_sleep_quality=("sleep_quality", "mean"),
            entry_count=("mood", "count"),
        )
        .round(1)
        .reset_index()
    )
    return monthly


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

def _apply_calm_layout(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        title=title,
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family="sans-serif", size=13, color="#333333"),
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOUR, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOUR, zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def chart_mood_trend(df: pd.DataFrame) -> go.Figure:
    """Line chart of daily mood with a 7-day rolling average."""
    df = _sort_by_date(df)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["mood"],
            mode="lines+markers",
            name="Mood",
            line=dict(color=COLOUR_MOOD, width=2),
            marker=dict(size=6),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=_rolling_mean(df["mood"]),
            mode="lines",
            name="7-day avg",
            line=dict(color=COLOUR_MOOD, width=2, dash="dash"),
        )
    )
    fig.update_yaxes(range=[0, 11], title_text="Rating (1–10)")
    return _apply_calm_layout(fig, "Mood Over Time")


def chart_stress_trend(df: pd.DataFrame) -> go.Figure:
    """Line chart of daily stress with a 7-day rolling average."""
    df = _sort_by_date(df)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["stress"],
            mode="lines+markers",
            name="Stress",
            line=dict(color=COLOUR_STRESS, width=2),
            marker=dict(size=6),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=_rolling_mean(df["stress"]),
            mode="lines",
            name="7-day avg",
            line=dict(color=COLOUR_STRESS, width=2, dash="dash"),
        )
    )
    fig.update_yaxes(range=[0, 11], title_text="Rating (1–10)")
    return _apply_calm_layout(fig, "Stress Over Time")


def chart_sleep_trend(df: pd.DataFrame) -> go.Figure:
    """Combined chart: sleep hours (bar) + sleep quality (line)."""
    df = _sort_by_date(df)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=df["date"],
            y=df["sleep_hours"],
            name="Sleep Hours",
            marker_color=COLOUR_SLEEP_HRS,
            opacity=0.75,
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["sleep_quality"],
            mode="lines+markers",
            name="Sleep Quality",
            line=dict(color=COLOUR_SLEEP_Q, width=2),
            marker=dict(size=6),
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Hours", secondary_y=False, range=[0, 14])
    fig.update_yaxes(title_text="Quality (1–10)", secondary_y=True, range=[0, 11])
    fig = _apply_calm_layout(fig, "Sleep Over Time")
    return fig


def chart_combined_overview(df: pd.DataFrame) -> go.Figure:
    """Single chart overlaying mood, stress, and sleep quality (all 1–10 scale)."""
    df = _sort_by_date(df)
    fig = go.Figure()
    for col, name, colour in [
        ("mood", "Mood", COLOUR_MOOD),
        ("stress", "Stress", COLOUR_STRESS),
        ("sleep_quality", "Sleep Quality", COLOUR_SLEEP_Q),
    ]:
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df[col],
                mode="lines+markers",
                name=name,
                line=dict(color=colour, width=2),
                marker=dict(size=5),
            )
        )
    fig.update_yaxes(range=[0, 11], title_text="Rating (1–10)")
    return _apply_calm_layout(fig, "Wellness Overview")


def chart_weekly_bar(weekly: pd.DataFrame) -> go.Figure:
    """Grouped bar chart of weekly averages."""
    if weekly.empty:
        return go.Figure()
    weekly["week_label"] = weekly["week_start"].dt.strftime("W/C %b %d")
    fig = go.Figure()
    for col, name, colour in [
        ("avg_mood", "Mood", COLOUR_MOOD),
        ("avg_stress", "Stress", COLOUR_STRESS),
        ("avg_sleep_quality", "Sleep Quality", COLOUR_SLEEP_Q),
    ]:
        fig.add_trace(
            go.Bar(x=weekly["week_label"], y=weekly[col], name=name, marker_color=colour)
        )
    fig.update_layout(barmode="group")
    fig.update_yaxes(range=[0, 11], title_text="Average Rating (1–10)")
    return _apply_calm_layout(fig, "Weekly Averages")


def chart_monthly_bar(monthly: pd.DataFrame) -> go.Figure:
    """Grouped bar chart of monthly averages."""
    if monthly.empty:
        return go.Figure()
    fig = go.Figure()
    for col, name, colour in [
        ("avg_mood", "Mood", COLOUR_MOOD),
        ("avg_stress", "Stress", COLOUR_STRESS),
        ("avg_sleep_quality", "Sleep Quality", COLOUR_SLEEP_Q),
    ]:
        fig.add_trace(
            go.Bar(x=monthly["month"], y=monthly[col], name=name, marker_color=colour)
        )
    fig.update_layout(barmode="group")
    fig.update_yaxes(range=[0, 11], title_text="Average Rating (1–10)")
    return _apply_calm_layout(fig, "Monthly Averages")
