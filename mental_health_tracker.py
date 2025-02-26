import streamlit as st
import pandas as pd
import sqlite3
import datetime
import random
import plotly.express as px

# Database connection
conn = sqlite3.connect("mental_health.db", check_same_thread=False)
c = conn.cursor()

# Create table if not exists
c.execute(
    """CREATE TABLE IF NOT EXISTS mood_tracker 
    (date TEXT, mood TEXT, stress_level INTEGER, journal_entry TEXT, email TEXT)"""
)
conn.commit()

quotes = [
    "Your mental health is a priority. Take care of yourself!",
    "Small steps every day lead to big changes.",
    "You are stronger than you think!",
    "Breathe. Relax. Everything will be okay.",
    "Self-care is not selfish. Take time for yourself!",
]

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Mood History", "Settings"])

st.markdown("<h1 style='color: red;'>🧠 Mental Health Tracker</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color: grey;'>Track your mood, stress levels, and improve your well-being!</h3>", unsafe_allow_html=True)
today = datetime.date.today()

# Home page
if page == "Home":
    mood = st.selectbox(
        "How are you feeling today?",
        ["Select your mood", "Happy 😊", "Sad 😢", "Stressed 😖", "Angry 😡", "Calm 😌", "Excited 🤩"],
        index=0
    )

    if mood == "Select your mood":
        mood = None  

    stress_level = st.slider("How stressed are you? (0 = No Stress, 10 = Very Stressed)", 0, 10, 5)
    journal = st.text_area("Write about your day", key="journal_entry_input")
    email = st.text_input("Enter your email for daily reminders")

    if st.button("Save Entry"):
        if mood:
            c.execute("INSERT INTO mood_tracker VALUES (?, ?, ?, ?, ?)", (today, mood, stress_level, journal, email))
            conn.commit()

            # Check if entries exceed 5, delete the oldest one
            c.execute("SELECT COUNT(*) FROM mood_tracker")
            count = c.fetchone()[0]

            if count > 5:
                c.execute("DELETE FROM mood_tracker WHERE date = (SELECT MIN(date) FROM mood_tracker)")
                conn.commit()

            st.success("Your entry has been saved! ✅")
        else:
            st.warning("Please select a mood before saving.")

# Mood History page
elif page == "Mood History":
    df = pd.read_sql("SELECT * FROM mood_tracker ORDER BY date DESC LIMIT 5", conn)  # Show only last 5 entries

    if not df.empty:
        st.subheader("📊 Mood Distribution")
        mood_counts = df["mood"].value_counts()
        
        if not mood_counts.empty:
            pie_chart = px.pie(
                names=mood_counts.index,
                values=mood_counts.values,
                title="Mood Distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(pie_chart, use_container_width=True)
        else:
            st.info("No mood data available yet.")

        st.subheader("📈 Stress Level Trend")
        df['date'] = pd.to_datetime(df['date']) 
        stress_chart = px.line(
            df, x='date', y='stress_level', markers=True,
            labels={'date': 'Date', 'stress_level': 'Stress Level'},
            title="Stress Level Over Time",
            color_discrete_sequence=['red']
        )
        st.plotly_chart(stress_chart, use_container_width=True)
        
        st.subheader("📅 Your Journal Entries (Last 5)")
        st.dataframe(df[["date", "mood", "stress_level", "journal_entry", "email"]])

        # Delete All Entries Button
        if st.button("Delete All Entries"):
            if st.button("Yes, Delete All"):
                c.execute("DELETE FROM mood_tracker")
                conn.commit()
                st.warning("All entries have been deleted! ❌")

# Settings page
elif page == "Settings":
    st.subheader("⚙️ Settings")
    st.markdown("**Dark mode is now handled by Streamlit’s theme settings!**")

st.subheader("🌟 Daily Motivation")
st.info(random.choice(quotes))

conn.close()
