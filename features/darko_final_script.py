import os
import numpy as np
import pandas as pd

# =====================================================
# CONFIG
# =====================================================

MASTER_CSV = r"C:\Users\gngim\Desktop\Darko\features\features_all_seasons_combined\all_darkoish_features_master.csv"
OUTPUT_CSV = r"C:\Users\gngim\Desktop\Darko\features\darko_final_player_season.csv"

LAMBDA_RIDGE = 300.0  # ridge penalty for RAPM

ALPHAS = {
    "pts_per100": 0.10,
    "reb_per100": 0.05,
    "ast_per100": 0.07,
    "stl_per100": 0.12,
    "blk_per100": 0.06,
    "to_per100": 0.10,
    "ts_pct_calc": 0.12,
    "efg_pct_calc": 0.12,
    "pm_per100": 0.18,
}

PRIORS = {
    "ts_pct_calc": 0.54,
    "efg_pct_calc": 0.52,
    "pm_per100": 0.0,
}


# =====================================================
# HELPERS
# =====================================================

def winsorize(s, lo=0.01, hi=0.99):
    if s.empty:
        return s
    return s.clip(s.quantile(lo), s.quantile(hi))


def ewma_smooth(values, alpha):
    out = np.zeros(len(values))
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = alpha * values[i] + (1 - alpha) * out[i - 1]
    return out


def z_score(df, col, group, outcol):
    def _z(s):
        sd = s.std(ddof=0)
        return (s - s.mean()) / (sd if sd > 0 else 1)
    df[outcol] = df.groupby(group)[col].transform(_z)
    return df


# =====================================================
# RAPM MODULE
# =====================================================

def safe_name(series):
    cleaned = series.dropna()
    cleaned = cleaned[cleaned.astype(str).str.strip() != ""]
    if cleaned.empty:
        return "Unknown"
    m = cleaned.mode()
    if not m.empty:
        return m.iloc[0]
    return cleaned.iloc[0]


def build_team_game_table(df):
    grp = df.groupby(["game_id", "team_id"], as_index=False)
    tg = grp.agg({
        "plus_minus_team": "first",
        "team_minutes": "first"
    })
    tg = tg[tg["team_minutes"] > 0].copy()
    tg["net_rating_team"] = tg["plus_minus_team"] / (tg["team_minutes"] / 48.0)
    tg["net_rating_team"] = winsorize(tg["net_rating_team"])
    tg["team_game_id"] = tg["game_id"].astype(str) + "_" + tg["team_id"].astype(str)
    return tg.set_index("team_game_id")


def build_design_matrix(df, team_games):
    df = df.copy()
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


def compute_ridge_rapm(design, team_games, lam):
    X = design.values
    y = team_games["net_rating_team"].values
    w = np.sqrt(team_games["team_minutes"].values / 48.0)
    Xw = X * w[:, None]
    yw = y * w

    n = X.shape[1]
    beta = np.linalg.solve(Xw.T @ Xw + lam * np.eye(n), Xw.T @ yw)
    rapm = pd.Series(beta, index=design.columns)
    return winsorize(rapm)


def compute_rapm_by_season(df):
    all_rapm = []
    seasons = sorted(df["season"].unique())
    print("RAPM seasons:", seasons)

    for season in seasons:
        print(f"\n--- RAPM {season} ---")
        sub = df[df["season"] == season].copy()

        sub = sub[(sub["minutes"] >= 4) & (sub["team_minutes"] >= 120)]
        if sub.empty:
            print("  No usable rows.")
            continue

        tg = build_team_game_table(sub)
        design = build_design_matrix(sub, tg)

        if design.empty:
            print("  No design matrix.")
            continue

        rapm_vals = compute_ridge_rapm(design, tg, LAMBDA_RIDGE)

        names = sub.groupby("player_id")["player_name"].agg(safe_name)

        df_out = pd.DataFrame({
            "player_id": rapm_vals.index,
            "rapm": rapm_vals.values,
            "season": season,
            "player_name": rapm_vals.index.map(names)
        })

        all_rapm.append(df_out)

    return pd.concat(all_rapm, ignore_index=True)


# =====================================================
# MAIN PIPELINE
# =====================================================

def main():
    print("Loading:", MASTER_CSV)
    df = pd.read_csv(MASTER_CSV, low_memory=False)

    df["game_id"] = df["game_id"].astype(str)
    df["team_id"] = df["team_id"].astype(str)
    df["player_id"] = df["player_id"].astype(int)
    df["game_date_team"] = pd.to_datetime(df["game_date_team"])
    df["season"] = df["season"].astype(str)

    # Clean box stats
    num_cols = [
        "pts_per100","reb_per100","ast_per100","stl_per100","blk_per100",
        "to_per100","fg3a_per100","fg3m_per100","fta_per100",
        "ts_pct_calc","efg_pct_calc","pm_per100"
    ]

    for col in num_cols:
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)

    for col, prior in PRIORS.items():
        df[col] = df[col].fillna(prior)

    for col in num_cols:
        df[col] = df.groupby("player_id")[col].transform(winsorize)

    df["minutes"] = df["minutes"].fillna(0)
    df["team_minutes"] = df["team_minutes"].fillna(240)

    # EWMA
    df = df.sort_values(["player_id", "game_date_team"])
    for stat, alpha in ALPHAS.items():
        print("EWMA:", stat)
        col_talent = f"{stat}_talent"

        def smooth(s):
            v = s.fillna(method="ffill").fillna(method="bfill").values
            return pd.Series(ewma_smooth(v, alpha), index=s.index)

        df[col_talent] = df.groupby("player_id")[stat].transform(smooth)

    # DARKO box
    print("Building DARKO box components...")

    df["darko_box_offense"] = (
        df["pts_per100_talent"] * 0.35 +
        df["ast_per100_talent"] * 0.25 +
        df["ts_pct_calc_talent"] * 15 +
        df["efg_pct_calc_talent"] * 10 -
        df["to_per100_talent"] * 0.20
    )

    df["darko_box_defense"] = (
        df["reb_per100_talent"] * 0.10 +
        df["blk_per100_talent"] * 0.25 +
        df["stl_per100_talent"] * 0.20 -
        df["to_per100_talent"] * 0.05
    )

    df["darko_box_total"] = df["darko_box_offense"] + df["darko_box_defense"]

    # SAFE collapse = mean over the season
    print("Collapsing to player-season…")
    df_box = (
        df.groupby(["player_id", "player_name", "season"], as_index=False)
          .agg({
              "darko_box_offense": "mean",
              "darko_box_defense": "mean",
              "darko_box_total": "mean",
          })
    )

    # Compute RAPM
    rapm_df = compute_rapm_by_season(df)

    df_box["season"] = df_box["season"].astype(str)
    rapm_df["season"] = rapm_df["season"].astype(str)

    # Merge
    df_merged = df_box.merge(
        rapm_df[["player_id", "season", "rapm"]],
        on=["player_id", "season"],
        how="left"
    )

    df_merged["rapm"] = df_merged["rapm"].fillna(0.0)

    # Scale
    df_merged = z_score(df_merged, "darko_box_total", "season", "box_z")
    df_merged = z_score(df_merged, "rapm", "season", "rapm_z")

    df_merged["darko_blend_z"] = 0.36 * df_merged["box_z"] + 0.64 * df_merged["rapm_z"]
    df_merged["darko_final_dpm"] = (df_merged["darko_blend_z"] * 4.0).clip(-10, 10)

    df_merged = df_merged.sort_values(["season", "darko_final_dpm"], ascending=[True, False])

    print("Saving →", OUTPUT_CSV)
    df_merged.to_csv(OUTPUT_CSV, index=False)
    print("DONE!")


if __name__ == "__main__":
    main()
