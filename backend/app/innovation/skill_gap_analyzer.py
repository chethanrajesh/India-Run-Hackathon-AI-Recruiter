import json
import os
import google.generativeai as genai
from typing import Dict, Any, List

API_KEY = os.environ.get("GEMINI_API_KEY", "DUMMY_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_skill_gap(job_skills: List[str], cand_skills: List[str]) -> Dict[str, Any]:
    """
    Analyzes missing skills and generates a learning roadmap.
    """
    missing_skills = [s for s in job_skills if s.lower() not in [cs.lower() for cs in cand_skills]]
    
    if not missing_skills:
        return {
            "missing_skills": [],
            "learning_roadmap": "Candidate meets all hard skill requirements.",
            "readiness_percentage": 100
        }

    prompt = f"""
    You are an expert technical mentor.
    A candidate is missing the following skills for a job: {', '.join(missing_skills)}
    
    Provide:
    1. An estimated learning roadmap (e.g., "2 weeks to learn basic Docker").
    2. A readiness percentage (how close are they to being ready, 0-99%). Assume they have the other core skills.
    
    Return a JSON object exactly like this:
    {{
        "learning_roadmap": "string",
        "readiness_percentage": integer
    }}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )
        data = json.loads(response.text)
        return {
            "missing_skills": missing_skills,
            "learning_roadmap": data.get("learning_roadmap", "Roadmap unavailable."),
            "readiness_percentage": data.get("readiness_percentage", 50)
        }
    except Exception as e:
        print(f"Error in Skill Gap Analyzer: {e}")
        return {
            "missing_skills": missing_skills,
            "learning_roadmap": "Error generating roadmap.",
            "readiness_percentage": 50
        }
