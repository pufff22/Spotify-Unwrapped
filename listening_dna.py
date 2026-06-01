import pandas as pd

df = pd.read_csv("tracks_clean.csv")

freshness = round((df["release_year"] >= 2023).sum() / len(df) * 100, 1)

top_artist_count = df["primary_artist"].value_counts().iloc[0]
loyalty = round((top_artist_count / len(df)) * 100, 1)

unique_artists = df["primary_artist"].nunique()
diversity = round((unique_artists / len(df)) * 100, 1)

# avg duration range: 1.5 mins (100) to 5 mins (0)
avg_duration = df["duration_mins"].mean()
brevity = round(max(0, min(100, (5 - avg_duration) / (5 - 1.5) * 100)), 1)

clean = round((1 - df["explicit"].mean()) * 100, 1)

print("🧬 Your Listening DNA Scores:")
print(f"  Freshness:  {freshness}")
print(f"  Loyalty:    {loyalty}")
print(f"  Diversity:  {diversity}")
print(f"  Brevity:    {brevity}")
print(f"  Clean:      {clean}")

# ── Generate personality label ─────────────────────────────
scores = {
    "Freshness": freshness,
    "Loyalty": loyalty,
    "Diversity": diversity,
    "Brevity": brevity,
    "Clean": clean
}

dominant = max(scores, key=scores.get)

labels = {
    "Freshness": "The Trendsetter",
    "Loyalty":   "The Devoted Fan",
    "Diversity": "The Explorer",
    "Brevity":   "The Snappy Listener",
    "Clean":     "The Pure Soul",
}

personality = labels[dominant]
print(f"\n🎭 Your Music Personality: {personality}")
print(f"   (Highest score: {dominant} at {scores[dominant]})")