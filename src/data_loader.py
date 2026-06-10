# src/data_loader.py
# Yeh file data padhne ka kaam karti hai
# Simple responsibility: sirf data load karo

import json
import gzip
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def load_sample_candidates():
    """
    50 sample candidates load karo (testing ke liye).
    Pehle yahi use karo jab tak poora system ready na ho.
    """
    print(f"📂 Loading sample candidates from {config.SAMPLE_FILE}...")
    
    with open(config.SAMPLE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data)} sample candidates")
    return data


def load_all_candidates(use_sample=False):
    """
    Sab candidates load karo.
    use_sample=True karo development ke time (fast hoga)
    use_sample=False karo final submission ke time
    """
    if use_sample:
        return load_sample_candidates()
    
    candidates = []
    filepath = config.CANDIDATES_FILE
    
    # Check karo file exist karti hai
    if not Path(filepath).exists():
        print(f"❌ File not found: {filepath}")
        print("   Sample file use kar rahe hain...")
        return load_sample_candidates()
    
    print(f"📂 Loading all candidates from {filepath}...")
    print("   (Yeh thoda time lagega — 1 lakh candidates hain)")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="Loading candidates"):
            line = line.strip()
            if line:  # empty lines skip karo
                try:
                    candidate = json.loads(line)
                    candidates.append(candidate)
                except json.JSONDecodeError:
                    continue  # bad line skip karo
    
    print(f"✅ Loaded {len(candidates):,} candidates")
    return candidates


def get_candidate_text(candidate):
    """
    Ek candidate ke saari important info ko
    ek bade text string mein convert karo.
    
    Kyun? Kyunki embedding model text hi samajhta hai.
    Hum candidate ka 'summary' banana chahte hain.
    """
    parts = []
    
    # --- Profile section ---
    profile = candidate.get('profile', {})
    
    if profile.get('headline'):
        parts.append(f"Headline: {profile['headline']}")
    
    if profile.get('summary'):
        parts.append(f"Summary: {profile['summary']}")
    
    if profile.get('current_title'):
        parts.append(f"Current Role: {profile['current_title']}")
    
    if profile.get('current_industry'):
        parts.append(f"Industry: {profile['current_industry']}")
    
    yoe = profile.get('years_of_experience', 0)
    parts.append(f"Years of Experience: {yoe}")
    
    # --- Skills section ---
    skills = candidate.get('skills', [])
    if skills:
        # Advanced aur expert skills ko zyada importance do
        strong_skills = [
            s['name'] for s in skills
            if s.get('proficiency') in ['advanced', 'expert']
        ]
        all_skills = [s['name'] for s in skills]
        
        if strong_skills:
            parts.append(f"Strong Skills: {', '.join(strong_skills)}")
        parts.append(f"All Skills: {', '.join(all_skills)}")
    
    # --- Career history section ---
    career = candidate.get('career_history', [])
    for job in career[:4]:  # Last 4 jobs kaafi hain
        title = job.get('title', '')
        company = job.get('company', '')
        desc = job.get('description', '')
        if title and company:
            parts.append(f"Role: {title} at {company}")
        if desc:
            # Description ke pehle 200 characters lo
            parts.append(f"Work: {desc[:200]}")
    
    # --- Education section ---
    education = candidate.get('education', [])
    for edu in education[:2]:  # Top 2 degrees
        degree = edu.get('degree', '')
        field = edu.get('field_of_study', '')
        institution = edu.get('institution', '')
        if degree and field:
            parts.append(f"Education: {degree} in {field} from {institution}")
    
    # Sab parts ko join karo
    return " | ".join(parts)


def inspect_candidate(candidate):
    """
    Ek candidate ki saari info print karo — debugging ke liye useful
    """
    cid = candidate.get('candidate_id', 'Unknown')
    profile = candidate.get('profile', {})
    signals = candidate.get('redrob_signals', {})
    
    print(f"\n{'='*60}")
    print(f"🧑 Candidate: {cid}")
    print(f"{'='*60}")
    print(f"  Title    : {profile.get('current_title', 'N/A')}")
    print(f"  Company  : {profile.get('current_company', 'N/A')}")
    print(f"  Location : {profile.get('location', 'N/A')}")
    print(f"  Exp (yrs): {profile.get('years_of_experience', 0)}")
    print(f"  Skills   : {len(candidate.get('skills', []))} skills")
    print(f"  Last seen: {signals.get('last_active_date', 'N/A')}")
    print(f"  Resp rate: {signals.get('recruiter_response_rate', 0):.0%}")
    print(f"  Open2work: {signals.get('open_to_work_flag', False)}")
    print(f"  Notice   : {signals.get('notice_period_days', '?')} days")
    print(f"{'='*60}")