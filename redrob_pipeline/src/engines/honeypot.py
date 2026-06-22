import json

def compute_inconsistency_penalty(candidate_row):
    """
    Analyzes the candidate features to detect signal inconsistencies.
    Returns a penalty score from 0.0 to 1.0.
    """
    penalty = 0.0
    
    # 1. Behavioral Contradictions (e.g., 0 response rate but claims to be super active)
    if candidate_row.get('open_to_work_flag') and candidate_row.get('recruiter_response_rate', 1.0) == 0.0:
        if candidate_row.get('saved_by_recruiters_30d', 0) > 5:
            # Highly targeted but ignores everyone despite being "open to work"
            penalty += 0.3
            
    # 2. Complete Profile vs Activity Inconsistency
    # If they have high profile views and recruiter saves, but 0 response rate, they might be a bot/honeypot
    if candidate_row.get('profile_views_received_30d', 0) > 100 and candidate_row.get('recruiter_response_rate', 1.0) < 0.05:
        penalty += 0.3
        
    return min(penalty, 1.0)
