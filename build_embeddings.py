# build_embeddings.py
# ⚠️ YEH SCRIPT EK BAAR CHALANI HAI ⚠️
# 1,00,000 candidates ke embeddings banata hai + FAISS index banata hai
# Time: 5-15 minutes (laptop ki speed pe depend karta hai)
# Result disk pe save hota hai - dobara chalane ki zaroorat nahi

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_all_candidates
from src.embeddings import generate_candidate_embeddings
from src.faiss_index import build_index, save_index
import time

print("=" * 60)
print("PRECOMPUTE — Generating embeddings for ALL candidates")
print("=" * 60)
print("\n⚠️  Yeh 5-15 minutes le sakta hai. Patience rakho!")
print("    Progress bar dikhega, ruk mat jaana.\n")

start_time = time.time()

# Step 1: Saare 1 lakh candidates load karo
candidates = load_all_candidates(use_sample=False)

# Step 2: Embeddings generate karo (yeh sabse slow step hai)
embeddings, candidate_ids = generate_candidate_embeddings(
    candidates,
    batch_size=128,   # bada batch = thoda fast
    save=True         # disk pe save karega automatically
)

# Step 3: FAISS index banao
index = build_index(embeddings)
save_index(index)

elapsed = time.time() - start_time
print("\n" + "=" * 60)
print(f"✅ DONE! Total time: {elapsed/60:.1f} minutes")
print(f"   Embeddings saved: {embeddings.shape}")
print(f"   FAISS index saved with {index.ntotal:,} vectors")
print("=" * 60)