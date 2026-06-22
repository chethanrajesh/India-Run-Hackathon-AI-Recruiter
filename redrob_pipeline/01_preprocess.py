import os
import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from config import CANDIDATES_JSONL, DATA_DIR, EMBEDDINGS_FILE, FEATURES_FILE, MODEL_NAME, EMBEDDING_DIM

BATCH_SIZE = 256

def build_candidate_text(c):
    """
    Tier 1 & 2 semantic components concatenated into a dense chunk for BGE embeddings.
    """
    text_parts = []
    
    profile = c.get('profile', {})
    if profile.get('headline'):
        text_parts.append(f"Headline: {profile['headline']}")
    if profile.get('summary'):
        text_parts.append(f"Summary: {profile['summary']}")
        
    skills = c.get('skills', [])
    if skills:
        skill_names = [s.get('name', '') for s in skills if s.get('name')]
        text_parts.append(f"Skills: {', '.join(skill_names)}")
        
    career = c.get('career_history', [])
    for job in career:
        title = job.get('title', '')
        desc = job.get('description', '')
        if title or desc:
            text_parts.append(f"Role: {title}. Experience: {desc}")
            
    return " ".join(text_parts)

def extract_features(c):
    profile = c.get('profile', {})
    signals = c.get('redrob_signals', {})
    
    skill_scores = signals.get('skill_assessment_scores', {})
    avg_assessment_score = np.mean(list(skill_scores.values())) if skill_scores else 0.0
    
    return {
        'candidate_id': c.get('candidate_id'),
        'years_of_experience': profile.get('years_of_experience', 0),
        'last_active_date': signals.get('last_active_date', ''),
        'recruiter_response_rate': signals.get('recruiter_response_rate', 0.0),
        'open_to_work_flag': signals.get('open_to_work_flag', False),
        'saved_by_recruiters_30d': signals.get('saved_by_recruiters_30d', 0),
        'search_appearance_30d': signals.get('search_appearance_30d', 0),
        'notice_period_days': signals.get('notice_period_days', 90),
        'endorsements_received': signals.get('endorsements_received', 0),
        'avg_assessment_score': avg_assessment_score,
        'avg_response_time_hours': signals.get('avg_response_time_hours', 48.0),
        'raw_skills': json.dumps(c.get('skills', [])), 
        'raw_career': json.dumps(c.get('career_history', []))
    }

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print(f"Loading {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    print("Counting total candidates...")
    total_candidates = 0
    with open(CANDIDATES_JSONL, 'r', encoding='utf-8') as f:
        for _ in f:
            total_candidates += 1
            
    print(f"Total candidates: {total_candidates}")
    
    # Initialize memmap for instant loading during ranking
    memmap_embeddings = np.memmap(
        EMBEDDINGS_FILE, 
        dtype='float32', 
        mode='w+', 
        shape=(total_candidates, EMBEDDING_DIM)
    )
    
    features_list = []
    text_batch = []
    idx_batch = []
    
    with open(CANDIDATES_JSONL, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(tqdm(f, total=total_candidates, desc="Embedding Candidates")):
            c = json.loads(line)
            features_list.append(extract_features(c))
            text_batch.append(build_candidate_text(c))
            idx_batch.append(idx)
            
            if len(text_batch) >= BATCH_SIZE or idx == total_candidates - 1:
                # BGE embeddings
                embeddings = model.encode(text_batch, normalize_embeddings=True)
                
                for i, embedding in zip(idx_batch, embeddings):
                    memmap_embeddings[i] = embedding
                    
                text_batch = []
                idx_batch = []
                
    memmap_embeddings.flush()
    print(f"Saved memmap embeddings to {EMBEDDINGS_FILE}")
    
    df = pd.DataFrame(features_list)
    df.to_parquet(FEATURES_FILE, index=False)
    print(f"Saved feature matrix to {FEATURES_FILE}")

if __name__ == "__main__":
    main()
