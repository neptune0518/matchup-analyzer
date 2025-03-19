import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from openai import OpenAI
import requests
from io import StringIO

# Initialize OpenAI API (Replace 'your-api-key' with your actual OpenAI API Key)
client = OpenAI(api_key="your-api-key")

# Define GitHub raw URLs for datasets
file_paths = {
    "Defense": "https://raw.githubusercontent.com/neptune0518/matchup-analyzer/main/defense25.csv",
    "Height": "https://raw.githubusercontent.com/neptune0518/matchup-analyzer/main/height25.csv",
    "Misc": "https://raw.githubusercontent.com/neptune0518/matchup-analyzer/main/misc25.csv",
    "Offense": "https://raw.githubusercontent.com/neptune0518/matchup-analyzer/main/offense25.csv",
    "Point Distribution": "https://raw.githubusercontent.com/neptune0518/matchup-analyzer/main/pointdist25.csv",
    "Summary": "https://raw.githubusercontent.com/neptune0518/matchup-analyzer/main/summary25.csv"
}

def load_data(url):
    """Fetch CSV file from GitHub and load into a DataFrame."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        csv_data = StringIO(response.text)
        return pd.read_csv(csv_data)
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading {url}: {e}")
        return None

dataframes = {name: load_data(url) for name, url in file_paths.items()}
dataframes = {k: v for k, v in dataframes.items() if v is not None}

st.title("College Basketball Matchup Analyzer")

if "Summary" in dataframes:
    team1 = st.selectbox("Select Team 1", dataframes["Summary"]["TeamName"].unique())
    team2 = st.selectbox("Select Team 2", dataframes["Summary"]["TeamName"].unique())

    st.subheader(f"📊 {team1} vs {team2} – Strength Comparison")
    categories = ["AdjOE", "AdjDE", "AdjTempo", "RankAdjEM"]
    team1_stats = [dataframes["Summary"].loc[dataframes["Summary"]["TeamName"] == team1, cat].values[0] for cat in categories]
    team2_stats = [dataframes["Summary"].loc[dataframes["Summary"]["TeamName"] == team2, cat].values[0] for cat in categories]

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    team1_stats += team1_stats[:1]
    team2_stats += team2_stats[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, team1_stats, color="blue", alpha=0.3, label=team1)
    ax.fill(angles, team2_stats, color="red", alpha=0.3, label=team2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_title("📊 Team Strength Comparison")
    ax.legend()
    st.pyplot(fig)

    st.subheader("💰 Betting Model – Best Value Picks")
    betting_teams = dataframes["Summary"][(dataframes["Summary"]["RankAdjDE"] < 50) & (dataframes["Summary"]["RankAdjEM"] > 100)]
    if not betting_teams.empty:
        st.dataframe(betting_teams[["TeamName", "AdjDE", "AdjEM"]])
    else:
        st.write("No clear value teams found.")

    st.subheader("🚨 Potential Upset Alerts")
    upset_alerts = dataframes["Summary"][(dataframes["Summary"]["RankAdjDE"] < 40) & (dataframes["Summary"]["RankAdjEM"] > 100) & (dataframes["Summary"]["AdjTempo"] > 70)]
    if not upset_alerts.empty:
        st.dataframe(upset_alerts[["TeamName", "AdjDE", "AdjTempo"]])
    else:
        st.write("No high-upset probability teams found.")

    st.subheader("🤖 AI Betting Insights")
    prompt = f"""
    Analyze the betting value for {team1} vs. {team2}. 
    - Consider efficiency, defensive metrics, and historical trends.
    - Predict which team is more likely to cover the spread.
    - Provide betting strategies.

    Data:
    - {team1}: {team1_stats[0]} Off Eff, {team1_stats[1]} Def Eff
    - {team2}: {team2_stats[0]} Off Eff, {team2_stats[1]} Def Eff
    """
    try:
        response = client.Completion.create(
            engine="gpt-4",
            prompt=prompt,
            max_tokens=300
        )
        st.write(response["choices"][0]["text"].strip())
    except Exception as e:
        st.error("AI could not generate an answer. Try again later.")

st.write("*Built for querying matchups, betting insights, and AI-driven analysis*")
