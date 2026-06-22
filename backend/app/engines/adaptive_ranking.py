from typing import Dict, Any
from app.models.domain import SubScores, JobProfile, CandidateProfile
from app.engines.semantic_matching import calculate_semantic_similarity
from app.engines.growth_learning import calculate_growth_score
from app.engines.anti_stuffing import detect_keyword_stuffing

def calculate_skill_match(job_skills: list, cand_skills: list) -> float:
    if not job_skills:
        return 100.0
    job_skills_lower = [s.lower() for s in job_skills]
    cand_skills_lower = [s.lower() for s in cand_skills]
    matches = sum(1 for s in job_skills_lower if s in cand_skills_lower)
    return (matches / len(job_skills)) * 100.0

def calculate_experience_score(required_exp: int, candidate_exp_blocks: list) -> float:
    # Very rudimentary for PoC: count blocks as ~1.5 years each if actual years not extracted
    # In a full version, the LLM would extract exact total years of experience
    estimated_years = len(candidate_exp_blocks) * 1.5 
    if required_exp == 0:
        return 100.0
    if estimated_years >= required_exp:
        return 100.0
    return (estimated_years / required_exp) * 100.0

def calculate_education_score(candidate_edu: list) -> float:
    # For PoC, just return 100 if they have a degree, 0 otherwise
    if candidate_edu:
        return 100.0
    return 0.0

def rank_candidate(job: JobProfile, candidate: CandidateProfile, weights: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Ranks a candidate against a job profile using the Adaptive Ranking formula.
    """
    if weights is None:
        weights = {
            "semantic": 0.35,
            "skill": 0.25,
            "exp": 0.20,
            "growth": 0.15,
            "edu": 0.05
        }
        
    # 1. Semantic Match
    job_text = " ".join(job.required_skills + job.responsibilities)
    cand_text = " ".join(candidate.extracted_skills + candidate.experience_blocks)
    semantic_score = calculate_semantic_similarity(job_text, cand_text)
    
    # 2. Skill Match
    skill_score = calculate_skill_match(job.required_skills, candidate.extracted_skills)
    
    # 3. Experience Match
    exp_score = calculate_experience_score(job.experience_required, candidate.experience_blocks)
    
    # 4. Growth & Learning
    growth_score = calculate_growth_score(candidate.learning_signals, candidate.experience_blocks)
    
    # 5. Education
    edu_score = calculate_education_score(candidate.degree_institution_cgpa)
    
    # 6. Anti-Stuffing Penalty
    stuffing_analysis = detect_keyword_stuffing(candidate.extracted_skills, candidate.experience_blocks)
    stuffing_penalty = stuffing_analysis["penalty"]
    
    # Final Formula
    final_score = (
        (weights["semantic"] * semantic_score) +
        (weights["skill"] * skill_score) +
        (weights["exp"] * exp_score) +
        (weights["growth"] * growth_score) +
        (weights["edu"] * edu_score)
    ) - stuffing_penalty
    
    # Ensure score bounds
    final_score = max(0.0, min(100.0, final_score))
    
    # Confidence Score (basic heuristic: length of resume data)
    data_points = len(candidate.extracted_skills) + len(candidate.experience_blocks)
    confidence = min(100.0, data_points * 5.0)
    
    sub_scores = SubScores(
        semantic_score=semantic_score,
        skill_match_score=skill_score,
        experience_score=exp_score,
        growth_score=growth_score,
        education_score=edu_score,
        stuffing_penalty=stuffing_penalty
    )
    
    return {
        "candidate_id": candidate.anonymized_id,
        "final_score": final_score,
        "confidence_score": confidence,
        "sub_scores": sub_scores.dict(),
        "flagged_skills": stuffing_analysis["flagged_skills"]
    }
