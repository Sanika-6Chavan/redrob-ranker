# tests/test_final_honeypot_check.py
# FINAL SAFETY CHECK - top 100 mein koi honeypot toh nahi?

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_all_candidates
from src.embeddings import embed_jd, load_embeddings
from src.faiss_index import load_index
from src.ranker import rank_candidates
from src.honeypot_detector import is_honeypot

print("Loading everything...")
faiss_index = load_index()
_, candidate_ids = load_embeddings()
candidates = load_all_candidates(use_sample=False)
jd_vector = embed_jd()

print("\nRunning ranker...")
top_candidates = rank_candidates(
    jd_vector, faiss_index, candidates, candidate_ids,
    top_k_retrieval=5000, top_n_final=100
)

print("\n" + "=" * 60)
print("FINAL SAFETY CHECK — Top 100 Honeypot Scan")
print("=" * 60)

honeypot_in_final = 0
for r in top_candidates:
    flagged, reasons = is_honeypot(r['candidate'])
    if flagged:
        honeypot_in_final += 1
        print(f"⚠️  {r['candidate_id']} flagged: {reasons}")

print(f"\nHoneypots in final top 100: {honeypot_in_final}")
print(f"Disqualification threshold: 10")

if honeypot_in_final == 0:
    print("✅ PERFECTLY SAFE — zero honeypots in final list")
elif honeypot_in_final < 10:
    print("✅ SAFE — under disqualification threshold")
else:
    print("❌ DANGER — disqualification risk!")

# Bonus check - duplicate candidate_ids?
ids = [r['candidate_id'] for r in top_candidates]
duplicates = len(ids) - len(set(ids))
print(f"\nDuplicate candidates in top 100: {duplicates}")

# Bonus check - exactly 100?
print(f"Total candidates in final list: {len(top_candidates)}")