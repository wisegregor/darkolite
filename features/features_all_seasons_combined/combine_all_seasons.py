import os
import pandas as pd

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
BASE_DIR = r"C:\Users\gngim\Desktop\Darko\historical_scraper\all_seasons"
OUTPUT_MASTER = os.path.join(BASE_DIR, "all_darkish_features_master.csv")


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def combine_all_seasons():
    all_rows = []

    # Get all season folders like "1996-97", "1997-98", ..., "2025-26"
    seasons = sorted([
        folder for folder in os.listdir(BASE_DIR)
        if os.path.isdir(os.path.join(BASE_DIR, folder))
    ])

    print("\n📅 Found seasons to combine:")
    for s in seasons:
        print("   •", s)

    print("\n🚀 Starting merge of all darko_feature CSVs...\n")

    # Loop through each season folder
    for season in seasons:
        season_dir = os.path.join(BASE_DIR, season)
        feature_path = os.path.join(season_dir, f"darko_features_{season}.csv")

        if not os.path.exists(feature_path):
            print(f"❌ Missing: {feature_path} — skipping")
            continue

        print(f"📥 Loading: {feature_path}")
        df = pd.read_csv(feature_path)

        # Make sure a "season" column exists
        df["season"] = season

        all_rows.append(df)

    # Combine all seasons into one DataFrame
    if not all_rows:
        print("\n❌ No season files found. Nothing to combine.")
        return

    master_df = pd.concat(all_rows, ignore_index=True)
    print(f"\n🔢 Combined total rows: {len(master_df):,}")

    # Save master CSV
    print(f"💾 Saving master file → {OUTPUT_MASTER}")
    master_df.to_csv(OUTPUT_MASTER, index=False)

    print("\n🎉 Successfully created master features file!")


if __name__ == "__main__":
    combine_all_seasons()
