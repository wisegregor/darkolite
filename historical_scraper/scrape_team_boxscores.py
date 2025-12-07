import time
import pandas as pd
import boto3
from nba_api.stats.endpoints import leaguegamelog
from nba_api.stats.library.parameters import SeasonAll
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# --------------------------
# CONFIG
# --------------------------

START_YEAR = 1996   # NBA API goes back to 1996-97
END_YEAR   = 2025   # update when new season begins

SAVE_LOCAL = True
UPLOAD_TO_S3 = False       # set to True after testing

S3_BUCKET = "greg-darko-data"
S3_PREFIX = "historical/boxscores/"  # folder inside bucket


# --------------------------
# HELPERS
# --------------------------

def make_season_str(year: int) -> str:
    """Convert 1996 → '1996-97'."""
    return f"{year}-{str(year+1)[-2:]}"


def fetch_season_boxscores(season: str) -> pd.DataFrame:
    """
    Pull a full season of player box scores (regular season only).
    Example: season = '2001-02'
    """
    print(f"📡 Fetching: {season}")

    # NBA API can fail randomly — retry logic included
    for attempt in range(5):
        try:
            data = leaguegamelog.LeagueGameLog(
                season=season,
                season_type_all_star="Regular Season"
            )
            df = data.get_data_frames()[0]
            
            if df.empty:
                print(f"⚠️ No data returned for {season} — skipping.")
            else:
                print(f"✅ Retrieved {len(df)} rows for {season}")
            
            return df

        except Exception as e:
            print(f"⚠️ Error fetching {season} (attempt {attempt+1}/5): {e}")
            time.sleep(2)

    print(f"❌ Failed to retrieve season: {season}")
    return pd.DataFrame()


def save_local_csv(df: pd.DataFrame, season: str):
    """Save a CSV file locally."""
    filename = f"boxscores_{season}.csv"
    df.to_csv(filename, index=False)
    print(f"💾 Saved locally: {filename}")


def upload_to_s3(df: pd.DataFrame, season: str):
    """Upload CSV of season data to S3."""
    s3 = boto3.client("s3")

    key = f"{S3_PREFIX}boxscores_{season}.csv"
    csv_data = df.to_csv(index=False)

    try:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=csv_data.encode("utf-8"),
            ContentType="text/csv"
        )
        print(f"☁️ Uploaded to S3: s3://{S3_BUCKET}/{key}")

    except (NoCredentialsError, PartialCredentialsError):
        print("❌ AWS credentials not found! Run `aws configure` and try again.")


# --------------------------
# MAIN LOOP
# --------------------------

def scrape_full_history(start_year=START_YEAR, end_year=END_YEAR):
    for year in range(start_year, end_year):
        season = make_season_str(year)
        print("\n==============================")
        print(f"🔎 Scraping season {season}")
        print("==============================")

        df = fetch_season_boxscores(season)
        if df.empty:
            continue

        # Save locally
        if SAVE_LOCAL:
            save_local_csv(df, season)

        # Upload to S3
        if UPLOAD_TO_S3:
            upload_to_s3(df, season)

        # Respect NBA API rate limiting
        print("⏳ Waiting 1.5 seconds to avoid NBA API ban…")
        time.sleep(1.5)


if __name__ == "__main__":
    print("\n🚀 Starting full NBA history scrape…\n")
    scrape_full_history()
    print("\n🏁 Done — full history downloaded!\n")
