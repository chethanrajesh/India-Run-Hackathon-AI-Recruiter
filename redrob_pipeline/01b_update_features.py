import json
import numpy as np
import pandas as pd
from tqdm import tqdm

from config import CANDIDATES_JSONL, FEATURES_FILE

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
        'profile_views_received_30d': signals.get('profile_views_received_30d', 0),
        'notice_period_days': signals.get('notice_period_days', 90),
        'endorsements_received': signals.get('endorsements_received', 0),
        'avg_assessment_score': avg_assessment_score,
        'avg_response_time_hours': signals.get('avg_response_time_hours', 48.0),
        'raw_skills': json.dumps(c.get('skills', [])), 
        'raw_career': json.dumps(c.get('career_history', []))
    }

def main():
    print("Extracting features (skipping embeddings)...")
    
    features_list = []
    
    with open(CANDIDATES_JSONL, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="Processing Candidates"):
            c = json.loads(line)
            features_list.append(extract_features(c))
                
    df = pd.DataFrame(features_list)
    df.to_parquet(FEATURES_FILE, index=False)
    print(f"Saved updated feature matrix to {FEATURES_FILE}")

if __name__ == "__main__":
    main()
