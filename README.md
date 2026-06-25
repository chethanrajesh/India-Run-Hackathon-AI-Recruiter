# Redrob Intelligent Candidate Discovery & Ranking Pipeline

This repository contains the winning high-performance, CPU-bound ranking pipeline optimized specifically for the **Redrob Intelligent Candidate Discovery & Ranking Challenge**. 

Given a Job Description and a dataset of 100,000 highly unstructured candidate profiles, this system retrieves, filters, and ranks the Top 100 candidates in **under 45 seconds** while staying well within the 16GB RAM constraint.

## 🏗️ Architecture & Pipeline

The system is designed as a strict deterministic pipeline to ensure speed and precision without relying on runtime LLM API calls:

1. **Offline Preprocessing (`01_preprocess.py` & `01b_update_features.py`)**
   - Parses the massive `candidates.jsonl` dataset.
   - Embeds candidate textual profiles (Summaries + Career Histories + Skills) using state-of-the-art **BGE Embeddings** (`BAAI/bge-small-en-v1.5`).
   - Exports the 100,000 embeddings to a `numpy.memmap` (`embeddings.npy`) to allow instantaneous loading during the ranking phase.
   - Extracts structured Tier 1 & 2 signals into a heavily optimized `features.parquet` matrix.
   - *Note: Precomputation happens offline. `01b_update_features.py` allows rapid re-extraction of tabular features without triggering the 1.5-hour embedding process.*

2. **The < 5 Minute Ranking Engine (`rank.py` / `rank_engine.py`)**
   - **FAISS Semantic Retrieval:** Queries the JD against the 100k memory-mapped candidates using `IndexFlatIP` to extract the Top 3000 semantic matches.
   - **MMR Diversification:** Applies Maximal Marginal Relevance (MMR) to winnow the Top 3000 down to a diverse Top 800, preventing the system from surfacing 800 clones of the same profile.
   - **Honeypot Detection:** Focuses on detecting signal inconsistencies, such as candidates claiming to be "open to work" but possessing 0% actual response rates, or having 100+ profile views with zero interactions.
   - **Signal Fusion:** Applies a rigorous 6-factor deterministic scoring algorithm:
     `Score = 0.35(Semantic) + 0.20(Career Depth) + 0.15(Skill Evidence) + 0.10(Availability) + 0.10(Market Demand) + 0.10(Experience Match) - Penalty`
   - **Dynamic Reasoning Generator:** Dynamically generates fact-based (no-hallucination) sentence rationales by explicitly extracting actual skills, notice periods, and experience from the candidate's JSON profile.

## 🚀 How to Run (Stage 3 Reproduction)

For Stage 3 evaluation, you can run the ranking engine using the single unified CLI command below. 
*(Note: This requires the `embeddings.npy` and `features.parquet` to have been pre-computed using `01_preprocess.py` first, as permitted by the pre-computation guidelines.)*

```bash
python rank.py --candidates ./India_runs_data_and_ai_challenge/candidates.jsonl --jd ./India_runs_data_and_ai_challenge/job_description.docx --out ./The-Big-OOPs.csv
```

### Pre-computation (If dataset changes)
If a new `candidates.jsonl` is provided for evaluation, you must generate the memmap features first (takes ~1.5 hours on CPU):
```bash
python redrob_pipeline/01_preprocess.py
```

## 🐳 Docker Sandbox (Stage 10.5 Requirement)

To satisfy the sandboxing requirement, a `Dockerfile` is included at the root. It packages the entire environment and pre-downloads the BGE embedding weights to satisfy the strictly offline network constraint.

```bash
# Build the image
docker build -t redrob-ranker .

# Run the container (Mounting your local data directory)
docker run -v $(pwd)/India_runs_data_and_ai_challenge:/app/data redrob-ranker --candidates /app/data/candidates.jsonl --jd /app/data/job_description.docx --out /app/The-Big-OOPs.csv
```

## 📂 Project Structure

```text
India/
├── redrob_pipeline/
│   ├── data/
│   │   └── processed/           # Auto-generated .npy memmap and .parquet features
│   ├── src/
│   │   └── engines/
│   │       ├── availability.py  # Evaluates response rates & notice period
│   │       ├── career_evidence.py # Evaluates role progression & product/search experience
│   │       ├── explanation.py   # Dynamic fact-extracting rationale generator
│   │       ├── fusion.py        # 6-factor deterministic algorithm
│   │       ├── honeypot.py      # Keyword stuffing & signal inconsistency detector
│   │       ├── market_demand.py # Calculates demand using recruiter saves & views
│   │       ├── semantic.py      # FAISS Index + MMR Diversification
│   │       └── skill_evidence.py # Validates skill depth using endorsements/duration
│   ├── 01_preprocess.py         # Heavy-lifting offline embedder
│   ├── 01b_update_features.py   # Fast tabular feature updater
│   ├── rank_engine.py           # Core ranking logic
│   └── config.py                # Environment-variable driven configuration
├── Dockerfile                   # Isolated Sandbox Container
├── rank.py                      # Stage 3 Unified CLI entrypoint
├── requirements.txt
├── submission_metadata.yaml     # Portal Metadata Template
└── The-Big-OOPs.csv             # Final generated output
```
