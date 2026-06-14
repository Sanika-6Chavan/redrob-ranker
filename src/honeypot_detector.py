# src/honeypot_detector.py
from datetime import datetime, date
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d").date()
    except:
        return None


def check_experience_vs_company_age(career_history):
    flags = []
    for job in career_history:
        start = parse_date(job.get('start_date'))
        end_str = job.get('end_date')
        end = parse_date(end_str) if end_str else date.today()

        if start and end:
            duration_months = job.get('duration_months', 0)
            calculated_months = (end.year - start.year) * 12 + (end.month - start.month)

            if abs(duration_months - calculated_months) > 12:
                flags.append(
                    f"Duration mismatch: claimed {duration_months}m "
                    f"but dates show {calculated_months}m"
                )
    return flags


def check_skills_sanity(skills):
    flags = []
    expert_zero_months = []

    for skill in skills:
        proficiency = skill.get('proficiency', '')
        duration = skill.get('duration_months', 0)
        if proficiency == 'expert' and duration == 0:
            expert_zero_months.append(skill['name'])

    if len(expert_zero_months) > 3:
        flags.append(
            f"Expert proficiency with 0 months: {', '.join(expert_zero_months[:5])}"
        )

    expert_count = sum(1 for s in skills if s.get('proficiency') == 'expert')
    if expert_count > 8:
        flags.append(f"Too many expert skills: {expert_count}")

    return flags


def check_experience_consistency(profile, career_history):
    flags = []
    claimed_years = profile.get('years_of_experience', 0)
    if not career_history:
        return flags

    total_months = sum(job.get('duration_months', 0) for job in career_history)
    calculated_years = total_months / 12

    if abs(claimed_years - calculated_years) > 5:
        flags.append(
            f"Experience mismatch: claimed {claimed_years:.1f}y "
            f"but history shows {calculated_years:.1f}y"
        )

    return flags


def check_title_skill_mismatch(profile, skills):
    flags = []
    title = profile.get('current_title', '').lower()
    skill_names = [s['name'].lower() for s in skills]
    skill_text = ' '.join(skill_names)

    ml_titles = ['ml', 'machine learning', 'ai ', 'data scientist', 'nlp']
    ml_skills = ['python', 'tensorflow', 'pytorch', 'scikit', 'ml',
                 'machine learning', 'deep learning', 'nlp', 'neural']

    is_ml_title = any(t in title for t in ml_titles)
    has_ml_skills = any(s in skill_text for s in ml_skills)

    if is_ml_title and not has_ml_skills and len(skills) > 5:
        flags.append(f"ML title '{title}' but no ML skills found")

    return flags


def is_honeypot(candidate, threshold=1):
    profile = candidate.get('profile', {})
    career = candidate.get('career_history', [])
    skills = candidate.get('skills', [])

    all_flags = []
    all_flags.extend(check_experience_vs_company_age(career))
    all_flags.extend(check_skills_sanity(skills))
    all_flags.extend(check_experience_consistency(profile, career))
    all_flags.extend(check_title_skill_mismatch(profile, skills))

    return len(all_flags) >= threshold, all_flags


def filter_honeypots(candidates, verbose=False):
    clean = []
    honeypots = []

    for c in candidates:
        flagged, reasons = is_honeypot(c)
        if flagged:
            honeypots.append({'candidate': c, 'reasons': reasons})
            if verbose:
                cid = c.get('candidate_id', '?')
                print(f"🚫 Honeypot detected: {cid}")
                for r in reasons:
                    print(f"   → {r}")
        else:
            clean.append(c)

    print(f"\n🔍 Honeypot Detection Results:")
    print(f"   Total checked : {len(candidates)}")
    print(f"   Clean         : {len(clean)}")
    print(f"   Honeypots     : {len(honeypots)}")

    return clean, honeypots