import pandas as pd
import numpy as np
import os

BASE_DIR = r"C:\Users\gngim\Desktop\Darko\features"

box_path  = os.path.join(BASE_DIR, "ewma_engine_data", "darko_ewma_talent_all_seasons.csv")
rapm_path = os.path.join(BASE_DIR, "rapm_by_player_season.csv")
out_path  = os.path.join(BASE_DIR, "darko_dpm_combined.csv")

box = pd.read_csv(box_path)
rapm = pd.read_csv(rapm_path)

# Ensure consistent merge keys
box["player_id"] = box["player_id"].astype(str)
rapm["player_id"] = rapm["player_id"].astype(str)

box["season"] = pd.to_numeric(box["season"], errors="coerce").astype("Int64")
rapm["season"] = pd.to_numeric(rapm["season"], errors="coerce").astype("Int64")

# Now merge works
df = box.merge(
    rapm[["player_id", "season", "rapm"]],
    on=["player_id", "season"],
    how="left"
)

# Fill any missing RAPM with 0 (totally replaceable with priors later)
df["rapm"] = df["rapm"].fillna(0.0)

# STANDARDIZE both components within each season
def standardize_by_season(s):
    return (s - s.mean()) / (s.std(ddof=0) + 1e-9)

df["box_z"]  = df.groupby("season")["darko_total"].transform(standardize_by_season)
df["rapm_z"] = df.groupby("season")["rapm"].transform(standardize_by_season)

# Combine (weights ~ DARKO's "box + RAPM" philosophy)
df["darko_dpm"] = 0.36 * df["box_z"] + 0.64 * df["rapm_z"]

# Rescale to roughly match DARKO’s range (~ -6 to +8)
SCALE = 4.0
df["darko_dpm"] = df["darko_dpm"] * SCALE

df.to_csv(out_path, index=False)
print("Saved combined DPM →", out_path)
