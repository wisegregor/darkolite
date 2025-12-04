# 🏀 DARKO-Lite: An End-to-End NBA Player Impact Model (1996–2024)

**DARKO-Lite** is a fully reproducible NBA analytics system inspired by the real DARKO model.
It builds a modern player impact metric using 29 years of NBA play-by-play–adjacent boxscore data, engineered features, dual-timescale EWMA talent curves, and ridge RAPM.

The result is a season-by-season **DPM-style player rating** available via an interactive **Streamlit dashboard**.

This project demonstrates **complete ownership of a full sports analytics pipeline**:

✔ historical data scraping
✔ merging & cleaning
✔ feature engineering
✔ modeling (EWMA talent, RAPM, blended DPM)
✔ visualization & deployment

---

## 🔥 Highlights

* **29 seasons of NBA data (1996–2024)**
* **Robust anti-rate-limit scraping system** for the NBA Stats API
* **Player + team boxscore merge** (provides contextual team metrics)
* **Feature engineering**: per-36, per-100, TS%, eFG%, possessions, PM/100
* **Dual-timescale EWMA talent curves** for 9 core performance stats
* **Box-only DARKO-Lite talent model** (offense, defense, blended total)
* **Ridge RAPM** with lineup minute shares and team net ratings
* **Final blended DARKO-Lite rating (0.55 box / 0.45 RAPM)**
* **Streamlit web app** for interactive player analysis
* **Fully reproducible pipeline** end-to-end

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
├── data/                         # Intermediate & final CSVs
│   ├── season folders...
│   ├── all_darkoish_features_master.csv
│   ├── darkolite_box_player_season.csv
│   ├── darkolite_rapm_player_season.csv
│   ├── darkolite_player_season_final.csv
│
├── app/
│   ├── streamlit_app.py          # Visualization layer
│
├── README.md
└── requirements.txt
```

---

# 🚀 Pipeline Overview

Below is the full end-to-end architecture diagram:

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
             │   Streamlit App        │
             │   Visualization        │
             └────────────────────────┘
```

---

# 🧠 Modeling Details

## 📌 Box-Score Talent Model (EWMA)

Each stat is smoothed using:

* **FAST EWMA** → captures recent form
* **SLOW EWMA** → long-term talent signal

Blended talent:

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

Produces:

```
darkolite_box_offense
darkolite_box_defense
darkolite_box_total
```

---

## 📌 Ridge RAPM Model

* Construct design matrix:

  ```
  X[game, player] = minutes / team_minutes
  ```
* Compute team net rating per 48 minutes
* Solve ridge regression:

  ```
  β = (XᵀWX + λI)⁻¹ XᵀWy
  ```
* λ = **1500** to stabilize small-sample seasons

Output:

```
rapm_darkolite
```

---

## 📌 Final DARKO-Lite Metric

Blend:

```
DARKO-lite Z = 0.55 * box_z + 0.45 * rapm_z
```

Scale to DPM-style units:

```
darkolite_dpm = 3.5 * DARKO-lite Z
```

---

# 📊 Streamlit App

Located in:

```
app/streamlit_app.py
```

Features:

* Player selection dropdown
* DPM trend visualization
* Season-by-season breakdown table
* Interactive filtering and comparison (optional additions)

---

# 📦 Installation

```
pip install -r requirements.txt
```

Run locally:

```
streamlit run app/streamlit_app.py
```

---

# ☁️ Deployment (Streamlit Cloud)

1. Push repo to GitHub
2. Go to [https://share.streamlit.io](https://share.streamlit.io)
3. Choose this file as entrypoint:

```
app/streamlit_app.py
```

4. Add your CSVs to `data/`

Done.
