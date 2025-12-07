import os
import pandas as pd
from nba_api.stats.endpoints import leaguegamelog

DATA_DIR = "../historical_scraper"
START_YEAR = 2024
END_YEAR = 2025

os.makedirs(DATA_DIR, exist_ok=True)

def make_season(year):
    return f"{year}-{str(year+1)[-2:]}"


def scrape_full_season(season):
    out_path = f"{DATA_DIR}/player_boxscores_season_{season}.csv"

    if os.path.exists(out_path):
        print(f"✔ Season {season} already scraped — skipping.")
        return

    print(f"📡 Scraping FULL season player data for {season}...")

    df = leaguegamelog.LeagueGameLog(
        season=season,
        season_type_all_star="Regular Season"
    ).get_data_frames()[0]

    # Clean and standardize
    df["GAME_ID"] = df["GAME_ID"].astype("int64")
    df["TEAM_ID"] = df["TEAM_ID"].astype("int64")
    df["PLAYER_ID"] = df["PLAYER_ID"].astype("int64")

    df.to_csv(out_path, index=False)
    print(f"💾 Saved → {out_path}")


def main():
    for year in range(START_YEAR, END_YEAR):
        season = make_season(year)
        scrape_full_season(season)

    print("\n🎉 ALL SEASONS DOWNLOADED SUCCESSFULLY")


if __name__ == "__main__":
    main()
