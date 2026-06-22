from .honeypot import compute_inconsistency_penalty
from .skill_evidence import compute_skill_evidence
from .availability import compute_availability

def compute_market_demand(candidate_row):
    """
    Score based on recruiter interest.
    """
    saved = candidate_row.get('saved_by_recruiters_30d', 0)
    search = candidate_row.get('search_appearance_30d', 0)
    
    # Normalize: e.g., max 20 saves, max 100 appearances
    score = (min(saved / 20.0, 1.0) * 0.6) + (min(search / 100.0, 1.0) * 0.4)
    return score

def compute_experience_match(candidate_row, jd_years_required=5):
    """
    Match candidate years of experience against JD requirement.
    """
    cand_years = candidate_row.get('years_of_experience', 0)
    if cand_years >= jd_years_required:
        return 1.0
    elif cand_years > 0:
        return cand_years / jd_years_required
    return 0.0

def compute_career_evidence(candidate_row):
    """
    Evaluate depth and stability of career history.
    """
    try:
        import json
        career = json.loads(candidate_row.get('raw_career', '[]'))
    except:
        career = []
        
    if not career:
        return 0.0
        
    num_roles = len(career)
    
    # Check if descriptions exist
    has_descriptions = sum(1 for c in career if len(c.get('description', '')) > 20)
    desc_score = has_descriptions / num_roles if num_roles > 0 else 0.0
    
    # Stability (fewer roles per year of experience is generally better, to a point)
    years = candidate_row.get('years_of_experience', 1)
    roles_per_year = num_roles / max(years, 1)
    
    stability_score = 1.0
    if roles_per_year > 1.5: # Job hopper penalty
        stability_score = 0.5
        
    return (desc_score * 0.7) + (stability_score * 0.3)

def compute_final_score(candidate_row, semantic_fit_score, jd_years_required=5):
    """
    Applies the new 6-factor deterministic formula.
    """
    sem_fit = semantic_fit_score
    car_evid = compute_career_evidence(candidate_row)
    ski_evid = compute_skill_evidence(candidate_row)
    avail = compute_availability(candidate_row)
    market = compute_market_demand(candidate_row)
    exp_match = compute_experience_match(candidate_row, jd_years_required)
    
    penalty = compute_inconsistency_penalty(candidate_row)
    
    final_score = (0.35 * sem_fit) + \
                  (0.20 * car_evid) + \
                  (0.15 * ski_evid) + \
                  (0.10 * avail) + \
                  (0.10 * market) + \
                  (0.10 * exp_match) - penalty
                  
    components = {
        'semantic_fit': sem_fit,
        'career_evidence': car_evid,
        'skill_evidence': ski_evid,
        'availability': avail,
        'market_demand': market,
        'experience_match': exp_match,
        'honeypot_penalty': penalty
    }
                  
    return final_score, components
