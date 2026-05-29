import pandas as pd
import plotly.express as px

df = pd.read_csv("tracks_clean.csv")

artist_counts = df["primary_artist"].value_counts().reset_index()
artist_counts.columns = ["artist", "track_count"]

fig1 = px.bar(
    artist_counts,
    x="track_count",
    y="artist",
    orientation="h",
    title="🎤 Your Top Artists",
    labels={"track_count": "Number of Tracks", "artist": ""},
    color="track_count",
    color_continuous_scale="Viridis",
)

fig1.update_layout(
    plot_bgcolor="black",
    paper_bgcolor="black",
    font_color="white",
    title_font_size=20,
    coloraxis_showscale=False,
    yaxis={"categoryorder": "total ascending"},
)

fig1.show()

# ── Chart 2: Release Year Distribution ────────────────────
year_counts = df["release_year"].value_counts().sort_index().reset_index()
year_counts.columns = ["year", "track_count"]

fig2 = px.bar(
    year_counts,
    x="year",
    y="track_count",
    title="📅 When Was Your Music Made?",
    labels={"track_count": "Number of Tracks", "year": "Release Year"},
    color="track_count",
    color_continuous_scale="Plasma",
)

fig2.update_layout(
    plot_bgcolor="black",
    paper_bgcolor="black",
    font_color="white",
    title_font_size=20,
    coloraxis_showscale=False,
)

fig2.show()

fig3 = px.histogram(
    df,
    x="duration_mins",
    nbins=15,
    title="⏱️ How Long Are Your Favourite Songs?",
    labels={"duration_mins": "Duration (mins)"},
    color_discrete_sequence=["#1DB954"],
    hover_data=["track_name"]
)

fig3.update_layout(
    plot_bgcolor="black",
    paper_bgcolor="black",
    font_color="white",
    title_font_size=20,
)

fig3.show()

print("✅ All 3 charts generated!")