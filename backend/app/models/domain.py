from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- Job Models ---
class JobDescriptionInput(BaseModel):
    raw_text: str

class JobProfile(BaseModel):
    title: str = Field(..., description="Job Title")
    role: str = Field(..., description="General role category (e.g., Backend Engineer, Data Scientist)")
    seniority: str = Field(..., description="Seniority level (e.g., Junior, Mid, Senior, Lead)")
    experience_required: int = Field(..., description="Minimum years of experience required")
    required_skills: List[str] = Field(..., description="List of mandatory technical skills")
    optional_skills: List[str] = Field(..., description="List of 'nice-to-have' technical skills")
    responsibilities: List[str] = Field(..., description="Key responsibilities")

# --- Candidate Models ---
class CandidateInput(BaseModel):
    raw_text: str

class Education(BaseModel):
    degree: str
    institution: str
    cgpa: Optional[float] = None

class CandidateProfile(BaseModel):
    anonymized_id: str = Field(..., description="Unique ID replacing the name")
    degree_institution_cgpa: List[Education] = Field(..., description="Education details")
    extracted_skills: List[str] = Field(..., description="All technical skills extracted")
    experience_blocks: List[str] = Field(..., description="Summary of past roles and accomplishments")
    learning_signals: List[str] = Field(..., description="Certifications, courses, hackathons, open source contributions")
    keyword_stuffing_flag: bool = Field(default=False, description="True if discrepancy found between skills and experience")

# --- Ranking Models ---
class SubScores(BaseModel):
    semantic_score: float = 0.0
    skill_match_score: float = 0.0
    experience_score: float = 0.0
    growth_score: float = 0.0
    education_score: float = 0.0
    stuffing_penalty: float = 0.0

class RankingResult(BaseModel):
    candidate_id: str
    job_id: str
    final_score: float
    confidence_score: float
    sub_scores: SubScores
    explainability_summary: str
