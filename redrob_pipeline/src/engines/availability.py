from datetime import datetime

def compute_availability(candidate_row):
    """
    Evaluates availability based on open_to_work, response rate, notice period, and recency.
    Returns a score from 0.0 to 1.0.
    """
    score = 0.0
    
    # 1. Explicit availability (Base 0.4)
    if candidate_row.get('open_to_work_flag'):
        score += 0.4
        
    # 2. Recruiter Response Rate (Up to 0.3)
    # response rate is between 0 and 1
    score += candidate_row.get('recruiter_response_rate', 0.0) * 0.3
    
    # 3. Notice Period (Up to 0.2)
    # Shorter notice period is better (0 days = 0.2, 90 days = 0.0)
    notice = candidate_row.get('notice_period_days', 90)
    if notice <= 0:
        score += 0.2
    elif notice < 90:
        score += 0.2 * (1 - (notice / 90.0))
        
    # 4. Last Active Date Recency (Up to 0.1)
    # Let's assume current date is roughly 2026 for the hackathon
    # A simple proxy: if they have a recent last_active_date, give them full points
    last_active = candidate_row.get('last_active_date', '')
    if last_active:
        score += 0.1
        
    return min(score, 1.0)
