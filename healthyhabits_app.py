
import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Try to import a translator. If not available, provide a simple fallback.
try:
    from googletrans import Translator
    translator = Translator()
    def translate_text(text, dest='hi'):
        try:
            return translator.translate(text, dest=dest).text
        except Exception:
            return text + " (translation unavailable)"
except Exception:
    translator = None
    def translate_text(text, dest='hi'):
        # Simple fallback: return the English text with a note.
        return text + " (Hindi translation not available - please install googletrans)"

DB_PATH = "healthyhabits_profiles.db"

# ----- Database helpers -----
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            conditions TEXT,
            goal TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_profile(name, age, gender, conditions, goal):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO users (name, age, gender, conditions, goal, created_at) VALUES (?, ?, ?, ?, ?, ?)', 
              (name, age, gender, ",".join(conditions), goal, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def fetch_profiles():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM users ORDER BY id DESC", conn)
    conn.close()
    return df

# ----- Recommendation Engine (simple rule-based) -----
def generate_recommendations(conditions, goal):
    diet_recs = []
    exercise_recs = []
    sleep_recs = []
    general_recs = []

    # Base suggestions
    diet_recs.append("Include more whole foods: vegetables, fruits, lean proteins, and whole grains.")
    exercise_recs.append("Aim for at least 30 minutes of moderate activity daily (walking, yoga, or cycling).")
    sleep_recs.append("Keep consistent sleep schedule. Avoid screens 1 hour before bed.")
    general_recs.append("Stay hydrated and avoid excessive sugary drinks.")

    # Condition-specific adjustments
    if "Thyroid" in conditions:
        diet_recs.append("For thyroid issues: include selenium-rich foods (nuts, seeds) and iodine sources in moderation; avoid highly processed foods and excessive soy.")
        exercise_recs.append("Include strength training twice a week to support metabolism.")
    if "Sleep Apnea" in conditions:
        diet_recs.append("For sleep apnea: avoid heavy meals and caffeine close to bedtime; maintain healthy weight.")
        exercise_recs.append("Practice breathing exercises and consider positional therapy (sleeping on side).")
        sleep_recs.append("Consult a clinician for breathing-related sleep disorders; avoid alcohol near bedtime.")
    if "Heart Risk" in conditions or "Cardiac History" in conditions:
        diet_recs.append("Heart-healthy diet: reduce saturated fats, increase fiber, include omega-3 sources like fish or flaxseed.")
        exercise_recs.append("Prefer low-impact cardio like brisk walking; check with a doctor before intense exercise.")
        general_recs.append("Monitor blood pressure and cholesterol regularly.")

    # Goal-specific tweaks
    if goal == "Weight Loss":
        diet_recs.append("Control portion sizes, prefer protein-rich breakfasts, and avoid late-night snacking.")
        exercise_recs.append("Incorporate interval walks or brisk walks to increase calorie burn.")
    elif goal == "Better Sleep":
        sleep_recs.append("Create a bedtime routine: warm shower, light stretching, and a calm environment.")
        diet_recs.append("Avoid heavy, spicy dinners and caffeine after late afternoon.")
    elif goal == "Energy Boost":
        diet_recs.append("Include small, frequent balanced meals; add nuts and fruits for healthy snacks.")
        exercise_recs.append("Short morning walks and light stretching improve daytime alertness.")

    # Collate into text blocks
    diet_text = "\\n- ".join([""] + diet_recs)
    exercise_text = "\\n- ".join([""] + exercise_recs)
    sleep_text = "\\n- ".join([""] + sleep_recs)
    general_text = "\\n- ".join([""] + general_recs)

    return {
        "diet": diet_text.strip(),
        "exercise": exercise_text.strip(),
        "sleep": sleep_text.strip(),
        "general": general_text.strip()
    }

# ----- Streamlit UI -----
st.set_page_config(page_title="HealthyHabits - Bilingual Lifestyle Helper", layout="centered")

st.title("HealthyHabits 🌿 — Personalized Lifestyle Recommendations (English / Hindi)")
st.markdown("Build a quick profile for a family member and get simple, safe lifestyle suggestions. This is a demo MVP — not medical advice.")

init_db()

menu = st.sidebar.selectbox("Menu", ["Create Profile", "View Profiles", "About & Instructions"])

if menu == "Create Profile":
    st.header("Create a New Profile")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value="")
        age = st.number_input("Age", min_value=12, max_value=120, value=30)
        gender = st.selectbox("Gender", ["Female", "Male", "Other"])
    with col2:
        conditions = st.multiselect("Known Health Conditions (select all that apply)",
                                     ["Thyroid", "Sleep Apnea", "Heart Risk", "Obesity", "Diabetes", "None"])
        goal = st.selectbox("Primary Goal", ["Weight Loss", "Better Sleep", "Energy Boost", "Healthy Habits"])

    if st.button("Save Profile and Generate Recommendations"):
        if name.strip() == "":
            st.error("Please enter a name.")
        else:
            save_profile(name, age, gender, conditions, goal)
            st.success(f"Profile saved for {name}.")
            recs = generate_recommendations(conditions, goal)
            language = st.radio("Choose Language / भाषा चुनें", ["English", "हिन्दी"])
            st.subheader("Personalized Recommendations")
            if language == "English":
                st.markdown("**Diet Suggestions:**")
                st.write(recs["diet"])
                st.markdown("**Exercise Suggestions:**")
                st.write(recs["exercise"])
                st.markdown("**Sleep Suggestions:**")
                st.write(recs["sleep"])
                st.markdown("**General Tips:**")
                st.write(recs["general"])
            else:
                st.markdown("**आहार सुझाव:**")
                st.write(translate_text(recs["diet"], dest='hi'))
                st.markdown("**व्यायाम सुझाव:**")
                st.write(translate_text(recs["exercise"], dest='hi'))
                st.markdown("**नींद सुझाव:**")
                st.write(translate_text(recs["sleep"], dest='hi'))
                st.markdown("**सामान्य सलाह:**")
                st.write(translate_text(recs["general"], dest='hi'))

elif menu == "View Profiles":
    st.header("Saved Profiles")
    df = fetch_profiles()
    if df.empty:
        st.info("No profiles created yet.")
    else:
        st.dataframe(df[['id','name','age','gender','conditions','goal','created_at']])
        st.markdown("---")
        st.subheader("Generate recommendations for an existing profile")
        selected_id = st.number_input("Enter Profile ID", min_value=1, value=1, step=1)
        if st.button("Generate for Selected ID"):
            row = df[df['id']==selected_id]
            if row.empty:
                st.error("Profile ID not found. Choose a valid ID from the table above.")
            else:
                conditions = row.iloc[0]['conditions'].split(",") if row.iloc[0]['conditions'] else []
                goal = row.iloc[0]['goal']
                recs = generate_recommendations(conditions, goal)
                language = st.radio("Choose Language / भाषा चुनें (Existing)", ["English", "हिन्दी"], key="viewlang")
                if language == "English":
                    st.markdown("**Diet Suggestions:**")
                    st.write(recs["diet"])
                    st.markdown("**Exercise Suggestions:**")
                    st.write(recs["exercise"])
                    st.markdown("**Sleep Suggestions:**")
                    st.write(recs["sleep"])
                    st.markdown("**General Tips:**")
                    st.write(recs["general"])
                else:
                    st.markdown("**आहार सुझाव:**")
                    st.write(translate_text(recs["diet"], dest='hi'))
                    st.markdown("**व्यायाम सुझाव:**")
                    st.write(translate_text(recs["exercise"], dest='hi'))
                    st.markdown("**नींद सुझाव:**")
                    st.write(translate_text(recs["sleep"], dest='hi'))
                    st.markdown("**सामान्य सलाह:**")
                    st.write(translate_text(recs["general"], dest='hi'))

else:
    st.header("About & Instructions")
    st.markdown("HealthyHabits is a demo MVP to generate simple lifestyle suggestions for users with conditions like thyroid, sleep apnea, obesity, or heart risk.")
    st.markdown("Important: This app is not a replacement for professional medical advice. Always consult a healthcare provider for diagnosis or treatment.")
    st.markdown("How to run locally (on your machine):")
    st.markdown("1) Create a virtual environment (recommended) and install dependencies: pip install streamlit pandas. Optionally install googletrans for Hindi translations: pip install googletrans==4.0.0-rc1")
    st.markdown("2) Run the app: streamlit run healthyhabits_app.py")
    st.markdown("3) If translation doesn't work, the app will show English text and a note recommending installing googletrans.")
    st.markdown("What you can extend later: Add daily logging and progress charts, Add reminders or notification via email/SMS, Add personalized meal plans or exercise videos, Integrate with wearable data (step count, sleep metrics)")

# Save a short demo CSV of guideline examples (for quick reference)
demo_examples = pd.DataFrame([
    {"condition":"Thyroid","diet":"Include selenium-containing foods, avoid processed sugar","exercise":"30 min walk, strength 2x/week"},
    {"condition":"Sleep Apnea","diet":"Avoid caffeine late, light dinner","exercise":"Breathing exercises, positional sleep"},
    {"condition":"Heart Risk","diet":"Low saturated fats, high fiber","exercise":"Low-impact cardio, consult physician"}
])
demo_examples.to_csv("healthyhabits_demo_examples.csv", index=False)
