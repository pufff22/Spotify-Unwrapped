import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="user-top-read user-read-recently-played user-read-private",
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI")
))

# ── Load your tracks ───────────────────────────────────────
df = pd.read_csv("tracks_clean.csv")
track_ids = df["track_id"].tolist()

# ── Fetch preview URLs ─────────────────────────────────────
print("Fetching preview URLs...")
results = sp.tracks(track_ids)["tracks"]

previews = []
for track in results:
    previews.append({
        "track_name":    track["name"],
        "primary_artist": track["artists"][0]["name"],
        "preview_url":   track["preview_url"]
    })

preview_df = pd.DataFrame(previews)

# ── Count available previews ───────────────────────────────
available = preview_df["preview_url"].notna().sum()
missing = preview_df["preview_url"].isna().sum()

print(f"\n✅ Tracks with preview URL: {available}/50")
print(f"❌ Tracks without preview URL: {missing}/50")

print("\n🔍 Tracks WITHOUT preview:")
print(preview_df[preview_df["preview_url"].isna()][["track_name", "primary_artist"]])

preview_df.to_csv("tracks_with_previews.csv", index=False)
print("\n💾 Saved to tracks_with_previews.csv")