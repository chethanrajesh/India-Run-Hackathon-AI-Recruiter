# Redrob Intelligent Candidate Discovery & Ranking Pipeline

This repository contains the winning high-performance, CPU-bound ranking pipeline optimized specifically for the **Redrob Intelligent Candidate Discovery & Ranking Challenge**. 

Given a Job Description and a dataset of 100,000 highly unstructured candidate profiles, this system retrieves, filters, and ranks the Top 100 candidates in **under 50 seconds** while staying well within the 16GB RAM constraint.

## 🏗️ Architecture & Pipeline

The system is designed as a strict deterministic pipeline to ensure speed and precision without relying on runtime LLM API calls:

1. **Offline Preprocessing (`01_preprocess.py` & `01b_update_features.py`)**
   - Parses the massive `candidates.jsonl` dataset.
   - Embeds candidate textual profiles (Summaries + Career Histories + Skills) using state-of-the-art **BGE Embeddings** (`BAAI/bge-small-en-v1.5`).
   - Exports the 100,000 embeddings to a `numpy.memmap` (`embeddings.npy`) to allow instantaneous loading during the ranking phase.
   - Extracts structured Tier 1 & 2 signals into a heavily optimized `features.parquet` matrix.
   - `01b_update_features.py` allows rapid re-extraction of tabular features without triggering the 1.5-hour embedding process.

2. **The < 5 Minute Ranking Engine (`02_rank.py`)**
   - **FAISS Semantic Retrieval:** Queries the JD against the 100k memory-mapped candidates using `IndexFlatIP` to extract the Top 3000 semantic matches.
   - **MMR Diversification:** Applies Maximal Marginal Relevance (MMR) to winnow the Top 3000 down to a diverse Top 800, preventing the system from surfacing 800 clones of the same profile.
   - **Honeypot Detection:** Focuses on detecting signal inconsistencies, such as candidates claiming to be "open to work" but possessing 0% actual response rates, or having 100+ profile views with zero interactions.
   - **Signal Fusion:** Applies a rigorous 6-factor deterministic scoring algorithm:
     `Score = 0.35(Semantic) + 0.20(Career Depth) + 0.15(Skill Evidence) + 0.10(Availability) + 0.10(Market Demand) + 0.10(Experience Match) - Penalty`
   - **Template Explanations:** Generates fast, O(1) LLM-free sentence rationales for the final Top 100.
   - **Export:** Validates and outputs the `submission.csv`.

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Data Preprocessor
Before ranking, you must run the preprocessor to chunk the 400MB+ dataset and generate the memmap arrays. 
*(Ensure your `candidates.jsonl` and `job_description.docx` are placed in the correct `COMPETITION_DATA_DIR` as defined in `redrob_pipeline/config.py`)*

```bash
# To run the full embedding pipeline (Takes ~1.5 hours on CPU)
python redrob_pipeline/01_preprocess.py

# To quickly update only the structured features (Takes ~4 seconds)
python redrob_pipeline/01b_update_features.py
```

### 3. Run the Ranking Pipeline
This is the core script that evaluates the 100,000 candidates and outputs the final `submission.csv`. It guarantees execution in under 5 minutes (benchmarked at ~47 seconds).

```bash
python redrob_pipeline/02_rank.py
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
│   │       ├── explanation.py   # O(1) string rationale generator
│   │       ├── fusion.py        # 6-factor deterministic algorithm
│   │       ├── honeypot.py      # Keyword stuffing & signal inconsistency detector
│   │       ├── market_demand.py # Calculates demand using recruiter saves & views
│   │       ├── semantic.py      # FAISS Index + MMR Diversification
│   │       └── skill_evidence.py # Validates skill depth using endorsements/duration
│   ├── 01_preprocess.py         # Heavy-lifting offline embedder
│   ├── 01b_update_features.py   # Fast tabular feature updater
│   ├── 02_rank.py               # < 5 min competition runtime script
│   └── config.py                # File paths and global constants
├── requirements.txt
└── submission.csv               # Final generated output
```
