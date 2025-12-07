import os
import numpy as np
import pandas as pd

# --------------------------------------------------------
# CONFIG
# --------------------------------------------------------
BASE_DIR = r"C:\Users\gngim\Desktop\Darko\features"
# INPUT_CSV = os.path.join(BASE_DIR, "features_all_seasons_combined\all_darkoish_features_master.csv")
INPUT_CSV = r"C:\Users\gngim\Desktop\Darko\features\features_all_seasons_combined\all_darkoish_features_master.csv"
OUTPUT_RAPM = os.path.join(BASE_DIR, "rapm_by_player_season.csv")

# Ridge penalty (tune if you want more/less shrinkage)
LAMBDA_RIDGE = 300.0


# --------------------------------------------------------
# CORE RAPM FUNCTIONS
# --------------------------------------------------------
def build_team_game_table(df_season: pd.DataFrame) -> pd.DataFrame:
    """
    Build a team-game level table with:
      - game_id
      - team_id
      - team_game_id (string key)
      - net_rating_team (per 48)
      - team_minutes
    Assumes plus_minus_team and team_minutes are constant per team-game
    in your master file (which they should be).
    """
    # Unique team-game rows
    grp = df_season.groupby(["game_id", "team_id"], as_index=False)

    team_games = grp.agg({
        "plus_minus_team": "first",
        "team_minutes": "first"
    })

    # Filter out junk
    team_games = team_games[team_games["team_minutes"] > 0].copy()

    # Approx net rating per 48 minutes
    team_games["net_rating_team"] = (
        team_games["plus_minus_team"] / (team_games["team_minutes"] / 48.0)
    )

    team_games["team_game_id"] = (
        team_games["game_id"].astype(str) + "_" + team_games["team_id"].astype(str)
    )

    team_games = team_games.set_index("team_game_id")

    return team_games


def build_design_matrix(df_season: pd.DataFrame, team_games: pd.DataFrame) -> pd.DataFrame:
    """
    Build the design matrix X (team-game x player) with entries equal to
    minutes share for each player in that team game.
    """
    df = df_season.copy()

    # Ensure minute_share exists
    if "minute_share" not in df.columns:
        df["minute_share"] = df["minutes"] / df["team_minutes"]

    # Build team_game_id key
    df["team_game_id"] = df["game_id"].astype(str) + "_" + df["team_id"].astype(str)

    # Keep only rows that correspond to valid team-games
    df = df[df["team_game_id"].isin(team_games.index)].copy()

    # Pivot: rows = team_game, columns = player_id, values = minute_share
    design = df.pivot_table(
        index="team_game_id",
        columns="player_id",
        values="minute_share",
        aggfunc="sum",
        fill_value=0.0
    )

    # Align the order of rows with team_games
    design = design.reindex(index=team_games.index)

    return design


def compute_ridge_rapm(design: pd.DataFrame,
                       team_games: pd.DataFrame,
                       lambda_ridge: float = LAMBDA_RIDGE) -> pd.Series:
    """
    Compute ridge-regression RAPM:
    y = team net rating per 48
    X = minutes-share design matrix
    Weights = team_minutes (more minutes → more weight)
    """
    X = design.values  # (n_games, n_players)
    y = team_games["net_rating_team"].values  # (n_games,)

    # Use team_minutes as weights (could be possessions if you prefer)
    weights = team_games["team_minutes"].values
    weights = np.sqrt(weights / 48.0)  # scale a bit; sqrt to reduce extremeness

    # Apply weights
    Xw = X * weights[:, None]   # each row scaled by sqrt(weight)
    yw = y * weights            # response scaled

    n_players = X.shape[1]
    I = np.eye(n_players)

    # Ridge solution: (XᵀX + λI)β = Xᵀy
    XtX = Xw.T @ Xw
    Xty = Xw.T @ yw

    reg_matrix = XtX + lambda_ridge * I
    beta = np.linalg.solve(reg_matrix, Xty)

    rapm = pd.Series(beta, index=design.columns, name="rapm")

    return rapm


def compute_rapm_by_season(df_all: pd.DataFrame,
                           lambda_ridge: float = LAMBDA_RIDGE) -> pd.DataFrame:
    """
    Loop over seasons and compute RAPM per player-season.
    """
    rapm_rows = []

    seasons = sorted(df_all["season"].unique())
    print("Seasons found:", seasons)

    for season in seasons:
        print("\n-------------------------------------------")
        print(f"Computing RAPM for season: {season}")
        print("-------------------------------------------")

        df_season = df_all[df_all["season"] == season].copy()

        # Basic sanity filtering
        df_season = df_season[(df_season["minutes"] > 0) &
                              (df_season["team_minutes"] > 0)]

        if df_season.empty:
            print("  No data for this season, skipping.")
            continue

        # Build team-game table
        team_games = build_team_game_table(df_season)

        # Build design matrix X
        design = build_design_matrix(df_season, team_games)

        if design.empty:
            print("  Empty design matrix, skipping.")
            continue

        # Compute RAPM
        rapm = compute_ridge_rapm(design, team_games, lambda_ridge)

        # Map player_id → player_name (use most common name that season)
        name_map = (
            df_season.groupby("player_id")["player_name"]
            .agg(lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0])
        )

        rapm_df = pd.DataFrame({
            "player_id": rapm.index,
            "rapm": rapm.values
        })
        rapm_df["player_name"] = rapm_df["player_id"].map(name_map)
        rapm_df["season"] = season

        rapm_rows.append(rapm_df)

    if not rapm_rows:
        raise ValueError("No RAPM results computed for any season")

    out = pd.concat(rapm_rows, ignore_index=True)
    return out


# --------------------------------------------------------
# MAIN
# --------------------------------------------------------
if __name__ == "__main__":
    print(f"Loading master features: {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV)

    # Ensure types
    df["game_id"] = df["game_id"].astype(str)
    df["team_id"] = df["team_id"].astype(str)

    # If season is not already in master, you can add it from game_date_team like this:
    if "season" not in df.columns:
        df["game_date_team"] = pd.to_datetime(df["game_date_team"])
        df["season"] = np.where(
            df["game_date_team"].dt.month >= 8,
            df["game_date_team"].dt.year,
            df["game_date_team"].dt.year - 1
        )

    print("Computing RAPM by player-season...")
    rapm_df = compute_rapm_by_season(df, lambda_ridge=LAMBDA_RIDGE)

    print(f"Saving RAPM results → {OUTPUT_RAPM}")
    rapm_df.to_csv(OUTPUT_RAPM, index=False)

    print("Done.")
