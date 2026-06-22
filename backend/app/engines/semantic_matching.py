import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Initialize Local Embedding Model
# using a fast, small model for the PoC
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Qdrant Client
try:
    qdrant = QdrantClient(host="localhost", port=6333, timeout=1.0)
    # Test connection to force an exception if not running
    qdrant.get_collections()
except Exception as e:
    print(f"Warning: Could not connect to Qdrant. Using in-memory. {e}")
    qdrant = QdrantClient(":memory:")

COLLECTION_NAME = "talent_graph"

def setup_collection():
    """Ensure the Qdrant collection exists."""
    try:
        collections = qdrant.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
    except Exception as e:
        print(f"Error setting up collection: {e}")

# Call it on module load
setup_collection()

def embed_text(text: str) -> List[float]:
    """Generates a dense vector for the given text."""
    return model.encode(text).tolist()

def store_job_vectors(job_id: str, required_skills: List[str], responsibilities: List[str]):
    """Stores job semantic vectors in Qdrant."""
    skills_text = " ".join(required_skills)
    resp_text = " ".join(responsibilities)
    
    vector = embed_text(f"Job Requirements: {skills_text}. Responsibilities: {resp_text}")
    
    point_id = str(uuid.uuid4())
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={"entity_type": "job", "job_id": job_id, "chunk_type": "core"}
            )
        ]
    )
    return point_id

def store_candidate_vectors(candidate_id: str, skills: List[str], experience: List[str]):
    """Stores candidate semantic vectors in Qdrant."""
    skills_text = " ".join(skills)
    exp_text = " ".join(experience)
    
    vector = embed_text(f"Candidate Skills: {skills_text}. Experience: {exp_text}")
    
    point_id = str(uuid.uuid4())
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={"entity_type": "candidate", "candidate_id": candidate_id, "chunk_type": "core"}
            )
        ]
    )
    return point_id

def calculate_semantic_similarity(job_text: str, candidate_text: str) -> float:
    """
    Utility to calculate raw cosine similarity between two strings.
    Used by the Ranking Engine for real-time scoring if not querying DB directly.
    """
    from numpy import dot
    from numpy.linalg import norm
    
    v1 = embed_text(job_text)
    v2 = embed_text(candidate_text)
    
    cos_sim = dot(v1, v2)/(norm(v1)*norm(v2))
    # Normalize to 0-100 score (assuming vectors are generally positive or shifting)
    # Cosine is -1 to 1. Usually text embeddings are > 0.
    return float(max(0, cos_sim) * 100)
