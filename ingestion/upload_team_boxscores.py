import polars as pl

# -------------------------------------
# CONFIG
# -------------------------------------

S3_BUCKET = "greg-darko-data"
S3_PATH = "historical/boxscores/*.csv"

FULL_S3_URI = f"s3://{S3_BUCKET}/{S3_PATH}"


def load_all_boxscores() -> pl.DataFrame:
    """
    Loads all boxscore CSV files from S3 and returns a combined Polars DataFrame.
    """

    print(f"📡 Reading boxscore files from: {FULL_S3_URI}")

    # Lazy scanning = memory efficient & fast
    df = (
        pl.scan_csv(FULL_S3_URI)
        .with_columns([
            pl.col("GAME_DATE").str.to_date(strict=False).alias("game_date"),
            pl.col("PLAYER_NAME").str.to_uppercase().alias("player_name"),
        ])
        .collect()
    )

    print(f"✅ Loaded {df.shape[0]:,} rows across {df['SEASON_ID'].n_unique()} seasons.")
    print(f"👤 Unique players: {df['PLAYER_ID'].n_unique()}")
    print(f"📅 Date range: {df['game_date'].min()} → {df['game_date'].max()}")

    return df


if __name__ == "__main__":
    df = load_all_boxscores()
    print(df.head(10))
