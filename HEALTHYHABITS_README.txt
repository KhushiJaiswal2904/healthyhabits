HealthyHabits - Bilingual Lifestyle Recommendation App (MVP)

Files:
- healthyhabits_app.py : Streamlit app (one-file)
- healthyhabits_profiles.db : SQLite DB (created on first run)
- healthyhabits_demo_examples.csv : Demo examples created by the app

How to run:
1. (Optional) Create and activate a Python virtual environment.
2. Install dependencies:
   pip install streamlit pandas
   pip install googletrans==4.0.0-rc1  # optional for Hindi translations
3. Run:
   streamlit run healthyhabits_app.py

Notes:
- The app uses googletrans for Hindi translation when available. If not installed or translation fails, the app shows a note.
- This is a demo MVP; not medical advice. Customize/add more features as needed.
