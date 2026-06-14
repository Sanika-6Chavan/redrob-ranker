# tests/test_honeypot_full.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_all_candidates
from src.honeypot_detector import is_honeypot

candidates = load_all_candidates(use_sample=False)

count = 0
for c in candidates:
    flagged, _ = is_honeypot(c)
    if flagged:
        count += 1

print(f"\nTotal honeypots detected in 100,000: {count}")
print(f"Expected: ~80")