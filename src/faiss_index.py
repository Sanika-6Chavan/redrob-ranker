# src/faiss_index.py
# FAISS index banata hai aur use karta hai fast similarity search ke liye

import faiss
import numpy as np
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def normalize(embeddings):
    """
    Vectors ko 'unit length' bana do (length = 1).
    Yeh isliye kyunki hum cosine similarity use karte hain —
    normalize karne ke baad, dot product = cosine similarity.
    """
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1  # divide by zero se bachao
    return embeddings / norms


def build_index(embeddings):
    """
    Embeddings se FAISS index banao.

    Args:
        embeddings: numpy array of shape (n_candidates, 384)

    Returns:
        FAISS index object
    """
    print(f"\n🔨 Building FAISS index for {embeddings.shape[0]:,} vectors...")

    normalized = normalize(embeddings).astype('float32')

    # IndexFlatIP = "Flat Index, Inner Product"
    # Simple but accurate - exhaustive search, sab vectors compare karta hai
    # 1 lakh ke liye yeh bilkul fine hai (milliseconds mein search hota hai)
    index = faiss.IndexFlatIP(config.EMBEDDING_DIM)
    index.add(normalized)

    print(f"✅ FAISS index built with {index.ntotal:,} vectors")
    return index


def save_index(index):
    """FAISS index ko disk pe save karo"""
    os.makedirs(config.EMBEDDINGS_DIR, exist_ok=True)
    faiss.write_index(index, config.FAISS_INDEX_FILE)
    print(f"💾 Saved FAISS index to: {config.FAISS_INDEX_FILE}")


def load_index():
    """Saved FAISS index ko load karo"""
    if not os.path.exists(config.FAISS_INDEX_FILE):
        print("❌ FAISS index not found. Pehle build_index() chalao.")
        return None
    index = faiss.read_index(config.FAISS_INDEX_FILE)
    print(f"✅ Loaded FAISS index with {index.ntotal:,} vectors")
    return index


def search(index, query_vector, k=None):
    """
    JD vector se sabse similar k candidates dhundo.

    Args:
        index: FAISS index
        query_vector: JD ka embedding (384 numbers)
        k: kitne results chahiye (default = config.TOP_K_RETRIEVAL = 5000)

    Returns:
        scores: similarity scores (1.0 = perfect match, -1.0 = opposite)
        indices: candidate positions in the original list (0 to n-1)
    """
    if k is None:
        k = config.TOP_K_RETRIEVAL

    query_normalized = normalize(query_vector.reshape(1, -1)).astype('float32')
    scores, indices = index.search(query_normalized, k)

    return scores[0], indices[0]