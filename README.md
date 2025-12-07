# 🏀 DARKO-Lite: An End-to-End NBA Player Impact Model (1996–2024)

**DARKO-Lite** is a fully reproducible NBA analytics system inspired by the real DARKO model.
It builds a modern player impact metric using nearly three decades of NBA data, engineered features, dual-timescale EWMA talent curves, and ridge RAPM.

The result is a season-by-season **DPM-style player rating** surfaced through an interactive **Streamlit dashboard**.

This project demonstrates **complete ownership of a full sports analytics pipeline**:

✔ Historical scraping
✔ Merging & cleaning
✔ Feature engineering
✔ Modeling (EWMA talent, RAPM, blended DPM)
✔ Visualization & deployment

---

## 🔥 Highlights

* **29 seasons of NBA player + team data (1996–2024)**
* **Robust anti-rate-limit scraping system** using NBA Stats API
* **Merged player + team boxscores** for contextual play-by-play-adjacent stats
* **Feature engineering:** per-36, per-100, TS%, eFG%, possessions, PM/100
* **Dual-timescale EWMA talent curves** for 9 core stats
* **Box-only talent components:** offensive, defensive, total
* **Ridge RAPM** using lineup minute-shares and team net ratings
* **Final blended DARKO-Lite rating (0.55 box, 0.45 RAPM)**
* **Streamlit dashboard** for interactive analysis
* **Fully reproducible pipeline end-to-end**

---

# 📁 Project Structure

```
darkolite/
│
├── scraping/                     # Raw NBA data collection
│   ├── scrape_player_boxscores.py
│   ├── scrape_team_boxscores.py
│   ├── merge_team_data_into_player_data.py
│
├── features/                     # Feature engineering
│   ├── feature_eng_all_seasons.py
│   ├── combine_all_seasons.py
│
├── darkolite_model/              # Modeling components
│   ├── darkolite_box_talent.py
│   ├── darkolite_rapm.py
│   ├── darkolite_final.py
│
├── data/                         # Intermediate & final CSVs (ignored in git)
│   ├── season folders...
│   ├── all_darkoish_features_master.csv
│   ├── darkolite_box_player_season.csv
│   ├── darkolite_rapm_player_season.csv
│   ├── darkolite_player_season_final.csv
│
├── app/                          # Streamlit app
│   ├── streamlit_app.py
│
├── README.md
└── requirements.txt
```

---

# 🚀 Pipeline Overview

```
             ┌─────────────────────────┐
             │     NBA API Scraper     │
             │  player + team logs     │
             └─────────────┬───────────┘
                           ▼
              ┌────────────────────────┐
              │ Player-Team Merging    │
              │ merged_player_team.csv │
              └─────────────┬──────────┘
                           ▼
              ┌────────────────────────┐
              │ Feature Engineering     │
              │ per100, TS%, PM100 etc │
              └─────────────┬──────────┘
                           ▼
              ┌────────────────────────┐
              │  Master Feature Set    │
              │ all_features_master    │
              └───────┬──────┬────────┘
             BOX       │      │   RAPM
           ┌───────────┘      └───────────────┐
           ▼                                    ▼
┌─────────────────────┐               ┌──────────────────────┐
│  Fast/Slow EWMA     │               │   Team Net Ratings   │
│  Box Talent Model   │               │   Design Matrix      │
└──────────┬──────────┘               └──────────┬───────────┘
           ▼                                     ▼
┌─────────────────────┐               ┌──────────────────────┐
│ box_off, box_def     │              │   Ridge RAPM          │
└──────────┬──────────┘               └──────────┬───────────┘
           └──────────────┬──────────────────────┘
                          ▼
             ┌────────────────────────┐
             │    DARKO-Lite Blend    │
             │ 0.55 box + 0.45 RAPM   │
             └─────────────┬──────────┘
                           ▼
             ┌────────────────────────┐
             │ darkolite_player_final │
             └─────────────┬──────────┘
                           ▼
             ┌────────────────────────┐
             │    Streamlit App       │
             └────────────────────────┘
```

---

# 🧠 Modeling Details

## 📌 1. Box-Score Talent Model (EWMA)

Dual-timescale EWMAs:

* **Fast EWMA** = recent performance
* **Slow EWMA** = long-term talent

Blend:

```
talent = 0.70 * slow + 0.30 * fast
```

Stats modeled:

```
pts_per100
reb_per100
ast_per100
stl_per100
blk_per100
to_per100
ts_pct_calc
efg_pct_calc
pm_per100
```

Outputs:

```
darkolite_box_offense
darkolite_box_defense
darkolite_box_total
```

---

## 📌 2. Ridge RAPM Model

Design matrix:

```
X[game, player] = minutes / team_minutes
```

Team net rating is regressed using ridge regression:

```
β = (XᵀWX + λI)⁻¹ XᵀWy
```

λ = **1500** for stability.

Output:

```
rapm_darkolite
```

---

## 📌 3. Final DARKO-Lite Metric

Blended Z-score:

```
Z = 0.55 * box_z + 0.45 * rapm_z
```

Scaled to a DPM-like value:

```
darkolite_dpm = 3.5 * Z
```

Final file:

```
darkolite_player_season_final.csv
```

---

# 📊 Streamlit App

Located in:

```
app/streamlit_app.py
```

Features:

* Player dropdown
* DPM rating over time
* Box vs RAPM components
* Season breakdown

---

# 📦 Installation

```
pip install -r requirements.txt
```

---

# ▶️ Running the App

```
streamlit run app/streamlit_app.py
```

Opens at:

```
http://localhost:8501
```

---

# ☁️ Deployment (Streamlit Cloud)

1. Push repo to GitHub
2. Visit: [https://share.streamlit.io](https://share.streamlit.io)
3. Set entrypoint:

```
app/streamlit_app.py
```

4. Deploy

---

# 🚀 Roadmap

* Player similarity search
* Team-level DARKO-Lite
* Aging curves & projections
* Bayesian RAPM shrinkage
* Real-time data refresh
* API endpoint for player queries

---
