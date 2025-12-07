import os
import pandas as pd
import numpy as np

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
BASE_DIR = r"C:\Users\gngim\Desktop\Darko\historical_scraper\all_seasons"


# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def parse_minutes_col(s: str) -> float:
    """
    Safely parse NBA API minutes.
    Valid patterns:
    - "MM:SS"
    - "MM:SS:00"
    - "0:00"
    - "DNP", "", None → 0.0
    """
    if pd.isna(s):
        return 0.0

    s = str(s).strip()
    if s in ["", "DNP", "NaN", "None"]:
        return 0.0

    parts = s.split(":")

    if len(parts) == 2:  # MM:SS
        m, sec = parts
        return int(m) + int(sec) / 60.0

    if len(parts) == 3:  # MM:SS:00
        m, sec, _ = parts
        return int(m) + int(sec) / 60.0

    try:
        return float(s)
    except:
        return 0.0


def to_numeric(df: pd.DataFrame, cols) -> pd.DataFrame:
    """Convert stats to numeric safely."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


# -------------------------------------------------
# CORE FEATURE ENGINEERING
# -------------------------------------------------
def build_darkish_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --------------------
    # Minutes
    # --------------------
    df["minutes"] = df["min"].apply(parse_minutes_col)

    if "min_team" in df.columns and df["min_team"].dtype == "O":
        df["team_minutes"] = df["min_team"].apply(parse_minutes_col)
    else:
        df["team_minutes"] = pd.to_numeric(df.get("min_team", 240), errors="coerce")

    df = df[df["minutes"] > 0].copy()
    df["team_minutes"] = df["team_minutes"].replace(0, np.nan)

    # --------------------
    # Numeric stats
    # --------------------
    numeric_cols = [
        "pts", "reb", "ast", "stl", "blk", "to",
        "fg3a", "fg3m", "fta", "fgm", "fga",
        "plus_minus",
        "fga_team", "fta_team", "oreb_team", "tov_team"
    ]
    df = to_numeric(df, numeric_cols)

    # --------------------
    # Team possessions
    # --------------------
    df["team_possessions"] = (
        df["fga_team"]
        + 0.4 * df["fta_team"]
        - df["oreb_team"]
        + df["tov_team"]
    )
    df = df[df["team_possessions"] > 0].copy()

    # --------------------
    # Player on-court possessions
    # --------------------
    df["player_possessions"] = df["team_possessions"] * (df["minutes"] / 48.0)
    df = df[df["player_possessions"] > 0].copy()

    # --------------------
    # Per-36 stats
    # --------------------
    per36_stats = ["pts", "reb", "ast", "stl", "blk", "to", "fg3a", "fg3m", "fta"]
    minutes_nonzero = df["minutes"].replace(0, np.nan)

    for stat in per36_stats:
        df[f"{stat}_per36"] = df[stat] / minutes_nonzero * 36.0

    # --------------------
    # Per-100 stats
    # --------------------
    poss_nonzero = df["player_possessions"].replace(0, np.nan)

    for stat in per36_stats:
        df[f"{stat}_per100"] = df[stat] / poss_nonzero * 100.0

    # --------------------
    # Shooting efficiency
    # --------------------
    fga_nonzero = df["fga"].replace(0, np.nan)

    df["efg_pct_calc"] = (df["fgm"] + 0.5 * df["fg3m"]) / fga_nonzero

    ts_denom = (2 * (df["fga"] + 0.44 * df["fta"])).replace(0, np.nan)
    df["ts_pct_calc"] = df["pts"] / ts_denom

    df["ftr"] = df["fta"] / fga_nonzero
    df["threepar"] = df["fg3a"] / fga_nonzero
    df["ast_tov"] = df["ast"] / df["to"].replace(0, np.nan)

    # --------------------
    # PM per 100
    # --------------------
    df["pm_per100"] = df["plus_minus"] / poss_nonzero * 100.0

    # --------------------
    # Context flags
    # --------------------
    if "matchup_team" in df.columns:
        df["is_home"] = df["matchup_team"].str.contains(r"vs\.", regex=True).astype(int)
    else:
        df["is_home"] = 0

    if "wl_team" in df.columns:
        df["won"] = (df["wl_team"] == "W").astype(int)
    else:
        df["won"] = np.nan

    return df


# -------------------------------------------------
# MAIN LOOP — PROCESS ALL SEASONS AUTOMATICALLY
# -------------------------------------------------
if __name__ == "__main__":

    # Detect all season folders: "1996-97", "1997-98", ..., "2025-26"
    seasons = sorted([
        folder for folder in os.listdir(BASE_DIR)
        if os.path.isdir(os.path.join(BASE_DIR, folder))
    ])

    print("\n🌟 Found season folders:")
    for s in seasons:
        print("   •", s)

    print("\n🚀 Starting batch feature processing...\n")

    for season in seasons:
        season_dir = os.path.join(BASE_DIR, season)
        input_path  = os.path.join(season_dir, f"merged_player_team_{season}.csv")
        output_path = os.path.join(season_dir, f"darko_features_{season}.csv")

        print("----------------------------------------------------")
        print(f"📅 Processing season: {season}")
        print("----------------------------------------------------")

        if not os.path.exists(input_path):
            print(f"❌ Missing input file (skipping): {input_path}\n")
            continue

        print(f"📥 Loading: {input_path}")
        raw = pd.read_csv(input_path)

        feats = build_darkish_features(raw)

        print(f"💾 Saving: {output_path}\n")
        feats.to_csv(output_path, index=False)

    print("\n🎉 All seasons processed successfully!")
