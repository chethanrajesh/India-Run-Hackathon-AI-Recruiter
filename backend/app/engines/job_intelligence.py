import json
import os
import google.generativeai as genai
from app.models.domain import JobProfile

# Try to get API key from environment, else use a placeholder for now
API_KEY = os.environ.get("GEMINI_API_KEY", "DUMMY_KEY")
genai.configure(api_key=API_KEY)

# Use flash for fast JSON extraction
model = genai.GenerativeModel('gemini-1.5-flash')

def parse_job_description(raw_text: str) -> JobProfile:
    """
    Parses a raw job description string into a structured JobProfile using Gemini.
    """
    prompt = f"""
    You are an expert technical recruiter AI. 
    Analyze the following job description and extract the key information into a structured JSON format.
    
    The JSON must match this structure exactly:
    {{
        "title": "string",
        "role": "string (e.g., Backend Engineer, Data Scientist)",
        "seniority": "string (e.g., Junior, Mid, Senior, Lead)",
        "experience_required": "integer (minimum years of experience, default to 0 if not specified)",
        "required_skills": ["string", "string"],
        "optional_skills": ["string", "string"],
        "responsibilities": ["string", "string"]
    }}
    
    Job Description:
    {raw_text}
    """
    
    # In a real scenario with proper API key, we call the model.
    # For this hackathon PoC, we handle potential lack of API key gracefully.
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        data = json.loads(response.text)
        return JobProfile(**data)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Fallback dummy data for demo purposes if API key is not set or fails
        return JobProfile(
            title="Senior MLOps Engineer",
            role="MLOps Engineer",
            seniority="Senior",
            experience_required=5,
            required_skills=["AWS", "Kubernetes", "Docker", "Python", "CI/CD"],
            optional_skills=["Terraform", "PyTorch"],
            responsibilities=["Deploy ML models", "Manage K8s clusters"]
        )
