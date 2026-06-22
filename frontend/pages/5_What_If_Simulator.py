import streamlit as st
import requests

st.set_page_config(page_title="What-If Simulator", page_icon="🔮", layout="wide")

API_URL = "http://localhost:8000/api"

st.title("🔮 What-If Ranking Simulator")
st.markdown("Change the ranking weights dynamically and watch the leaderboard re-rank live to find the perfect balance.")

if not st.session_state.get("candidates") or not st.session_state.get("job_id"):
    st.warning("Please upload a Job Description and Candidates first.")
    st.stop()

st.sidebar.header("Adjust Formula Weights")
st.sidebar.markdown("Total should roughly equal 1.0, though the algorithm handles normalization.")

w_semantic = st.sidebar.slider("Semantic Fit", 0.0, 1.0, 0.35, 0.05)
w_skill = st.sidebar.slider("Skill Match", 0.0, 1.0, 0.25, 0.05)
w_exp = st.sidebar.slider("Experience Match", 0.0, 1.0, 0.20, 0.05)
w_growth = st.sidebar.slider("Growth & Agility", 0.0, 1.0, 0.15, 0.05)
w_edu = st.sidebar.slider("Education", 0.0, 1.0, 0.05, 0.05)

if st.sidebar.button("Run Simulation", type="primary"):
    with st.spinner("Running Live Simulation..."):
        weights = {
            "semantic": w_semantic,
            "skill": w_skill,
            "exp": w_exp,
            "growth": w_growth,
            "edu": w_edu
        }
        res = requests.post(
            f"{API_URL}/simulate",
            json={
                "job_id": st.session_state["job_id"],
                "weights": weights
            }
        )
        if res.status_code == 200:
            simulated_rankings = res.json()["rankings"]
            
            st.success("Simulation Complete!")
            st.markdown("### Simulated Leaderboard")
            
            for i, rank in enumerate(simulated_rankings):
                st.markdown(f"**#{i+1} Candidate {rank['candidate_id']}** - Score: {rank['final_score']:.1f}")
                
        else:
            st.error("Failed to run simulation.")
