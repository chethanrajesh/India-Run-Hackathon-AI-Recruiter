from .honeypot import compute_inconsistency_penalty
from .skill_evidence import compute_skill_evidence
from .availability import compute_availability
from .career_evidence import compute_career_evidence
from .market_demand import compute_market_demand

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
