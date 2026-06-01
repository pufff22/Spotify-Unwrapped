import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv("tracks_clean.csv")

freshness  = round((df["release_year"] >= 2023).sum() / len(df) * 100, 1)
top_count  = df["primary_artist"].value_counts().iloc[0]
loyalty    = round((top_count / len(df)) * 100, 1)
diversity  = round((df["primary_artist"].nunique() / len(df)) * 100, 1)
avg_dur    = df["duration_mins"].mean()
brevity    = round(max(0, min(100, (5 - avg_dur) / (5 - 1.5) * 100)), 1)
clean      = round((1 - df["explicit"].mean()) * 100, 1)

dimensions = ["Freshness", "Loyalty", "Diversity", "Brevity", "Clean"]
scores     = [freshness, loyalty, diversity, brevity, clean]

# close the polygon
dimensions_closed = dimensions + [dimensions[0]]
scores_closed     = scores + [scores[0]]

score_dict = dict(zip(dimensions, scores))
dominant   = max(score_dict, key=score_dict.get)
labels = {
    "Freshness": "The Trendsetter",
    "Loyalty":   "The Devoted Fan",
    "Diversity": "The Explorer",
    "Brevity":   "The Snappy Listener",
    "Clean":     "The Pure Soul",
}
personality = labels[dominant]

fig = go.Figure()

# background shading rings
for level in [25, 50, 75, 100]:
    fig.add_trace(go.Scatterpolar(
        r=[level] * len(dimensions_closed),
        theta=dimensions_closed,
        mode="lines",
        line=dict(color="#eeeeee", width=1),
        showlegend=False,
        hoverinfo="skip",
    ))

# your DNA polygon
fig.add_trace(go.Scatterpolar(
    r=scores_closed,
    theta=dimensions_closed,
    fill="toself",
    fillcolor="rgba(29,185,84,0.15)",
    line=dict(color="#1DB954", width=2.5),
    mode="lines+markers",
    marker=dict(color="#1DB954", size=8),
    name="Your DNA",
    hovertemplate="<b>%{theta}</b><br>Score: %{r}<extra></extra>",
))

fig.update_layout(
    polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(
            visible=True,
            range=[0, 100],
            tickfont=dict(size=10, color="#888888"),
            gridcolor="#f0f0f0",
            linecolor="#eeeeee",
        ),
        angularaxis=dict(
            tickfont=dict(size=13, color="#1a1a1a", family="Inter"),
            linecolor="#eeeeee",
            gridcolor="#f0f0f0",
        ),
    ),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#1a1a1a"),
    showlegend=False,
    height=500,
    margin=dict(t=60, b=60, l=60, r=60),
    title=dict(
        text=f"<b>{personality}</b><br><sup>Your unique music fingerprint</sup>",
        x=0.5,
        font=dict(size=18, color="#1a1a1a"),
    )
)

fig.show()
print(f"\n✅ Radar chart generated!")
print(f"🎭 Personality: {personality}")