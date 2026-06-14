# src/reasoning.py
# Har candidate ke liye 1-2 line ka human-readable reasoning banata hai
# Yeh template-based hai - candidate ke ACTUAL data se banta hai, hallucinated nahi

import sys, os
from datetime import datetime, date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def days_since(date_str):
    """Kitne din pehle tha yeh date?"""
    if not date_str:
        return None
    try:
        d = datetime.strptime(str(date_str), "%Y-%m-%d").date()
        return (date.today() - d).days
    except:
        return None


def get_top_skills(candidate, n=3):
    """Candidate ke top n skills nikalo (advanced/expert priority)"""
    skills = candidate.get('skills', [])

    # Pehle expert, phir advanced
    expert = [s['name'] for s in skills if s.get('proficiency') == 'expert']
    advanced = [s['name'] for s in skills if s.get('proficiency') == 'advanced']

    top = expert + advanced
    if len(top) >= n:
        return top[:n]

    # Agar kam hain, baaki skills se fill karo
    others = [s['name'] for s in skills if s['name'] not in top]
    return (top + others)[:n]


def get_company_type_note(candidate):
    """Career history se ek-line note - product company ya consulting"""
    career = candidate.get('career_history', [])
    if not career:
        return ""

    from src.career_scorer import is_consulting_company

    current = career[0] if career else {}
    company = current.get('company', '')

    if is_consulting_company(company):
        return f"currently at {company} (consulting background)"
    return f"at {company}"


def generate_reasoning(scored_candidate):
    """
    Ek candidate ke liye reasoning string banata hai.

    Args:
        scored_candidate: dict from ranker.py with 'candidate' and scores

    Returns:
        str: 1-2 sentence reasoning
    """
    c = scored_candidate['candidate']
    profile = c.get('profile', {})
    signals = c.get('redrob_signals', {})

    title = profile.get('current_title', 'Professional')
    years = profile.get('years_of_experience', 0)
    location = profile.get('location', 'location unknown')
    location = ", ".join(part.strip().title() for part in location.split(","))

    top_skills = get_top_skills(c, n=3)
    skills_text = ", ".join(top_skills) if top_skills else "general skills"

    company_note = get_company_type_note(c)

    # ── Sentence 1: Core profile ──────────────────────────────
    sentence1 = f"{title} with {years} yrs experience {company_note}, " \
                f"strong in {skills_text}."

    # ── Sentence 2: Behavioral / fit signal ────────────────────
    notes = []

    # Location fit
    loc_score = scored_candidate.get('location', 0)
    if loc_score >= 0.9:
        notes.append(f"based in {location} (preferred location)")
    elif loc_score <= 0.2:
        notes.append(f"based in {location} (outside India, location concern)")

    # Behavioral - response rate
    response_rate = signals.get('recruiter_response_rate', 0)
    if response_rate >= 0.7:
        notes.append(f"{response_rate:.0%} recruiter response rate")
    elif response_rate <= 0.2:
        notes.append(f"low response rate ({response_rate:.0%}, availability concern)")

    # Behavioral - last active
    days = days_since(signals.get('last_active_date'))
    if days is not None:
        if days <= 30:
            notes.append("recently active on platform")
        elif days >= 180:
            notes.append(f"inactive for {days} days (availability concern)")

   # Notice period
    notice = signals.get('notice_period_days')
    if notice is not None:
        if notice == 0:
            notes.append("immediately available")
        elif notice <= 15:
            notes.append(f"short {notice}-day notice period")

    # Open to work
    if signals.get('open_to_work_flag'):
        notes.append("open to work")

    # Honeypot-adjacent concerns (career score low but not filtered)
    career_score = scored_candidate.get('career', 0)
    if career_score <= 0.4:
        notes.append("career background may need closer review")

    if notes:
        joined = ", ".join(notes[:3])
        # Sirf pehla letter capital karo, baaki text waisa hi rakho
        sentence2 = joined[0].upper() + joined[1:] + "."
    else:
        sentence2 = ""
    reasoning = sentence1
    if sentence2:
        reasoning += " " + sentence2

    return reasoning