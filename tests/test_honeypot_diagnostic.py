# tests/test_honeypot_diagnostic.py
# Har individual check kitne candidates flag kar raha hai - dekho

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_all_candidates
from src.honeypot_detector import (
    check_experience_vs_company_age,
    check_skills_sanity,
    check_experience_consistency,
    check_title_skill_mismatch,
)

candidates = load_all_candidates(use_sample=False)

# Har check ko alag se count karo
check1_count = 0  # experience vs company age
check2_count = 0  # skills sanity
check3_count = 0  # experience consistency
check4_count = 0  # title skill mismatch

# Flag count distribution (0, 1, 2, 3, 4 flags wale kitne candidates)
flag_distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

for c in candidates:
    profile = c.get('profile', {})
    career = c.get('career_history', [])
    skills = c.get('skills', [])

    f1 = check_experience_vs_company_age(career)
    f2 = check_skills_sanity(skills)
    f3 = check_experience_consistency(profile, career)
    f4 = check_title_skill_mismatch(profile, skills)

    if f1: check1_count += 1
    if f2: check2_count += 1
    if f3: check3_count += 1
    if f4: check4_count += 1

    total_flags = sum([bool(f1), bool(f2), bool(f3), bool(f4)])
    flag_distribution[total_flags] += 1

print("=" * 60)
print("INDIVIDUAL CHECK RESULTS (100,000 candidates):")
print("=" * 60)
print(f"Check 1 (experience vs company age) : {check1_count}")
print(f"Check 2 (skills sanity)             : {check2_count}")
print(f"Check 3 (experience consistency)    : {check3_count}")
print(f"Check 4 (title-skill mismatch)       : {check4_count}")

print("\n" + "=" * 60)
print("FLAG COUNT DISTRIBUTION:")
print("=" * 60)
for flags, count in flag_distribution.items():
    print(f"{flags} flags: {count} candidates")

print(f"\nWith threshold>=1: {sum(v for k,v in flag_distribution.items() if k>=1)}")
print(f"With threshold>=2: {sum(v for k,v in flag_distribution.items() if k>=2)}")
print(f"With threshold>=3: {sum(v for k,v in flag_distribution.items() if k>=3)}")