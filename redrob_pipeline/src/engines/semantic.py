import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def create_faiss_index(embeddings):
    """
    Creates a FAISS IndexFlatIP (Inner Product = Cosine Sim since embeddings are normalized).
    """
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(embeddings)
    return index

def retrieve_top_k(query_embedding, index, k=3000):
    """
    Retrieves Top K indices and scores from FAISS.
    """
    scores, indices = index.search(query_embedding.reshape(1, -1), k)
    return indices[0], scores[0]

def apply_mmr(query_embedding, candidate_embeddings, candidate_indices, candidate_scores, top_n=800, lambda_param=0.5):
    """
    Applies Maximal Marginal Relevance (MMR) to diversify the results.
    """
    if len(candidate_indices) <= top_n:
        return candidate_indices, candidate_scores
        
    selected_indices = []
    selected_scores = []
    
    # Precompute similarities between all candidates to speed up MMR
    # For large sets (e.g. 3000), this is 3000x3000 which is 9M floats (~36MB RAM), completely fine.
    sim_matrix = cosine_similarity(candidate_embeddings)
    
    unselected = list(range(len(candidate_indices)))
    
    # Select the first candidate (highest semantic score)
    best_idx = unselected.pop(0)
    selected_indices.append(candidate_indices[best_idx])
    selected_scores.append(candidate_scores[best_idx])
    
    selected_local_idx = [best_idx]
    
    while len(selected_indices) < top_n and unselected:
        best_score = -np.inf
        best_candidate = -1
        
        for i in unselected:
            # Query similarity is already computed by FAISS
            sim_q = candidate_scores[i]
            
            # Max similarity to already selected candidates
            sim_selected = np.max(sim_matrix[i, selected_local_idx])
            
            # MMR Equation
            mmr_score = (lambda_param * sim_q) - ((1 - lambda_param) * sim_selected)
            
            if mmr_score > best_score:
                best_score = mmr_score
                best_candidate = i
                
        # Add the best candidate to selected
        unselected.remove(best_candidate)
        selected_indices.append(candidate_indices[best_candidate])
        selected_scores.append(candidate_scores[best_candidate])
        selected_local_idx.append(best_candidate)
        
    return np.array(selected_indices), np.array(selected_scores)
