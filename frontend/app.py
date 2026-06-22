import streamlit as st

st.set_page_config(
    page_title="Intelligent Recruiter",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧠 AI-Powered Candidate Intelligence Platform")
st.markdown("""
Welcome to the next generation of hiring. This platform uses an ensemble of AI engines to:
*   **Deeply understand** job requirements beyond keywords.
*   **Semantically match** candidates to roles based on context.
*   **Evaluate growth & learning agility** using continuous learning signals.
*   **Detect keyword stuffing** and skill inflation.
*   **Provide fully explainable** AI rankings and analytics.

---
### 🚀 Get Started (Demo Story)
1. Go to **Upload JD & Resumes** to load the trick dataset.
2. Go to the **Dashboard** to view the live AI rankings.
3. Use **Candidate Comparison** to see why the 'Hidden Gem' outperformed the 'Spammer'.
4. Try the **What-If Simulator** to change weights and watch the board re-rank.
5. Ask the **Recruiter Copilot** for insights.
""")

# Initialize Session State
if "job_id" not in st.session_state:
    st.session_state["job_id"] = None
if "candidates" not in st.session_state:
    st.session_state["candidates"] = []
if "rankings" not in st.session_state:
    st.session_state["rankings"] = []
