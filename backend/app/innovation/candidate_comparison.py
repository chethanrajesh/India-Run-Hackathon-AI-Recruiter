import json
import os
import google.generativeai as genai
from typing import Dict, Any

API_KEY = os.environ.get("GEMINI_API_KEY", "DUMMY_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def compare_candidates(job_title: str, cand_a: Dict[str, Any], cand_b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compares two candidates side-by-side and returns structured analysis.
    """
    prompt = f"""
    You are an expert technical recruiter AI.
    Compare Candidate A and Candidate B for the {job_title} role.
    
    Candidate A (ID: {cand_a['anonymized_id']}):
    Skills: {', '.join(cand_a.get('extracted_skills', []))}
    Experience: {chr(10).join(cand_a.get('experience_blocks', []))}
    Learning: {chr(10).join(cand_a.get('learning_signals', []))}
    
    Candidate B (ID: {cand_b['anonymized_id']}):
    Skills: {', '.join(cand_b.get('extracted_skills', []))}
    Experience: {chr(10).join(cand_b.get('experience_blocks', []))}
    Learning: {chr(10).join(cand_b.get('learning_signals', []))}
    
    Return a JSON object matching this structure exactly:
    {{
        "candidate_a_strengths": ["string"],
        "candidate_b_strengths": ["string"],
        "key_differentiators": ["string"],
        "recommendation": "string (Who is better suited and why?)"
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
        return json.loads(response.text)
    except Exception as e:
        print(f"Error in Candidate Comparison: {e}")
        return {
            "candidate_a_strengths": ["Data unavailable"],
            "candidate_b_strengths": ["Data unavailable"],
            "key_differentiators": ["API Error occurred"],
            "recommendation": "Unable to compare due to an error."
        }
