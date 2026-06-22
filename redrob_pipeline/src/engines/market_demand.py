def compute_market_demand(candidate_row):
    """
    Score based on recruiter interest and search appearances.
    """
    saved = candidate_row.get('saved_by_recruiters_30d', 0)
    search = candidate_row.get('search_appearance_30d', 0)
    views = candidate_row.get('profile_views_received_30d', 0)
    
    # Normalize with reasonable upper bounds for a 30-day window
    # e.g., max 20 saves, max 100 searches, max 200 views
    saved_norm = min(saved / 20.0, 1.0)
    search_norm = min(search / 100.0, 1.0)
    views_norm = min(views / 200.0, 1.0)
    
    # 0.4 * recruiter_saves + 0.3 * search_appearances + 0.3 * profile_views
    score = (0.4 * saved_norm) + (0.3 * search_norm) + (0.3 * views_norm)
    
    return min(score, 1.0)
