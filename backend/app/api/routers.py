import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.models.domain import JobDescriptionInput, CandidateInput, JobProfile, CandidateProfile
from app.engines.job_intelligence import parse_job_description
from app.engines.candidate_intelligence import process_candidate_resume
from app.engines.semantic_matching import store_job_vectors, store_candidate_vectors
from app.engines.adaptive_ranking import rank_candidate
from app.engines.explainability import generate_explainability
from app.innovation.candidate_comparison import compare_candidates
from app.innovation.interview_generator import generate_interview_questions
from app.innovation.skill_gap_analyzer import analyze_skill_gap
from app.innovation.recruiter_copilot import ask_copilot

router = APIRouter()

# --- In-Memory DB for PoC ---
db_jobs: Dict[str, JobProfile] = {}
db_candidates: Dict[str, CandidateProfile] = {}
db_rankings: Dict[str, List[Dict[str, Any]]] = {}

# --- Schemas ---
class CopilotRequest(BaseModel):
    job_id: str
    query: str

class SimulatorRequest(BaseModel):
    job_id: str
    weights: Dict[str, float]

class ComparisonRequest(BaseModel):
    job_id: str
    candidate_a_id: str
    candidate_b_id: str

# --- Endpoints ---

@router.post("/jobs/parse")
async def create_job(input_data: JobDescriptionInput):
    job_profile = parse_job_description(input_data.raw_text)
    job_id = str(uuid.uuid4())
    db_jobs[job_id] = job_profile
    
    # Store in Vector DB
    store_job_vectors(job_id, job_profile.required_skills, job_profile.responsibilities)
    
    return {"job_id": job_id, "profile": job_profile}

@router.post("/candidates/process")
async def process_candidate(input_data: CandidateInput):
    cand_profile = process_candidate_resume(input_data.raw_text)
    db_candidates[cand_profile.anonymized_id] = cand_profile
    
    # Store in Vector DB
    store_candidate_vectors(cand_profile.anonymized_id, cand_profile.extracted_skills, cand_profile.experience_blocks)
    
    return {"candidate_id": cand_profile.anonymized_id, "profile": cand_profile}

@router.post("/rank/{job_id}")
async def rank_candidates_for_job(job_id: str):
    if job_id not in db_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = db_jobs[job_id]
    rankings = []
    
    for cand_id, cand in db_candidates.items():
        result = rank_candidate(job, cand)
        # Generate explainability
        explanation = generate_explainability(job.title, cand.dict(), result)
        result["explainability_summary"] = explanation
        
        # Skill gap
        gap = analyze_skill_gap(job.required_skills, cand.extracted_skills)
        result["skill_gap"] = gap
        
        # Interview prep
        questions = generate_interview_questions(job.required_skills, cand.extracted_skills, cand.experience_blocks)
        result["interview_questions"] = questions
        
        rankings.append(result)
    
    # Sort descending
    rankings.sort(key=lambda x: x["final_score"], reverse=True)
    db_rankings[job_id] = rankings
    
    return {"job_id": job_id, "rankings": rankings}

@router.post("/simulate")
async def simulate_ranking(req: SimulatorRequest):
    if req.job_id not in db_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = db_jobs[req.job_id]
    rankings = []
    
    for cand_id, cand in db_candidates.items():
        result = rank_candidate(job, cand, weights=req.weights)
        rankings.append(result)
        
    rankings.sort(key=lambda x: x["final_score"], reverse=True)
    return {"job_id": req.job_id, "rankings": rankings}

@router.post("/compare")
async def compare_two_candidates(req: ComparisonRequest):
    if req.job_id not in db_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    if req.candidate_a_id not in db_candidates or req.candidate_b_id not in db_candidates:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    job = db_jobs[req.job_id]
    cand_a = db_candidates[req.candidate_a_id]
    cand_b = db_candidates[req.candidate_b_id]
    
    comparison = compare_candidates(job.title, cand_a.dict(), cand_b.dict())
    return comparison

@router.post("/copilot/chat")
async def copilot_chat(req: CopilotRequest):
    if req.job_id not in db_rankings:
        raise HTTPException(status_code=404, detail="Rankings not found for job")
        
    context = db_rankings[req.job_id]
    answer = ask_copilot(req.query, context)
    return {"answer": answer}
