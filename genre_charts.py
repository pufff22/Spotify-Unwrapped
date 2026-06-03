import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv("tracks_with_genres.csv")

CHART_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#1a1a1a"),
    margin=dict(t=30, b=20, l=10, r=10),
)

GREEN_PALETTE = [
    "#1DB954", "#168d3e", "#4cd97b",
    "#a8dfc3", "#d4edda", "#0a5c2a", "#83c9a0"
]

# ── Chart 1: Genre Breakdown Donut ────────────────────────
genre_counts = df["genre_bucket"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig1 = go.Figure(data=[go.Pie(
    labels=genre_counts["genre"],
    values=genre_counts["count"],
    hole=0.6,
    marker_colors=GREEN_PALETTE[:len(genre_counts)],
    textinfo="percent+label",
)])
fig1.update_layout(
    **CHART_THEME,
    title="Your Genre Mix",
    height=400,
    showlegend=False,
    annotations=[dict(
        text=f"{len(df)}<br>Tracks",
        x=0.5, y=0.5,
        font_size=16,
        showarrow=False,
        font_color="#1a1a1a"
    )]
)
fig1.show()

# ── Chart 2: Genre Evolution Stacked Bar ──────────────────
genre_year = pd.crosstab(df["release_year"], df["genre_bucket"]).reset_index()
genre_year_melted = genre_year.melt(
    id_vars="release_year",
    var_name="genre",
    value_name="count"
)

fig2 = px.bar(
    genre_year_melted,
    x="release_year",
    y="count",
    color="genre",
    title="How Your Taste Evolved",
    labels={"count": "Tracks", "release_year": "Year", "genre": "Genre"},
    color_discrete_sequence=GREEN_PALETTE,
)
fig2.update_layout(
    **CHART_THEME,
    height=400,
    xaxis=dict(tickmode="linear", gridcolor="#f0f0f0"),
    yaxis=dict(gridcolor="#f0f0f0"),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    )
)
fig2.update_traces(marker_line_width=0)
fig2.show()

print("✅ Genre charts generated!")