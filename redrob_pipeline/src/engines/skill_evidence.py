import json

def compute_skill_evidence(candidate_row):
    """
    Evaluates depth of skills based on duration, endorsements, and assessments.
    Returns a score from 0.0 to 1.0.
    """
    score = 0.0
    
    try:
        skills = json.loads(candidate_row.get('raw_skills', '[]'))
    except:
        skills = []
        
    if not skills:
        return 0.0
        
    total_months = 0
    total_endorsements = 0
    
    for s in skills:
        total_months += s.get('duration_months', 0)
        total_endorsements += s.get('endorsements', 0)
        
    # Normalize
    # Max expected duration across all listed skills ~ 120 months (10 years)
    duration_score = min(total_months / 120.0, 1.0)
    
    # Max expected endorsements ~ 50
    endorsement_score = min(total_endorsements / 50.0, 1.0)
    
    # Assessment score (0 to 100)
    assessment_score = candidate_row.get('avg_assessment_score', 0) / 100.0
    
    # Weighted fusion
    final_score = (duration_score * 0.4) + (endorsement_score * 0.3) + (assessment_score * 0.3)
    
    return min(final_score, 1.0)
