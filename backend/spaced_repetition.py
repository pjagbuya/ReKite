from datetime import datetime, timedelta
from typing import Tuple

def calculate_next_review(
    quality: int,
    ease_factor: float,
    interval: int,
    repetitions: int
) -> Tuple[float, int, int, datetime]:
    """
    Calculate next review parameters using SM-2 spaced repetition algorithm
    
    Args:
        quality: Quality of response (0=Again, 1=Hard, 2=Normal, 3=Easy)
        ease_factor: Current ease factor (default 2.5)
        interval: Current interval in days
        repetitions: Number of successful repetitions
        
    Returns:
        Tuple of (new_ease_factor, new_interval, new_repetitions, next_review_date)
    """
    # Convert quality to SM-2 scale (0-5)
    # 0=Again -> 0, 1=Hard -> 2, 2=Normal -> 3, 3=Easy -> 5
    quality_map = {
        0: 0,  # Again (complete failure)
        1: 2,  # Hard (difficult)
        2: 3,  # Normal (hesitant)
        3: 5   # Easy (perfect)
    }
    sm2_quality = quality_map.get(quality, 3)
    
    # Calculate new ease factor
    new_ease_factor = ease_factor + (0.1 - (5 - sm2_quality) * (0.08 + (5 - sm2_quality) * 0.02))
    
    # Ensure ease factor doesn't go below 1.3
    new_ease_factor = max(1.3, new_ease_factor)
    
    # Calculate new interval and repetitions
    if sm2_quality < 3:  # Failed (Again or Hard)
        new_repetitions = 0
        new_interval = 1  # Review again tomorrow
    else:  # Passed (Normal or Easy)
        new_repetitions = repetitions + 1
        
        if new_repetitions == 1:
            new_interval = 1  # First successful review: 1 day
        elif new_repetitions == 2:
            new_interval = 6  # Second successful review: 6 days
        else:
            # Subsequent reviews: multiply previous interval by ease factor
            new_interval = int(interval * new_ease_factor)
    
    # Adjust interval based on quality for fine-tuning
    if quality == 1:  # Hard
        new_interval = max(1, int(new_interval * 0.5))  # Reduce interval by half
    elif quality == 3:  # Easy
        new_interval = max(1, int(new_interval * 1.3))  # Increase interval by 30%
    
    # Calculate next review date
    next_review_date = datetime.utcnow() + timedelta(days=new_interval)
    
    return new_ease_factor, new_interval, new_repetitions, next_review_date

def get_quality_from_similarity(similarity_score: float) -> int:
    """
    Suggest a quality rating based on similarity score
    User can override this
    
    Args:
        similarity_score: Similarity score from 0.0 to 1.0
        
    Returns:
        Suggested quality (0-3)
    """
    if similarity_score >= 0.85:
        return 3  # Easy
    elif similarity_score >= 0.70:
        return 2  # Normal
    elif similarity_score >= 0.50:
        return 1  # Hard
    else:
        return 0  # Again
