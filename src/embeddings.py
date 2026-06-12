# src/embeddings.py
# Yeh file text ko vectors (numbers) mein convert karti hai
# aur unhe disk pe save karti hai future use ke liye

import numpy as np
import json
import sys, os
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.data_loader import get_candidate_text
from src.jd_analyzer import get_jd_text


# ── Model load karo (ek baar hota hai) ───────────────────────────
_model = None

def get_model():
    """
    Sentence Transformer model load karo.
    Pehli baar internet se download hoga (~80MB), phir local save ho jayega.
    """
    global _model
    if _model is None:
        print(f"📥 Loading embedding model: {config.EMBEDDING_MODEL}")
        print("   (Pehli baar download hoga, thoda time lagega)")
        _model = SentenceTransformer(config.EMBEDDING_MODEL)
        print("✅ Model loaded!")
    return _model


def embed_text(text):
    """
    Ek single text ko vector mein convert karo.
    Returns: numpy array of 384 numbers
    """
    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding


def embed_jd():
    """
    Job description ko ek vector mein convert karo.
    Returns: numpy array of 384 numbers
    """
    from src.jd_analyzer import get_jd_embedding_text
    jd_text = get_jd_embedding_text()   # ⬅️ chota, keyword-dense version use karo
    return embed_text(jd_text)


def generate_candidate_embeddings(candidates, batch_size=64, save=True):
    """
    Saare candidates ko vectors mein convert karo.

    Args:
        candidates: list of candidate dicts
        batch_size: ek baar mein kitne candidates process karo (memory ke liye)
        save: True hai toh disk pe save karega

    Returns:
        embeddings: numpy array of shape (n_candidates, 384)
        candidate_ids: list of candidate IDs (same order as embeddings)
    """
    model = get_model()

    print(f"\n🔄 Generating embeddings for {len(candidates):,} candidates...")
    print(f"   Batch size: {batch_size}")

    # Sab candidates ka text nikal lo pehle
    texts = []
    candidate_ids = []
    for c in candidates:
        texts.append(get_candidate_text(c))
        candidate_ids.append(c['candidate_id'])

    # Batches mein embed karo (memory efficient)
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    print(f"✅ Generated embeddings: shape = {embeddings.shape}")

    if save:
        save_embeddings(embeddings, candidate_ids)

    return embeddings, candidate_ids


def save_embeddings(embeddings, candidate_ids):
    """
    Embeddings aur candidate IDs ko disk pe save karo.
    """
    os.makedirs(config.EMBEDDINGS_DIR, exist_ok=True)

    # Embeddings ko .npy file mein save karo (numpy binary format - fast)
    np.save(config.EMBEDDINGS_FILE, embeddings)
    print(f"💾 Saved embeddings to: {config.EMBEDDINGS_FILE}")

    # Candidate IDs ko JSON mein save karo (order match karne ke liye)
    with open(config.CANDIDATE_IDS_FILE, 'w') as f:
        json.dump(candidate_ids, f)
    print(f"💾 Saved candidate IDs to: {config.CANDIDATE_IDS_FILE}")


def load_embeddings():
    """
    Saved embeddings aur candidate IDs load karo.

    Returns:
        embeddings: numpy array
        candidate_ids: list of IDs
    """
    if not Path(config.EMBEDDINGS_FILE).exists():
        print("❌ Embeddings file not found. Pehle generate_candidate_embeddings() chalao.")
        return None, None

    embeddings = np.load(config.EMBEDDINGS_FILE)

    with open(config.CANDIDATE_IDS_FILE, 'r') as f:
        candidate_ids = json.load(f)

    print(f"✅ Loaded embeddings: shape = {embeddings.shape}")
    print(f"✅ Loaded {len(candidate_ids)} candidate IDs")

    return embeddings, candidate_ids