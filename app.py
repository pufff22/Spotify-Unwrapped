import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import time

# spotipy kept for future API mode — not used in current upload flow
try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    spotipy = None
    SpotifyOAuth = None

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="Spotify Unwrapped",
    page_icon="🎵",
    layout="wide"
)

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

[data-testid="stAppViewContainer"] { background-color: #f9f9f7; }
[data-testid="stMain"] { background-color: #f9f9f7; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
    padding: 2.5rem 3rem 2rem 3rem;
    max-width: 1200px;
}
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #eeeeee;
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
[data-testid="stMetricLabel"] {
    font-size: 12px !important;
    font-weight: 500 !important;
    color: #888888 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #1a1a1a !important;
}
[data-testid="stMetricDelta"] {
    font-size: 12px !important;
    color: #1DB954 !important;
}
[data-testid="stMetricDelta"] svg { display: none; }
[data-testid="stTabs"] button {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: #888888;
    border: none;
    padding: 0.5rem 1.2rem;
    border-radius: 8px;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #1DB954 !important;
    background-color: #f0faf3 !important;
    font-weight: 600;
}
hr { border: none; border-top: 1px solid #eeeeee; margin: 1.5rem 0; }
h2, h3 { font-weight: 600 !important; color: #1a1a1a !important; letter-spacing: -0.02em; }
[data-testid="stInfo"] {
    background-color: #f0faf3;
    border: 1px solid #d4edda;
    border-radius: 12px;
    color: #1a1a1a;
}
[data-testid="stPlotlyChart"] {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #eeeeee;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
</style>
""", unsafe_allow_html=True)

# ── Chart theme ────────────────────────────────────────────
CHART_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#1a1a1a"),
    margin=dict(t=20, b=20, l=10, r=10),
)

GREEN_PALETTE = [
    "#1DB954", "#168d3e", "#4cd97b",
    "#a8dfc3", "#d4edda", "#0a5c2a", "#83c9a0"
]

# ── Auth Manager ───────────────────────────────────────────
def get_auth_manager(redirect_uri):
    return SpotifyOAuth(
        client_id=st.secrets["SPOTIPY_CLIENT_ID"],
        client_secret=st.secrets["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=redirect_uri,
        scope="user-top-read user-read-recently-played user-read-private",
        cache_handler=spotipy.cache_handler.MemoryCacheHandler(),
        show_dialog=True
    )

# ── Data fetching ──────────────────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_top_tracks(access_token):
    sp = spotipy.Spotify(auth=access_token)
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
    df["release_year"] = pd.to_datetime(df["release_date"], format="mixed", dayfirst=False).dt.year
    return df

@st.cache_data(show_spinner=False)
def fetch_genres(track_data_hash, primary_artists_tuple):
    unique_artists = list(primary_artists_tuple)
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
            time.sleep(0.5)
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

    return {artist: classify(artist) for artist in unique_artists}

# ── Parse StreamingHistory JSON → DataFrame ────────────────
@st.cache_data(show_spinner=False)
def parse_streaming_history(raw_bytes):
    """
    Accepts Spotify's StreamingHistory*.json (array of objects with
    'artistName', 'trackName', 'msPlayed', 'endTime') and returns a
    DataFrame shaped like tracks_clean.csv so show_dashboard() works
    unchanged.
    """
    import json, hashlib
    data = json.loads(raw_bytes)
    if not isinstance(data, list) or len(data) == 0:
        return None, "File appears empty or in unexpected format."

    df_raw = pd.DataFrame(data)

    # Normalise column names — Spotify has used two naming conventions
    col_map = {}
    for c in df_raw.columns:
        cl = c.lower()
        if "artistname" in cl or "master_metadata_album_artist_name" in cl:
            col_map[c] = "primary_artist"
        elif "trackname" in cl or "master_metadata_track_name" in cl:
            col_map[c] = "track_name"
        elif "msplayed" in cl or "ms_played" in cl:
            col_map[c] = "ms_played"
        elif "endtime" in cl or "ts" == cl:
            col_map[c] = "end_time"
    df_raw = df_raw.rename(columns=col_map)

    needed = {"primary_artist", "track_name", "ms_played"}
    missing = needed - set(df_raw.columns)
    if missing:
        return None, f"Could not find columns: {missing}. Make sure you uploaded StreamingHistory*.json."

    # Drop skipped tracks (< 30 s)
    df_raw = df_raw[df_raw["ms_played"] >= 30_000].copy()
    if df_raw.empty:
        return None, "No tracks with >30 s play time found."

    df_raw["primary_artist"] = df_raw["primary_artist"].fillna("Unknown")
    df_raw["track_name"]     = df_raw["track_name"].fillna("Unknown")

    # Aggregate: sum play time per track+artist, keep top 50
    df_agg = (
        df_raw.groupby(["track_name", "primary_artist"], as_index=False)
              .agg(ms_total=("ms_played", "sum"), play_count=("ms_played", "count"))
              .sort_values("ms_total", ascending=False)
              .head(50)
              .reset_index(drop=True)
    )

    df_agg["duration_mins"] = round(df_agg["ms_total"] / 60_000, 2)

    # Parse year from end_time if available
    if "end_time" in df_raw.columns:
        time_map = df_raw.groupby(["track_name","primary_artist"])["end_time"].max()
        df_agg["end_time"] = df_agg.set_index(["track_name","primary_artist"]).index.map(time_map).values
        df_agg["release_year"] = pd.to_datetime(df_agg["end_time"], errors="coerce").dt.year.fillna(2024).astype(int)
    else:
        df_agg["release_year"] = 2024

    # Stub columns expected by show_dashboard
    df_agg["track_id"]      = df_agg["track_name"].apply(lambda x: hashlib.md5(x.encode()).hexdigest()[:22])
    df_agg["all_artists"]   = df_agg["primary_artist"]
    df_agg["album_name"]    = "Unknown Album"
    df_agg["album_type"]    = "album"
    df_agg["release_date"]  = df_agg["release_year"].astype(str) + "-01-01"
    df_agg["explicit"]      = False
    df_agg["album_art_url"] = ""
    df_agg["spotify_url"]   = ""
    df_agg["duration_bucket"] = df_agg["duration_mins"].apply(
        lambda m: "Short" if m < 2.5 else ("Long" if m > 4 else "Standard"))

    # Genre classification from artist name heuristics (no API needed)
    kpop_artists = {
        "enhypen","twice","illit","seventeen","txt","bts","blackpink","aespa",
        "ive","stray kids","nct dream","nct 127","red velvet","exo","shinee",
        "2pm","got7","monsta x","ateez","the boyz","cravity","treasure",
        "newjeans","le sserafim","itzy","loona","mamamoo","g-idle","gfriend",
        "artms","cnco","tripleS"
    }
    bollywood_artists = {
        "arijit singh","shreya ghoshal","jubin nautiyal","armaan malik",
        "neha kakkar","atif aslam","sonu nigam","kumar sanu","udit narayan",
        "pritam","vishal-shekhar","a.r. rahman","shankar-ehsaan-loy"
    }
    punjabi_artists = {
        "diljit dosanjh","ap dhillon","sidhu moosewala","karan aujla",
        "shubh","babbal rai","amrit maan","jass manak","guru randhawa",
        "b praak","jasmine sandlas","talwiinder","sufr"
    }

    def infer_genre(artist):
        a = artist.lower().strip()
        if a in kpop_artists: return "K-Pop"
        if a in bollywood_artists: return "Bollywood"
        if a in punjabi_artists: return "Punjabi"
        return "Pop"

    df_agg["genre_bucket"] = df_agg["primary_artist"].apply(infer_genre)

    return df_agg, None


# ── Upload landing page ────────────────────────────────────
def show_upload_landing():
    st.markdown("""
        <div style='max-width:560px; margin:5rem auto 0; text-align:center;'>
            <div style='font-size:13px; font-weight:500; color:#1DB954;
            background:#f0faf3; padding:4px 12px; border-radius:20px;
            display:inline-block; margin-bottom:1.5rem;'>
            Your Music Report
            </div>
            <h1 style='font-size:2.8rem; font-weight:700;
            letter-spacing:-0.03em; margin-bottom:0.8rem; line-height:1.1;'>
            Your Spotify<br>Unwrapped
            </h1>
            <p style='color:#888; font-size:15px; margin-bottom:0.5rem;'>
            Deeper than Wrapped. Upload your Spotify data to see your
            personal music analytics — no login required.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Drop your StreamingHistory.json here",
            type=["json"],
            help="From Spotify: Account → Privacy → Download your data → StreamingHistory*.json",
            label_visibility="collapsed"
        )
        st.markdown("""
            <p style='color:#aaa; font-size:12px; text-align:center; margin-top:0.5rem;'>
            How to get your file: <b>Spotify app → Settings → Account → Privacy →
            Download your data</b> → you'll receive an email with a zip.
            Open it and upload any <code>StreamingHistory*.json</code> file.
            </p>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.divider()
        st.markdown("<p style='color:#aaa; font-size:12px; text-align:center;'>or</p>", unsafe_allow_html=True)

        if st.button("👀  View demo with Arushi's data", use_container_width=True):
            st.session_state["use_demo"] = True
            st.rerun()

    return uploaded


# ── Main dashboard ─────────────────────────────────────────
def show_dashboard(df, user_name):

    # ── Upload-another / back to demo banner ──────────────────
    is_demo = st.session_state.get("use_demo", False)
    banner_msg = (
        "👀 You're viewing the demo with Arushi's data. "
        "Upload your own <code>StreamingHistory.json</code> to see your report."
        if is_demo else
        f"✅ Showing your personal Spotify report. "
        "Click <b>Start over</b> to analyse a different file."
    )
    col_b1, col_b2 = st.columns([5, 1])
    with col_b1:
        st.markdown(
            f"<div style='background:#f0faf3; border:1px solid #d4edda; border-radius:10px;"
            f"padding:10px 16px; font-size:13px; color:#1a1a1a;'>{banner_msg}</div>",
            unsafe_allow_html=True
        )
    with col_b2:
        if st.button("↩ Start over", use_container_width=True):
            for k in ["use_demo", "uploaded_df", "uploaded_name"]:
                st.session_state.pop(k, None)
            st.rerun()

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    # Header
    col_hero, col_stats = st.columns([3, 1])
    with col_hero:
        st.markdown("""
            <div style='margin-bottom: 0.5rem;'>
                <span style='font-size:13px; font-weight:500; color:#1DB954;
                background:#f0faf3; padding:4px 12px; border-radius:20px;'>
                Your Music Report
                </span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<h1 style='font-size:2.8rem; font-weight:700; letter-spacing:-0.03em; margin-bottom:0.4rem; line-height:1.1;'>{user_name}'s<br>Spotify Unwrapped</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; font-size:16px; margin-bottom:0; max-width:480px;'>Deeper than Wrapped. Built from your actual listening data.</p>", unsafe_allow_html=True)

    with col_stats:
        st.markdown("""
            <div style='background:#ffffff; border:1px solid #eeeeee;
            border-radius:20px; padding:1.5rem;
            box-shadow:0 2px 8px rgba(0,0,0,0.04);
            text-align:center; margin-top:0.5rem;'>
                <div style='font-size:11px;font-weight:600;color:#1DB954;
                text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem;'>
                Built with
                </div>
                <div style='font-size:14px;color:#1a1a1a;line-height:2;'>
                Spotify API<br>Python + Pandas<br>Plotly + Streamlit
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Metric cards
    top_artist = df["primary_artist"].value_counts().index[0]
    top_artist_count = df["primary_artist"].value_counts().iloc[0]
    avg_duration = round(df["duration_mins"].mean(), 2)
    newest_year = int(df["release_year"].max())
    oldest_year = int(df["release_year"].min())
    total_artists = df["primary_artist"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Top Artist", top_artist, f"{top_artist_count} of your top 50")
    with col2:
        st.metric("Unique Artists", total_artists, "across all 50 tracks")
    with col3:
        st.metric("Avg Song Length", f"{avg_duration} mins", "you like it short")
    with col4:
        st.metric("Year Range", f"{oldest_year} – {newest_year}", "your musical timeline")

    st.divider()

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Taste DNA", "Listening DNA", "Genre Evolution"])

    # ── Tab 1: Overview ────────────────────────────────────
    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### Your Top Artists")
            artist_counts = df["primary_artist"].value_counts().reset_index()
            artist_counts.columns = ["artist", "track_count"]
            fig1 = px.bar(artist_counts, x="track_count", y="artist",
                orientation="h", labels={"track_count": "Tracks", "artist": ""},
                color="track_count", color_continuous_scale=["#d4edda", "#1DB954"])
            fig1.update_layout(**CHART_THEME, coloraxis_showscale=False,
                yaxis={"categoryorder": "total ascending"}, height=480,
                xaxis=dict(gridcolor="#f0f0f0"), yaxis_gridcolor="#f0f0f0")
            fig1.update_traces(marker_line_width=0)
            st.plotly_chart(fig1, use_container_width=True)

        with col_b:
            st.markdown("#### When Was Your Music Made?")
            year_counts = df["release_year"].value_counts().sort_index().reset_index()
            year_counts.columns = ["year", "track_count"]
            fig2 = px.bar(year_counts, x="year", y="track_count",
                labels={"track_count": "Tracks", "year": "Release Year"},
                color="track_count", color_continuous_scale=["#d4edda", "#1DB954"])
            fig2.update_layout(**CHART_THEME, coloraxis_showscale=False, height=480,
                xaxis=dict(gridcolor="#f0f0f0", tickmode="linear"),
                yaxis=dict(gridcolor="#f0f0f0"))
            fig2.update_traces(marker_line_width=0)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("#### How Long Are Your Favourite Songs?")
        fig3 = px.histogram(df, x="duration_mins", nbins=15,
            labels={"duration_mins": "Duration (mins)"},
            color_discrete_sequence=["#1DB954"])
        fig3.update_layout(**CHART_THEME, height=280,
            xaxis=dict(gridcolor="#f0f0f0"), yaxis=dict(gridcolor="#f0f0f0"), bargap=0.05)
        fig3.update_traces(marker_line_width=0)
        st.plotly_chart(fig3, use_container_width=True)

    # ── Tab 2: Taste DNA ───────────────────────────────────
    with tab2:
        def get_era(year):
            if year < 1980: return "Classic"
            elif year < 2000: return "Retro"
            elif year < 2010: return "2000s Kid"
            elif year < 2020: return "2010s Era"
            else: return "Current"

        df["era"] = df["release_year"].apply(get_era)
        diversity_score = round((total_artists / len(df)) * 100, 1)
        explicit_pct = round((df["explicit"].sum() / len(df)) * 100, 1)
        loyalty_score = round((top_artist_count / len(df)) * 100, 1)

        st.markdown("#### Your Music Personality")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Artist Loyalty", f"{loyalty_score}%", f"{top_artist} dominates")
        with c2:
            st.metric("Diversity Score", f"{diversity_score}%", "Balanced listener")
        with c3:
            st.metric("Clean Tracks", f"{round(100-explicit_pct,1)}%", "of your top 50")

        st.divider()

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### Artist Loyalty")
            ac2 = df["primary_artist"].value_counts().head(8).reset_index()
            ac2.columns = ["artist", "count"]
            fig_a = px.bar(ac2, x="count", y="artist", orientation="h",
                color="count", color_continuous_scale=["#d4edda", "#1DB954"],
                labels={"count": "Tracks", "artist": ""})
            fig_a.update_layout(**CHART_THEME, coloraxis_showscale=False,
                yaxis={"categoryorder": "total ascending"}, height=350)
            fig_a.update_traces(marker_line_width=0)
            st.plotly_chart(fig_a, use_container_width=True)

        with col_b:
            st.markdown("#### Your Music Era")
            era_order = ["Classic", "Retro", "2000s Kid", "2010s Era", "Current"]
            era_counts = df["era"].value_counts().reindex(era_order).fillna(0).reset_index()
            era_counts.columns = ["era", "count"]
            fig_b = px.bar(era_counts, x="era", y="count",
                color="count", color_continuous_scale=["#d4edda", "#1DB954"],
                labels={"count": "Tracks", "era": ""})
            fig_b.update_layout(**CHART_THEME, coloraxis_showscale=False, height=350)
            fig_b.update_traces(marker_line_width=0)
            st.plotly_chart(fig_b, use_container_width=True)

        col_c, col_d, col_e = st.columns(3)
        with col_c:
            st.markdown("#### Clean vs Explicit")
            ec = int(df["explicit"].sum())
            cc = len(df) - ec
            fig_c = go.Figure(data=[go.Pie(labels=["Clean","Explicit"],
                values=[cc,ec], hole=0.65,
                marker_colors=["#1DB954","#d4edda"], textinfo="percent+label")])
            fig_c.update_layout(**CHART_THEME, height=300, showlegend=False,
                annotations=[dict(text=f"{cc}/50<br>Clean", x=0.5, y=0.5,
                    font_size=14, showarrow=False, font_color="#1a1a1a")])
            st.plotly_chart(fig_c, use_container_width=True)

        with col_d:
            st.markdown("#### Singles vs Albums")
            alb = df["album_type"].value_counts().reset_index()
            alb.columns = ["type", "count"]
            fig_d = go.Figure(data=[go.Pie(labels=alb["type"], values=alb["count"],
                hole=0.65, marker_colors=["#1DB954","#d4edda"],
                textinfo="percent+label")])
            fig_d.update_layout(**CHART_THEME, height=300, showlegend=False,
                annotations=[dict(text="50<br>Tracks", x=0.5, y=0.5,
                    font_size=14, showarrow=False, font_color="#1a1a1a")])
            st.plotly_chart(fig_d, use_container_width=True)

        with col_e:
            st.markdown("#### Song Length")
            fig_e = px.histogram(df, x="duration_mins", nbins=15,
                color_discrete_sequence=["#1DB954"],
                labels={"duration_mins": "Duration (mins)"})
            fig_e.update_layout(**CHART_THEME, height=300, bargap=0.05)
            fig_e.update_traces(marker_line_width=0)
            st.plotly_chart(fig_e, use_container_width=True)

    # ── Tab 3: Listening DNA ───────────────────────────────
    with tab3:
        freshness = round((df["release_year"] >= 2023).sum() / len(df) * 100, 1)
        loyalty   = round((df["primary_artist"].value_counts().iloc[0] / len(df)) * 100, 1)
        diversity = round((df["primary_artist"].nunique() / len(df)) * 100, 1)
        avg_dur   = df["duration_mins"].mean()
        brevity   = round(max(0, min(100, (5 - avg_dur) / (5 - 1.5) * 100)), 1)
        clean     = round((1 - df["explicit"].mean()) * 100, 1)

        dimensions = ["Freshness","Loyalty","Diversity","Brevity","Clean"]
        scores     = [freshness, loyalty, diversity, brevity, clean]
        dim_closed = dimensions + [dimensions[0]]
        sc_closed  = scores + [scores[0]]

        score_dict  = dict(zip(dimensions, scores))
        dominant    = max(score_dict, key=score_dict.get)
        personality_map = {
            "Freshness": "The Trendsetter",
            "Loyalty":   "The Devoted Fan",
            "Diversity": "The Explorer",
            "Brevity":   "The Snappy Listener",
            "Clean":     "The Pure Soul",
        }
        personality = personality_map[dominant]

        st.markdown("#### Your Music Fingerprint")
        p1,p2,p3,p4,p5 = st.columns(5)
        with p1: st.metric("Freshness", f"{freshness}", "Current music")
        with p2: st.metric("Loyalty", f"{loyalty}", "Artist devotion")
        with p3: st.metric("Diversity", f"{diversity}", "Artist variety")
        with p4: st.metric("Brevity", f"{brevity}", "Song length score")
        with p5: st.metric("Clean", f"{clean}", "Explicit-free")

        st.divider()

        col_radar, col_card = st.columns([2, 1])
        with col_radar:
            fig_radar = go.Figure()
            for level in [25, 50, 75, 100]:
                fig_radar.add_trace(go.Scatterpolar(
                    r=[level]*len(dim_closed), theta=dim_closed,
                    mode="lines", line=dict(color="#eeeeee", width=1),
                    showlegend=False, hoverinfo="skip"))
            fig_radar.add_trace(go.Scatterpolar(
                r=sc_closed, theta=dim_closed, fill="toself",
                fillcolor="rgba(29,185,84,0.15)",
                line=dict(color="#1DB954", width=2.5),
                mode="lines+markers",
                marker=dict(color="#1DB954", size=8),
                hovertemplate="<b>%{theta}</b><br>Score: %{r}<extra></extra>"))
            fig_radar.update_layout(
                polar=dict(bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0,100],
                        tickfont=dict(size=10, color="#888888"),
                        gridcolor="#f0f0f0", linecolor="#eeeeee"),
                    angularaxis=dict(tickfont=dict(size=13, color="#1a1a1a"),
                        linecolor="#eeeeee", gridcolor="#f0f0f0")),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#1a1a1a"),
                showlegend=False, height=480,
                margin=dict(t=40, b=40, l=60, r=60))
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_card:
            st.markdown(f"""
                <div style='background:#ffffff; border:1px solid #eeeeee;
                border-radius:20px; padding:2rem 1.5rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.04);
                text-align:center; margin-top:1rem;'>
                    <div style='font-size:48px; margin-bottom:1rem;'>🎭</div>
                    <div style='font-size:11px; font-weight:600; color:#1DB954;
                    text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;'>
                    Your Music Personality
                    </div>
                    <div style='font-size:26px; font-weight:700; color:#1a1a1a;
                    letter-spacing:-0.02em; margin-bottom:1rem;'>
                    {personality}
                    </div>
                    <div style='font-size:13px; color:#888; line-height:1.6;'>
                    Your highest score is <b style='color:#1a1a1a;'>{dominant}</b> at
                    <b style='color:#1DB954;'>{scores[dimensions.index(dominant)]}</b> —
                    this defines your unique listening fingerprint.
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # ── Tab 4: Genre Evolution ─────────────────────────────
    with tab4:
        if "genre_bucket" not in df.columns:
            st.info("Genre data is loading — please wait a moment and refresh.")
        else:
            top_genre = df["genre_bucket"].value_counts().index[0]
            top_genre_pct = round(
                df["genre_bucket"].value_counts().iloc[0] / len(df) * 100, 1)

            st.markdown("#### Your Genre Identity")
            g1, g2, g3 = st.columns(3)
            with g1:
                st.metric("Dominant Genre", top_genre, f"{top_genre_pct}% of your top 50")
            with g2:
                st.metric("Total Genres", df["genre_bucket"].nunique(), "across your library")
            with g3:
                dom_year = df[df["genre_bucket"]==top_genre]["release_year"].max()
                st.metric("Most Recent", str(int(dom_year)), f"latest {top_genre} track year")

            st.divider()
            col_a, col_b = st.columns([1, 2])

            with col_a:
                st.markdown("#### Your Genre Mix")
                gc = df["genre_bucket"].value_counts().reset_index()
                gc.columns = ["genre", "count"]
                fig_g1 = go.Figure(data=[go.Pie(
                    labels=gc["genre"], values=gc["count"], hole=0.6,
                    marker_colors=GREEN_PALETTE[:len(gc)],
                    textinfo="percent", textposition="inside")])
                fig_g1.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#1a1a1a"),
                    height=420, showlegend=True,
                    legend=dict(orientation="v", yanchor="middle", y=0.5,
                        xanchor="left", x=1.05, font=dict(size=12)),
                    margin=dict(t=20, b=20, l=20, r=120),
                    annotations=[dict(text="50<br>Tracks", x=0.5, y=0.5,
                        font_size=14, showarrow=False, font_color="#1a1a1a")])
                st.plotly_chart(fig_g1, use_container_width=True)

            with col_b:
                st.markdown("#### How Your Taste Evolved")
                gy = pd.crosstab(df["release_year"], df["genre_bucket"]).reset_index()
                gy_melted = gy.melt(id_vars="release_year",
                    var_name="genre", value_name="count")
                fig_g2 = px.bar(gy_melted, x="release_year", y="count", color="genre",
                    labels={"count":"Tracks","release_year":"Year","genre":"Genre"},
                    color_discrete_sequence=GREEN_PALETTE)
                fig_g2.update_layout(**CHART_THEME, height=380,
                    xaxis=dict(tickmode="linear", gridcolor="#f0f0f0"),
                    yaxis=dict(gridcolor="#f0f0f0"),
                    legend=dict(orientation="h", yanchor="bottom",
                        y=1.02, xanchor="left", x=0))
                fig_g2.update_traces(marker_line_width=0)
                st.plotly_chart(fig_g2, use_container_width=True)

# ── App flow ───────────────────────────────────────────────
def main():
    # ── Priority 1: already have uploaded data in session ──
    if "uploaded_df" in st.session_state:
        show_dashboard(
            st.session_state["uploaded_df"],
            st.session_state.get("uploaded_name", "Your")
        )
        return

    # ── Priority 2: demo mode chosen ──────────────────────
    if st.session_state.get("use_demo"):
        df = pd.read_csv("tracks_clean.csv")
        if "genre_bucket" not in df.columns:
            df["genre_bucket"] = df["primary_artist"].apply(
                lambda a: "K-Pop" if a.upper() in {
                    "ENHYPEN","TWICE","ILLIT","SEVENTEEN","BTS","BLACKPINK",
                    "AESPA","IVE","ARTMS","CNCO"
                } else (
                    "Punjabi" if a in {
                        "Karan Aujla","Guru Randhawa","Jasmine Sandlas","Talwiinder","sufr"
                    } else (
                        "Bollywood" if a in {"Pritam","Kushagra","Runa Laila"}
                        else "Pop"
                    )
                )
            )
        show_dashboard(df, "Arushi")
        return

    # ── Priority 3: show upload landing ───────────────────
    uploaded = show_upload_landing()

    if uploaded is not None:
        with st.spinner("Analysing your listening history..."):
            df, err = parse_streaming_history(uploaded.read())
        if err:
            st.error(f"Could not parse file: {err}")
            return
        # Extract first name from filename e.g. "StreamingHistory_music_0.json"
        raw_name = uploaded.name.replace("StreamingHistory","").replace(".json","").strip("_- ")
        user_name = raw_name if raw_name and not raw_name[0].isdigit() else "Your"

        # Ask for name
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            entered = st.text_input("What's your first name?", placeholder="e.g. Priya")
            if st.button("Generate my report →", use_container_width=True):
                st.session_state["uploaded_df"]   = df
                st.session_state["uploaded_name"] = entered.strip() or "Your"
                st.rerun()

main()
