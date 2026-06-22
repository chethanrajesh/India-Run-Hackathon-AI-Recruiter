import streamlit as st

st.set_page_config(page_title="Dashboard & Explainability", page_icon="🏆", layout="wide")

st.title("🏆 AI Recruiter Dashboard")

if not st.session_state.get("rankings"):
    st.warning("No rankings available. Please go to 'Upload & Parse' to generate rankings.")
    st.stop()

st.subheader("Leaderboard")

# Display Leaderboard
for i, rank in enumerate(st.session_state["rankings"]):
    with st.expander(f"Rank #{i+1} | Candidate ID: {rank['candidate_id']} | Score: {rank['final_score']:.1f}/100", expanded=(i==0)):
        
        # Top Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Semantic Match", f"{rank['sub_scores']['semantic_score']:.1f}%")
        c2.metric("Skill Match", f"{rank['sub_scores']['skill_match_score']:.1f}%")
        c3.metric("Growth & Agility", f"{rank['sub_scores']['growth_score']:.1f}")
        c4.metric("Stuffing Penalty", f"-{rank['sub_scores']['stuffing_penalty']:.1f}", delta_color="inverse")
        
        st.divider()
        
        # Explainability & Insights
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown("### 🧠 AI Explainability")
            st.info(rank.get('explainability_summary', "Explanation missing."))
            
            st.markdown("### 🛠️ Skill Gap Analyzer")
            gap = rank.get('skill_gap', {})
            if gap.get('missing_skills'):
                st.warning(f"**Missing Skills:** {', '.join(gap['missing_skills'])}")
                st.markdown(f"**Learning Roadmap:** {gap['learning_roadmap']}")
            else:
                st.success("Candidate meets all hard skill requirements.")
                
        with col_right:
            st.markdown("### 🎤 AI Interview Generator")
            questions = rank.get('interview_questions', [])
            for q_idx, q in enumerate(questions):
                st.markdown(f"**Q{q_idx+1}:** {q}")
                
            if rank.get('flagged_skills'):
                st.markdown("### 🚨 Anti-Stuffing Flags")
                st.error(f"Flagged Skills: {', '.join(rank['flagged_skills'])}")
