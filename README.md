# 🎵 Spotify Unwrapped

> Deeper than Wrapped. A personal analytics report built from your actual Spotify listening data.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)
![Plotly](https://img.shields.io/badge/Plotly-5.x-purple)
![Spotipy](https://img.shields.io/badge/Spotipy-2.26-green)

---

## What is this?

Spotify Wrapped tells you what you listened to. Spotify Unwrapped tells you *who you are* as a listener.

Built in 2 weeks as a data analytics portfolio project — combining Spotify API data, Python data processing, and interactive visualizations into a deployed web app.

---

## Features

**Overview Tab**
- Your top artists ranked by listening frequency
- Music era distribution — when was your music made?
- Song length distribution across your top 50

**Taste DNA Tab**
- Artist loyalty score — how devoted are you to one artist?
- Music era personality — are you a current or classic listener?
- Clean vs explicit ratio
- Singles vs albums breakdown
- Song length personality

**Listening DNA Tab**
- Radar chart across 5 dimensions: Freshness, Loyalty, Diversity, Brevity, Clean
- Auto-generated music personality label (The Pure Soul, The Trendsetter, etc.)
- Your unique music fingerprint — no two users have the same shape

---

## Tech Stack

| Tool | Purpose |
|---|---|
| `Spotipy` | Spotify API authentication + data fetching |
| `Pandas` | Data cleaning, transformation, feature engineering |
| `Plotly` | Interactive charts (bar, histogram, donut, radar) |
| `Streamlit` | Web app framework + deployment |

---

## Project Structure

spotify-unwrapped/
├── app.py                          # Main Streamlit app
├── spotify_auth.py                 # Spotify OAuth + top tracks fetch
├── data_cleaner.py                 # Raw JSON → clean DataFrame
├── taste_dna.py                    # Taste DNA score calculations
├── listening_dna.py                # Listening DNA radar scores
├── radar_chart.py                  # Radar chart prototype
├── tracks_clean.csv                # Cleaned track data
├── taste_dna_summary.csv           # DNA scores summary
├── .streamlit/config.toml          # Streamlit theme config
└── README.md

---

## How to Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/pufff22/Spotify-Unwrapped.git
cd Spotify-Unwrapped
```

**2. Install dependencies**
```bash
pip install spotipy pandas plotly streamlit python-dotenv
```

**3. Set up Spotify credentials**

Create a `.env` file:
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback

Get credentials from [developer.spotify.com](https://developer.spotify.com/dashboard)

**4. Fetch your data**
```bash
python spotify_auth.py
python data_cleaner.py
```

**5. Run the app**
```bash
streamlit run app.py
```

---

## Key Technical Decisions

**Why not Spotify's audio features API?**
Spotify deprecated the Audio Features endpoint for new apps in November 2024. Rather than abandon the mood analysis concept, I pivoted to building custom DNA dimensions calculated directly from track metadata — a more resilient and transparent approach.

**Why Plotly over Matplotlib?**
Plotly gives interactive hover effects, zoom, and beautiful defaults out of the box. For a user-facing analytics app, interactivity is essential.

**Why Streamlit?**
Streamlit lets Python data work become a shareable web app with minimal overhead — perfect for a portfolio project that needs to be deployed and tested by others.

---

## What I Learned

- End-to-end API integration with OAuth authentication
- Real-world data cleaning and feature engineering with Pandas
- Building interactive dashboards with Plotly and Streamlit
- Handling API deprecation gracefully and pivoting to alternative data sources
- Deploying a data app to the web

---

## Live Demo

🔗 *Coming soon — deploying to Streamlit Cloud*

---

## Author

**Arushi** — CS Engineering student at Manipal University Jaipur  
[GitHub](https://github.com/pufff22)