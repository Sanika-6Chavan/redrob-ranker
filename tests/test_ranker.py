# tests/test_ranker.py
# Phase 10 test - poora ranking pipeline test karo

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from src.data_loader import load_all_candidates
from src.embeddings import embed_jd, load_embeddings
from src.faiss_index import load_index
from src.ranker import rank_candidates

print("=" * 70)
print("PHASE 10 TEST — Full Ranking Pipeline")
print("=" * 70)

start_time = time.time()

# Step 1: Load everything
print("\n[1] Loading FAISS index...")
faiss_index = load_index()

print("\n[2] Loading candidate embeddings/IDs...")
_, candidate_ids = load_embeddings()

print("\n[3] Loading all candidate data...")
candidates = load_all_candidates(use_sample=False)

print("\n[4] Embedding JD...")
jd_vector = embed_jd()

# Step 2: Run the ranker
print("\n[5] Running ranker...")
top_candidates = rank_candidates(
    jd_vector, faiss_index, candidates, candidate_ids,
    top_k_retrieval=5000, top_n_final=100
)

elapsed = time.time() - start_time

# Step 3: Show results
print("\n" + "=" * 70)
print(f"TOP 20 OF {len(top_candidates)} FINAL CANDIDATES:")
print("=" * 70)

for i, r in enumerate(top_candidates[:20], 1):
    c = r['candidate']
    profile = c.get('profile', {})
    title = profile.get('current_title', 'N/A')
    company = profile.get('current_company', 'N/A')
    years = profile.get('years_of_experience', 0)
    location = profile.get('location', 'N/A')

    print(f"{i:3d}. {r['candidate_id']} | final={r['final_score']:.3f} | "
          f"sem={r['semantic']:.2f} car={r['career']:.2f} "
          f"exp={r['experience']:.2f} beh={r['behavioral']:.2f} "
          f"loc={r['location']:.2f}")
    print(f"     {title[:35]:35} | {company[:18]:18} | {years}yrs | {location}")

print("\n" + "=" * 70)
print(f"TOTAL TIME: {elapsed:.2f} seconds (limit: 300 seconds)")
print("=" * 70)

if elapsed < 300:
    print("✅ Within 5-minute limit!")
else:
    print("⚠️ EXCEEDED 5-minute limit — needs optimization")