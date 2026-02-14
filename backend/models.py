from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    decks = relationship("Deck", back_populates="user", cascade="all, delete-orphan")
    card_progress = relationship("UserCardProgress", back_populates="user", cascade="all, delete-orphan")

class Deck(Base):
    __tablename__ = "decks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="decks")
    cards = relationship("Card", back_populates="deck", cascade="all, delete-orphan")

class Card(Base):
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id"), nullable=False)
    concept = Column(String, nullable=False)  # The term/word to define
    definition = Column(Text, nullable=False)  # The correct definition
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    deck = relationship("Deck", back_populates="cards")
    user_progress = relationship("UserCardProgress", back_populates="card", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="card", cascade="all, delete-orphan")

class UserCardProgress(Base):
    """Tracks user's progress on each card using spaced repetition"""
    __tablename__ = "user_card_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    
    # Spaced repetition fields
    ease_factor = Column(Float, default=2.5)  # SM-2 algorithm ease factor
    interval = Column(Integer, default=0)  # Days until next review
    repetitions = Column(Integer, default=0)  # Number of successful repetitions
    next_review = Column(DateTime(timezone=True), nullable=True)  # When to review next
    last_reviewed = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="card_progress")
    card = relationship("Card", back_populates="user_progress")

class Review(Base):
    """Stores history of review attempts"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Review data
    user_answer = Column(Text, nullable=False)  # Transcribed answer
    similarity_score = Column(Float, nullable=False)  # 0.0 to 1.0
    quality = Column(Integer, nullable=False)  # 0=Again, 1=Hard, 2=Normal, 3=Easy
    
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    card = relationship("Card", back_populates="reviews")
