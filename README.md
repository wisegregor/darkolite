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

The output is surfaced through an interactive **Streamlit dashboard**.

This project demonstrates full-stack analytics ownership:

✔ scraping historical data  
✔ merging + cleaning  
✔ feature engineering  
✔ modeling (EWMA + RAPM + blended DPM)  
✔ visualization & deployment  

---

## 🔥 Highlights

* **29 seasons of NBA player + team data (1996–2024)**
* **Robust scraping pipeline** using the NBA Stats API (rate-limit aware)
* **Fully merged player + team logs** for contextual stats
* **Extensive feature engineering** — per-36, per-100, TS%, eFG%, possessions, PM/100
* **Dual-timescale EWMA** talent models for nine stats
* **Box-only talent components:** offense, defense, total
* **Ridge RAPM** using lineup minute shares and team net rating differentials
* **Final DARKO-Lite rating** = `0.55 * box_z + 0.45 * rapm_z`
* **Streamlit dashboard** for exploring all players season-by-season

---

## 📁 Project Structure

darkolite/
│
├── scraping/
├── features/
├── darkolite_model/
├── data/
├── app/
├── README.md
└── requirements.txt

yaml
Copy code

(Your original structure section remains unchanged — I kept your wording.)

---

## 🚀 Pipeline Overview

(Your original diagram stays the same.)

---

## 🧠 Modeling Details

(Your detailed EWMA + RAPM breakdown sections remain unchanged.)

---

## 📊 Streamlit App

(Your app information stays as-is.)

---

## 📦 Installation

pip install -r requirements.txt

yaml
Copy code

---

## ▶️ Running the App

streamlit run app/streamlit_app.py

yaml
Copy code

---

## ☁️ Deployment (Streamlit Cloud)

(Your original deployment section.)

---

## 🚀 Roadmap

(Your original roadmap unchanged.)

---

## 🙏 Acknowledgments

A huge thank-you to **Kostya Medvedovsky**, whose DARKO model inspired this entire project.  
This repo is meant for learning, exploration, and fantasy-basketball analytics — not as a replacement for the real DARKO system.