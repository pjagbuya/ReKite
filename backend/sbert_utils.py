from sentence_transformers import SentenceTransformer, util
from typing import List, Tuple
import re

# Load model once at module level for efficiency
model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast and efficient model

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate semantic similarity between two texts using Sentence-BERT
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        float: Similarity score between 0.0 and 1.0
    """
    # Encode texts using SBERT
    embeddings = model.encode([text1, text2], convert_to_tensor=True)
    
    # Calculate cosine similarity
    similarity = util.cos_sim(embeddings[0], embeddings[1])
    
    # Convert to float and ensure range [0, 1]
    score = float(similarity.item())
    return max(0.0, min(1.0, score))

def extract_keywords(text: str) -> List[str]:
    """
    Extract important keywords from text (simple implementation)
    Filters out common stop words and short words
    
    Args:
        text: Input text
        
    Returns:
        List of keywords
    """
    # Common stop words to exclude
    stop_words = {
        'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'of', 'in', 'to', 'for',
        'with', 'on', 'at', 'from', 'by', 'about', 'as', 'into', 'through',
        'during', 'before', 'after', 'above', 'below', 'between', 'under',
        'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
        'why', 'how', 'all', 'both', 'each', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
        'than', 'too', 'very', 'that', 'which', 'who', 'and', 'but', 'or',
        'if', 'because', 'while', 'it', 'its', 'this', 'these', 'those'
    }
    
    # Convert to lowercase, split into words, remove punctuation
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    # Filter keywords (length > 3, not stop words)
    keywords = [w for w in words if len(w) > 3 and w not in stop_words]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)
    
    return unique_keywords

def find_matched_keywords(user_answer: str, correct_definition: str) -> List[str]:
    """
    Find keywords that appear in both texts (case-insensitive)
    
    Args:
        user_answer: User's transcribed answer
        correct_definition: Correct definition
        
    Returns:
        List of matched keywords
    """
    user_keywords = set(extract_keywords(user_answer))
    correct_keywords = set(extract_keywords(correct_definition))
    
    # Find intersection
    matched = list(user_keywords.intersection(correct_keywords))
    return sorted(matched)

def highlight_keywords(text: str, keywords: List[str]) -> str:
    """
    Highlight keywords in text with HTML markup
    
    Args:
        text: Original text
        keywords: List of keywords to highlight
        
    Returns:
        Text with highlighted keywords
    """
    if not keywords:
        return text
    
    highlighted_text = text
    
    # Sort keywords by length (longest first) to avoid partial matches
    sorted_keywords = sorted(keywords, key=len, reverse=True)
    
    for keyword in sorted_keywords:
        # Use word boundaries for whole word matching (case-insensitive)
        pattern = re.compile(r'\b(' + re.escape(keyword) + r')\b', re.IGNORECASE)
        highlighted_text = pattern.sub(r'<mark>\1</mark>', highlighted_text)
    
    return highlighted_text

def evaluate_answer(user_answer: str, correct_definition: str) -> Tuple[float, List[str], str, str]:
    """
    Evaluate user's answer against correct definition
    
    Args:
        user_answer: User's transcribed answer
        correct_definition: Correct definition
        
    Returns:
        Tuple of (similarity_score, matched_keywords, highlighted_user_answer, highlighted_definition)
    """
    # Calculate semantic similarity
    similarity_score = calculate_similarity(user_answer, correct_definition)
    
    # Find matched keywords
    matched_keywords = find_matched_keywords(user_answer, correct_definition)
    
    # Highlight keywords in both texts
    highlighted_user = highlight_keywords(user_answer, matched_keywords)
    highlighted_definition = highlight_keywords(correct_definition, matched_keywords)
    
    return similarity_score, matched_keywords, highlighted_user, highlighted_definition
