import json
import os
import google.generativeai as genai
from typing import Dict, Any, List

API_KEY = os.environ.get("GEMINI_API_KEY", "DUMMY_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_interview_questions(job_skills: List[str], cand_skills: List[str], experience: List[str]) -> List[str]:
    """
    Generates tailored interview questions based on candidate gaps.
    """
    missing_skills = [s for s in job_skills if s.lower() not in [cs.lower() for cs in cand_skills]]
    
    prompt = f"""
    You are an expert technical interviewer.
    Generate 3 highly specific interview questions for a candidate.
    
    The candidate LACKS these required skills: {', '.join(missing_skills) if missing_skills else 'None, they have all required skills.'}
    
    The candidate HAS these skills: {', '.join(cand_skills)}
    Their Experience:
    {chr(10).join(experience)}
    
    Generate 3 questions. If they lack a skill, ask how they would solve a problem using the tools they DO have, or how they plan to learn the missing skill. If they have all skills, ask advanced deep-dive questions based on their experience.
    
    Return a JSON object:
    {{
        "questions": ["Question 1", "Question 2", "Question 3"]
    }}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.4
            )
        )
        data = json.loads(response.text)
        return data.get("questions", [])
    except Exception as e:
        print(f"Error in Interview Generator: {e}")
        return ["Could you describe your most challenging technical project?"]
