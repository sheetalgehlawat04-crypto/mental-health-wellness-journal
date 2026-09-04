# 🌿 Mental Health Wellness Journal

A private, AI-assisted wellness journaling application built with **Streamlit** and **Google Gemini 2.5 Flash**.

> **Disclaimer:** This application is for personal wellness tracking only. It is not a medical device, clinical assessment tool, or substitute for professional mental health care. All pattern flags are wellness indicators and are not medical diagnoses. If you are in crisis, please contact emergency services or a crisis helpline.

---

## Features

| Feature | Description |
|---|---|
| 📓 Daily Entry | Log mood (1–10), stress (1–10), sleep hours, sleep quality, and personal notes |
| 📚 Journal History | Browse, filter, and delete past entries; export as CSV |
| 📊 Analytics | Trend charts, 7-day rolling averages, weekly & monthly summaries |
| ⚡ Pattern Detection | Rule-based flags for sustained low mood, high stress, and poor sleep |
| 🤖 AI Insights | Gemini 2.5 Flash wellness trend summary, note themes, and weekly reflection |
| 🔒 Privacy & Consent | Local-only storage; optional therapist report with explicit consent toggle |

---

## Project Structure

```
mental_health_journal/
├── app.py                        # Main entry point
├── requirements.txt              # Python dependencies
├── .env.example                  # API key template (copy → .env)
├── data/                         # Auto-created; stores journal_entries.csv
├── pages/
│   ├── 1_Journal_Entry.py        # Daily entry form
│   ├── 2_Journal_History.py      # Entry browser and export
│   ├── 3_Analytics.py            # Charts, summaries, pattern detection
│   ├── 4_AI_Insights.py          # Gemini AI wellness reflections
│   └── 5_Privacy_Consent.py      # Privacy info and therapist report
└── utils/
    ├── __init__.py
    ├── data_manager.py           # CSV read/write, validation
    ├── analytics.py              # Stats and Plotly charts
    ├── pattern_detection.py      # Rule-based wellness flags
    └── ai_insights.py            # Gemini API integration
```

---

## Setup & Installation

### 1. Prerequisites

- Python 3.10 or higher
- A Google Gemini API key (free tier available at [Google AI Studio](https://aistudio.google.com/app/apikey))

### 2. Clone or download the project

```bash
git clone <your-repo-url>
cd mental_health_journal
```

Or simply place the `mental_health_journal/` folder anywhere on your machine.

### 3. Create a virtual environment (recommended)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure your API key

```bash
# Copy the example file
cp .env.example .env     # macOS/Linux
copy .env.example .env   # Windows
```

Open `.env` and replace `your_gemini_api_key_here` with your actual key:

```
GEMINI_API_KEY=AIzaSy...your_real_key_here
```

> The app works without an API key — AI Insights features will be disabled,
> but all other features (journaling, analytics, pattern detection) function fully.

### 6. Run the application

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## Pattern Detection Thresholds

The following rule-based thresholds are used by the Analytics page. They are documented here for full transparency.

| Pattern | Threshold |
|---|---|
| Sustained low mood | Average mood ≤ 4 over the last 7 days (min. 5 entries) |
| Sustained high stress | Average stress ≥ 7 over the last 7 days (min. 5 entries) |
| Chronic poor sleep | Average sleep < 6 hours over the last 7 days (min. 5 entries) |
| Very low mood spike | Any single entry with mood ≤ 2 |
| Very high stress spike | Any single entry with stress ≥ 9 |

All flags are **wellness indicators only** — they are not medical diagnoses.

---

## Data Storage

- Entries are stored in `data/journal_entries.csv` (created automatically on first use).
- No data is sent to any server by default.
- When you use AI Insights, aggregated statistics (not raw notes, unless you use "Notes Themes") are sent to the Google Gemini API.
- You can export or delete your data at any time from the **Journal History** page.

---

## AI Scope Boundaries

The Gemini model is configured with a system prompt that **explicitly prohibits**:

- Diagnosing any mental health condition
- Recommending specific medications or clinical treatments
- Making definitive statements about a user's mental health status

The AI is used **only** for:

- Summarising wellness score trends in a warm, reflective tone
- Identifying recurring themes in journal notes
- Writing an encouraging weekly wellness reflection

---

## Deploying to Streamlit Community Cloud

1. Push the `mental_health_journal/` folder contents to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo.
3. Set the main file path to `app.py`.
4. Add your `GEMINI_API_KEY` as a **Secret** in the Streamlit Cloud settings (do NOT commit your `.env` file).
5. Deploy.

---

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit >= 1.35` | Web UI framework |
| `pandas >= 2.0` | Data handling and analysis |
| `plotly >= 5.18` | Interactive charts |
| `google-generativeai >= 0.7` | Gemini API client |
| `python-dotenv >= 1.0` | Load API key from `.env` |

---

## Privacy

- All data is local to your machine by default.
- No accounts, logins, or cloud sync are included.
- Therapist report generation is **opt-in** with an explicit consent toggle.
- See the **Privacy & Consent** page in the app for full details.
