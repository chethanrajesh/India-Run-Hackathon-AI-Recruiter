import json
import os
import google.generativeai as genai
from typing import List, Dict

API_KEY = os.environ.get("GEMINI_API_KEY", "DUMMY_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def detect_keyword_stuffing(skills: List[str], experience_blocks: List[str]) -> Dict:
    """
    Analyzes skills against experience to detect unsupported claims (keyword stuffing).
    Returns a dictionary with a penalty score and a list of flagged skills.
    """
    if not skills or not experience_blocks:
        return {"penalty": 0.0, "flagged_skills": []}

    prompt = f"""
    You are an AI auditor for an applicant tracking system.
    Your task is to identify "keyword stuffing" where a candidate lists skills but has no supporting evidence in their experience section.
    
    Skills Listed: {', '.join(skills)}
    
    Experience Blocks:
    {chr(10).join(experience_blocks)}
    
    Analyze the skills against the experience. Identify skills that have ZERO contextual support in the experience blocks.
    
    Return a JSON object exactly like this:
    {{
        "flagged_skills": ["skill1", "skill2"],
        "stuffing_severity": "float between 0.0 and 1.0 (0 means all skills supported, 1 means almost all are stuffed)"
    }}
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
        
        severity = data.get("stuffing_severity", 0.0)
        # Max penalty is 20 points in our ranking formula
        penalty = float(severity) * 20.0
        
        return {
            "penalty": penalty,
            "flagged_skills": data.get("flagged_skills", [])
        }
    except Exception as e:
        print(f"Error in Anti-Stuffing Engine: {e}")
        return {"penalty": 0.0, "flagged_skills": []}
