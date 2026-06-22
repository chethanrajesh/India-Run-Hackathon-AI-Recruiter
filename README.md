# AI-Powered Intelligent Candidate Discovery Platform

This is a complete end-to-end Proof of Concept (PoC) built for the India Run Hackathon.

## Architecture Highlights
- **Backend:** Modular FastAPI Architecture
- **Frontend:** Streamlit
- **Vector DB:** Qdrant
- **AI Models:** Gemini 1.5 Flash (via `google-generativeai`) and SentenceTransformers (`all-MiniLM-L6-v2`)

## How to Run

1. **Set your API Key:**
   You must set your Gemini API key as an environment variable before running the backend.
   ```bash
   # Windows (PowerShell)
   $env:GEMINI_API_KEY="your_actual_api_key_here"
   ```

2. **Start the Infrastructure (Optional but recommended for Vector DB):**
   ```bash
   docker-compose up -d
   ```
   *(Note: The system will fall back to an in-memory Qdrant instance if Docker is not running)*

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Backend (FastAPI):**
   Open a terminal, navigate to the project root, and run:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

5. **Start the Frontend (Streamlit):**
   Open a *second* terminal, navigate to the project root, and run:
   ```bash
   streamlit run frontend/app.py
   ```

## Demo Instructions (The Trick Dataset)
1. Open the Streamlit App.
2. Go to the **Upload & Parse** page.
3. Open `data/job_description.txt` and paste it into the Job Description box. Click Parse.
4. Open `data/resume_1_spammer.txt` and paste it into the Candidate box. Click Parse.
5. Do the same for `resume_2_classic.txt` and `resume_3_hiddengem.txt`.
6. Click **Generate Rankings**.
7. Navigate through the **Dashboard**, **Comparison Engine**, and **What-If Simulator** to see the system in action!
