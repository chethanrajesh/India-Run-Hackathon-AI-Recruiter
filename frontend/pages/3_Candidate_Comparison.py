import streamlit as st
import requests

st.set_page_config(page_title="Candidate Comparison", page_icon="⚖️", layout="wide")

API_URL = "http://localhost:8000/api"

st.title("⚖️ Candidate Comparison Engine")

if not st.session_state.get("candidates") or len(st.session_state["candidates"]) < 2:
    st.warning("Please upload and process at least 2 candidates first.")
    st.stop()

cand_ids = [c["candidate_id"] for c in st.session_state["candidates"]]

col1, col2 = st.columns(2)
with col1:
    cand_a = st.selectbox("Select Candidate A", cand_ids, index=0)
with col2:
    cand_b = st.selectbox("Select Candidate B", cand_ids, index=1)

if st.button("Generate Deep Comparison", type="primary"):
    with st.spinner("AI is analyzing and comparing candidates..."):
        res = requests.post(
            f"{API_URL}/compare", 
            json={
                "job_id": st.session_state.get("job_id", "DUMMY"),
                "candidate_a_id": cand_a,
                "candidate_b_id": cand_b
            }
        )
        if res.status_code == 200:
            data = res.json()
            
            st.divider()
            st.markdown("### 🔍 Key Differentiators")
            for diff in data.get("key_differentiators", []):
                st.markdown(f"- {diff}")
                
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"**Strengths of {cand_a}**")
                for s in data.get("candidate_a_strengths", []):
                    st.markdown(f"- {s}")
            with c2:
                st.info(f"**Strengths of {cand_b}**")
                for s in data.get("candidate_b_strengths", []):
                    st.markdown(f"- {s}")
                    
            st.divider()
            st.markdown("### 🎯 Final Recommendation")
            st.write(data.get("recommendation", ""))
        else:
            st.error("Failed to compare candidates.")
