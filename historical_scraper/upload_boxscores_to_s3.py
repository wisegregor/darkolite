import boto3

# -----------------------------
# CONFIG
# -----------------------------
LOCAL_FILE = r"C:\Users\gngim\Desktop\Darko\features\features_all_seasons_combined\all_darko_features.csv"

BUCKET = "greg-darko-data"
S3_KEY = "raw/nba_api/player_boxscores/all_darko_features.csv"

# -----------------------------
# UPLOAD
# -----------------------------
s3 = boto3.client("s3")

try:
    s3.upload_file(LOCAL_FILE, BUCKET, S3_KEY)
    print(f"Uploaded successfully → s3://{BUCKET}/{S3_KEY}")
except Exception as e:
    print("Upload failed:", e)
