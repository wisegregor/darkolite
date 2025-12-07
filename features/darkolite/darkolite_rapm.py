import os
import numpy as np
import pandas as pd

# --------------------------------------------------------
# CONFIG
# --------------------------------------------------------
MASTER_CSV = r"C:\Users\gngim\Desktop\Darko\features\features_all_seasons_combined\all_darkoish_features_master.csv"
OUTPUT_RAPM = r"C:\Users\gngim\Desktop\Darko\features\darkolite_rapm_player_season.csv"

LAMBDA_RIDGE = 1500.0  # heavier ridge to shrink noise


# --------------------------------------------------------
# HELPERS
# --------------------------------------------------------
def winsorize(s: pd.Series, lo: float = 0.01, hi: float = 0.99) -> pd.Series:
    if s.empty:
        return s
    return s.clip(s.quantile(lo), s.quantile(hi))


def safe_name(series: pd.Series) -> str:
    cleaned = series.dropna()
    cleaned = cleaned[cleaned.astype(str).str.strip() != ""]
    if cleaned.empty:
        return "Unknown"
    m = cleaned.mode()
    if not m.empty:
        return m.iloc[0]
    return cleaned.iloc[0]


def build_team_game_table(df_season: pd.DataFrame) -> pd.DataFrame:
    grp = df_season.groupby(["game_id", "team_id"], as_index=False)
    tg = grp.agg({
        "plus_minus_team": "first",
        "team_minutes": "first"
    })

    tg = tg[tg["team_minutes"] > 0].copy()
    tg["net_rating_team"] = tg["plus_minus_team"] / (tg["team_minutes"] / 48.0)
    tg["net_rating_team"] = winsorize(tg["net_rating_team"])
    tg["team_game_id"] = tg["game_id"].astype(str) + "_" + tg["team_id"].astype(str)
    return tg.set_index("team_game_id")


def build_design_matrix(df_season: pd.DataFrame, team_games: pd.DataFrame) -> pd.DataFrame:
    df = df_season.copy()
    df["minute_share"] = (df["minutes"] / df["team_minutes"]).clip(0, 1)
    df["team_game_id"] = df["game_id"].astype(str) + "_" + df["team_id"].astype(str)
    df = df[df["team_game_id"].isin(team_games.index)]

    design = df.pivot_table(
        index="team_game_id",
        columns="player_id",
        values="minute_share",
        aggfunc="sum",
        fill_value=0.0
    )

    return design.reindex(team_games.index)


def compute_ridge_rapm(design: pd.DataFrame, team_games: pd.DataFrame, lam: float) -> pd.Series:
    X = design.values
    y = team_games["net_rating_team"].values
    w = np.sqrt(team_games["team_minutes"].values / 48.0)

    Xw = X * w[:, None]
    yw = y * w

    n = X.shape[1]
    beta = np.linalg.solve(Xw.T @ Xw + lam * np.eye(n), Xw.T @ yw)
    rapm = pd.Series(beta, index=design.columns)
    return winsorize(rapm)


# --------------------------------------------------------
# MAIN
# --------------------------------------------------------
if __name__ == "__main__":
    print("Loading:", MASTER_CSV)
    df = pd.read_csv(MASTER_CSV, low_memory=False)

    df["game_id"] = df["game_id"].astype(str)
    df["team_id"] = df["team_id"].astype(str)
    df["player_id"] = df["player_id"].astype(int)
    df["season"] = df["season"].astype(str)

    # Clean minutes
    df["minutes"] = df["minutes"].fillna(0)
    df["team_minutes"] = df["team_minutes"].fillna(240)

    rapm_rows = []
    seasons = sorted(df["season"].unique())
    print("Seasons:", seasons)

    for season in seasons:
        print(f"\n--- RAPM for season {season} ---")
        sub = df[df["season"] == season].copy()

        # Filter junk
        sub = sub[(sub["minutes"] >= 4) & (sub["team_minutes"] >= 120)]
        if sub.empty:
            print("  No usable rows for this season.")
            continue

        team_games = build_team_game_table(sub)
        design = build_design_matrix(sub, team_games)

        if design.empty:
            print("  Empty design matrix, skipping.")
            continue

        rapm = compute_ridge_rapm(design, team_games, LAMBDA_RIDGE)

        names = sub.groupby("player_id")["player_name"].agg(safe_name)

        out = pd.DataFrame({
            "player_id": rapm.index,
            "rapm_darkolite": rapm.values,
            "season": season,
        })
        out["player_name"] = out["player_id"].map(names)
        rapm_rows.append(out)

    if not rapm_rows:
        raise ValueError("No RAPM results computed.")

    rapm_all = pd.concat(rapm_rows, ignore_index=True)

    print("Saving RAPM output →", OUTPUT_RAPM)
    rapm_all.to_csv(OUTPUT_RAPM, index=False)
    print("Done.")
