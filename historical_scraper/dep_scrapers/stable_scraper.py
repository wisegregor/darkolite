import os
import time
import pandas as pd
from nba_api.stats.endpoints import leaguegamelog, leaguegamedetails

DATA_DIR = "./player_boxscores"
META_DIR = "./team_boxscores"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)

START_YEAR = 1996
END_YEAR = 2024


def make_season(year):
    return f"{year}-{str(year+1)[-2:]}"


def safe_request(func, *args, retries=5, base_delay=2, **kwargs):
    for i in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            wait = base_delay * (i + 1)
            print(f"⚠ API error: {e} — retrying in {wait}s")
            time.sleep(wait)
    print("❌ Failed after max retries")
    return None


def scrape_team_metadata(season):
    """One call per season."""
    out_path = f"{META_DIR}/boxscores_{season}.csv"
    if os.path.exists(out_path):
        print(f"✔ Team metadata already exists for {season} — skipping")
        return

    print(f"📡 Scraping team metadata for {season}...")

    df = leaguegamelog.LeagueGameLog(
        season=season,
        season_type_all_star="Regular Season"
    ).get_data_frames()[0]

    df.to_csv(out_path, index=False)
    print(f"💾 Saved → {out_path}")


def scrape_player_boxscores(season):
    """One call per game — using stable LeagueGameDetails."""
    meta_path = f"{META_DIR}/boxscores_{season}.csv"
    if not os.path.exists(meta_path):
        print(f"❌ No team metadata for {season}")
        return

    meta = pd.read_csv(meta_path)
    game_ids = meta["GAME_ID"].unique().tolist()

    print(f"🧮 Found {len(game_ids)} games for {season}")

    for gid in game_ids:
        out_path = f"{DATA_DIR}/player_boxscore_{season}_{gid}.csv"

        if os.path.exists(out_path):
            # Skip already scraped games
            continue

        print(f"📡 Scraping player data for GAME_ID {gid}...")

        resp = safe_request(leaguegamedetails.LeagueGameDetails, game_id=str(gid))
        if resp is None:
            print(f"❌ Skipping GAME_ID {gid}")
            continue

        df = resp.get_data_frames()[1]  # index 1 = player stats table

        df.to_csv(out_path, index=False)
        print(f"💾 Saved → {out_path}")

        time.sleep(1)  # obey rate limits


def main():
    for year in range(START_YEAR, END_YEAR):
        season = make_season(year)
        print("\n==============================")
        print(f"🏀 Processing {season}")
        print("==============================")

        scrape_team_metadata(season)
        scrape_player_boxscores(season)

        print(f"🎉 Season {season} complete.\n")


if __name__ == "__main__":
    main()
