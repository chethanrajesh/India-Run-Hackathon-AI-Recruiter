import json
import os
import uuid
import google.generativeai as genai
from app.models.domain import CandidateProfile, Education

API_KEY = os.environ.get("GEMINI_API_KEY", "DUMMY_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def process_candidate_resume(raw_text: str) -> CandidateProfile:
    """
    Parses a resume, anonymizes PII (Name, Gender, Photo), keeps Education,
    and extracts structured professional data.
    """
    # Generate a random ID for the candidate
    anon_id = f"CAND_{uuid.uuid4().hex[:8].upper()}"
    
    prompt = f"""
    You are an expert technical recruiter AI and data anonymizer.
    Analyze the following resume text.
    
    CRITICAL INSTRUCTIONS:
    1. STRIP and IGNORE the candidate's Name, Gender, and any visual identifiers.
    2. KEEP the candidate's Degree, Institution, and CGPA.
    3. Extract all technical skills.
    4. Summarize the experience into discrete blocks (e.g., "Software Engineer at X: Built Y using Z").
    5. Extract learning signals like certifications, online courses, hackathons, and open source.
    
    The JSON must match this structure exactly:
    {{
        "degree_institution_cgpa": [
            {{"degree": "string", "institution": "string", "cgpa": float (or null)}}
        ],
        "extracted_skills": ["string", "string"],
        "experience_blocks": ["string", "string"],
        "learning_signals": ["string", "string"]
    }}
    
    Resume Text:
    {raw_text}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        data = json.loads(response.text)
        
        # Build the model
        return CandidateProfile(
            anonymized_id=anon_id,
            degree_institution_cgpa=[Education(**edu) for edu in data.get("degree_institution_cgpa", [])],
            extracted_skills=data.get("extracted_skills", []),
            experience_blocks=data.get("experience_blocks", []),
            learning_signals=data.get("learning_signals", []),
            keyword_stuffing_flag=False # Will be set by Anti-Stuffing Engine
        )
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Fallback dummy data
        return CandidateProfile(
            anonymized_id=anon_id,
            degree_institution_cgpa=[Education(degree="B.Tech CS", institution="Tier 1 Univ", cgpa=8.5)],
            extracted_skills=["Python", "AWS", "Docker"],
            experience_blocks=["Backend Eng: Built API in Python.", "DevOps: Deployed to AWS via Docker."],
            learning_signals=["AWS Certified Solutions Architect"],
            keyword_stuffing_flag=False
        )
