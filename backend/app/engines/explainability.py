import os
import google.generativeai as genai
from typing import Dict, Any

API_KEY = os.environ.get("GEMINI_API_KEY", "DUMMY_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_explainability(job_title: str, candidate_data: Dict[str, Any], ranking_results: Dict[str, Any]) -> str:
    """
    Generates a human-readable explanation of the candidate's ranking.
    """
    prompt = f"""
    You are an Explainable AI for a recruitment platform.
    Your job is to explain WHY a candidate received their specific scores for the {job_title} role.
    
    Candidate Data:
    Skills: {', '.join(candidate_data.get('extracted_skills', []))}
    Experience: {chr(10).join(candidate_data.get('experience_blocks', []))}
    Learning: {chr(10).join(candidate_data.get('learning_signals', []))}
    
    Scores Received:
    Final Score: {ranking_results['final_score']:.2f}
    Semantic Match: {ranking_results['sub_scores']['semantic_score']:.2f}
    Skill Match: {ranking_results['sub_scores']['skill_match_score']:.2f}
    Growth Score: {ranking_results['sub_scores']['growth_score']:.2f}
    Stuffing Penalty: {ranking_results['sub_scores']['stuffing_penalty']:.2f}
    Flagged Skills: {', '.join(ranking_results.get('flagged_skills', []))}
    
    Write a concise, transparent 3-4 sentence explanation for the recruiter.
    Highlight strengths, gaps, and any penalties (like keyword stuffing if applicable).
    Be objective and data-driven.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error in Explainability Engine: {e}")
        return "Explanation could not be generated due to an API error. The candidate's scores are based on the core matching algorithm."
