def generate_explanation(components):
    """
    Generates a 1-2 sentence rationale based on the highest contributing sub-scores.
    This runs in O(1) time without any LLM calls.
    """
    # Find the top 2 strongest signals
    scores = {
        "Semantic Fit": components['semantic_fit'],
        "Career Evidence": components['career_evidence'],
        "Skill Evidence": components['skill_evidence'],
        "Availability": components['availability'],
        "Market Demand": components['market_demand']
    }
    
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_1, top_2 = sorted_scores[0], sorted_scores[1]
    
    explanation = f"Candidate ranks highly due to exceptional {top_1[0]} "
    
    if top_2[1] > 0.6:
        explanation += f"and very strong {top_2[0]}. "
    else:
        explanation += f"and solid {top_2[0]}. "
        
    if components['honeypot_penalty'] > 0:
        explanation += "However, minor inconsistencies were detected in the profile."
        
    return explanation.strip()
