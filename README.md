# 🎯 Redrob AI — Candidate Ranking System

AI-powered candidate ranking system built for the **Redrob Intelligent Candidate Discovery & Ranking Hackathon**.

> Ranks the best 100 candidates from 1,00,000 profiles for a Senior AI Engineer role — not by keyword matching, but by understanding who actually fits.

---

## 🔗 Links

| | |
|---|---|
| 📁 GitHub | https://github.com/Sanika-6Chavan/redrob-ranker |
| 🌐 Live Demo | https://redrob-ranking-system.streamlit.app |

---

## 🧠 How It Works

Our system uses a **two-stage pipeline**:

**Stage 1 — Semantic Search (Fast)**
- Job Description converted to a 384-dimension vector using `sentence-transformers`
- FAISS index searches 1,00,000 candidates in **13.75 milliseconds**
- Top 5,000 semantically similar candidates shortlisted

**Stage 2 — Multi-Factor Scoring (Accurate)**
- Each of the 5,000 candidates scored on 5 factors
- Honeypot (fake profile) detection applied
- Final **Top 100** selected and ranked

---

## 📊 Scoring Formula
Final Score = Semantic×0.35 + Career×0.25 + Experience×0.20 + Behavioral×0.15 + Location×0.05

| Factor | Weight | What it checks |
|---|---|---|
| Semantic | 35% | AI similarity between JD and candidate profile |
| Career | 25% | Company type, job title, stability, industry |
| Experience | 20% | Years (ideal 5-9), seniority, company size |
| Behavioral | 15% | Last active, response rate, notice period, availability |
| Location | 5% | Pune/Noida preference, willingness to relocate |

---

## 🛡️ Honeypot Detection

Dataset contains ~80 fake profiles. Our detector flags candidates with:
- Impossible experience vs company age
- Expert skills with 0 months usage
- Title-skill mismatches

**Result:** 118 fake profiles filtered from top 5,000 → **0 honeypots in final top 100**

---

## ⚡ Performance

| Metric | Result |
|---|---|
| Total pipeline time | ~12 seconds |
| Time limit | 300 seconds |
| FAISS search time | 13.75 ms |
| Candidates processed | 1,00,000 |
| Final output | 100 ranked candidates |
| Validator result | ✅ Submission is valid |

---

## 🗂️ Project Structure

redrob-ranker/

├── src/

│   ├── data_loader.py         # Load and parse candidate data

│   ├── jd_analyzer.py         # Job description signals

│   ├── embeddings.py          # Sentence Transformer embeddings

│   ├── faiss_index.py         # FAISS vector search

│   ├── career_scorer.py       # Career quality scoring

│   ├── experience_scorer.py   # Experience depth scoring

│   ├── behavioral_scorer.py   # Behavioral signals scoring

│   ├── location_scorer.py     # Location match scoring

│   ├── honeypot_detector.py   # Fake profile detection

│   ├── ranker.py              # Combines all scores → top 100

│   └── reasoning.py           # Generates candidate explanations

├── app/

│   └── streamlit_app.py       # Web demo

├── data/

│   └── job_description.txt    # JD text

├── outputs/

│   └── submission/

│       └── submission.csv     # Final ranked output

├── build_embeddings.py        # One-time precompute script

├── main.py                    # Main entry point

├── config.py                  # All settings

└── requirements.txt

---

## 🚀 Setup & Run

### 1. Clone & Install
```bash
git clone https://github.com/Sanika-6Chavan/redrob-ranker.git
cd redrob-ranker
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 2. Add Data Files
Place these in the `data/` folder (share separately — too large for GitHub):
- `candidates.jsonl` (1,00,000 candidates, ~465MB)

### 3. Precompute Embeddings (One-time, ~50 min)
```bash
python build_embeddings.py
```

### 4. Generate Submission CSV
```bash
python main.py --candidates data/candidates.jsonl --out outputs/submission/submission.csv
```

### 5. Validate
```bash
python validate_submission.py outputs/submission/submission.csv
# Expected: "Submission is valid."
```

### 6. Run Demo
```bash
streamlit run app/streamlit_app.py
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| `sentence-transformers` | Text → vector embeddings |
| `FAISS` | Fast vector similarity search |
| `pandas` / `numpy` | Data processing |
| `streamlit` | Web demo |
| `Python 3.10+` | Core language |

---

## 📁 Submission

| Item | Details |
|---|---|
| CSV | `outputs/submission/submission.csv` — 100 ranked candidates |
| GitHub | https://github.com/Sanika-6Chavan/redrob-ranker |
| Demo | https://redrob-ranking-system.streamlit.app |