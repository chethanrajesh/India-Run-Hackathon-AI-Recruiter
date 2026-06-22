import os
import google.generativeai as genai
from typing import List, Dict, Any

API_KEY = os.environ.get("GEMINI_API_KEY", "DUMMY_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def ask_copilot(query: str, context_candidates: List[Dict[str, Any]]) -> str:
    """
    RAG-style copilot answering questions based on the candidate pool.
    """
    # Build a context string from the candidates
    context_str = "Candidate Pool Data:\n"
    for cand in context_candidates:
        context_str += f"- Candidate ID: {cand.get('candidate_id', 'Unknown')}\n"
        context_str += f"  Final Score: {cand.get('final_score', 0)}\n"
        if 'sub_scores' in cand:
            context_str += f"  Growth Score: {cand['sub_scores'].get('growth_score', 0)}\n"
            context_str += f"  Stuffing Penalty: {cand['sub_scores'].get('stuffing_penalty', 0)}\n"
        context_str += "\n"

    prompt = f"""
    You are the 'AI Recruiter Copilot'. The recruiter is asking you a question about the current pool of candidates.
    
    {context_str}
    
    Recruiter's Question: "{query}"
    
    Answer the question directly, citing candidate IDs and their scores to justify your answer. Keep it concise.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error in Recruiter Copilot: {e}")
        return "Sorry, I am currently unable to process your request."
