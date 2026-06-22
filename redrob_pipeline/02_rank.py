import os
import time
import numpy as np
import pandas as pd
import docx2txt
from sentence_transformers import SentenceTransformer

from config import JD_DOCX, EMBEDDINGS_FILE, FEATURES_FILE, MODEL_NAME, EMBEDDING_DIM
from src.engines.semantic import create_faiss_index, retrieve_top_k, apply_mmr
from src.engines.fusion import compute_final_score
from src.engines.explanation import generate_explanation

def main():
    start_time = time.time()
    
    # 1. Load JD
    print("Loading JD...")
    jd_text = docx2txt.process(JD_DOCX)
    
    # 2. Embed JD
    print(f"Embedding JD using {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    instruction = "Represent this sentence for searching relevant passages: "
    jd_embedding = model.encode([instruction + jd_text], normalize_embeddings=True)[0]
    
    # 3. Load Memmap
    print("Loading Embeddings from memmap...")
    num_candidates = os.path.getsize(EMBEDDINGS_FILE) // (EMBEDDING_DIM * 4)
    memmap_embeddings = np.memmap(
        EMBEDDINGS_FILE, 
        dtype='float32', 
        mode='r', 
        shape=(num_candidates, EMBEDDING_DIM)
    )
    
    # 4. FAISS Search
    print("Building FAISS Index and searching Top 3000...")
    index = create_faiss_index(memmap_embeddings)
    top_3000_idx, top_3000_scores = retrieve_top_k(jd_embedding, index, k=3000)
    
    # 5. MMR Diversification
    print("Applying MMR to filter to Top 800...")
    top_3000_embeddings = memmap_embeddings[top_3000_idx]
    top_800_idx, top_800_scores = apply_mmr(
        jd_embedding, 
        top_3000_embeddings, 
        top_3000_idx, 
        top_3000_scores, 
        top_n=800, 
        lambda_param=0.5
    )
    
    # 6. Load Structured Features
    print("Loading candidate structured features...")
    df_features = pd.read_parquet(FEATURES_FILE)
    
    top_800_df = df_features.iloc[top_800_idx].copy()
    top_800_df['semantic_fit'] = top_800_scores
    
    # 7. Fusion
    print("Applying Signal Consistency & Fusion...")
    final_scores = []
    explanations = []
    
    for _, row in top_800_df.iterrows():
        # Assuming JD requires 5 years exp; this could be extracted dynamically
        score, components = compute_final_score(row.to_dict(), row['semantic_fit'], jd_years_required=5)
        final_scores.append(score)
        explanations.append(generate_explanation(components))
        
    top_800_df['final_score'] = final_scores
    top_800_df['explanation'] = explanations
    
    # 8. Sort and slice Top 100
    print("Selecting Top 100...")
    top_100_df = top_800_df.sort_values(by='final_score', ascending=False).head(100).copy()
    top_100_df['rank'] = range(1, 101)
    
    # 9. Submission
    submission_df = top_100_df[['rank', 'candidate_id', 'final_score', 'explanation']].rename(columns={'final_score': 'score'})
    
    submission_path = "submission.csv"
    submission_df.to_csv(submission_path, index=False)
    
    end_time = time.time()
    
    print(f"Successfully generated {submission_path}")
    print(f"Total time: {end_time - start_time:.2f} seconds")
    
if __name__ == "__main__":
    main()
