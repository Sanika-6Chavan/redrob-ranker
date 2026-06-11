# src/location_scorer.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.jd_analyzer import get_jd_signals


def score_location(candidate):
    signals_data = get_jd_signals()
    profile = candidate.get('profile', {})
    redrob = candidate.get('redrob_signals', {})

    location = profile.get('location', '').lower()
    country  = profile.get('country', '').lower()
    willing  = redrob.get('willing_to_relocate', False)

    if country and country not in ['india', 'in', '']:
        return 0.1

    preferred = signals_data['preferred_cities']
    if any(city in location for city in preferred):
        return 1.0

    acceptable = signals_data['acceptable_cities']
    if any(city in location for city in acceptable):
        base = 0.75
        return min(1.0, base + 0.15) if willing else base

    if willing:
        return 0.6

    return 0.4