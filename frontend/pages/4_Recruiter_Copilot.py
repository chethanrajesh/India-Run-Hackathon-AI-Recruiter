import streamlit as st
import requests

st.set_page_config(page_title="Recruiter Copilot", page_icon="🤖", layout="wide")

API_URL = "http://localhost:8000/api"

st.title("🤖 AI Recruiter Copilot")
st.markdown("Ask natural language questions about the talent pool (e.g., *'Who is the best fit for backend?'*, *'Why was Candidate A ranked lower?'*).")

if not st.session_state.get("rankings"):
    st.warning("Please generate rankings first to give the Copilot context.")
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Display Chat
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input
if prompt := st.chat_input("Ask the Copilot..."):
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Copilot is thinking..."):
            res = requests.post(
                f"{API_URL}/copilot/chat",
                json={
                    "job_id": st.session_state["job_id"],
                    "query": prompt
                }
            )
            if res.status_code == 200:
                answer = res.json()["answer"]
                st.write(answer)
                st.session_state["chat_history"].append({"role": "assistant", "content": answer})
            else:
                st.error("Failed to connect to Copilot.")
