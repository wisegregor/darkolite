import os
import time
import random
import logging
import pandas as pd
from nba_api.stats.endpoints import boxscoretraditionalv2
from nba_api.stats.endpoints import leaguegamelog

# ------------------------------------------------------------------
# NEW: Prevent NBA API throttling
# ------------------------------------------------------------------
from nba_api.stats.library.http import NBAStatsHTTP

NBAStatsHTTP.headers.update({
    "Host": "stats.nba.com",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
    "Connection": "keep-alive",
})
# ------------------------------------------------------------------


# ---------------------------------------------------
# LOGGING
# ---------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------
START_YEAR = 1996
END_YEAR = 2025
SAVE_LOCAL = True
UPLOAD_TO_S3 = False
OUTPUT_DIR = "./"   # unchanged


# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------
def make_season_str(year: int) -> str:
    return f"{year}-{str(year + 1)[-2:]}"


def list_existing_files():
    return set(
        f.replace("player_boxscore_", "").replace(".csv", "")
        for f in os.listdir(".")
        if f.startswith("player_boxscore_") and f.endswith(".csv")
    )


def fetch_player_boxscore(game_id: str) -> pd.DataFrame:
    """
    Fetch player box scores with retry logic.
    """
    MAX_RETRIES = 12

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            data = boxscoretraditionalv2.BoxScoreTraditionalV2(
                game_id=game_id,
                timeout=90
            )
            df = data.get_data_frames()[0]
            return df

        except Exception as e:
            e_str = str(e).lower()

            # Very NBA-specific connection-drop case
            if "forcibly closed" in e_str or "connection aborted" in e_str:
                wait = 8 + random.uniform(2, 5)
                logging.warning(
                    f"⚠️ Host reset for {game_id}. Cooling {wait:.1f}s "
                    f"(attempt {attempt}/{MAX_RETRIES})"
                )
                time.sleep(wait)
                continue

            # Normal retry (NBA likes slow ramp-up)
            wait = min(2 * attempt + random.uniform(0.5, 1.5), 20)
            logging.warning(
                f"⚠️ Error fetching {game_id}: {e} "
                f"(attempt {attempt}/{MAX_RETRIES}) — waiting {wait:.1f}s"
            )
            time.sleep(wait)

    logging.error(f"❌ FAILED after {MAX_RETRIES} attempts: {game_id}")
    return pd.DataFrame()


def scrape_season(season: str):
    logging.info(f"===== Scraping season {season} =====")

    games = leaguegamelog.LeagueGameLog(
        season=season,
        season_type_all_star="Regular Season"
    ).get_data_frames()[0]

    meta_cols = [
        "GAME_ID", "GAME_DATE", "TEAM_ID",
        "TEAM_ABBREVIATION", "MATCHUP", "WL"
    ]
    game_meta = games[meta_cols]

    existing = list_existing_files()

    for game_id in game_meta["GAME_ID"].unique():
        filename_key = f"{season}_{game_id}"

        if filename_key in existing:
            logging.info(f"⏩ Skipping (already scraped): {filename_key}")
            continue

        bs = fetch_player_boxscore(game_id)
        if bs.empty:
            logging.warning(f"⚠️ Empty result for {game_id}")
            continue

        meta_this_game = game_meta[game_meta["GAME_ID"] == game_id]

        merged = bs.merge(
            meta_this_game,
            on=["GAME_ID", "TEAM_ID", "TEAM_ABBREVIATION"],
            how="left"
        )

        outname = f"player_boxscore_{season}_{game_id}.csv"
        merged.to_csv(outname, index=False)
        logging.info(f"💾 Saved merged boxscore: {outname}")

        # anti-ban sleep (small but necessary)
        time.sleep(1.0 + random.uniform(0.4, 1.2))


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------
if __name__ == "__main__":
    logging.info("🚀 Starting improved V2 player boxscore scraper...")

    for year in range(START_YEAR, END_YEAR):
        season = make_season_str(year)
        scrape_season(season)

    logging.info("🏁 DONE — full historical player box scores scraped.")
