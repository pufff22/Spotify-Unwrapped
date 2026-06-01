import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

hr {
    border: none;
    border-top: 1px solid #eeeeee;
    margin: 1.5rem 0;
}

h2, h3 {
    font-weight: 600 !important;
    color: #1a1a1a !important;
    letter-spacing: -0.02em;
}

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

# ── Load data ──────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("tracks_clean.csv")

df = load_data()

# ── Chart theme ────────────────────────────────────────────
CHART_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#1a1a1a"),
    margin=dict(t=20, b=20, l=10, r=10),
)

# ── Header ─────────────────────────────────────────────────
st.markdown("""
    <div style='margin-bottom: 0.5rem;'>
        <span style='font-size:13px; font-weight:500; color:#1DB954;
        background:#f0faf3; padding:4px 12px; border-radius:20px;'>
        Your Music Report
        </span>
    </div>
""", unsafe_allow_html=True)

st.markdown("<h1 style='font-size:2.2rem; font-weight:700; letter-spacing:-0.03em; margin-bottom:0.2rem;'>Your Spotify Unwrapped</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#888; font-size:15px; margin-bottom:1.5rem;'>Deeper than Wrapped. Built from your actual listening data.</p>", unsafe_allow_html=True)

st.divider()

# ── Metric Cards ───────────────────────────────────────────
top_artist = df["primary_artist"].value_counts().index[0]
top_artist_count = df["primary_artist"].value_counts().iloc[0]
avg_duration = round(df["duration_mins"].mean(), 2)
newest_year = int(df["release_year"].max())
oldest_year = int(df["release_year"].min())
total_artists = df["primary_artist"].nunique()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Top Artist", top_artist, f"{top_artist_count} of your top 50 tracks")
with col2:
    st.metric("Unique Artists", total_artists, "across 50 tracks")
with col3:
    st.metric("Avg Song Length", f"{avg_duration} mins", "across all tracks")
with col4:
    st.metric("Year Range", f"{oldest_year} – {newest_year}", "of your music taste")

st.divider()

# ── Tabs ───────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Overview", "Taste DNA", "Listening DNA"])

# ── Tab 1: Overview ────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Your Top Artists")
        artist_counts = df["primary_artist"].value_counts().reset_index()
        artist_counts.columns = ["artist", "track_count"]

        fig1 = px.bar(
            artist_counts,
            x="track_count", y="artist",
            orientation="h",
            labels={"track_count": "Tracks", "artist": ""},
            color="track_count",
            color_continuous_scale=["#d4edda", "#1DB954"],
        )
        fig1.update_layout(
            **CHART_THEME,
            coloraxis_showscale=False,
            yaxis={"categoryorder": "total ascending"},
            height=480,
            xaxis=dict(gridcolor="#f0f0f0"),
            yaxis_gridcolor="#f0f0f0",
        )
        fig1.update_traces(marker_line_width=0)
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.markdown("#### When Was Your Music Made?")
        year_counts = df["release_year"].value_counts().sort_index().reset_index()
        year_counts.columns = ["year", "track_count"]

        fig2 = px.bar(
            year_counts,
            x="year", y="track_count",
            labels={"track_count": "Tracks", "year": "Release Year"},
            color="track_count",
            color_continuous_scale=["#d4edda", "#1DB954"],
        )
        fig2.update_layout(
            **CHART_THEME,
            coloraxis_showscale=False,
            height=480,
            xaxis=dict(gridcolor="#f0f0f0", tickmode="linear"),
            yaxis=dict(gridcolor="#f0f0f0"),
        )
        fig2.update_traces(marker_line_width=0)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### How Long Are Your Favourite Songs?")
    fig3 = px.histogram(
        df, x="duration_mins", nbins=15,
        labels={"duration_mins": "Duration (mins)"},
        color_discrete_sequence=["#1DB954"],
    )
    fig3.update_layout(
        **CHART_THEME,
        height=280,
        xaxis=dict(gridcolor="#f0f0f0"),
        yaxis=dict(gridcolor="#f0f0f0"),
        bargap=0.05,
    )
    fig3.update_traces(marker_line_width=0)
    st.plotly_chart(fig3, use_container_width=True)

# ── Tab 2: Taste DNA ───────────────────────────────────────
with tab2:

    def get_era(year):
        if year < 1980: return "Classic"
        elif year < 2000: return "Retro"
        elif year < 2010: return "2000s Kid"
        elif year < 2020: return "2010s Era"
        else: return "Current"

    df["era"] = df["release_year"].apply(get_era)

    unique_artists = df["primary_artist"].nunique()
    diversity_score = round((unique_artists / len(df)) * 100, 1)
    explicit_pct = round((df["explicit"].sum() / len(df)) * 100, 1)
    loyalty_score = round((top_artist_count / len(df)) * 100, 1)

    # ── Personality summary cards ──────────────────────────
    st.markdown("#### Your Music Personality")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Artist Loyalty", f"{loyalty_score}%", f"{top_artist} dominates your taste")
    with c2:
        st.metric("Diversity Score", f"{diversity_score}%", "Balanced listener")
    with c3:
        st.metric("Clean Tracks", f"{round(100 - explicit_pct, 1)}%", "of your top 50")

    st.divider()

    # ── Row 1: Artist loyalty + Era ────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Artist Loyalty")
        artist_counts2 = df["primary_artist"].value_counts().head(8).reset_index()
        artist_counts2.columns = ["artist", "count"]

        fig_a = px.bar(
            artist_counts2,
            x="count", y="artist",
            orientation="h",
            color="count",
            color_continuous_scale=["#d4edda", "#1DB954"],
            labels={"count": "Tracks", "artist": ""},
        )
        fig_a.update_layout(
            **CHART_THEME,
            coloraxis_showscale=False,
            yaxis={"categoryorder": "total ascending"},
            height=350,
        )
        fig_a.update_traces(marker_line_width=0)
        st.plotly_chart(fig_a, use_container_width=True)

    with col_b:
        st.markdown("#### Your Music Era")
        era_order = ["Classic", "Retro", "2000s Kid", "2010s Era", "Current"]
        era_counts = df["era"].value_counts().reindex(era_order).fillna(0).reset_index()
        era_counts.columns = ["era", "count"]

        fig_b = px.bar(
            era_counts,
            x="era", y="count",
            color="count",
            color_continuous_scale=["#d4edda", "#1DB954"],
            labels={"count": "Tracks", "era": ""},
        )
        fig_b.update_layout(
            **CHART_THEME,
            coloraxis_showscale=False,
            height=350,
        )
        fig_b.update_traces(marker_line_width=0)
        st.plotly_chart(fig_b, use_container_width=True)

    # ── Row 2: Donuts + Duration ───────────────────────────
    col_c, col_d, col_e = st.columns(3)

    with col_c:
        st.markdown("#### Clean vs Explicit")
        explicit_count = int(df["explicit"].sum())
        clean_count = len(df) - explicit_count
        fig_c = go.Figure(data=[go.Pie(
            labels=["Clean", "Explicit"],
            values=[clean_count, explicit_count],
            hole=0.65,
            marker_colors=["#1DB954", "#d4edda"],
            textinfo="percent+label",
        )])
        fig_c.update_layout(
            **CHART_THEME,
            height=300,
            showlegend=False,
            annotations=[dict(
                text=f"{clean_count}/50<br>Clean",
                x=0.5, y=0.5,
                font_size=14,
                showarrow=False,
                font_color="#1a1a1a"
            )]
        )
        st.plotly_chart(fig_c, use_container_width=True)

    with col_d:
        st.markdown("#### Singles vs Albums")
        album_counts = df["album_type"].value_counts().reset_index()
        album_counts.columns = ["type", "count"]
        fig_d = go.Figure(data=[go.Pie(
            labels=album_counts["type"],
            values=album_counts["count"],
            hole=0.65,
            marker_colors=["#1DB954", "#d4edda"],
            textinfo="percent+label",
        )])
        fig_d.update_layout(
            **CHART_THEME,
            height=300,
            showlegend=False,
            annotations=[dict(
                text="50<br>Tracks",
                x=0.5, y=0.5,
                font_size=14,
                showarrow=False,
                font_color="#1a1a1a"
            )]
        )
        st.plotly_chart(fig_d, use_container_width=True)

    with col_e:
        st.markdown("#### Song Length")
        fig_e = px.histogram(
            df, x="duration_mins", nbins=15,
            color_discrete_sequence=["#1DB954"],
            labels={"duration_mins": "Duration (mins)"},
        )
        fig_e.update_layout(
            **CHART_THEME,
            height=300,
            bargap=0.05,
        )
        fig_e.update_traces(marker_line_width=0)
        st.plotly_chart(fig_e, use_container_width=True)

# ── Tab 3: Listening DNA ───────────────────────────────────
with tab3:

    # ── Calculate scores ───────────────────────────────────
    freshness  = round((df["release_year"] >= 2023).sum() / len(df) * 100, 1)
    top_count  = df["primary_artist"].value_counts().iloc[0]
    loyalty    = round((top_count / len(df)) * 100, 1)
    diversity  = round((df["primary_artist"].nunique() / len(df)) * 100, 1)
    avg_dur    = df["duration_mins"].mean()
    brevity    = round(max(0, min(100, (5 - avg_dur) / (5 - 1.5) * 100)), 1)
    clean      = round((1 - df["explicit"].mean()) * 100, 1)

    dimensions = ["Freshness", "Loyalty", "Diversity", "Brevity", "Clean"]
    scores     = [freshness, loyalty, diversity, brevity, clean]
    dimensions_closed = dimensions + [dimensions[0]]
    scores_closed     = scores + [scores[0]]

    score_dict  = dict(zip(dimensions, scores))
    dominant    = max(score_dict, key=score_dict.get)
    labels = {
        "Freshness": "The Trendsetter",
        "Loyalty":   "The Devoted Fan",
        "Diversity": "The Explorer",
        "Brevity":   "The Snappy Listener",
        "Clean":     "The Pure Soul",
    }
    personality = labels[dominant]

    # ── Personality header ─────────────────────────────────
    st.markdown(f"#### Your Music Fingerprint")
    
    p1, p2, p3, p4, p5 = st.columns(5)
    with p1:
        st.metric("Freshness", f"{freshness}", "Current music")
    with p2:
        st.metric("Loyalty", f"{loyalty}", "Artist devotion")
    with p3:
        st.metric("Diversity", f"{diversity}", "Artist variety")
    with p4:
        st.metric("Brevity", f"{brevity}", "Song length score")
    with p5:
        st.metric("Clean", f"{clean}", "Explicit-free")

    st.divider()

    # ── Radar chart + personality card ─────────────────────
    col_radar, col_card = st.columns([2, 1])

    with col_radar:
        fig_radar = go.Figure()

        for level in [25, 50, 75, 100]:
            fig_radar.add_trace(go.Scatterpolar(
                r=[level] * len(dimensions_closed),
                theta=dimensions_closed,
                mode="lines",
                line=dict(color="#eeeeee", width=1),
                showlegend=False,
                hoverinfo="skip",
            ))

        fig_radar.add_trace(go.Scatterpolar(
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

        fig_radar.update_layout(
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
            height=480,
            margin=dict(t=40, b=40, l=60, r=60),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_card:
        st.markdown(f"""
            <div style='
                background: #ffffff;
                border: 1px solid #eeeeee;
                border-radius: 20px;
                padding: 2rem 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                text-align: center;
                margin-top: 1rem;
            '>
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