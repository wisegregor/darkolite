# 🏀 DARKO-Lite: An End-to-End NBA Player Impact Model (1996–2024)

## 🌟 Inspiration & Credits

This project is deeply inspired by **Kostya Medvedovsky’s incredible DARKO model**, one of the most respected public impact metrics in basketball analytics.

🔗 **Original DARKO Model:** https://apanalytics.shinyapps.io/DARKO/

I’m an active fantasy basketball player (multiple leagues — dynasty and redraft), and DARKO has consistently helped me understand *true underlying talent* beyond basic box-score stats.  
Curiosity turned into obsession — I wanted to build my own version, partly to learn, partly to experiment, and partly to see whether I could create a system that matched my personal intuition and fantasy decision-making style.

**DARKO-Lite is the result** — a fully reproducible, educational take on player impact modeling, borrowing core ideas from DARKO while implementing my own pipeline, modeling assumptions, and EWMA/RAPM blending strategy.

---

## 📘 Overview

**DARKO-Lite** is a complete NBA analytics system that reconstructs a DARKO-style player impact rating using:

- ~30 years of NBA data  
- engineered box-score + possession-based features  
- dual-timescale EWMA talent curves  
- ridge-regularized RAPM  
- a blended DPM-style final metric  

The output is presented through an interactive **Streamlit dashboard**.

This project demonstrates full-stack analytics ownership:

✔ Historical scraping  
✔ Merging & cleaning  
✔ Feature engineering  
✔ Modeling (EWMA, RAPM, blended DPM)  
✔ Visualization & deployment  

---

## 🔥 Highlights

* **29 seasons of NBA player + team data (1996–2024)**
* **Robust NBA Stats API scraping pipeline**
* **Merged player + team logs** for contextual metrics
* **Extensive feature engineering** — per-36, per-100, TS%, eFG%, possessions, PM/100
* **Dual-timescale EWMA** talent modeling
* **Box-only talent components:** offense, defense, total
* **Ridge RAPM** using lineup shares and net rating regression
* **Final DARKO-Lite score** = `0.55 * box_z + 0.45 * rapm_z`
* **Streamlit dashboard** for interactive exploration

---

## 📁 Project Structure

```
darkolite/
│
├── scraping/ # Raw NBA data collection
│ ├── scrape_player_boxscores.py
│ ├── scrape_team_boxscores.py
│ ├── merge_team_data_into_player_data.py
│
├── features/ # Feature engineering
│ ├── feature_eng_all_seasons.py
│ ├── combine_all_seasons.py
│
├── darkolite_model/ # Modeling components
│ ├── darkolite_box_talent.py
│ ├── darkolite_rapm.py
│ ├── darkolite_final.py
│
├── data/ # Intermediate & final CSVs (ignored in git)
│ ├── season folders...
│ ├── all_darkoish_features_master.csv
│ ├── darkolite_box_player_season.csv
│ ├── darkolite_rapm_player_season.csv
│ ├── darkolite_player_season_final.csv
│
├── app/ # Streamlit app
│ ├── streamlit_app.py
│
├── README.md
└── requirements.txt
```
---

## 🚀 Pipeline Overview

                               ┌─────────────────────────┐
                               │     NBA API Scraper     │
                               │   Player + Team Logs    │
                               └─────────────┬───────────┘
                                             ▼
                               ┌─────────────────────────┐
                               │    Player-Team Merge    │
                               │ merged_player_team.csv  │
                               └─────────────┬───────────┘
                                             ▼
                               ┌─────────────────────────┐
                               │   Feature Engineering   │
                               │ per100, TS%, PM100, etc │
                               └─────────────┬───────────┘
                                             ▼
                               ┌─────────────────────────┐
                               │   Master Feature Set    │
                               │   all_features_master   │
                               └───────┬────────┬────────┘
                                       │        │
                                   BOX │        │ RAPM
                                       ▼        ▼

             ┌─────────────────────────────┐       ┌────────────────────────────┐
             │        Fast / Slow EWMA     │       │       Team Net Ratings     │
             │      Box Talent Modeling    │       │        Design Matrix       │
             └──────────────┬──────────────┘       └──────────────┬─────────────┘
                            ▼                                     ▼
             ┌────────────────────────────┐       ┌────────────────────────────┐
             │   box_off, box_def,        │       │         Ridge RAPM         │
             │   box_total components     │       └──────────────┬─────────────┘
             └──────────────┬─────────────┘                      │
                            └─────────────────┬──────────────────┘
                                              ▼
                               ┌─────────────────────────┐
                               │     DARKO-Lite Blend    │
                               │   0.55 box + 0.45 RAPM  │
                               └─────────────┬───────────┘
                                             ▼
                               ┌─────────────────────────┐
                               │ darkolite_player_final  │
                               └─────────────┬───────────┘
                                             ▼
                               ┌─────────────────────────┐
                               │      Streamlit App      │
                               └─────────────────────────┘


---

## 🧠 Modeling Details

### 📌 1. Box-Score Talent Model (EWMA)

Dual-timescale EWMAs:

* **Fast EWMA** = recent performance  
* **Slow EWMA** = long-term talent  

Blend:

talent = 0.70 * slow + 0.30 * fast


Stats modeled:

pts_per100
reb_per100
ast_per100
stl_per100
blk_per100
to_per100
ts_pct_calc
efg_pct_calc
pm_per100


Outputs:

darkolite_box_offense
darkolite_box_defense
darkolite_box_total


---

### 📌 2. Ridge RAPM Model

Design matrix:

X[game, player] = minutes / team_minutes


Regression:

β = (XᵀWX + λI)⁻¹ XᵀWy


λ = **1500** for stability.

Output:

rapm_darkolite


---

### 📌 3. Final DARKO-Lite Metric

Blended Z-score:

Z = 0.55 * box_z + 0.45 * rapm_z


Scaled DPM-like value:

darkolite_dpm = 3.5 * Z


Final dataset:

darkolite_player_season_final.csv


---

## 📊 Streamlit App

Located in:

app/streamlit_app.py


Features:

* Player dropdown  
* DPM rating over time  
* Box vs RAPM components  
* Season breakdown  

---

## 📦 Installation

pip install -r requirements.txt


---

## ▶️ Running the App

streamlit run app/streamlit_app.py


Open in browser:

http://localhost:8501


---

## ☁️ Deployment (Streamlit Cloud)

1. Push repo to GitHub  
2. Visit https://share.streamlit.io  
3. Set entrypoint:

app/streamlit_app.py


4. Deploy  

---

## 🚀 Roadmap

* Player similarity search  
* Team-level DARKO-Lite  
* Aging curves & projections  
* Bayesian RAPM shrinkage  
* Real-time data refresh  
* API endpoint for player queries  

---
