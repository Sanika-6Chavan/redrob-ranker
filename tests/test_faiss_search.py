# tests/test_faiss_search.py
# Real test - 1 lakh candidates mein se JD ke sabse close kaun hain?

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embeddings import embed_jd, load_embeddings
from src.faiss_index import load_index, search
from src.data_loader import load_all_candidates
import time

print("=" * 70)
print("PHASE 9 TEST — FAISS Search on Full 1,00,000 Candidates")
print("=" * 70)

# Step 1: FAISS index load karo (fast - seconds mein)
print("\n[Step 1] Loading FAISS index...")
index = load_index()

# Step 2: JD ko embed karo
print("\n[Step 2] Embedding JD...")
jd_vector = embed_jd()

# Step 3: Search karo - top 20 nikalo (fast - milliseconds!)
print("\n[Step 3] Searching for similar candidates...")
start = time.time()
scores, indices = search(index, jd_vector, k=20)
elapsed = time.time() - start
print(f"✅ Search completed in {elapsed*1000:.2f} milliseconds!")

# Step 4: Candidate IDs load karo (order match karne ke liye)
_, candidate_ids = load_embeddings()

# Step 5: Full candidate data load karo (titles dekhne ke liye)
print("\n[Step 4] Loading full candidate data for inspection...")
all_candidates = load_all_candidates(use_sample=False)

# Candidate_id se candidate dhundne ke liye dictionary banao (fast lookup)
candidate_lookup = {c['candidate_id']: c for c in all_candidates}

# Step 6: Results dikhao
print("\n" + "=" * 70)
print("TOP 20 CANDIDATES (semantic similarity to JD):")
print("=" * 70)

for rank, (score, idx) in enumerate(zip(scores, indices), 1):
    cid = candidate_ids[idx]
    cand = candidate_lookup.get(cid, {})
    profile = cand.get('profile', {})
    title = profile.get('current_title', 'N/A')
    company = profile.get('current_company', 'N/A')
    years = profile.get('years_of_experience', 0)
    location = profile.get('location', 'N/A')

    print(f"{rank:2d}. {cid} | sim={score:.4f} | {title[:30]:30} | "
          f"{company[:20]:20} | {years}yrs | {location[:20]}")

print("\n" + "=" * 70)
print("TEST COMPLETE!")
print("=" * 70)