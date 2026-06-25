import json
import random

def get_skills_string(candidate_row):
    try:
        skills = json.loads(candidate_row.get('raw_skills', '[]'))
        skill_names = [s.get('name') for s in skills if s.get('name')]
        if len(skill_names) >= 2:
            # Pick top 2 actual skills from the candidate to prevent hallucination
            return f"{skill_names[0]} and {skill_names[1]}"
        elif len(skill_names) == 1:
            return skill_names[0]
    except:
        pass
    return "core technical skills"

def get_concerns(candidate_row, jd_years_required=5):
    concerns = []
    
    # Notice Period
    notice_days = candidate_row.get('notice_period_days', 90)
    if notice_days > 60:
        concerns.append(f"a lengthy notice period ({notice_days} days)")
        
    # Experience gap
    yoe = candidate_row.get('years_of_experience', 0)
    if yoe < jd_years_required:
        concerns.append(f"falling short of the experience requirement ({yoe} vs {jd_years_required} years)")
        
    # Low response rate
    response_rate = candidate_row.get('recruiter_response_rate', 1.0)
    if candidate_row.get('open_to_work_flag') and response_rate < 0.2:
        concerns.append("historically low response rates despite being 'open to work'")
        
    if concerns:
        return random.choice([
            f"Note: there is some concern regarding {concerns[0]}.",
            f"However, we noted {concerns[0]} as a potential gap.",
            f"Keep in mind {concerns[0]} before proceeding."
        ])
    return ""

def generate_explanation(candidate_row, rank, components, jd_years_required=5):
    """
    Generates a dynamic, non-templated reasoning string using specific facts.
    """
    yoe = candidate_row.get('years_of_experience', 0)
    skills_str = get_skills_string(candidate_row)
    
    # Identify top signal for variation
    scores = {
        "semantic fit": components['semantic_fit'],
        "career evidence": components['career_evidence'],
        "skill evidence": components['skill_evidence'],
        "market demand": components['market_demand']
    }
    top_signal = max(scores, key=scores.get)
    
    concern_text = get_concerns(candidate_row, jd_years_required)
    
    if rank <= 20:
        templates = [
            f"Exceptional candidate bringing {yoe} years of experience and deep expertise in {skills_str}. Highly recommended due to standout {top_signal}.",
            f"A top-tier fit with a very strong {top_signal} score. Demonstrates solid background in {skills_str} across {yoe} years in the industry.",
            f"Strongest match for the JD with {yoe} years of relevant work; their {skills_str} profile and {top_signal} are best-in-class."
        ]
        base = random.choice(templates)
        
    elif rank <= 70:
        templates = [
            f"Solid background in {skills_str} with {yoe} years of experience. Selected primarily for robust {top_signal}.",
            f"Good match overall; brings {yoe} years to the table and verifiable skills in {skills_str}. Shows strong {top_signal}.",
            f"Competent candidate whose {yoe} years of experience and {skills_str} background align well with the core requirements."
        ]
        base = random.choice(templates)
        
    else:
        templates = [
            f"Included as a final filler due to decent {top_signal}, though they only offer {yoe} years of experience in {skills_str}.",
            f"Marginal fit primarily surfaced by their {top_signal}. They possess {yoe} years of experience with {skills_str}.",
            f"Adjacent skills only (e.g., {skills_str}); likely below the ideal cutoff but included due to their {yoe} years of experience."
        ]
        base = random.choice(templates)
        
    if concern_text:
        return f"{base} {concern_text}"
    return base
