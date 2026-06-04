import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import requests
import time
import os

# ── Spotify Auth ───────────────────────────────────────────
def get_spotify_client(token_info):
    return spotipy.Spotify(auth=token_info["access_token"])

def get_auth_manager():
    return SpotifyOAuth(
        client_id=st.secrets["SPOTIPY_CLIENT_ID"],
        client_secret=st.secrets["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=st.secrets["SPOTIPY_REDIRECT_URI"],
        scope="user-top-read user-read-recently-played user-read-private",
        cache_handler=spotipy.cache_handler.MemoryCacheHandler(),
        show_dialog=True
    )

# ── Fetch top tracks ───────────────────────────────────────
def fetch_top_tracks(sp):
    results = sp.current_user_top_tracks(limit=50, time_range="medium_term")
    rows = []
    for track in results["items"]:
        rows.append({
            "track_name":     track["name"],
            "track_id":       track["id"],
            "primary_artist": track["artists"][0]["name"],
            "all_artists":    ", ".join([a["name"] for a in track["artists"]]),
            "album_name":     track["album"]["name"],
            "album_type":     track["album"]["album_type"],
            "release_date":   track["album"]["release_date"],
            "duration_mins":  round(track["duration_ms"] / 60000, 2),
            "explicit":       track["explicit"],
            "album_art_url":  track["album"]["images"][0]["url"],
            "spotify_url":    track["external_urls"]["spotify"],
        })
    df = pd.DataFrame(rows)
    df["release_year"] = pd.to_datetime(df["release_date"]).dt.year
    return df

# ── Fetch genres from MusicBrainz ─────────────────────────
def fetch_genres(df):
    unique_artists = df["primary_artist"].unique()
    artist_genres = {}
    headers = {
        "User-Agent": "SpotifyUnwrapped/1.0.0 (github.com/pufff22/Spotify-Unwrapped)"
    }

    for name in unique_artists:
        url = f"https://musicbrainz.org/ws/2/artist/?query=artist:{requests.utils.quote(name)}&fmt=json"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            artists = data.get("artists", [])
            if artists:
                tags = artists[0].get("tags", [])
                sorted_tags = sorted(tags, key=lambda x: x.get("count", 0), reverse=True)
                artist_genres[name] = [t["name"] for t in sorted_tags]
            else:
                artist_genres[name] = []
            time.sleep(1.1)
        except:
            artist_genres[name] = []

    genre_map = {
        "K-Pop":     ["k-pop", "korean", "kpop", "k pop"],
        "Punjabi":   ["punjabi", "bhangra", "desi"],
        "Bollywood": ["bollywood", "filmi", "hindi", "indian"],
        "Pop":       ["pop", "dance-pop", "synth-pop", "boy band", "girl group"],
        "Hip-Hop":   ["hip hop", "rap", "trap", "drill"],
        "Rock":      ["rock", "metal", "grunge", "alternative rock"],
        "R&B":       ["r&b", "soul", "funk"],
        "Indie":     ["indie", "folk", "singer-songwriter"],
    }

    def classify(artist_name):
        genres = artist_genres.get(artist_name, [])
        genres_lower = [g.lower() for g in genres]
        for bucket, keywords in genre_map.items():
            for keyword in keywords:
                if any(keyword in g for g in genres_lower):
                    return bucket
        return "Other"

    df["genre_bucket"] = df["primary_artist"].apply(classify)
    return df