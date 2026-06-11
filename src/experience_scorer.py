# src/experience_scorer.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def score_years_of_experience(years):
    if years < 1:
        return 0.1
    elif years < 3:
        return 0.3
    elif years < 4:
        return 0.5
    elif years < 5:
        return 0.7
    elif years <= 9:
        return 1.0
    elif years <= 11:
        return 0.85
    else:
        return 0.6


def score_career_trajectory(career_history):
    if not career_history:
        return 0.3

    latest = career_history[0] if career_history else {}
    title = latest.get('title', '').lower()

    seniority_score = 0.5

    if any(t in title for t in ['lead', 'principal', 'staff', 'architect']):
        seniority_score = 1.0
    elif any(t in title for t in ['senior', 'sr.', 'sr ']):
        seniority_score = 0.85
    elif any(t in title for t in ['mid', 'engineer ii', 'engineer 2']):
        seniority_score = 0.65
    elif any(t in title for t in ['junior', 'jr.', 'entry', 'associate']):
        seniority_score = 0.4
    elif any(t in title for t in ['intern', 'trainee']):
        seniority_score = 0.1

    return seniority_score


def score_company_size_experience(career_history):
    if not career_history:
        return 0.3

    scores = []
    size_map = {
        "1-10": 0.9,
        "11-50": 1.0,
        "51-200": 0.95,
        "201-500": 0.85,
        "501-1000": 0.75,
        "1001-5000": 0.65,
        "5001-10000": 0.55,
        "10001+": 0.4
    }

    for job in career_history[:4]:
        size = job.get('company_size', '')
        scores.append(size_map.get(size, 0.5))

    return sum(scores) / len(scores) if scores else 0.3


def score_experience(candidate):
    profile = candidate.get('profile', {})
    career = candidate.get('career_history', [])

    yoe_score = score_years_of_experience(
        profile.get('years_of_experience', 0)
    )
    trajectory_score = score_career_trajectory(career)
    company_size_score = score_company_size_experience(career)

    final = (
        yoe_score * 0.50 +
        trajectory_score * 0.30 +
        company_size_score * 0.20
    )

    return round(final, 4)