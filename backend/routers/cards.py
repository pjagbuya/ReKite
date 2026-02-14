from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Deck, Card, UserCardProgress
from schemas import CardCreate, CardUpdate, CardResponse
from auth_utils import get_current_user
from datetime import datetime

router = APIRouter()

@router.get("/deck/{deck_id}", response_model=List[CardResponse])
def get_deck_cards(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all cards for a specific deck"""
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
    
    cards = db.query(Card).filter(Card.deck_id == deck_id).all()
    
    # Add next_review info from UserCardProgress
    for card in cards:
        progress = db.query(UserCardProgress).filter(
            UserCardProgress.card_id == card.id,
            UserCardProgress.user_id == current_user.id
        ).first()
        card.next_review = progress.next_review if progress else None
    
    return cards

@router.post("/", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
def create_card(
    card: CardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new card"""
    # Verify deck ownership
    deck = db.query(Deck).filter(
        Deck.id == card.deck_id,
        Deck.user_id == current_user.id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    db_card = Card(
        deck_id=card.deck_id,
        concept=card.concept,
        definition=card.definition
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    
    # Initialize progress for this card
    progress = UserCardProgress(
        user_id=current_user.id,
        card_id=db_card.id,
        next_review=datetime.utcnow()  # Available immediately
    )
    db.add(progress)
    db.commit()
    
    db_card.next_review = progress.next_review
    return db_card

@router.get("/{card_id}", response_model=CardResponse)
def get_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific card"""
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Add next_review info
    progress = db.query(UserCardProgress).filter(
        UserCardProgress.card_id == card.id,
        UserCardProgress.user_id == current_user.id
    ).first()
    card.next_review = progress.next_review if progress else None
    
    return card

@router.put("/{card_id}", response_model=CardResponse)
def update_card(
    card_id: int,
    card_update: CardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a card"""
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    if card_update.concept is not None:
        card.concept = card_update.concept
    if card_update.definition is not None:
        card.definition = card_update.definition
    
    db.commit()
    db.refresh(card)
    
    # Add next_review info
    progress = db.query(UserCardProgress).filter(
        UserCardProgress.card_id == card.id,
        UserCardProgress.user_id == current_user.id
    ).first()
    card.next_review = progress.next_review if progress else None
    
    return card

@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a card"""
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    db.delete(card)
    db.commit()
    return None
