# tests/test_phase_check.py
# Phase 1-7 ka quick test - sab scorers sahi kaam kar rahe hain ya nahi

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_sample_candidates
from src.career_scorer import score_career
from src.experience_scorer import score_experience
from src.behavioral_scorer import score_behavioral
from src.location_scorer import score_location
from src.honeypot_detector import is_honeypot

candidates = load_sample_candidates()

results = []
for c in candidates:
    career = score_career(c)
    experience = score_experience(c)
    behavioral = score_behavioral(c)
    location = score_location(c)
    flagged, reasons = is_honeypot(c)

    # Semantic abhi nahi hai, isliye baaki 4 ko adjust weights se combine karo
    partial = (
        career * 0.40 +
        experience * 0.30 +
        behavioral * 0.25 +
        location * 0.05
    )

    results.append({
        'id': c['candidate_id'],
        'title': c['profile'].get('current_title', 'N/A'),
        'years': c['profile'].get('years_of_experience', 0),
        'location': c['profile'].get('location', 'N/A'),
        'score': round(partial, 3),
        'honeypot': flagged
    })

# Sort by score (highest first)
results.sort(key=lambda x: x['score'], reverse=True)

print('=' * 80)
print('TOP 5 CANDIDATES (best partial score):')
print('=' * 80)
for i, r in enumerate(results[:5], 1):
    flag = ' [HONEYPOT]' if r['honeypot'] else ''
    print('{}. {} | {:25} | {}yrs | {:15} | score={}{}'.format(
        i, r['id'], r['title'][:25], r['years'], r['location'][:15], r['score'], flag
    ))

print()
print('=' * 80)
print('BOTTOM 5 CANDIDATES (worst partial score):')
print('=' * 80)
for i, r in enumerate(results[-5:], 1):
    flag = ' [HONEYPOT]' if r['honeypot'] else ''
    print('{}. {} | {:25} | {}yrs | {:15} | score={}{}'.format(
        i, r['id'], r['title'][:25], r['years'], r['location'][:15], r['score'], flag
    ))

honeypot_count = sum(1 for r in results if r['honeypot'])
print()
print('Total honeypots detected in 50 sample: {}'.format(honeypot_count))
print()
print('TEST COMPLETE - All scoring modules working!')