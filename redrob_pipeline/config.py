import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# Paths to the competition dataset
COMPETITION_DATA_DIR = os.environ.get("REDROB_COMPETITION_DATA_DIR", r"D:\Projects\India Run Hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge")
CANDIDATES_JSONL = os.environ.get("REDROB_CANDIDATES_JSONL", os.path.join(COMPETITION_DATA_DIR, "candidates.jsonl"))
JD_DOCX = os.environ.get("REDROB_JD_DOCX", os.path.join(COMPETITION_DATA_DIR, "job_description.docx"))

# Output files
EMBEDDINGS_FILE = os.path.join(DATA_DIR, "embeddings.npy")
FEATURES_FILE = os.path.join(DATA_DIR, "features.parquet")

MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIM = 384
