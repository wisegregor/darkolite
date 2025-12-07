import pandas as pd
import os
import glob

# =====================================================
# CONFIG
# =====================================================
SEASON = "2025-26"
BASE_DIR = r"C:\Users\gngim\Desktop\Darko\historical_scraper"

SEASON_FOLDER = os.path.join(BASE_DIR, SEASON)
PLAYER_PATTERN = os.path.join(SEASON_FOLDER, f"player_boxscore_{SEASON}_*.csv")
TEAM_FILE      = os.path.join(BASE_DIR, "team_boxscores", f"boxscores_{SEASON}.csv")
OUTPUT_FILE    = os.path.join(SEASON_FOLDER, f"merged_player_team_{SEASON}.csv")

# =====================================================
# LOAD TEAM DATA
# =====================================================
df_team = pd.read_csv(TEAM_FILE)

# Normalize join keys
df_team.rename(columns={"TEAM_ID": "team_id", "GAME_ID": "game_id"}, inplace=True)

# Lowercase for consistency
df_team.columns = [c.lower() for c in df_team.columns]

# Add "_team" suffix to all team columns EXCEPT join keys
team_cols_rename = {
    c: f"{c}_team" 
    for c in df_team.columns 
    if c not in ["team_id", "game_id"]
}
df_team.rename(columns=team_cols_rename, inplace=True)

# =====================================================
# MERGE EACH PLAYER FILE
# =====================================================
player_files = glob.glob(PLAYER_PATTERN)
merged_frames = []

print(f"Found {len(player_files)} player files to merge.")

for file in player_files:
    print("Merging:", os.path.basename(file))

    df_p = pd.read_csv(file)

    # Normalize join keys
    df_p.rename(columns={"TEAM_ID": "team_id", "GAME_ID": "game_id"}, inplace=True)
    df_p.columns = [c.lower() for c in df_p.columns]

    # Perfect merge: all player cols + all team cols
    df_m = df_p.merge(df_team, on=["game_id", "team_id"], how="left")

    merged_frames.append(df_m)

# =====================================================
# FINAL CONCAT + SAVE
# =====================================================
df_final = pd.concat(merged_frames, ignore_index=True)

df_final.to_csv(OUTPUT_FILE, index=False)
print("Saved merged dataset →", OUTPUT_FILE)
