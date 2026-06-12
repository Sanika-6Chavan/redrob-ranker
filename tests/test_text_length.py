# tests/test_text_length.py
# Check karo JD aur candidate texts kitne lambe hain

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.jd_analyzer import get_jd_embedding_text as get_jd_text
from src.data_loader import load_sample_candidates, get_candidate_text
from src.embeddings import get_model

model = get_model()
max_tokens = model.max_seq_length
print(f"Model max tokens: {max_tokens}")

# JD text check karo
jd_text = get_jd_text()
jd_tokens = model.tokenizer.tokenize(jd_text)
print(f"\nJD text length: {len(jd_text)} chars, {len(jd_tokens)} tokens")
if len(jd_tokens) > max_tokens:
    print(f"⚠️  JD TRUNCATED! {len(jd_tokens) - max_tokens} tokens cut off")
print(f"\nJD text:\n{jd_text}")

# Candidate text check karo
candidates = load_sample_candidates()
c = candidates[0]
cand_text = get_candidate_text(c)
cand_tokens = model.tokenizer.tokenize(cand_text)
print(f"\n\nCandidate text length: {len(cand_text)} chars, {len(cand_tokens)} tokens")
if len(cand_tokens) > max_tokens:
    print(f"⚠️  CANDIDATE TRUNCATED! {len(cand_tokens) - max_tokens} tokens cut off")
    # Dikhao kya cut ho raha hai
    cut_text = model.tokenizer.convert_tokens_to_string(cand_tokens[max_tokens:])
    print(f"\nCUT-OFF PORTION (yeh model nahi padh raha):\n{cut_text}")
print(f"\nCandidate text:\n{cand_text}")