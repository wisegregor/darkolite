import os
import time
import random
import logging
from datetime import datetime

import pandas as pd
from nba_api.stats.endpoints import leaguegamelog, boxscoretraditionalv2


# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)          # folder where this script lives
DATA_DIR = os.path.join(BASE_DIR, ".")       # player boxscores live here
TEAM_DIR = os.path.join(BASE_DIR, "team_boxscores")
LOG_DIR = os.path.join(BASE_DIR, "logs")

START_YEAR = 1997
END_YEAR = 2024   # non-inclusive; last season is 2023-24

os.makedirs(TEAM_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


# -------------------------------------------------------------------
# LOGGING SETUP
# -------------------------------------------------------------------
def init_logger():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = os.path.join(LOG_DIR, f"scrape_{ts}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(logfile, encoding="utf-8")
        ]
    )

    logging.info(f"📜 Logging to {logfile}")


# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------
def make_season_str(year: int) -> str:
    """Convert 1996 → '1996-97'."""
    return f"{year}-{str(year + 1)[-2:]}"


def list_existing_game_keys(season: str):
    """
    Return a set of 'season_GAMEID' for which player boxscore files already exist.
    Example key: '1996-97_0029600001'
    """
    prefix = f"player_boxscore_{season}_"
    existing = set()
    for f in os.listdir(DATA_DIR):
        if f.startswith(prefix) and f.endswith(".csv"):
            # player_boxscore_1996-97_0029600001.csv -> 1996-97_0029600001
            key = f.replace("player_boxscore_", "").replace(".csv", "")
            existing.add(key)
    return existing


def safe_request_boxscore(game_id: str) -> pd.DataFrame:
    """
    Extreme anti-ban boxscore fetcher.
    Retries with exponential backoff & jitter.
    """
    MAX_RETRIES = 25

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"📡 Requesting boxscore for GAME_ID {game_id} (attempt {attempt})")
            data = boxscoretraditionalv2.BoxScoreTraditionalV2(
                game_id=game_id,
                timeout=120,
            )
            df = data.get_data_frames()[0]
            return df

        except Exception as e:
            e_str = str(e).lower()

            # Conditions that look like throttling / connection issues
            throttle_tokens = [
                "read timed out",
                "timeout",
                "resultset",
                "too many requests",
                "forcibly closed",
                "connection aborted",
                "max retries exceeded",
            ]
            if any(tok in e_str for tok in throttle_tokens):
                base = 5 * attempt
                jitter = random.uniform(1, 5)
                wait = min(180, base + jitter)  # cap at 3 minutes

                logging.warning(
                    f"🚧 Throttled fetching {game_id}: {e}\n"
                    f"   → Cooling down for {wait:.1f} seconds "
                    f"(attempt {attempt}/{MAX_RETRIES})"
                )
                time.sleep(wait)
                continue

            # Generic error fallback
            wait = 3 * attempt + random.uniform(1, 3)
            logging.warning(
                f"⚠️ Error fetching {game_id}: {e}\n"
                f"   → Retrying in {wait:.1f} seconds "
                f"(attempt {attempt}/{MAX_RETRIES})"
            )
            time.sleep(wait)

    logging.error(f"❌ FAILED permanently for GAME_ID {game_id} after {MAX_RETRIES} attempts.")
    return pd.DataFrame()


def get_season_metadata(season: str) -> pd.DataFrame | None:
    """
    Get (or load from disk) team-level game metadata: one row per team per game.
    Saved to TEAM_DIR/boxscores_<season>.csv
    """
    out_path = os.path.join(TEAM_DIR, f"boxscores_{season}.csv")

    if os.path.exists(out_path):
        logging.info(f"✔ Team metadata already exists for {season} — loading from disk.")
        return pd.read_csv(out_path)

    logging.info(f"📡 Scraping team metadata for {season}...")

    # Retry logic around LeagueGameLog as well
    MAX_RETRIES = 10
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            data = leaguegamelog.LeagueGameLog(
                season=season,
                season_type_all_star="Regular Season",
                timeout=60
            )
            df = data.get_data_frames()[0]
            df.to_csv(out_path, index=False)
            logging.info(f"💾 Saved team metadata → {out_path}")
            return df

        except Exception as e:
            wait = 5 * attempt + random.uniform(1, 5)
            logging.warning(
                f"⚠️ Error fetching team metadata for {season}: {e}\n"
                f"   → Retrying in {wait:.1f} seconds (attempt {attempt}/{MAX_RETRIES})"
            )
            time.sleep(wait)

    logging.error(f"❌ Failed to fetch team metadata for {season} after {MAX_RETRIES} attempts.")
    return None


def season_sleep_base(season: str) -> float:
    """
    Slower scraping for older seasons to keep API happy.
    """
    if season.startswith("199") or season.startswith("2000"):
        return 2.5
    return 1.2


# -------------------------------------------------------------------
# CORE PIPELINE
# -------------------------------------------------------------------
def scrape_season(season: str):
    logging.info("")
    logging.info("================================================")
    logging.info(f"🏀 Processing season {season}")
    logging.info("================================================")

    # 1. Get metadata
    meta = get_season_metadata(season)
    if meta is None or meta.empty:
        logging.error(f"❌ No metadata for {season}, skipping season.")
        return

    # Standardize types & key columns (for joining)
    meta["GAME_ID"] = meta["GAME_ID"].astype(str)
    if "TEAM_ID" in meta.columns:
        meta["TEAM_ID"] = pd.to_numeric(meta["TEAM_ID"], errors="coerce")
    if "TEAM_ABBREVIATION" in meta.columns:
        meta["TEAM_ABBREVIATION"] = meta["TEAM_ABBREVIATION"].astype(str).str.upper()

    # 2. Determine game IDs (one per unique GAME_ID from metadata)
    game_ids = sorted(meta["GAME_ID"].unique())
    logging.info(f"📊 Found {len(game_ids)} unique GAME_IDs in metadata for {season}.")

    # 3. Determine which games already scraped (resume support)
    existing_keys = list_existing_game_keys(season)
    logging.info(f"⏩ Found {len(existing_keys)} existing player boxscores for {season} (will skip these).")

    # 4. Scrape each missing game
    base_sleep = season_sleep_base(season)

    for idx, game_id in enumerate(game_ids, start=1):
        key = f"{season}_{game_id}"
        out_path = os.path.join(DATA_DIR, f"player_boxscore_{season}_{game_id}.csv")

        if key in existing_keys and os.path.exists(out_path):
            logging.info(f"⏭ Skipping already-scraped game {key} ({idx}/{len(game_ids)})")
            continue

        logging.info(f"🎯 Scraping game {key} ({idx}/{len(game_ids)})")

        # --- Fetch player boxscore ---
        bs = safe_request_boxscore(game_id)
        if bs.empty:
            logging.warning(f"⚠️ Empty result for GAME_ID {game_id}, skipping.")
            continue

        # Standardize for join
        bs["GAME_ID"] = bs["GAME_ID"].astype(str)
        if "TEAM_ID" in bs.columns:
            bs["TEAM_ID"] = pd.to_numeric(bs["TEAM_ID"], errors="coerce")
        if "TEAM_ABBREVIATION" in bs.columns:
            bs["TEAM_ABBREVIATION"] = bs["TEAM_ABBREVIATION"].astype(str).str.upper()

        # --- Join with metadata (local, no extra network) ---
        meta_this_game = meta[meta["GAME_ID"] == game_id].copy()
        join_cols = [c for c in ["GAME_ID", "TEAM_ID", "TEAM_ABBREVIATION"] if c in bs.columns and c in meta_this_game.columns]

        if not join_cols:
            logging.warning(f"⚠️ No common join keys for GAME_ID {game_id}; saving stats only.")
            merged = bs
        else:
            merged = bs.merge(meta_this_game, on=join_cols, how="left")

        # --- Save result ---
        merged.to_csv(out_path, index=False)
        logging.info(f"💾 Saved merged boxscore: {out_path}")

        # --- Sleep between games to respect rate limits ---
        sleep_time = base_sleep + random.uniform(0.8, 1.6)
        logging.info(f"😴 Sleeping {sleep_time:.1f}s before next game...")
        time.sleep(sleep_time)

    logging.info(f"🎉 Completed season {season}")


def main():
    init_logger()

    for year in range(START_YEAR, END_YEAR):
        season = make_season_str(year)
        scrape_season(season)

        # pause a bit between seasons
        logging.info("🧊 Cooling down 10 seconds between seasons...")
        time.sleep(10)


# -------------------------------------------------------------------
# ENTRYPOINT
# -------------------------------------------------------------------
if __name__ == "__main__":
    main()
