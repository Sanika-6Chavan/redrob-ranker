# app/streamlit_app.py
# Redrob AI - Candidate Ranking System - Web Demo
#
# Run locally with: streamlit run app/streamlit_app.py

import sys, os
import json
import pandas as pd
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.embeddings import embed_jd, embed_text, get_model
from src.faiss_index import normalize
from src.career_scorer import score_career
from src.experience_scorer import score_experience
from src.behavioral_scorer import score_behavioral
from src.location_scorer import score_location
from src.honeypot_detector import is_honeypot
from src.reasoning import generate_reasoning
from src.data_loader import get_candidate_text
from src.jd_analyzer import get_jd_text
import numpy as np


st.set_page_config(
    page_title="Redrob AI — Candidate Ranker",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Redrob AI — Candidate Ranking System")
st.caption("AI-powered candidate ranking for the Redrob Hackathon")

# ── Sidebar: About ───────────────────────────────────────────────
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    This demo shows our ranking system on a small sample.

    **Full system** (1,00,000 candidates):
    `python main.py`

    **This demo** (small sample, for verification):
    Upload a JSON file with candidate profiles below.
    """)
    st.markdown("---")
    st.write("**Scoring weights:**")
    for k, v in config.WEIGHTS.items():
        st.write(f"- {k.capitalize()}: {v:.0%}")


# ── Job Description Section ──────────────────────────────────────
st.subheader("📋 Job Description")
with st.expander("View Job Description", expanded=False):
    st.text(get_jd_text())


# ── File Upload ───────────────────────────────────────────────────
st.subheader("📁 Upload Candidates")
st.caption("Upload a JSON file with candidate profiles (e.g. sample_candidates.json). Max ~100 candidates recommended for demo speed.")

uploaded_file = st.file_uploader("Choose a JSON file", type=["json"])

# Option to use the bundled sample file
use_sample = st.checkbox("Or use the bundled sample_candidates.json (50 candidates)")


def load_candidates_for_demo():
    if uploaded_file is not None:
        return json.load(uploaded_file)
    elif use_sample:
        with open(config.SAMPLE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


# ── Run Button ────────────────────────────────────────────────────
if st.button("🚀 Run Ranking", type="primary"):
    candidates = load_candidates_for_demo()

    if candidates is None:
        st.warning("⚠️ Please upload a JSON file or check the sample box.")
    else:
        with st.spinner("Loading AI model and ranking candidates..."):

            # Step 1: Embed JD
            jd_vector = embed_jd()
            jd_norm = normalize(jd_vector.reshape(1, -1))[0]

            # Step 2: Score every candidate (small list, so no FAISS needed)
            results = []
            honeypot_count = 0

            for c in candidates:
                # Honeypot check
                is_fake, _ = is_honeypot(c)
                if is_fake:
                    honeypot_count += 1
                    continue

                # Semantic score
                cand_text = get_candidate_text(c)
                cand_vector = embed_text(cand_text)
                cand_norm = normalize(cand_vector.reshape(1, -1))[0]
                semantic_raw = float(np.dot(jd_norm, cand_norm))

                # Other scores
                career = score_career(c)
                experience = score_experience(c)
                behavioral = score_behavioral(c)
                location = score_location(c)

                results.append({
                    'candidate_id': c['candidate_id'],
                    'candidate': c,
                    'semantic_raw': semantic_raw,
                    'career': career,
                    'experience': experience,
                    'behavioral': behavioral,
                    'location': location,
                })

            # Step 3: Normalize semantic scores (min-max across this batch)
            if results:
                sem_values = [r['semantic_raw'] for r in results]
                min_s, max_s = min(sem_values), max(sem_values)
                range_s = (max_s - min_s) if max_s > min_s else 1.0

                for r in results:
                    sem_norm = (r['semantic_raw'] - min_s) / range_s
                    r['semantic'] = sem_norm
                    r['final_score'] = round(
                        sem_norm * config.WEIGHTS['semantic'] +
                        r['career'] * config.WEIGHTS['career'] +
                        r['experience'] * config.WEIGHTS['experience'] +
                        r['behavioral'] * config.WEIGHTS['behavioral'] +
                        r['location'] * config.WEIGHTS['location'],
                        4
                    )

                # Sort and assign ranks
                results.sort(key=lambda x: (-x['final_score'], x['candidate_id']))
                top_n = min(len(results), config.FINAL_TOP_N)
                results = results[:top_n]

                # Generate reasoning + build table
                table_rows = []
                for rank, r in enumerate(results, 1):
                    reasoning = generate_reasoning(r)
                    table_rows.append({
                        'rank': rank,
                        'candidate_id': r['candidate_id'],
                        'score': r['final_score'],
                        'title': r['candidate']['profile'].get('current_title', 'N/A'),
                        'company': r['candidate']['profile'].get('current_company', 'N/A'),
                        'reasoning': reasoning,
                    })

                df = pd.DataFrame(table_rows)

                # ── Results ──────────────────────────────────────
               
                st.info(
    "ℹ️ **Note:** This demo scores and ranks the uploaded candidates "
    "relative to EACH OTHER. The official submission (`outputs/submission/submission.csv`, "
    "generated via `python main.py`) ranks the full 1,00,000-candidate pool using the "
    "same scoring logic, with semantic similarity computed via FAISS across the full dataset."
              )
               
               
                st.success(f"✅ Ranked {len(candidates)} candidates "
                           f"({honeypot_count} honeypots filtered)")

                st.subheader("📊 Ranked Results")
                st.dataframe(
                    df[['rank', 'candidate_id', 'score', 'title', 'company', 'reasoning']],
                    use_container_width=True,
                    hide_index=True
                )

                # ── Download CSV ─────────────────────────────────
                csv_df = df[['candidate_id', 'rank', 'score', 'reasoning']]
                csv_df = csv_df[['candidate_id', 'rank', 'score', 'reasoning']]
                # Reorder to match submission format
                csv_df = csv_df.rename(columns={})
                csv_output = csv_df.to_csv(index=False)

                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_output,
                    file_name="demo_ranking.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No valid candidates after filtering honeypots.")

else:
    st.info("👆 Upload a candidates JSON file (or check the sample box) and click 'Run Ranking' to see results.")