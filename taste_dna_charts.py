import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv("tracks_clean.csv")

CHART_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#1a1a1a"),
    margin=dict(t=30, b=20, l=10, r=10),
)

# ── Chart 1: Artist Loyalty ────────────────────────────────
artist_counts = df["primary_artist"].value_counts().reset_index()
artist_counts.columns = ["artist", "count"]
artist_counts = artist_counts.head(8)

fig1 = px.bar(
    artist_counts,
    x="count",
    y="artist",
    orientation="h",
    color="count",
    color_continuous_scale=["#d4edda", "#1DB954"],
    labels={"count": "Tracks", "artist": ""},
    title="Artist Loyalty"
)
fig1.update_layout(
    **CHART_THEME,
    coloraxis_showscale=False,
    yaxis={"categoryorder": "total ascending"},
    height=350,
)
fig1.update_traces(marker_line_width=0)
fig1.show()

# ── Chart 2: Era Breakdown ─────────────────────────────────
era_order = ["Classic", "Retro", "2000s Kid", "2010s Era", "Current"]

def get_era(year):
    if year < 1980: return "Classic"
    elif year < 2000: return "Retro"
    elif year < 2010: return "2000s Kid"
    elif year < 2020: return "2010s Era"
    else: return "Current"

df["era"] = df["release_year"].apply(get_era)
era_counts = df["era"].value_counts().reindex(era_order).fillna(0).reset_index()
era_counts.columns = ["era", "count"]

fig2 = px.bar(
    era_counts,
    x="era",
    y="count",
    color="count",
    color_continuous_scale=["#d4edda", "#1DB954"],
    labels={"count": "Tracks", "era": ""},
    title="Your Music Era"
)
fig2.update_layout(
    **CHART_THEME,
    coloraxis_showscale=False,
    height=350,
)
fig2.update_traces(marker_line_width=0)
fig2.show()

# ── Chart 3: Explicit vs Clean Donut ──────────────────────
explicit_count = int(df["explicit"].sum())
clean_count = len(df) - explicit_count

fig3 = go.Figure(data=[go.Pie(
    labels=["Clean", "Explicit"],
    values=[clean_count, explicit_count],
    hole=0.65,
    marker_colors=["#1DB954", "#d4edda"],
    textinfo="percent+label",
    hoverinfo="label+value",
)])
fig3.update_layout(
    **CHART_THEME,
    title="Clean vs Explicit",
    height=350,
    showlegend=False,
    annotations=[dict(
        text=f"{clean_count}/50<br>Clean",
        x=0.5, y=0.5,
        font_size=16,
        showarrow=False,
        font_color="#1a1a1a"
    )]
)
fig3.show()

# ── Chart 4: Album Type Breakdown ─────────────────────────
album_counts = df["album_type"].value_counts().reset_index()
album_counts.columns = ["type", "count"]

fig4 = go.Figure(data=[go.Pie(
    labels=album_counts["type"],
    values=album_counts["count"],
    hole=0.65,
    marker_colors=["#1DB954", "#d4edda", "#a8dfc3"],
    textinfo="percent+label",
)])
fig4.update_layout(
    **CHART_THEME,
    title="Singles vs Albums",
    height=350,
    showlegend=False,
    annotations=[dict(
        text=f"{len(df)}<br>Tracks",
        x=0.5, y=0.5,
        font_size=16,
        showarrow=False,
        font_color="#1a1a1a"
    )]
)
fig4.show()

# ── Chart 5: Song Duration Distribution ───────────────────
fig5 = px.histogram(
    df,
    x="duration_mins",
    nbins=15,
    color_discrete_sequence=["#1DB954"],
    labels={"duration_mins": "Duration (mins)"},
    title="Song Length Distribution"
)
fig5.update_layout(
    **CHART_THEME,
    height=300,
    bargap=0.05,
)
fig5.update_traces(marker_line_width=0)
fig5.show()

print("✅ All Taste DNA charts generated!")