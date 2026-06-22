import streamlit as st
import requests
import PyPDF2
import docx2txt
import io

st.set_page_config(page_title="Upload & Parse", page_icon="📄", layout="wide")

# Initialize Session State
if "job_id" not in st.session_state:
    st.session_state["job_id"] = None
if "candidates" not in st.session_state:
    st.session_state["candidates"] = []
if "rankings" not in st.session_state:
    st.session_state["rankings"] = []

API_URL = "http://localhost:8000/api"

st.title("📄 Upload JD & Resumes")

def extract_text(file):
    """Helper to extract text from TXT, PDF, or DOCX"""
    file.seek(0)
    if file.name.endswith('.txt'):
        return file.getvalue().decode("utf-8")
    elif file.name.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        return "".join(page.extract_text() for page in pdf_reader.pages)
    elif file.name.endswith('.docx'):
        return docx2txt.process(file)
    return ""

col1, col2 = st.columns(2)

with col1:
    st.header("Step 1: Upload Job Description")
    
    # JD can be text or file
    jd_input_mode = st.radio("Input Method", ["Upload File", "Paste Text"], key="jd_mode")
    jd_text = ""
    
    if jd_input_mode == "Upload File":
        jd_file = st.file_uploader("Upload Job Description (.txt, .pdf, .docx)", type=['txt', 'pdf', 'docx'], key="jd_file")
        if jd_file:
            jd_text = extract_text(jd_file)
            st.success("File uploaded successfully!")
    else:
        jd_text = st.text_area("Paste Job Description here", height=200)

    if st.button("Parse Job Description", type="primary"):
        if not jd_text.strip():
            st.error("Please provide a Job Description.")
        else:
            with st.spinner("AI is parsing the Job Description..."):
                res = requests.post(f"{API_URL}/jobs/parse", json={"raw_text": jd_text})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state["job_id"] = data["job_id"]
                    st.success(f"Job Parsed! Detected Role: {data['profile']['title']}")
                    st.json(data["profile"])
                else:
                    st.error("Failed to parse JD.")

with col2:
    st.header("Step 2: Upload Candidates")
    
    cand_input_mode = st.radio("Input Method", ["Upload File", "Paste Text"], key="cand_mode")
    cand_text = ""
    
    if cand_input_mode == "Upload File":
        cand_files = st.file_uploader("Upload Resumes (.txt, .pdf, .docx)", type=['txt', 'pdf', 'docx'], accept_multiple_files=True, key="cand_files")
        
        if st.button("Parse All Uploaded Candidates"):
            if not cand_files:
                st.error("Please upload at least one resume.")
            else:
                for file in cand_files:
                    c_text = extract_text(file)
                    with st.spinner(f"Anonymizing & extracting {file.name}..."):
                        res = requests.post(f"{API_URL}/candidates/process", json={"raw_text": c_text})
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state["candidates"].append(data)
                            st.success(f"Processed: {file.name} (Anonymized ID: {data['candidate_id']})")
                        else:
                            st.error(f"Failed to process {file.name}.")
    else:
        cand_text = st.text_area("Paste Candidate Resume text here", height=200)
        if st.button("Parse Candidate & Anonymize"):
            if not cand_text.strip():
                st.error("Please provide resume text.")
            else:
                with st.spinner("AI is anonymizing and extracting..."):
                    res = requests.post(f"{API_URL}/candidates/process", json={"raw_text": cand_text})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state["candidates"].append(data)
                        st.success(f"Candidate Anonymized & Processed! ID: {data['candidate_id']}")
                        st.json(data["profile"])
                    else:
                        st.error("Failed to process candidate.")

st.divider()
st.header("Step 3: Run Adaptive Ranking Engine")
if st.button("Generate Rankings", type="primary", use_container_width=True):
    if not st.session_state.get("job_id"):
        st.error("Please parse a Job Description first.")
    elif not st.session_state.get("candidates"):
        st.error("Please parse at least one candidate first.")
    else:
        with st.spinner("Calculating Semantic Matches, Growth Scores, and Checking for Stuffing..."):
            res = requests.post(f"{API_URL}/rank/{st.session_state['job_id']}")
            if res.status_code == 200:
                data = res.json()
                st.session_state["rankings"] = data["rankings"]
                st.success("Rankings Generated! Head to the Dashboard.")
            else:
                st.error("Failed to generate rankings.")
