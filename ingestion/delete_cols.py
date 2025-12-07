import pandas as pd
import os
import glob

# ============================================
# CONFIG
# ============================================
SEASON = "1996-97"
BASE_DIR = r"C:\Users\gngim\Desktop\Darko\historical_scraper"
SEASON_FOLDER = os.path.join(BASE_DIR, SEASON)

PLAYER_PATTERN = os.path.join(SEASON_FOLDER, f"player_boxscore_{SEASON}_*.csv")

# Column AD = 30th column = zero-index 29
CUT_INDEX = 29   # delete all columns from here onward

# ============================================
# PROCESS FILES
# ============================================
files = glob.glob(PLAYER_PATTERN)
print(f"Found {len(files)} player files.")

for file in files:
    print("Cleaning:", os.path.basename(file))

    df = pd.read_csv(file)

    # Keep only columns up to AC (index 0–28)
    df_clean = df.iloc[:, :CUT_INDEX]

    # Overwrite original file
    df_clean.to_csv(file, index=False)

print("Done cleaning all player files.")
