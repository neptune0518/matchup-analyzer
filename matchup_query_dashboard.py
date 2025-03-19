import streamlit as st
import pandas as pd
import requests

# Define GitHub raw URLs
file_paths = {
    "Defense": "https://raw.githubusercontent.com/neptune0518/matchup-analyzer/main/defense25.csv",
    "Height": "https://raw.githubusercontent.com/neptune0518/matchup-analyzer/main/height25.csv",
    "Misc": "https://raw.githubusercontent.com/neptune0518/matchup-analyzer/main/misc25.csv",
    "Offense": "https://raw.githubusercontent.com/neptune0518/matchup-analyzer/main/offense25.csv",
    "Point Distribution": "https://raw.githubusercontent.com/neptune0518/matchup-analyzer/main/pointdist25.csv",
    "Summary": "https://raw.githubusercontent.com/neptune0518/matchup-analyzer/main/summary25 (1).csv"
}

def load_data(url):
    """Fetch CSV file from GitHub and load into a DataFrame."""
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(url)
    else:
        st.error(f"Failed to load {url} - Status Code {response.status_code}")
        return None

# Load all datasets
dataframes = {name: load_data(url) for name, url in file_paths.items()}

# Remove None values if any files failed
dataframes = {k: v for k, v in dataframes.items() if v is not None}

# Streamlit UI
st.title("College Basketball Matchup Analyzer")

# Check if data loaded correctly
if dataframes:
    st.success("All data files loaded successfully!")
else:
    st.error("Error loading data. Check file URLs or repository settings.")

# Team selection
if "Summary" in dataframes:
    team1 = st.selectbox("Select Team 1", dataframes["Summary"]["TeamName"].unique())
    team2 = st.selectbox("Select Team 2", dataframes["Summary"]["TeamName"].unique())

    if st.button("Compare Teams"):
        def get_team_stats(team_name):
            stats = {}
            for name, df in dataframes.items():
                team_data = df[df['TeamName'] == team_name]
                if not team_data.empty:
                    stats[name] = team_data.iloc[0].to_dict()
            return stats

        stats1 = get_team_stats(team1)
        stats2 = get_team_stats(team2)

        st.subheader(f"Comparison: {team1} vs {team2}")
        for category in stats1.keys():
            st.write(f"**{category} Metrics**")
            df_compare = pd.DataFrame([stats1[category], stats2[category]], index=[team1, team2])
            st.dataframe(df_compare)

st.write("*Built for querying matchups and key metrics*")
