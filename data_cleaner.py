import json
import pandas as pd

# ── Load raw JSON ──────────────────────────────────────────
with open("top_tracks_raw.json", "r") as f:
    data = json.load(f)

tracks = data["items"]

# ── Extract fields ─────────────────────────────────────────
rows = []
for track in tracks:
    rows.append({
        "track_name":      track["name"],
        "track_id":        track["id"],
        "primary_artist":  track["artists"][0]["name"],
        "all_artists":     ", ".join([a["name"] for a in track["artists"]]),
        "album_name":      track["album"]["name"],
        "album_type":      track["album"]["album_type"],
        "release_date":    track["album"]["release_date"],
        "duration_mins":   round(track["duration_ms"] / 60000, 2),
        "explicit":        track["explicit"],
        "album_art_url":   track["album"]["images"][0]["url"],
        "spotify_url":     track["external_urls"]["spotify"],
    })

df = pd.DataFrame(rows)

# ── Derived columns ────────────────────────────────────────
df["release_year"] = pd.to_datetime(df["release_date"]).dt.year
df["duration_bucket"] = pd.cut(
    df["duration_mins"],
    bins=[0, 2.5, 3.5, 4.5, 100],
    labels=["Short", "Standard", "Long", "Epic"]
)

# ── Sanity check ───────────────────────────────────────────
print(f"✅ Total tracks: {len(df)}")
print(f"\n🎵 Sample:")
print(df[["track_name", "primary_artist", "duration_mins", "duration_bucket", "release_year"]].head(10))
print(f"\n🎤 Top artists:")
print(df["primary_artist"].value_counts().head(10))
print(f"\n📅 Release years:")
print(df["release_year"].value_counts().sort_index())

# ── Save ───────────────────────────────────────────────────
df.to_csv("tracks_clean.csv", index=False)
print("\n💾 Saved to tracks_clean.csv")