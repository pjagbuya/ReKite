from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Deck Schemas
class DeckBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

class DeckCreate(DeckBase):
    pass

class DeckUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None

class DeckResponse(DeckBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    card_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

# Card Schemas
class CardBase(BaseModel):
    concept: str = Field(..., min_length=1, max_length=200)
    definition: str = Field(..., min_length=1)

class CardCreate(CardBase):
    deck_id: int

class CardUpdate(BaseModel):
    concept: Optional[str] = Field(None, min_length=1, max_length=200)
    definition: Optional[str] = Field(None, min_length=1)

class CardResponse(CardBase):
    id: int
    deck_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    next_review: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Review Schemas
class ReviewSubmit(BaseModel):
    card_id: int
    user_answer: str
    quality: int = Field(..., ge=0, le=3)  # 0=Again, 1=Hard, 2=Normal, 3=Easy

class ReviewResponse(BaseModel):
    id: int
    card_id: int
    similarity_score: float
    quality: int
    matched_keywords: List[str]
    reviewed_at: datetime
    
    class Config:
        from_attributes = True

# Transcription Schemas
class TranscriptionRequest(BaseModel):
    audio_base64: str  # Base64 encoded audio

class TranscriptionResponse(BaseModel):
    transcript: str
    confidence: Optional[float] = None

# Similarity Evaluation Schemas
class SimilarityRequest(BaseModel):
    user_answer: str
    correct_definition: str

class SimilarityResponse(BaseModel):
    similarity_score: float
    matched_keywords: List[str]
    highlighted_user_answer: str
    highlighted_definition: str

# Study Session Schemas
class NextCardResponse(BaseModel):
    card: Optional[CardResponse] = None
    deck_name: str
    cards_remaining: int
    
    class Config:
        from_attributes = True
