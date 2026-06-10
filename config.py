# config.py
# Yeh file saari settings ek jagah rakhti hai
# Agar kuch change karna ho, sirf yahan aao

import os

# ── Paths ──────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR           = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR        = os.path.join(BASE_DIR, "outputs")
EMBEDDINGS_DIR     = os.path.join(OUTPUTS_DIR, "embeddings")
SUBMISSION_DIR     = os.path.join(OUTPUTS_DIR, "submission")

CANDIDATES_FILE    = os.path.join(DATA_DIR, "candidates.jsonl")
SAMPLE_FILE        = os.path.join(DATA_DIR, "sample_candidates.json")
JD_FILE            = os.path.join(DATA_DIR, "job_description.txt")

EMBEDDINGS_FILE    = os.path.join(EMBEDDINGS_DIR, "candidate_embeddings.npy")
FAISS_INDEX_FILE   = os.path.join(EMBEDDINGS_DIR, "faiss_index.bin")
CANDIDATE_IDS_FILE = os.path.join(EMBEDDINGS_DIR, "candidate_ids.json")

# ── Model Settings ─────────────────────────────────
# all-MiniLM-L6-v2: fast, CPU friendly, good quality
EMBEDDING_MODEL    = "all-MiniLM-L6-v2"
EMBEDDING_DIM      = 384

# ── Ranking Settings ───────────────────────────────
TOP_K_RETRIEVAL    = 5000   # FAISS se pehle itne nikalo
FINAL_TOP_N        = 100    # Final mein itne chahiye

# ── Scoring Weights ────────────────────────────────
# Yeh weights batate hain kaun sa factor kitna important hai
# Sab milake 1.0 (100%) hone chahiye
WEIGHTS = {
    "semantic":   0.35,   # JD se similarity
    "career":     0.25,   # Career quality
    "experience": 0.20,   # Experience depth
    "behavioral": 0.15,   # Platform activity
    "location":   0.05,   # Location match
}

# ── Behavioral Signal Thresholds ───────────────────
# Kitne din se inactive ho toh down-rank karein
INACTIVE_DAYS_THRESHOLD     = 90   # 3 mahine
VERY_INACTIVE_DAYS_THRESHOLD = 180  # 6 mahine

MIN_RESPONSE_RATE           = 0.3   # 30% se kam = bad
GOOD_NOTICE_PERIOD_DAYS     = 30    # 30 din ya kam = good

# ── Location Settings ──────────────────────────────
PREFERRED_LOCATIONS = [
    "pune", "noida", "delhi", "ncr", "gurgaon",
    "hyderabad", "mumbai", "bangalore", "bengaluru"
]
BEST_LOCATIONS = ["pune", "noida"]

# ── Honeypot Detection ─────────────────────────────
MAX_SKILLS_EXPERT_THRESHOLD   = 8   # 8+ expert skills = suspicious
MIN_EXPERIENCE_FOR_SENIOR     = 3   # Senior title but <3 years = suspicious