import json
import os
import google.generativeai as genai
from typing import List

API_KEY = os.environ.get("GEMINI_API_KEY", "DUMMY_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def calculate_growth_score(learning_signals: List[str], experience_blocks: List[str]) -> float:
    """
    Evaluates learning agility and career velocity.
    Returns a score out of 100.
    """
    if not learning_signals and not experience_blocks:
        return 0.0

    prompt = f"""
    You are an AI specialized in HR and Talent Analytics.
    Evaluate the candidate's "Growth & Learning Agility".
    
    Learning Signals (Certs, Courses, Open Source, Hackathons):
    {chr(10).join(learning_signals) if learning_signals else "None"}
    
    Experience Blocks (Look for career velocity, promotions, increasing complexity):
    {chr(10).join(experience_blocks)}
    
    Based on these, assign a Growth Score from 0 to 100.
    - 0-20: Stagnant, no recent learning, repetitive work.
    - 30-50: Average progression, some self-learning.
    - 60-80: Strong continuous learning, multiple certs/projects, clear promotions.
    - 85-100: Exceptional agility, hackathon wins, major open source, rapid career advancement.
    
    Return a JSON object exactly like this:
    {{
        "growth_score": 85.0
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
        return float(data.get("growth_score", 50.0))
    except Exception as e:
        print(f"Error in Growth & Learning Engine: {e}")
        # Default average score if LLM fails
        return 50.0
