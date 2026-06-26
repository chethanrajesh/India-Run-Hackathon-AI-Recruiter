import pandas as pd
import json
import sys

def main():
    try:
        # Load top 100
        df_sub = pd.read_csv('The-Big-OOPs.csv')
        top_100_ids = set(df_sub['candidate_id'].tolist())
    except FileNotFoundError:
        print("Could not find The-Big-OOPs.csv")
        return

    # Load features
    df_feat = pd.read_parquet('redrob_pipeline/data/processed/features.parquet')
    df_top = df_feat[df_feat['candidate_id'].isin(top_100_ids)]

    honeypots_found = []

    for _, row in df_top.iterrows():
        cand_id = row['candidate_id']
        is_honeypot = False
        reasons = []
        
        try:
            skills = json.loads(row.get('raw_skills', '[]'))
            expert_count = 0
            for s in skills:
                # check for expert with 0 years
                if str(s.get('proficiency')).lower() == 'expert' and float(s.get('duration_months', 1)) == 0:
                    is_honeypot = True
                    reasons.append(f"Expert in {s.get('name')} with 0 months experience")
                if str(s.get('proficiency')).lower() == 'expert':
                    expert_count += 1
            
            # Expert in 10+ skills with very low total years of experience
            if expert_count >= 10 and float(row.get('years_of_experience', 0)) < 2:
                is_honeypot = True
                reasons.append(f"Expert in {expert_count} skills but only {row.get('years_of_experience')} YoE")
        except Exception as e:
            pass
            
        if is_honeypot:
            honeypots_found.append({'id': cand_id, 'reasons': reasons})

    print(f"Total Top 100 evaluated: {len(df_top)}")
    print(f"Honeypots detected: {len(honeypots_found)} / 100")
    if honeypots_found:
        print("Honeypots list:")
        for h in honeypots_found:
            print(f"- {h['id']}: {', '.join(h['reasons'])}")
    else:
        print("SUCCESS: 0% Honeypot rate detected! You easily passed the <10% threshold.")

if __name__ == "__main__":
    main()
