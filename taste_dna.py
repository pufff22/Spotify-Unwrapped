import pandas as pd

# ── Load clean data ────────────────────────────────────────
df = pd.read_csv("tracks_clean.csv")

# ── 1. Artist Loyalty Score ────────────────────────────────
top_artist = df["primary_artist"].value_counts().index[0]
top_artist_count = df["primary_artist"].value_counts().iloc[0]
loyalty_score = round((top_artist_count / len(df)) * 100, 1)

print(f"🎤 Artist Loyalty Score: {loyalty_score}% of your top 50 is {top_artist}")

# ── 2. Era Personality ─────────────────────────────────────
era_map = {
    range(1950, 1980): "Classic",
    range(1980, 2000): "Retro",
    range(2000, 2010): "2000s Kid",
    range(2010, 2020): "2010s Era",
    range(2020, 2027): "Current"
}

def get_era(year):
    for r, label in era_map.items():
        if year in r:
            return label
    return "Unknown"

df["era"] = df["release_year"].apply(get_era)
era_counts = df["era"].value_counts()
dominant_era = era_counts.index[0]

print(f"\n📅 Era Breakdown:")
print(era_counts)
print(f"Dominant Era: {dominant_era}")

# ── 3. Song Length Personality ─────────────────────────────
avg_duration = df["duration_mins"].mean()

if avg_duration < 2.5:
    length_personality = "Snappy — you like things short and punchy"
elif avg_duration < 3.5:
    length_personality = "Sweet Spot — classic pop song length"
else:
    length_personality = "Patient — you enjoy longer, deeper tracks"

print(f"\n⏱️ Avg Duration: {round(avg_duration, 2)} mins")
print(f"Length Personality: {length_personality}")

# ── 4. Explicitness Ratio ──────────────────────────────────
explicit_count = df["explicit"].sum()
clean_count = len(df) - explicit_count
explicit_pct = round((explicit_count / len(df)) * 100, 1)

print(f"\n🔞 Explicit: {explicit_count} tracks ({explicit_pct}%)")
print(f"✅ Clean: {clean_count} tracks ({round(100-explicit_pct, 1)}%)")

# ── 5. Album Type Breakdown ────────────────────────────────
album_types = df["album_type"].value_counts()
print(f"\n💿 Album Types:")
print(album_types)

# ── 6. Artist Diversity Score ──────────────────────────────
unique_artists = df["primary_artist"].nunique()
diversity_score = round((unique_artists / len(df)) * 100, 1)

if diversity_score < 30:
    diversity_label = "Devoted — you're deeply loyal to a few artists"
elif diversity_score < 60:
    diversity_label = "Balanced — mix of favourites and exploration"
else:
    diversity_label = "Explorer — you listen widely across many artists"

print(f"\n🌍 Unique Artists: {unique_artists}")
print(f"Diversity Score: {diversity_score}% — {diversity_label}")

# ── Save summary ───────────────────────────────────────────
summary = {
    "top_artist": top_artist,
    "loyalty_score": loyalty_score,
    "dominant_era": dominant_era,
    "avg_duration": round(avg_duration, 2),
    "length_personality": length_personality,
    "explicit_pct": explicit_pct,
    "clean_pct": round(100 - explicit_pct, 1),
    "unique_artists": unique_artists,
    "diversity_score": diversity_score,
    "diversity_label": diversity_label,
}

pd.DataFrame([summary]).to_csv("taste_dna_summary.csv", index=False)
print("\n💾 Saved to taste_dna_summary.csv")