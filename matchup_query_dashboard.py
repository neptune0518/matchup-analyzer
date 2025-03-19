import streamlit as st
import pandas as pd

# Load datasets
file_paths = {
    "Defense": "/mnt/data/defense25.csv",
    "Height": "/mnt/data/height25.csv",
    "Misc": "/mnt/data/misc25.csv",
    "Offense": "/mnt/data/offense25.csv",
    "Point Distribution": "/mnt/data/pointdist25.csv",
    "Summary": "/mnt/data/summary25 (1).csv"
}

dataframes = {name: pd.read_csv(path) for name, path in file_paths.items()}

def get_team_stats(team_name):
    """Retrieve team statistics across multiple data sources."""
    stats = {}
    for name, df in dataframes.items():
        team_data = df[df['TeamName'] == team_name]
        if not team_data.empty:
            stats[name] = team_data.iloc[0].to_dict()
    return stats

# Streamlit UI
st.title("College Basketball Matchup Analyzer")

# Team selection
team1 = st.selectbox("Select Team 1", dataframes["Summary"]["TeamName"].unique())
team2 = st.selectbox("Select Team 2", dataframes["Summary"]["TeamName"].unique())

if st.button("Compare Teams"):
    stats1 = get_team_stats(team1)
    stats2 = get_team_stats(team2)
    
    st.subheader(f"Comparison: {team1} vs {team2}")
    for category in stats1.keys():
        st.write(f"**{category} Metrics**")
        df_compare = pd.DataFrame([stats1[category], stats2[category]], index=[team1, team2])
        st.dataframe(df_compare)

st.write("*Built for querying matchups and key metrics*")
