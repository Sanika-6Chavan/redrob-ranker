# main.py
# ⚙️ MAIN ENTRY POINT — Yeh command judges run karenge
#
# Usage:
#   python main.py --candidates data/candidates.jsonl --out outputs/submission/team_xxx.csv
#
# Yeh script:
# 1. Pre-computed FAISS index aur embeddings load karta hai (fast - seconds)
# 2. JD ko embed karta hai
# 3. Ranker chalata hai - top 100 nikalta hai
# 4. Har candidate ke liye reasoning generate karta hai
# 5. Final CSV likhta hai
#
# ⚠️ NOTE: Pehli baar chalane se pehle "python build_embeddings.py" chalao
#    (ek baar, ~50 min) - yeh embeddings + FAISS index banayega.

import sys, os
import argparse
import time
import csv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from src.data_loader import load_all_candidates
from src.embeddings import embed_jd, load_embeddings
from src.faiss_index import load_index
from src.ranker import rank_candidates
from src.reasoning import generate_reasoning


def main():
    parser = argparse.ArgumentParser(description="Redrob AI Candidate Ranker")
    parser.add_argument(
        "--candidates",
        default=config.CANDIDATES_FILE,
        help="Path to candidates.jsonl"
    )
    parser.add_argument(
        "--out",
        default=os.path.join(config.SUBMISSION_DIR, "submission.csv"),
        help="Output CSV path"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("REDROB AI — Candidate Ranking System")
    print("=" * 60)

    start_time = time.time()

    # ── Step 1: Load precomputed FAISS index + embeddings ──────
    print("\n[1/5] Loading FAISS index...")
    faiss_index = load_index()
    if faiss_index is None:
        print("\n❌ FAISS index not found!")
        print("   Run this first: python build_embeddings.py")
        sys.exit(1)

    print("\n[2/5] Loading candidate embeddings metadata...")
    _, candidate_ids = load_embeddings()

    # ── Step 2: Load full candidate data ────────────────────────
    print("\n[3/5] Loading candidate data...")
    candidates = load_all_candidates(use_sample=False)
    # Agar custom path diya hai (different from default), load wahi se
    # (load_all_candidates already config se path leta hai - yeh future-proof hai)

    # ── Step 3: Embed JD ─────────────────────────────────────────
    print("\n[4/5] Embedding job description...")
    jd_vector = embed_jd()

    # ── Step 4: Run ranker ───────────────────────────────────────
    print("\n[5/5] Ranking candidates...")
    top_candidates = rank_candidates(
        jd_vector, faiss_index, candidates, candidate_ids,
        top_k_retrieval=config.TOP_K_RETRIEVAL,
        top_n_final=config.FINAL_TOP_N
    )

    # ── Step 5: Generate reasoning + write CSV ──────────────────
    print("\n📝 Generating reasoning for each candidate...")
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['candidate_id', 'rank', 'score', 'reasoning'])

        for rank, r in enumerate(top_candidates, 1):
            reasoning = generate_reasoning(r)
            writer.writerow([
                r['candidate_id'],
                rank,
                f"{r['final_score']:.4f}",
                reasoning
            ])

    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print(f"✅ DONE! Submission saved to: {args.out}")
    print(f"   Total candidates: {len(top_candidates)}")
    print(f"   Total time: {elapsed:.2f} seconds (limit: 300s)")
    if elapsed < 300:
        print("   ✅ Within 5-minute limit!")
    else:
        print("   ⚠️ EXCEEDED 5-minute limit!")
    print("=" * 60)


if __name__ == "__main__":
    main()