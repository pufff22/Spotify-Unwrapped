import pandas as pd
import requests
import time

# ── Load data ──────────────────────────────────────────────
df = pd.read_csv("tracks_clean.csv")
unique_artists = df["primary_artist"].unique()

print(f"Found {len(unique_artists)} unique artists")
print("Fetching genres from MusicBrainz...\n")

artist_genres = {}

headers = {
    "User-Agent": "SpotifyUnwrapped/1.0.0 (github.com/pufff22/Spotify-Unwrapped)"
}

# ── Query MusicBrainz for each artist ─────────────────────
for name in unique_artists:
    url = f"https://musicbrainz.org/ws/2/artist/?query=artist:{requests.utils.quote(name)}&fmt=json"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        artists = data.get("artists", [])

        if artists:
            top_match = artists[0]
            tags = top_match.get("tags", [])
            sorted_tags = sorted(tags, key=lambda x: x.get("count", 0), reverse=True)
            genres = [t["name"] for t in sorted_tags]
            artist_genres[name] = genres
            print(f"  ✅ {name}: {genres[:3]}")
        else:
            print(f"  ❌ {name}: not found")
            artist_genres[name] = []

        time.sleep(1.1)  # MusicBrainz limit: 1 req/sec

    except Exception as e:
        print(f"  ⚠️ Error for {name}: {e}")
        artist_genres[name] = []

# ── Genre bucket mapping ───────────────────────────────────
genre_map = {
    "K-Pop":     ["k-pop", "korean", "kpop", "k-rock"],
    "Punjabi":   ["punjabi", "bhangra", "desi", "indian pop"],
    "Bollywood": ["bollywood", "filmi", "ghazal", "hindi"],
    "Pop":       ["pop", "dance-pop", "synth-pop", "boy band", "girl group"],
    "Hip-Hop":   ["hip hop", "rap", "trap", "drill", "hip-hop"],
    "Rock":      ["rock", "metal", "grunge", "alternative rock"],
    "R&B":       ["r&b", "soul", "funk", "rhythm and blues"],
    "Indie":     ["indie", "folk", "singer-songwriter", "indie pop"],
}

def classify_genre(artist_name):
    genres = artist_genres.get(artist_name, [])
    genres_lower = [g.lower() for g in genres]
    for bucket, keywords in genre_map.items():
        for keyword in keywords:
            if any(keyword in g for g in genres_lower):
                return bucket
    return "Other"

# ── Apply & save ───────────────────────────────────────────
df["genre_bucket"] = df["primary_artist"].apply(classify_genre)

print(f"\n📊 Genre Breakdown:")
print(df["genre_bucket"].value_counts())

print(f"\n📅 Genre by Year:")
print(pd.crosstab(df["release_year"], df["genre_bucket"]))

df.to_csv("tracks_with_genres.csv", index=False)
print("\n💾 Saved to tracks_with_genres.csv")