# src/career_scorer.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.jd_analyzer import get_jd_signals


def is_consulting_company(company_name):
    signals = get_jd_signals()
    company_lower = company_name.lower()
    return any(
        bad in company_lower
        for bad in signals['disqualified_companies']
    )


def score_company_type(career_history):
    if not career_history:
        return 0.3

    consulting_months = 0
    product_months = 0

    for job in career_history:
        company = job.get('company', '')
        duration = job.get('duration_months', 0)

        if is_consulting_company(company):
            consulting_months += duration
        else:
            product_months += duration

    total = consulting_months + product_months
    if total == 0:
        return 0.5

    product_ratio = product_months / total

    if product_ratio >= 0.8:
        return 1.0
    elif product_ratio >= 0.6:
        return 0.8
    elif product_ratio >= 0.4:
        return 0.6
    elif product_ratio >= 0.2:
        return 0.4
    else:
        return 0.2


def score_job_stability(career_history):
    if not career_history or len(career_history) < 2:
        return 0.7

    tenures = [job.get('duration_months', 0) for job in career_history]
    avg_tenure = sum(tenures) / len(tenures)

    if avg_tenure >= 30:
        return 1.0
    elif avg_tenure >= 18:
        return 0.75
    elif avg_tenure >= 12:
        return 0.5
    else:
        return 0.2


def score_industry_relevance(career_history):
    signals = get_jd_signals()
    good_industries = signals['good_industries']

    if not career_history:
        return 0.3

    scores = []
    for job in career_history[:4]:
        industry = job.get('industry', '').lower()
        if any(g in industry for g in good_industries):
            scores.append(1.0)
        else:
            scores.append(0.4)

    return sum(scores) / len(scores) if scores else 0.3


def score_current_title(profile):
    signals = get_jd_signals()
    title = profile.get('current_title', '').lower()

    for bad in signals['bad_titles']:
        if bad in title:
            return 0.0

    for good in signals['good_titles']:
        if good in title:
            return 1.0

    tech_keywords = ['engineer', 'developer', 'scientist', 'analyst',
                     'architect', 'researcher', 'specialist']
    if any(k in title for k in tech_keywords):
        return 0.6

    return 0.3


def score_career(candidate):
    profile = candidate.get('profile', {})
    career = candidate.get('career_history', [])

    title_score      = score_current_title(profile)
    company_score    = score_company_type(career)
    stability_score  = score_job_stability(career)
    industry_score   = score_industry_relevance(career)

    if title_score == 0.0:
        return 0.05

    final = (
        title_score     * 0.35 +
        company_score   * 0.35 +
        stability_score * 0.15 +
        industry_score  * 0.15
    )

    return round(final, 4)