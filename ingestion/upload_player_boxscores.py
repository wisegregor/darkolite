import polars as pl
import glob
import os

# -------------------------------------
# CONFIG
# -------------------------------------

# Path to your local scraper output
LOCAL_DATA_PATH = "../historical_scraper/player_boxscore_*.csv"


def load_player_boxscores() -> pl.DataFrame:
    """
    Loads ALL player-level box score CSVs from local disk
    and returns a unified Polars DataFrame.
    """
    print(f"📁 Looking for files: {LOCAL_DATA_PATH}")

    files = glob.glob(LOCAL_DATA_PATH)
    print(f"📄 Found {len(files):,} game files.")

    if not files:
        raise FileNotFoundError("❌ No player boxscore CSVs found. Run scraper first.")

    # Polars lazy scan = massively faster
    df = (
        pl.scan_csv(files)
        .with_columns([
            # Core normalization
            pl.col("GAME_DATE").str.to_date(strict=False).alias("game_date"),
            pl.col("PLAYER_NAME").str.to_uppercase().alias("player_name"),
            pl.col("TEAM_ABBREVIATION").str.to_uppercase().alias("team"),
            pl.col("START_POSITION").fill_null("BENCH").alias("start_pos"),

            # Numeric conversions
            pl.col("MIN").cast(pl.Float64).alias("minutes"),
            pl.col("PTS").cast(pl.Int64),
            pl.col("REB").cast(pl.Int64),
            pl.col("AST").cast(pl.Int64),
            pl.col("STL").cast(pl.Int64),
            pl.col("BLK").cast(pl.Int64),
            pl.col("TOV").cast(pl.Int64),
            pl.col("PF").cast(pl.Int64),
            pl.col("PLUS_MINUS").cast(pl.Int64),

            # Game metadata
            pl.col("PLAYER_ID").cast(pl.Int64),
            pl.col("TEAM_ID").cast(pl.Int64),
            pl.col("GAME_ID"),
        ])
        .collect()
    )

    print("====================================")
    print(f"✅ Loaded rows: {df.shape[0]:,}")
    print(f"🧍 Unique players: {df['PLAYER_ID'].n_unique()}")
    print(f"📅 Date range: {df['game_date'].min()} → {df['game_date'].max()}")
    print(f"🕒 Columns: {df.columns}")
    print("====================================")

    return df


if __name__ == "__main__":
    df = load_player_boxscores()
    print(df.head(20))
