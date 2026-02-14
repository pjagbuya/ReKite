from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Deck, Card
from schemas import DeckCreate, DeckUpdate, DeckResponse
from auth_utils import get_current_user

router = APIRouter()

@router.get("/", response_model=List[DeckResponse])
def get_user_decks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all decks for the current user"""
    decks = db.query(Deck).filter(Deck.user_id == current_user.id).all()
    
    # Add card count to each deck
    for deck in decks:
        deck.card_count = db.query(Card).filter(Card.deck_id == deck.id).count()
    
    return decks

@router.post("/", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
def create_deck(
    deck: DeckCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new deck"""
    db_deck = Deck(
        user_id=current_user.id,
        name=deck.name,
        description=deck.description
    )
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    
    db_deck.card_count = 0
    return db_deck

@router.get("/{deck_id}", response_model=DeckResponse)
def get_deck(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific deck"""
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    deck.card_count = db.query(Card).filter(Card.deck_id == deck.id).count()
    return deck

@router.put("/{deck_id}", response_model=DeckResponse)
def update_deck(
    deck_id: int,
    deck_update: DeckUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a deck"""
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    if deck_update.name is not None:
        deck.name = deck_update.name
    if deck_update.description is not None:
        deck.description = deck_update.description
    
    db.commit()
    db.refresh(deck)
    
    deck.card_count = db.query(Card).filter(Card.deck_id == deck.id).count()
    return deck

@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a deck"""
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    db.delete(deck)
    db.commit()
    return None
