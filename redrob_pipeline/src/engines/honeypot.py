import json
import re
import numpy as np

def compute_inconsistency_penalty(candidate_row):
    """
    Analyzes the candidate features to detect honeypots or keyword stuffers.
    Returns a penalty score from 0.0 to 1.0.
    """
    penalty = 0.0
    
    try:
        skills = json.loads(candidate_row.get('raw_skills', '[]'))
        career = json.loads(candidate_row.get('raw_career', '[]'))
    except:
        skills = []
        career = []
        
    # 1. Skill Density (Stuffing)
    skill_names = [s.get('name', '').lower() for s in skills if s.get('name')]
    career_text = " ".join([c.get('description', '').lower() for c in career])
    
    if skill_names and career_text:
        words = re.findall(r'\w+', career_text)
        total_words = len(words)
        
        if total_words > 0:
            # How many claimed skills actually appear in their experience description?
            skills_found = sum(1 for s in skill_names if s in career_text)
            coverage_ratio = skills_found / len(skill_names)
            
            # If they list 50 skills but mention none in their actual job history
            if coverage_ratio < 0.1 and len(skill_names) > 15:
                penalty += 0.4
                
            # If their description is literally just a list of skills (density > 30%)
            if len(skill_names) / total_words > 0.3:
                penalty += 0.5
                
    # 2. Behavioral Contradictions (e.g., 0 response rate but claims to be super active)
    if candidate_row.get('open_to_work_flag') and candidate_row.get('recruiter_response_rate') == 0.0:
        if candidate_row.get('saved_by_recruiters_30d', 0) > 10:
            # Highly targeted but ignores everyone despite being "open to work"
            penalty += 0.2
            
    return min(penalty, 1.0)
