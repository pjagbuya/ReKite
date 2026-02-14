from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime
from database import get_db
from models import User, Deck, Card, UserCardProgress, Review
from schemas import (
    NextCardResponse, CardResponse, TranscriptionRequest, TranscriptionResponse,
    SimilarityRequest, SimilarityResponse, ReviewSubmit, ReviewResponse
)
from auth_utils import get_current_user
from deepgram_utils import transcribe_audio
from sbert_utils import evaluate_answer
from spaced_repetition import calculate_next_review
import random

router = APIRouter()

@router.get("/card/{card_id}", response_model=CardResponse)
def get_single_card_for_study(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single card for study"""
    # Get the card
    card = db.query(Card).filter(Card.id == card_id).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Verify deck ownership
    deck = db.query(Deck).filter(
        Deck.id == card.deck_id,
        Deck.user_id == current_user.id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get or create progress
    progress = db.query(UserCardProgress).filter(
        UserCardProgress.card_id == card_id,
        UserCardProgress.user_id == current_user.id
    ).first()
    
    if not progress:
        progress = UserCardProgress(
            user_id=current_user.id,
            card_id=card_id,
            ease_factor=2.5,
            interval=0,
            repetitions=0,
            next_review=datetime.utcnow()
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    return CardResponse(
        id=card.id,
        deck_id=card.deck_id,
        concept=card.concept,
        definition=card.definition,
        created_at=card.created_at,
        updated_at=card.updated_at,
        next_review=progress.next_review
    )

@router.get("/deck/{deck_id}/next", response_model=NextCardResponse)
def get_next_card_for_review(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the next card due for review in a deck"""
    # Verify deck ownership
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Find cards that are due for review
    now = datetime.utcnow()
    cards_query = db.query(Card, UserCardProgress).join(
        UserCardProgress,
        and_(
            Card.id == UserCardProgress.card_id,
            UserCardProgress.user_id == current_user.id
        )
    ).filter(
        Card.deck_id == deck_id,
        UserCardProgress.next_review <= now
    ).order_by(UserCardProgress.next_review.asc())
    
    card_progress_pair = cards_query.first()
    
    # Count total cards due
    total_due = cards_query.count()
    
    if not card_progress_pair:
        return NextCardResponse(
            card=None,
            deck_name=deck.name,
            cards_remaining=0
        )
    
    card, progress = card_progress_pair
    
    # Prepare card response
    card_response = CardResponse(
        id=card.id,
        deck_id=card.deck_id,
        concept=card.concept,
        definition=card.definition,
        created_at=card.created_at,
        updated_at=card.updated_at,
        next_review=progress.next_review
    )
    
    return NextCardResponse(
        card=card_response,
        deck_name=deck.name,
        cards_remaining=total_due
    )

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_speech(
    request: TranscriptionRequest,
    current_user: User = Depends(get_current_user)
):
    """Transcribe audio to text using Deepgram"""
    try:
        transcript, confidence = transcribe_audio(request.audio_base64)
        
        return TranscriptionResponse(
            transcript=transcript,
            confidence=confidence
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )

@router.post("/evaluate", response_model=SimilarityResponse)
def evaluate_similarity(
    request: SimilarityRequest,
    current_user: User = Depends(get_current_user)
):
    """Evaluate semantic similarity between user answer and correct definition"""
    try:
        similarity_score, matched_keywords, highlighted_user, highlighted_def = evaluate_answer(
            request.user_answer,
            request.correct_definition
        )
        
        return SimilarityResponse(
            similarity_score=similarity_score,
            matched_keywords=matched_keywords,
            highlighted_user_answer=highlighted_user,
            highlighted_definition=highlighted_def
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )

@router.post("/review", response_model=ReviewResponse)
def submit_review(
    review: ReviewSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a review for a card and update spaced repetition data"""
    # Get the card and verify access
    card = db.query(Card).filter(Card.id == review.card_id).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Verify deck ownership
    deck = db.query(Deck).filter(
        Deck.id == card.deck_id,
        Deck.user_id == current_user.id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Evaluate the answer
    similarity_score, matched_keywords, _, _ = evaluate_answer(
        review.user_answer,
        card.definition
    )
    
    # Get or create progress
    progress = db.query(UserCardProgress).filter(
        UserCardProgress.card_id == review.card_id,
        UserCardProgress.user_id == current_user.id
    ).first()
    
    if not progress:
        progress = UserCardProgress(
            user_id=current_user.id,
            card_id=review.card_id,
            ease_factor=2.5,
            interval=0,
            repetitions=0
        )
        db.add(progress)
    
    # Calculate next review using spaced repetition algorithm
    new_ease, new_interval, new_reps, next_review = calculate_next_review(
        quality=review.quality,
        ease_factor=progress.ease_factor,
        interval=progress.interval,
        repetitions=progress.repetitions
    )
    
    # Update progress
    progress.ease_factor = new_ease
    progress.interval = new_interval
    progress.repetitions = new_reps
    progress.next_review = next_review
    progress.last_reviewed = datetime.utcnow()
    
    # Create review record
    db_review = Review(
        card_id=review.card_id,
        user_id=current_user.id,
        user_answer=review.user_answer,
        similarity_score=similarity_score,
        quality=review.quality
    )
    db.add(db_review)
    
    db.commit()
    db.refresh(db_review)
    
    return ReviewResponse(
        id=db_review.id,
        card_id=db_review.card_id,
        similarity_score=similarity_score,
        quality=review.quality,
        matched_keywords=matched_keywords,
        reviewed_at=db_review.reviewed_at
    )

@router.delete("/progress/card/{card_id}")
def reset_card_progress(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset progress for a specific card"""
    # Verify card exists and user has access
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    deck = db.query(Deck).filter(
        Deck.id == card.deck_id,
        Deck.user_id == current_user.id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Reset progress
    progress = db.query(UserCardProgress).filter(
        UserCardProgress.card_id == card_id,
        UserCardProgress.user_id == current_user.id
    ).first()
    
    if progress:
        progress.ease_factor = 2.5
        progress.interval = 0
        progress.repetitions = 0
        progress.next_review = datetime.utcnow()
        progress.last_reviewed = None
        db.commit()
    
    return {"message": "Card progress reset successfully"}

@router.delete("/progress/deck/{deck_id}")
def reset_deck_progress(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset progress for all cards in a deck"""
    # Verify deck ownership
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Get all cards in the deck
    card_ids = db.query(Card.id).filter(Card.deck_id == deck_id).all()
    card_ids = [card_id[0] for card_id in card_ids]
    
    # Reset progress for all cards
    progress_records = db.query(UserCardProgress).filter(
        UserCardProgress.card_id.in_(card_ids),
        UserCardProgress.user_id == current_user.id
    ).all()
    
    for progress in progress_records:
        progress.ease_factor = 2.5
        progress.interval = 0
        progress.repetitions = 0
        progress.next_review = datetime.utcnow()
        progress.last_reviewed = None
    
    db.commit()
    
    return {"message": f"Reset progress for {len(progress_records)} cards"}

@router.post("/paraphrase")
def generate_paraphrases(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Generate paraphrased versions of a definition"""
    definition = request.get("definition", "")
    
    if not definition:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Definition is required"
        )
    
    # Generate paraphrases using templates and word variations
    paraphrases = _generate_paraphrases(definition)
    
    return {"paraphrases": paraphrases}

def _generate_paraphrases(text: str) -> List[str]:
    """Generate simple paraphrased versions of text"""
    paraphrases = []
    
    # Template 1: Start with "In other words,"
    paraphrases.append(f"In other words, {text.lower()}")
    
    # Template 2: Start with "Simply put,"
    paraphrases.append(f"Simply put, {text.lower()}")
    
    # Template 3: Start with "This refers to"
    paraphrases.append(f"This refers to {text.lower()}")
    
    # Template 4: Start with "It can be described as"
    paraphrases.append(f"It can be described as {text.lower()}")
    
    # Template 5: Start with "Essentially,"
    paraphrases.append(f"Essentially, {text.lower()}")
    
    # Shuffle and return random 5
    random.shuffle(paraphrases)
    return paraphrases[:5]
