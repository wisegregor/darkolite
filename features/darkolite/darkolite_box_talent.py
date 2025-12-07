import os
import numpy as np
import pandas as pd

# --------------------------------------------------------
# CONFIG
# --------------------------------------------------------
MASTER_CSV = r"C:\Users\gngim\Desktop\Darko\features\features_all_seasons_combined\all_darkoish_features_master.csv"
OUTPUT_BOX_SEASON = r"C:\Users\gngim\Desktop\Darko\features\darkolite\darkolite_box_player_season.csv"

# Fast/slow decay rates per stat (approx DARKO-ish)
ALPHA_FAST = {
    "pts_per100": 0.35,
    "reb_per100": 0.25,
    "ast_per100": 0.30,
    "stl_per100": 0.45,
    "blk_per100": 0.40,
    "to_per100": 0.35,
    "ts_pct_calc": 0.25,
    "efg_pct_calc": 0.25,
    "pm_per100": 0.50,
}

ALPHA_SLOW = {
    "pts_per100": 0.10,
    "reb_per100": 0.07,
    "ast_per100": 0.08,
    "stl_per100": 0.15,
    "blk_per100": 0.12,
    "to_per100": 0.10,
    "ts_pct_calc": 0.07,
    "efg_pct_calc": 0.07,
    "pm_per100": 0.20,
}

PRIORS = {
    "ts_pct_calc": 0.54,
    "efg_pct_calc": 0.52,
    "pm_per100": 0.0,
}

# --------------------------------------------------------
# HELPERS
# --------------------------------------------------------
def winsorize(s: pd.Series, lo: float = 0.01, hi: float = 0.99) -> pd.Series:
    if s.empty:
        return s
    return s.clip(s.quantile(lo), s.quantile(hi))


def ewma_smooth(values: np.ndarray, alpha: float) -> np.ndarray:
    if len(values) == 0:
        return values
    out = np.zeros(len(values))
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = alpha * values[i] + (1 - alpha) * out[i - 1]
    return out


def z_score(df: pd.DataFrame, col: str, group: str, outcol: str) -> pd.DataFrame:
    def _z(s: pd.Series) -> pd.Series:
        sd = s.std(ddof=0)
        if sd <= 0 or np.isnan(sd):
            return pd.Series(0.0, index=s.index)
        return (s - s.mean()) / sd
    df[outcol] = df.groupby(group)[col].transform(_z)
    return df


# --------------------------------------------------------
# MAIN
# --------------------------------------------------------
if __name__ == "__main__":
    print("Loading master features:", MASTER_CSV)
    df = pd.read_csv(MASTER_CSV, low_memory=False)

    # Types & ordering
    df["game_date_team"] = pd.to_datetime(df["game_date_team"])
    df["player_id"] = df["player_id"].astype(int)
    df["season"] = df["season"].astype(str)

    df = df.sort_values(["player_id", "game_date_team"])

    # Clean base stats
    base_stats = [
        "pts_per100", "reb_per100", "ast_per100", "stl_per100", "blk_per100",
        "to_per100", "ts_pct_calc", "efg_pct_calc", "pm_per100"
    ]

    for col in base_stats:
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)

    for col, prior in PRIORS.items():
        if col in df.columns:
            df[col] = df[col].fillna(prior)

    for col in base_stats:
        df[col] = df.groupby("player_id")[col].transform(winsorize)

    # Fast/slow EWMA & blend into "talent"
    for stat in base_stats:
        if stat not in df.columns:
            print(f"Warning: missing {stat}, skipping.")
            continue

        alpha_f = ALPHA_FAST[stat]
        alpha_s = ALPHA_SLOW[stat]

        def smooth_pair(s: pd.Series) -> pd.DataFrame:
            v = s.fillna(method="ffill").fillna(method="bfill").values
            fast = ewma_smooth(v, alpha_f)
            slow = ewma_smooth(v, alpha_s)
            # 70% slow, 30% fast → stable but responsive
            blended = 0.70 * slow + 0.30 * fast
            return pd.DataFrame({
                f"{stat}_fast": fast,
                f"{stat}_slow": slow,
                f"{stat}_talent": blended
            }, index=s.index)

        print(f"EWMA fast/slow for {stat} ...")
        talent_df = (
            df.groupby("player_id", group_keys=False)[stat]
              .apply(smooth_pair)
        )

        df = pd.concat([df, talent_df], axis=1)

    # Box-only DARKO-lite components
    print("Building DARKO-Lite box components...")

    df["darkolite_box_offense"] = (
        df["pts_per100_talent"] * 0.40 +
        df["ast_per100_talent"] * 0.25 +
        df["ts_pct_calc_talent"] * 12 +
        df["efg_pct_calc_talent"] * 8 -
        df["to_per100_talent"] * 0.25
    )

    df["darkolite_box_defense"] = (
        df["reb_per100_talent"] * 0.12 +
        df["blk_per100_talent"] * 0.30 +
        df["stl_per100_talent"] * 0.25 -
        df["to_per100_talent"] * 0.05
    )

    df["darkolite_box_total"] = df["darkolite_box_offense"] + df["darkolite_box_defense"]

    # Collapse to player-season via average of talent
    print("Collapsing DARKO-Lite box talents to player-season...")
    box_cols = [
        "darkolite_box_offense",
        "darkolite_box_defense",
        "darkolite_box_total",
    ]

    df_box = (
        df.groupby(["player_id", "player_name", "season"], as_index=False)
          .agg({c: "mean" for c in box_cols})
    )

    # Within-season z-scoring of box-total to make it comparable across seasons
    df_box = z_score(df_box, "darkolite_box_total", "season", "darkolite_box_z")

    print("Saving box-only DARKO-Lite player-season file →", OUTPUT_BOX_SEASON)
    df_box.to_csv(OUTPUT_BOX_SEASON, index=False)
    print("Done.")
