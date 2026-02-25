import numpy as np
import streamlit as st
import json
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import hashlib
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FILE = "database.json"

# ---------- DATA HANDLING ----------
def load_data():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "goals": [],
            "expenses": [],
            "mood_log": [],
            "learning_hours": 0
        }

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

# helper functions

def check_achievements(data):
    badges = []

    completed = sum(1 for g in data["goals"] if g["completed"])

    if completed >= 5:
        badges.append("🏆 Goal Crusher")
    if data["learning_hours"] >= 50:
        badges.append("📚 Knowledge Builder")
    if data["expenses"] and sum(e["amount"] for e in data["expenses"]) < 2000:
        badges.append("💰 Smart Saver")

    return badges

def calculate_streak(data):
    streak = 0
    for goal in reversed(data["goals"]):
        if goal["completed"]:
            streak += 1
        else:
            break
    return streak

#------PASSWORD PROTECTION 🔒-----
def check_password(password):
    stored_hash = hashlib.sha256("blacklifeos".encode()).hexdigest()
    return hashlib.sha256(password.encode()).hexdigest() == stored_hash


data = load_data()

#---------- AI REFLECTION ----------

def generate_real_ai_reflection(data):
    summary = f"""
    Goals: {len(data['goals'])}
    Completed: {sum(1 for g in data['goals'] if g['completed'])}
    Mood Entries: {len(data['mood_log'])}
    Total Expenses: {sum(e['amount'] for e in data['expenses']) if data['expenses'] else 0}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a strict but intelligent life performance advisor."},
                {"role": "user", "content": summary}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI Analysis currently unavailable. (Error: {str(e)})"

# ---------- BLACK EDITION THEME ----------
st.set_page_config(page_title="LifeOS", layout="centered")

# ---------- AUTHENTICATION ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 LifeOS Login")

    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if check_password(password):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Access Denied")

    st.stop()


st.markdown("""
<style>

/* App background */
.stApp {
    background-color: #0e0e0e;
    color: white;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111;
}

/* Buttons */
.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 45px;
    background-color: #d4af37;
    color: black;
    font-weight: bold;
}

/* Input fields */
.stTextInput>div>div>input,
.stNumberInput>div>div>input {
    background-color: #1c1c1c;
    color: white;
    border-radius: 8px;
}

/* Cards */
.metric-card {
    background-color: #1a1a1a;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0px 0px 10px rgba(212,175,55,0.2);
}

h1, h2, h3 {
    color: #d4af37;
}

</style>
""", unsafe_allow_html=True)

st.title("🧠 LifeOS – Black Edition")

# ---------- TOP NAVIGATION ----------
menu = st.radio(
    "Navigation",
    ["Dashboard", "Goals", "Finance", "Mood", "Learning"],
    horizontal=True
)

# Global Performance Metrics (for Footer)
total_goals = len(data["goals"])
completed = sum(1 for g in data["goals"] if g["completed"])
productivity = (completed / total_goals * 100) if total_goals > 0 else 0

life_score = 0
life_score += productivity
life_score += calculate_streak(data) * 5

if data["mood_log"]:
    moods = [m["mood_score"] for m in data["mood_log"]]
    life_score += (sum(moods) / len(moods)) * 10

life_score = min(life_score, 100)

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.header("📊 Performance Overview")

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Goals", total_goals)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Completed", completed)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Productivity %", f"{productivity:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Mood Trend")
    if data["mood_log"]:
        df = pd.DataFrame(data["mood_log"])
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(df["date"], df["mood_score"])
        ax.set_ylabel("Mood Score")
        st.pyplot(fig)

        # productivity heatmap based on mood
        st.subheader("📊 Productivity Heatmap")
        df["day"] = df["date"].dt.day
        df["month"] = df["date"].dt.month

        pivot = df.pivot_table(
            index="month",
            columns="day",
            values="mood_score",
            aggfunc="mean"
        )

        fig2, ax2 = plt.subplots(figsize=(6,3))
        sns.heatmap(pivot, cmap="YlOrBr", ax=ax2)
        st.pyplot(fig2)

    st.subheader("� AI Strategic Analysis")
    st.subheader(" AI Strategic Analysis")
    ai_text = generate_real_ai_reflection(data)
    st.write(ai_text)


    st.subheader("🎯 Monthly Life Score")
    st.progress(life_score / 100)
    st.write(f"{life_score:.1f} / 100")

    st.subheader("🏅 Achievements")

    badges = check_achievements(data)

    if badges:
        for badge in badges:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{badge}</h3>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No achievements yet. Stay disciplined.")

# ---------- GOALS ----------
elif menu == "Goals":
    st.header("🎯 Goals")

    new_goal = st.text_input("Add New Goal")
    if st.button("Add Goal"):
        data["goals"].append({
            "text": new_goal,
            "completed": False
        })
        save_data(data)
        st.success("Goal Added")

    for i, goal in enumerate(data["goals"]):
        col1, col2 = st.columns([4,1])
        col1.write(goal["text"])
        if not goal["completed"]:
            if col2.button("Done", key=i):
                data["goals"][i]["completed"] = True
                save_data(data)
                st.rerun()

# ---------- FINANCE ----------
elif menu == "Finance":
    st.header("💰 Finance Tracker")

    amount = st.number_input("Amount")
    category = st.text_input("Category")

    if st.button("Add Expense"):
        data["expenses"].append({
            "amount": amount,
            "category": category,
            "date": str(datetime.date.today())
        })
        save_data(data)
        st.success("Expense Added")

    if data["expenses"]:
        df = pd.DataFrame(data["expenses"])
        total_spent = df["amount"].sum()
        st.metric("Total Spent", f"R {total_spent:.2f}")

    monthly_savings = st.number_input("Monthly Savings Amount", 0)

    if monthly_savings > 0:
        months = np.arange(1, 13)
        forecast = monthly_savings * months

        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(months, forecast)
        ax.set_title("12-Month Savings Projection")
        ax.set_xlabel("Months")
        ax.set_ylabel("Projected Savings")
        st.pyplot(fig)

# ---------- MOOD ----------
elif menu == "Mood":
    st.header("💬 Mood Tracker")

    mood_score = st.slider("Mood Score (1 = Bad, 5 = Excellent)", 1, 5)
    note = st.text_area("Notes")

    if st.button("Log Mood"):
        data["mood_log"].append({
            "date": str(datetime.date.today()),
            "mood_score": mood_score,
            "note": note
        })
        save_data(data)
        st.success("Mood Logged")

# ---------- LEARNING ----------
elif menu == "Learning":
    st.header("📚 Learning Hours")

    hours = st.number_input("Hours Studied Today", 0, 24)
    if st.button("Add Hours"):
        data["learning_hours"] += hours
        save_data(data)
        st.success("Hours Added")

    st.metric("Total Learning Hours", data["learning_hours"])

# ---------- GLOBAL FOOTER ----------
st.markdown(f"""
<div style="position:fixed;
bottom:0;
left:0;
width:100%;
background:#111;
padding:10px;
text-align:center;
border-top:1px solid #333;
z-index: 1000;">
🔥 Streak: {calculate_streak(data)} |
🎯 Life Score: {life_score:.1f}
</div>
""", unsafe_allow_html=True)

#-----STREAK SYSTEM 🏆-----
def calculate_streak(data):
    streak = 0
    for goal in reversed(data["goals"]):
        if goal["completed"]:
            streak += 1
        else:
            break
    return streak



