import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------
# LOAD DATA
# -----------------------------------------------------
@st.cache_data
def load_darkolite():
    return pd.read_csv("app/data/darkolite_player_season_final.csv")


df = load_darkolite()

st.title("🏀 DARKO-Lite Player Impact Explorer")
st.write("Explore player impact ratings from 1996–2024 using a DARKO-inspired blended DPM metric.")

# -----------------------------------------------------
# PLAYER SELECTION
# -----------------------------------------------------
players = sorted(df["player_name"].unique())
player = st.selectbox(
    "Select a player",
    players,
    index=players.index("Stephen Curry") if "Stephen Curry" in players else 0
)

pdf = df[df["player_name"] == player].sort_values("season")
pdf["season"] = pdf["season"].astype(str)  # ensure categorical-like string

# -----------------------------------------------------
# TOP-LEVEL METRICS
# -----------------------------------------------------
latest = pdf.iloc[-1]

col1, col2, col3 = st.columns(3)
col1.metric("Latest DPM", f"{latest['darkolite_dpm']:.2f}")
col2.metric("Box Z-Score", f"{latest['box_z']:.2f}")
col3.metric("RAPM Z-Score", f"{latest['rapm_z']:.2f}")

# -----------------------------------------------------
# DARKO-Lite DPM OVER TIME
# -----------------------------------------------------
st.subheader(f"{player} — DARKO-Lite DPM Over Time")

fig = px.line(
    pdf,
    x="season",
    y="darkolite_dpm",
    markers=True,
    title=f"{player} — DARKO-Lite Rating by Season"
)

fig.update_layout(
    xaxis_title="Season",
    yaxis_title="DARKO-Lite DPM"
)

# 🔥 FORCE X-AXIS TO BE CATEGORICAL (fixes the "Jan 2010" issue)
fig.update_xaxes(type="category")

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------
# BOX vs RAPM CONTRIBUTION
# -----------------------------------------------------
st.subheader("Box vs RAPM Components")

fig2 = px.line(
    pdf,
    x="season",
    y=["box_z", "rapm_z"],
    markers=True,
    title=f"{player} — Component Z-Scores"
)

fig2.update_layout(
    xaxis_title="Season",
    yaxis_title="Z-Score (within-season)",
    legend_title="Component"
)

# 🔥 categorical x-axis here too
fig2.update_xaxes(type="category")

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------------
# FULL TABLE
# -----------------------------------------------------
st.subheader("Season-by-Season Details")
st.dataframe(pdf.reset_index(drop=True))

st.write("Built with ❤️ using Python, EWMA smoothing, ridge RAPM, and a DARKO-inspired blend.")
