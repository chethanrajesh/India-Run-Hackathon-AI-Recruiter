# Redrob Intelligent Candidate Discovery & Ranking Pipeline

This repository contains the high-performance, CPU-bound ranking pipeline optimized specifically for the **Redrob Intelligent Candidate Discovery & Ranking Challenge**. 

Given a Job Description and a dataset of 100,000 highly unstructured candidate profiles, this system retrieves, filters, and ranks the Top 100 candidates in **under 45 seconds** while staying strictly within the 16GB RAM constraint.

## 📋 Prerequisites

Before running this project on a clean machine, ensure you have the following installed:
- **Python 3.10+**
- **Git**
- **pip**

Install all required Python dependencies:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Runtime Separation

To strictly comply with the < 5 minute runtime limit during ranking, our system architecture is split into two distinct phases:

### 1. Offline Preprocessing (Feature & Vector Extraction)
If a new `candidates.jsonl` is provided for evaluation, you must first generate the memory-mapped features. This step parses the 100k JSON records and generates BGE embeddings. (Takes ~1.5 hours on CPU).
```bash
python redrob_pipeline/01_preprocess.py
```

### 2. Online Ranking (< 5 min)
Once the offline preprocessing is complete, the actual ranking step executes in **~42 seconds**, easily clearing the 5-minute limit.

---

## Single Reproduction Command (Stage 3)

For Stage 3 evaluation, run the ranking engine using this single unified CLI command. *(Note: Ensure the offline preprocessing step has already run to generate the embeddings).*

```bash
python rank.py \
  --candidates ./candidates.jsonl \
  --jd ./job_description.docx \
  --out ./The-Big-OOPs.csv
```
*(You can pass any path to `--candidates` and `--jd`)*

---

## Docker Sandbox (Stage 10.5 Requirement)

To satisfy the **Sandbox / Demo link requirement**, we have included a self-contained Docker recipe as an acceptable sandbox alternative (as per Section 10.5 of the spec). The `Dockerfile` packages the environment and pre-downloads the model weights to guarantee the network remains entirely **Off** during ranking.

You can verify the sandbox using these exact commands:

```bash
# 1. Build the image
docker build -t redrob-ranker .

# 2. Run the container
docker run -v $(pwd):/app/data redrob-ranker \
  --candidates /app/data/candidates.jsonl \
  --jd /app/data/job_description.docx \
  --out /app/data/The-Big-OOPs.csv
```

---

##  Output Format Compliance

Our pipeline guarantees the output strictly follows the required format and ordering:
1. `candidate_id`: The ID from candidates.jsonl.
2. `rank`: Int (1-100).
3. `score`: Float (monotonically non-increasing).
4. `reasoning`: Dynamic, fact-based rationale generation that explicitly avoids hallucination by parsing actual skills and experience from the raw JSON profile.

---

##  Submission Metadata

The required **`submission_metadata.yaml`** is located at the root of the repository, containing all declared AI tools, team member information, and methodology summaries.

---

##  Project Structure

```text
India/
├── redrob_pipeline/
│   ├── data/
│   │   └── processed/           # Auto-generated .npy memmap and .parquet features
│   ├── src/
│   │   └── engines/             # Custom heuristics (fusion, honeypot, career_evidence, etc.)
│   ├── 01_preprocess.py         # Heavy-lifting offline embedder
│   ├── rank_engine.py           # Core ranking logic
│   └── config.py                # Environment-variable driven configuration
├── Dockerfile                   # Isolated Docker Sandbox
├── rank.py                      # Stage 3 Unified CLI entrypoint
├── requirements.txt             # Dependency list
├── submission_metadata.yaml     # Portal Metadata
└── The-Big-OOPs.csv             # Final generated output
```
