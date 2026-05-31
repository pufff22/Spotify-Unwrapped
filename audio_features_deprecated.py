import pandas as pd

# ── Load your top 50 tracks ────────────────────────────────
your_tracks = pd.read_csv("tracks_clean.csv")

# ── Load Kaggle dataset ────────────────────────────────────
print("Loading Kaggle dataset...")
kaggle = pd.read_csv("spotify_kaggle.csv")

# ── Clean for matching ─────────────────────────────────────
your_tracks["track_name_clean"] = your_tracks["track_name"].str.lower().str.strip()

kaggle["track_name_clean"] = kaggle["track_name"].str.lower().str.strip()

# ── Keep only audio features ───────────────────────────────
kaggle_features = kaggle[[
    "track_name_clean",
    "energy", "valence", "danceability",
    "acousticness", "instrumentalness",
    "speechiness", "tempo"
]].drop_duplicates(subset=["track_name_clean"])

# ── Match on track name ONLY (drop artist matching) ───────
merged = your_tracks.merge(
    kaggle_features,
    on="track_name_clean",
    how="left"
)

matched = merged["energy"].notna().sum()
unmatched = merged["energy"].isna().sum()

print(f"\n✅ Matched: {matched}/50 tracks")
print(f"❌ Unmatched: {unmatched}/50 tracks")

if unmatched > 0:
    print("\n🔍 Still unmatched:")
    print(merged[merged["energy"].isna()][["track_name", "primary_artist"]])

merged.to_csv("tracks_with_features.csv", index=False)
print("\n💾 Saved!")