# src/ranker.py
# Yeh sabse important file hai — sab scoring modules ko combine karta hai
# aur final top 100 candidates nikalta hai

import sys, os
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.faiss_index import search
from src.career_scorer import score_career
from src.experience_scorer import score_experience
from src.behavioral_scorer import score_behavioral
from src.location_scorer import score_location
from src.honeypot_detector import is_honeypot


def rank_candidates(jd_vector, faiss_index, candidates, candidate_ids,
                     top_k_retrieval=None, top_n_final=None):
    """
    Main ranking function — sab kuch combine karta hai.

    Args:
        jd_vector: JD ka embedding (384 numbers)
        faiss_index: loaded FAISS index
        candidates: list of all candidate dicts
        candidate_ids: list of candidate IDs (FAISS order ke according)
        top_k_retrieval: FAISS se kitne candidates nikalein (default 5000)
        top_n_final: final list mein kitne chahiye (default 100)

    Returns:
        list of dicts — har dict mein candidate info + scores, sorted by final_score
    """
    if top_k_retrieval is None:
        top_k_retrieval = config.TOP_K_RETRIEVAL
    if top_n_final is None:
        top_n_final = config.FINAL_TOP_N

    print(f"\n🔍 Step 1: FAISS se top {top_k_retrieval:,} candidates retrieve kar rahe hain...")
    sem_scores, indices = search(faiss_index, jd_vector, k=top_k_retrieval)

    # Semantic scores ko 0-1 range mein normalize karo (min-max)
    min_s, max_s = sem_scores.min(), sem_scores.max()
    range_s = max_s - min_s if max_s > min_s else 1.0
    normalized_semantic = (sem_scores - min_s) / range_s

    print(f"   Semantic similarity range: {min_s:.4f} to {max_s:.4f}")

    # Fast lookup ke liye dictionary banao
    print(f"\n🔍 Step 2: Candidate data lookup table bana rahe hain...")
    candidate_lookup = {c['candidate_id']: c for c in candidates}

    print(f"\n🔍 Step 3: {top_k_retrieval:,} candidates ko score kar rahe hain...")
    results = []
    honeypot_count = 0

    for idx, sem_norm, sem_raw in zip(indices, normalized_semantic, sem_scores):
        cid = candidate_ids[idx]
        c = candidate_lookup.get(cid)
        if c is None:
            continue

        # Honeypot check — agar fake hai toh skip karo
        is_fake, hp_reasons = is_honeypot(c)
        if is_fake:
            honeypot_count += 1
            continue

        # Baaki 4 scores calculate karo
        career = score_career(c)
        experience = score_experience(c)
        behavioral = score_behavioral(c)
        location = score_location(c)

        # Final weighted score
        final_score = (
            sem_norm    * config.WEIGHTS['semantic'] +
            career      * config.WEIGHTS['career'] +
            experience  * config.WEIGHTS['experience'] +
            behavioral  * config.WEIGHTS['behavioral'] +
            location    * config.WEIGHTS['location']
        )

        results.append({
            'candidate_id': cid,
            'candidate': c,
            'semantic_raw': round(float(sem_raw), 4),
            'semantic': round(float(sem_norm), 4),
            'career': career,
            'experience': experience,
            'behavioral': behavioral,
            'location': location,
            'final_score': round(float(final_score), 4),
        })

    print(f"   ✅ Scored {len(results):,} candidates")
    print(f"   🚫 Filtered out {honeypot_count} honeypots")

    # Sort by final score (highest first)
    results.sort(key=lambda x: x['final_score'], reverse=True)

    final_results = results[:top_n_final]
    print(f"\n✅ Final top {len(final_results)} candidates selected")

    return final_results