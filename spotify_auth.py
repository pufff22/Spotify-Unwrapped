import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import json
import os

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="user-top-read user-read-recently-played",
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI")
))

# Fetch your top 50 tracks
top_tracks = sp.current_user_top_tracks(limit=50, time_range="medium_term")

# Print it human-readable
for i, track in enumerate(top_tracks["items"]):
    print(f"{i+1}. {track['name']} — {track['artists'][0]['name']}")

# Save raw JSON for tomorrow
with open("top_tracks_raw.json", "w") as f:
    json.dump(top_tracks, f, indent=2)

print("\n✅ Saved to top_tracks_raw.json")