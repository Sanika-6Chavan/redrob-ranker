# src/behavioral_scorer.py
from datetime import datetime, date
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def days_since(date_str):
    if not date_str:
        return 999
    try:
        d = datetime.strptime(str(date_str), "%Y-%m-%d").date()
        return (date.today() - d).days
    except:
        return 999


def score_recency(signals):
    days = days_since(signals.get('last_active_date'))

    if days <= 7:      return 1.0
    elif days <= 30:   return 0.9
    elif days <= 60:   return 0.75
    elif days <= 90:   return 0.55
    elif days <= 180:  return 0.3
    else:              return 0.1


def score_availability(signals):
    score = 0.5

    if signals.get('open_to_work_flag'):
        score += 0.3

    notice = signals.get('notice_period_days', 90)
    if notice <= 15:
        score += 0.2
    elif notice <= 30:
        score += 0.15
    elif notice <= 60:
        score += 0.05
    elif notice > 90:
        score -= 0.1

    return min(1.0, max(0.0, score))


def score_responsiveness(signals):
    response_rate = signals.get('recruiter_response_rate', 0)
    avg_time = signals.get('avg_response_time_hours', 48)

    if response_rate >= 0.8:    rate_score = 1.0
    elif response_rate >= 0.6:  rate_score = 0.8
    elif response_rate >= 0.4:  rate_score = 0.6
    elif response_rate >= 0.2:  rate_score = 0.4
    else:                        rate_score = 0.1

    if avg_time <= 4:       time_score = 1.0
    elif avg_time <= 12:    time_score = 0.85
    elif avg_time <= 24:    time_score = 0.7
    elif avg_time <= 48:    time_score = 0.5
    else:                   time_score = 0.3

    return (rate_score * 0.7 + time_score * 0.3)


def score_platform_activity(signals):
    views = signals.get('profile_views_received_30d', 0)
    saved = signals.get('saved_by_recruiters_30d', 0)
    applications = signals.get('applications_submitted_30d', 0)
    connections = signals.get('connection_count', 0)

    view_score  = min(1.0, views / 50)
    saved_score = min(1.0, saved / 10)
    app_score   = min(1.0, applications / 5)
    conn_score  = min(1.0, connections / 200)

    return (
        view_score  * 0.3 +
        saved_score * 0.4 +
        app_score   * 0.2 +
        conn_score  * 0.1
    )


def score_interview_reliability(signals):
    interview_rate = signals.get('interview_completion_rate', 0.5)
    offer_rate = signals.get('offer_acceptance_rate', -1)

    interview_score = interview_rate

    if offer_rate == -1:
        offer_score = 0.6
    else:
        offer_score = offer_rate

    return (interview_score * 0.6 + offer_score * 0.4)


def score_behavioral(candidate):
    signals = candidate.get('redrob_signals', {})

    recency_score      = score_recency(signals)
    availability_score = score_availability(signals)
    response_score     = score_responsiveness(signals)
    activity_score     = score_platform_activity(signals)
    reliability_score  = score_interview_reliability(signals)

    final = (
        recency_score      * 0.30 +
        availability_score * 0.25 +
        response_score     * 0.20 +
        activity_score     * 0.15 +
        reliability_score  * 0.10
    )

    return round(final, 4)