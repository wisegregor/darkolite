<<<<<<< HEAD
Absolutely — here is the **full, polished, production-ready `README.md`** you can copy/paste directly into GitHub.

It is recruiter-optimized, clean, structured, and contains everything a hiring manager wants to see: pipeline, modeling methodology, diagrams, installation, and app instructions.

---

# 📘 **README.md (Final Version)**

```markdown
# 🏀 DARKO-Lite: An End-to-End NBA Player Impact Model (1996–2024)

**DARKO-Lite** is a fully reproducible NBA analytics system inspired by the DARKO model.  
It builds a modern player impact metric using nearly three decades of NBA data, engineered features, dual-timescale EWMA talent curves, and ridge RAPM.  
The final output powers a Streamlit dashboard for exploring player impact across seasons.

This project demonstrates end-to-end ownership of a complete analytics pipeline:  
data ingestion → feature engineering → modeling → deployment → visualization.

---

## 🔥 Key Features

- **29 seasons of NBA data (1996–2024)** automatically scraped
- **Robust anti-rate-limit scraping** (retry logic + randomized backoff)
- **Player + team boxscore merging** (provides full game context)
- **Feature engineering:** per-100, TS%, eFG%, possessions, PM/100, etc.
- **Dual-timescale fast/slow EWMA talent curves** for 9 core stats
- **Box-score DARKO-Lite talent model:** offense, defense, total
- **Ridge RAPM** with minute-share lineup matrices and team net ratings
- **Season-level blended DPM metric** (0.55 box, 0.45 RAPM)
- **Interactive Streamlit web app**
- **Fully reproducible scripts** for every pipeline stage
=======
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
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848

---

# 📁 Project Structure

```
<<<<<<< HEAD

darkolite/
│
├── scraping/
=======
darkolite/
│
├── scraping/                     # Raw NBA data collection
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
│   ├── scrape_player_boxscores.py
│   ├── scrape_team_boxscores.py
│   ├── merge_team_data_into_player_data.py
│
<<<<<<< HEAD
├── features/
│   ├── feature_eng_all_seasons.py
│   ├── combine_all_seasons.py
│
├── darkolite_model/
=======
├── features/                     # Feature engineering
│   ├── feature_eng_all_seasons.py
│   ├── combine_all_seasons.py
│
├── darkolite_model/              # Modeling components
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
│   ├── darkolite_box_talent.py
│   ├── darkolite_rapm.py
│   ├── darkolite_final.py
│
<<<<<<< HEAD
├── data/
│   ├── (season folders)
=======
├── data/                         # Intermediate & final CSVs
│   ├── season folders...
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
│   ├── all_darkoish_features_master.csv
│   ├── darkolite_box_player_season.csv
│   ├── darkolite_rapm_player_season.csv
│   ├── darkolite_player_season_final.csv
│
├── app/
<<<<<<< HEAD
│   ├── streamlit_app.py
│
└── requirements.txt

=======
│   ├── streamlit_app.py          # Visualization layer
│
├── README.md
└── requirements.txt
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
```

---

<<<<<<< HEAD
# 🧱 Architectural Overview

```

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
```

=======
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
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
┌─────────────────────┐               ┌──────────────────────┐
│  Fast/Slow EWMA     │               │   Team Net Ratings   │
│  Box Talent Model   │               │   Design Matrix      │
└──────────┬──────────┘               └──────────┬───────────┘
<<<<<<< HEAD
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

=======
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
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
```

---

<<<<<<< HEAD
# 🧠 Modeling Breakdown

## 1. Box-Score Talent Model (Dual-Timescale EWMA)

Each stat is smoothed using both fast and slow EWMAs:

- **Fast EWMA** → captures hot streaks, recent performance  
- **Slow EWMA** → captures underlying talent level  

Blended talent estimate:

```

talent = 0.70 * slow + 0.30 * fast

=======
# 🧠 Modeling Details

## 📌 Box-Score Talent Model (EWMA)

Each stat is smoothed using:

* **FAST EWMA** → captures recent form
* **SLOW EWMA** → long-term talent signal

Blended talent:

```
talent = 0.70 * slow + 0.30 * fast
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
```

Stats modeled:

<<<<<<< HEAD
- pts_per100  
- ast_per100  
- reb_per100  
- stl_per100  
- blk_per100  
- to_per100  
- ts_pct_calc  
- efg_pct_calc  
- pm_per100  

### Box Components

**Offense**
```

0.40 * pts100
+0.25 * ast100
+12  * ts_talent
+8   * efg_talent
-0.25 * to100

```

**Defense**
```

0.12 * reb100
+0.30 * blk100
+0.25 * stl100
-0.05 * to100

=======
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
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
```

Produces:

```
<<<<<<< HEAD

darkolite_box_offense
darkolite_box_defense
darkolite_box_total

=======
darkolite_box_offense
darkolite_box_defense
darkolite_box_total
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
```

---

<<<<<<< HEAD
## 2. Ridge RAPM

Constructs a minute-share design matrix:

```

X[game, player] = minutes / team_minutes

```

Compute team net rating per 48 minutes, then solve:

```

β = (XᵀWX + λI)⁻¹ XᵀWy

```

with **λ = 1500** for stability.
=======
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
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848

Output:

```
<<<<<<< HEAD

rapm_darkolite

=======
rapm_darkolite
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
```

---

<<<<<<< HEAD
## 3. Final DARKO-Lite DPM Blend

Blend the two signals:

```

Z = 0.55 * box_z  + 0.45 * rapm_z

=======
## 📌 Final DARKO-Lite Metric

Blend:

```
DARKO-lite Z = 0.55 * box_z + 0.45 * rapm_z
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
```

Scale to DPM-style units:

```
<<<<<<< HEAD

darkolite_dpm = 3.5 * Z

```

Clipped to range [-10, +10].

Final output file:

```

darkolite_player_season_final.csv

=======
darkolite_dpm = 3.5 * DARKO-lite Z
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
```

---

# 📊 Streamlit App

<<<<<<< HEAD
The dashboard lives in:

```

app/streamlit_app.py

=======
Located in:

```
app/streamlit_app.py
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
```

Features:

<<<<<<< HEAD
- Player dropdown  
- DARKO-Lite rating over time  
- Box vs RAPM component comparison  
- Season-by-season breakdown table  
=======
* Player selection dropdown
* DPM trend visualization
* Season-by-season breakdown table
* Interactive filtering and comparison (optional additions)
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848

---

# 📦 Installation

```
<<<<<<< HEAD

pip install -r requirements.txt

```

---

# ▶️ Running the Streamlit App

```

streamlit run app/streamlit_app.py

```

Then open:

```

[http://localhost:8501](http://localhost:8501)

=======
pip install -r requirements.txt
```

Run locally:

```
streamlit run app/streamlit_app.py
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
```

---

# ☁️ Deployment (Streamlit Cloud)

<<<<<<< HEAD
1. Push repo to GitHub  
2. Go to https://share.streamlit.io  
3. Select repo  
4. Choose entry file:  
```

app/streamlit_app.py

```
5. Deploy

You’re live.

---

# 🚀 Roadmap / Future Enhancements

- Player similarity search engine  
- Team-level DARKO-Lite  
- Aging curves & projections  
- Bayesian shrinkage for RAPM  
- Real-time data refresh via NBA API  
- REST API endpoint for querying ratings  
=======
1. Push repo to GitHub
2. Go to [https://share.streamlit.io](https://share.streamlit.io)
3. Choose this file as entrypoint:

```
app/streamlit_app.py
```

4. Add your CSVs to `data/`

Done.
>>>>>>> 65c118b81b5dc7fd79c1b9d9e25c36fa8f283848
