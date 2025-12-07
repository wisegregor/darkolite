import os
import numpy as np
import pandas as pd

# --------------------------------------------------------
# CONFIG
# --------------------------------------------------------
BOX_CSV = r"C:\Users\gngim\Desktop\Darko\features\darkolite\darkolite_box_player_season.csv"
RAPM_CSV = r"C:\Users\gngim\Desktop\Darko\features\darkolite\darkolite_rapm_player_season.csv"
OUTPUT_FINAL = r"C:\Users\gngim\Desktop\Darko\features\darkolite\darkolite_player_season_final.csv"

# Blend weights (tweakable)
BOX_WEIGHT = 0.55
RAPM_WEIGHT = 0.45

# Scaling to DARKO-ish range
SCALE = 3.5  # typical range ends up around -6 to +8


# --------------------------------------------------------
# HELPERS
# --------------------------------------------------------
def z_score_qualified(df, col, group_col, outcol, min_minutes=None, minutes_col=None):
    """
    Z-score col within group_col, but compute mean/std only on 'qualified' players
    (e.g., season_minutes >= 1000) if min_minutes is provided.
    """
    df[outcol] = np.nan

    def _apply(group):
        g = group.copy()
        if min_minutes is not None and minutes_col is not None and minutes_col in g.columns:
            qual = g[g[minutes_col] >= min_minutes]
        else:
            qual = g

        if qual.empty:
            mu = g[col].mean()
            sd = g[col].std(ddof=0)
        else:
            mu = qual[col].mean()
            sd = qual[col].std(ddof=0)

        if sd <= 0 or np.isnan(sd):
            g[outcol] = 0.0
        else:
            g[outcol] = (g[col] - mu) / sd
        return g

    df = df.groupby(group_col, group_keys=False).apply(_apply)
    return df


# --------------------------------------------------------
# MAIN
# --------------------------------------------------------
if __name__ == "__main__":
    print("Loading box:", BOX_CSV)
    box = pd.read_csv(BOX_CSV)

    print("Loading RAPM:", RAPM_CSV)
    rapm = pd.read_csv(RAPM_CSV)

    box["season"] = box["season"].astype(str)
    rapm["season"] = rapm["season"].astype(str)
    box["player_id"] = box["player_id"].astype(int)
    rapm["player_id"] = rapm["player_id"].astype(int)

    # Merge
    df = box.merge(
        rapm[["player_id", "season", "rapm_darkolite"]],
        on=["player_id", "season"],
        how="left"
    )

    df["rapm_darkolite"] = df["rapm_darkolite"].fillna(0.0)

    # If you have season_minutes, merge it in for better z-scoring
    # (optional but recommended – you can compute this in the box script later)
    # For now, we'll assume not present and do simple season z-scores.

    # Z-score box total & RAPM within season
    df = z_score_qualified(df, "darkolite_box_total", "season", "box_z",
                           min_minutes=None, minutes_col=None)
    df = z_score_qualified(df, "rapm_darkolite", "season", "rapm_z",
                           min_minutes=None, minutes_col=None)

    # DARKO-Lite blend
    df["darkolite_blend_z"] = BOX_WEIGHT * df["box_z"] + RAPM_WEIGHT * df["rapm_z"]

    # Scale to DPM-like units
    df["darkolite_dpm"] = (df["darkolite_blend_z"] * SCALE).clip(-10, 10)

    # Sort nicely
    df = df.sort_values(["season", "darkolite_dpm"], ascending=[True, False])

    print("Saving final DARKO-Lite file →", OUTPUT_FINAL)
    df.to_csv(OUTPUT_FINAL, index=False)
    print("Done.")
