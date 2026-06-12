# tests/test_embeddings.py
# Embeddings generate karke test karo - sirf 50 sample candidates pe

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_sample_candidates
from src.embeddings import embed_jd, generate_candidate_embeddings, get_model
import numpy as np

print("=" * 60)
print("PHASE 8 TEST — Embeddings Generation")
print("=" * 60)

# Step 1: Model load karo
print("\n[Step 1] Loading model...")
model = get_model()
print(f"Model dimension: {model.get_sentence_embedding_dimension()}")

# Step 2: JD ko embed karo
print("\n[Step 2] Embedding Job Description...")
jd_vector = embed_jd()
print(f"JD vector shape: {jd_vector.shape}")
print(f"JD vector sample (first 5 numbers): {jd_vector[:5]}")

# Step 3: Sample candidates load karo
print("\n[Step 3] Loading sample candidates...")
candidates = load_sample_candidates()

# Step 4: Candidates ko embed karo (sample folder mein save karenge, alag se)
print("\n[Step 4] Embedding candidates...")
embeddings, candidate_ids = generate_candidate_embeddings(
    candidates, batch_size=16, save=False  # abhi save nahi karna, sirf test
)

print(f"\nEmbeddings shape: {embeddings.shape}")
print(f"Number of candidate IDs: {len(candidate_ids)}")

# Step 5: Similarity check karo - JD se kaun sa candidate sabse similar hai?
print("\n[Step 5] Finding most similar candidates to JD...")

from numpy.linalg import norm

def cosine_similarity(a, b):
    """Do vectors kitne similar hain - 1.0 = same, 0 = unrelated, -1 = opposite"""
    return np.dot(a, b) / (norm(a) * norm(b))

similarities = []
for i, emb in enumerate(embeddings):
    sim = cosine_similarity(jd_vector, emb)
    similarities.append((candidate_ids[i], sim))

# Sort by similarity (highest first)
similarities.sort(key=lambda x: x[1], reverse=True)

print("\nTOP 5 MOST SIMILAR TO JD (by semantic meaning):")
print("-" * 60)
for cid, sim in similarities[:5]:
    # Candidate ka title bhi dikhao
    cand = next(c for c in candidates if c['candidate_id'] == cid)
    title = cand['profile'].get('current_title', 'N/A')
    print(f"{cid} | similarity={sim:.4f} | {title}")

print("\nBOTTOM 5 LEAST SIMILAR TO JD:")
print("-" * 60)
for cid, sim in similarities[-5:]:
    cand = next(c for c in candidates if c['candidate_id'] == cid)
    title = cand['profile'].get('current_title', 'N/A')
    print(f"{cid} | similarity={sim:.4f} | {title}")

print("\n" + "=" * 60)
print("TEST COMPLETE!")
print("=" * 60)