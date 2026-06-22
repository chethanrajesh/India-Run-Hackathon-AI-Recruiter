import json
import re

def compute_career_evidence(candidate_row):
    """
    Evaluate depth and relevance of career history, specifically looking for:
    - Role progression
    - Product-company experience
    - Retrieval/search experience
    - Ranking/recommendation systems
    - Production deployment evidence
    """
    try:
        career = json.loads(candidate_row.get('raw_career', '[]'))
    except:
        career = []
        
    if not career:
        return 0.0
        
    score = 0.0
    num_roles = len(career)
    
    # Text aggregation for regex search
    all_descriptions = " ".join([c.get('description', '').lower() for c in career])
    all_titles = " ".join([c.get('title', '').lower() for c in career])
    
    # 1. Role progression (0.2)
    # Check if they went from Junior/Engineer -> Senior/Lead/Principal
    progression = False
    has_senior = 'senior' in all_titles or 'lead' in all_titles or 'principal' in all_titles or 'staff' in all_titles
    if has_senior and num_roles > 1:
        progression = True
    if progression:
        score += 0.2
        
    # 2. Product-company experience (0.2)
    product_keywords = ['product', 'saas', 'platform', 'b2b', 'b2c', 'user base']
    if any(k in all_descriptions for k in product_keywords):
        score += 0.2
        
    # 3. Retrieval/Search experience (0.2)
    search_keywords = ['retrieval', 'search', 'elasticsearch', 'solr', 'vector', 'faiss', 'qdrant', 'pinecone']
    if any(k in all_descriptions or k in all_titles for k in search_keywords):
        score += 0.2
        
    # 4. Ranking/Recommendation systems (0.2)
    ranking_keywords = ['ranking', 'recommendation', 'recsys', 'personalization', 'ltr', 'learning to rank']
    if any(k in all_descriptions or k in all_titles for k in ranking_keywords):
        score += 0.2
        
    # 5. Production deployment evidence (0.2)
    prod_keywords = ['production', 'deployment', 'scale', 'latency', 'kubernetes', 'k8s', 'docker', 'aws', 'gcp', 'pipeline']
    if any(k in all_descriptions for k in prod_keywords):
        score += 0.2
        
    return min(score, 1.0)
