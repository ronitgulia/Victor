import json
import pandas as pd
import numpy as np
from datetime import datetime

LOG_FILE = "data/traffic_logs.json"

def load_logs():
    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    df = pd.DataFrame(logs)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df = df.sort_values("timestamp").reset_index(drop=True)

    print(f"Loaded {len(df)} log entries.")
    return df

def extract_features(df):

    features = pd.DataFrame()

    BOT_KEYWORDS = ["python", "scrapy", "curl", "go-http", "wget", "bot", "crawl", "spider"]

    features["ua_is_suspicious"] = df["user_agent"].str.lower().apply(
        lambda ua: 1 if any(kw in ua for kw in BOT_KEYWORDS) else 0
    )
    # bots often just hit URLs directly with no referer
    features["has_referer"] = df["referer"].apply(
        lambda r: 0 if r == "none" else 1
    )

    features["has_accept_lang"] = df["accept_lang"].apply(
        lambda a: 0 if a == "none" else 1
    )

    features["hit_secret_page"] = df["path"].apply(
        lambda p: 1 if "secret" in p else 0
    )

    features["ua_length"] = df["user_agent"].str.len()

    df["time_gap"] = df.groupby("ip")["timestamp"].diff().dt.total_seconds().fillna(5)
    features["time_gap_seconds"] = df["time_gap"]

    page_counts = df.groupby("ip")["path"].nunique()
    features["unique_pages_visited"] = df["ip"].map(page_counts)

    request_counts = df.groupby("ip")["path"].count()
    features["total_requests_from_ip"] = df["ip"].map(request_counts)

    features["label"] = df["label"].values

    print(f"Extracted {features.shape[1]-1} features from {len(features)} entries.")
    return features

def save_features(features):
    features.to_csv("data/features.csv", index=False)
    print("Saved to data/features.csv")


if __name__ == "__main__":
    df       = load_logs()
    features = extract_features(df)
    save_features(features)

    print("\nSample of extracted features:")
    print(features.head(10).to_string())

    print("\nBot vs Human label counts:")
    print(features["label"].value_counts())